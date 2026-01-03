import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { Camera, Search, Check, X } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { UserCardProps, UserCard } from '../../../components/UserCard';
import { groupService } from '../../../services/group';
import { userService } from '../../../services/user';
import type { UserCoreInfo, GroupMembership } from '../../../services/schema/groupSchema';

// Helper function to get display name from user
function getDisplayName(user: UserCoreInfo | null): string {
  if (!user) return 'Người dùng';
  if (user.first_name && user.last_name) {
    return `${user.last_name} ${user.first_name}`;
  }
  if (user.first_name) return user.first_name;
  if (user.last_name) return user.last_name;
  return user.username || 'Người dùng';
}

// Helper function to map backend role to UI role
function mapRoleToUI(role: 'head_chef' | 'member'): 'Trưởng nhóm' | 'Thành viên' {
  return role === 'head_chef' ? 'Trưởng nhóm' : 'Thành viên';
}

type GroupData = {
  id: string;
  name: string;
  members: Array<{ id: string; name: string; role: string; email?: string }>;
  currentUserRole: 'head_chef' | 'member';
  currentUserId: string | null;
};

const EditGroup: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const groupToEdit = location.state?.group as GroupData;

  // For fetching group detail if not passed via location state
  const [fetchedGroupData, setFetchedGroupData] = useState<GroupData | null>(null);
  const [isLoadingGroup, setIsLoadingGroup] = useState(!groupToEdit);
  const [groupError, setGroupError] = useState<string | null>(null);

  // Use either passed group data or fetched data
  const currentGroupData = groupToEdit || fetchedGroupData;

  if (!id || (!currentGroupData && !isLoadingGroup)) {
    navigate('/main/family-group');
    return null;
  }

  // --- State Management ---
  const [groupName, setGroupName] = useState(currentGroupData?.name || '');
  const [memberSearch, setMemberSearch] = useState('');

  // Loading and error states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // Search states
  const [searchResult, setSearchResult] = useState<UserCoreInfo | null>(null);
  const [showNotFound, setShowNotFound] = useState(false);

  // Selected members list
  const [selectedMembers, setSelectedMembers] = useState<UserCardProps[]>(
    currentGroupData?.members.map(m => ({
      id: m.id,
      name: m.name,
      role: m.role,
      email: m.email,
      isRemovable: m.role !== 'Trưởng nhóm' && m.id !== 'user-me',
    })) || []
  );

  // Fetch group detail if not provided
  useEffect(() => {
    if (!groupToEdit && id) {
      const fetchGroup = async () => {
        setIsLoadingGroup(true);
        setGroupError(null);

        // Fetch current user to get ID
        const currentUserResult = await userService.getCurrentUser();
        const currentUserId = currentUserResult.isOk() ? currentUserResult.value.data.id : null;

        // Fetch group detail
        const groupResult = await groupService.getGroupById(id);

        groupResult.match(
          (response) => {
            const group = response.data;
            const memberships = group.group_memberships || [];

            // Find current user's role
            const currentUserMembership = memberships.find(
              (m: GroupMembership) => m.user.id === currentUserId
            );
            const currentUserRole = currentUserMembership?.role || 'member';

            // Map members to display format
            const members = memberships.map((membership: GroupMembership) => ({
              id: membership.user.id,
              name: getDisplayName(membership.user),
              role: mapRoleToUI(membership.role),
              email: membership.user.email
            }));

            setFetchedGroupData({
              id: group.id,
              name: group.group_name,
              members,
              currentUserRole,
              currentUserId
            });
            setGroupName(group.group_name);
          },
          (err) => {
            console.error('Failed to fetch group detail:', err);
            if (err.type === 'unauthorized') {
              setGroupError('Bạn cần đăng nhập để xem nhóm');
            } else if (err.type === 'not-found') {
              setGroupError('Không tìm thấy nhóm');
            } else {
              setGroupError('Không thể tải thông tin nhóm');
            }
          }
        );

        setIsLoadingGroup(false);
      };

      fetchGroup();
    }
  }, [groupToEdit, id]);

  // --- Search Logic (Debounced) ---
  useEffect(() => {
    // 300ms delay to simulate network request and avoid flickering
    const delayDebounceFn = setTimeout(async () => {
      if (!memberSearch.trim()) {
        setSearchResult(null);
        setShowNotFound(false);
        return;
      }

      // Check if this user is already added to the list
      const isAlreadyAdded = selectedMembers.some(
        (m) => m.email === memberSearch
      );

      if (isAlreadyAdded) {
        setSearchResult(null);
        setShowNotFound(true);
        return;
      }

      // Search for user by email
      setIsSearching(true);
      const result = await userService.searchUsersByEmail(memberSearch.trim());

      result.match(
        (response) => {
          if (response.data.user) {
            setSearchResult(response.data.user);
            setShowNotFound(false);
          } else {
            setSearchResult(null);
            setShowNotFound(true);
          }
        },
        () => {
          // If search endpoint doesn't exist, fall back to mock search
          // TODO: Remove this when backend implements user search endpoint
          console.log('User search not available, using mock data');
          if (memberSearch === 'hungdeptrai@gmail.com') {
            setSearchResult({
              id: 'user-hung-123',
              username: 'hungbm',
              email: 'hungdeptrai@gmail.com',
              phone_num: '0123456789',
              first_name: 'Mạnh Hưng',
              last_name: 'Bùi',
              avatar_url: null
            });
            setShowNotFound(false);
          } else {
            setSearchResult(null);
            setShowNotFound(true);
          }
        }
      );

      setIsSearching(false);
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [memberSearch, selectedMembers]);

  // --- Handlers ---
  const handleAddMember = (user: UserCoreInfo) => {
    const newUser: UserCardProps = {
      id: user.id,
      name: getDisplayName(user),
      role: 'Thành viên',
      email: user.email,
      isRemovable: true,
    };

    setSelectedMembers((prev) => [...prev, newUser]);
    setMemberSearch(''); // Clear search input
    setSearchResult(null); // Clear result
    setShowNotFound(false);
  };

  const handleRemoveMember = (id: string | number) => {
    setSelectedMembers((prev) => prev.filter((member) => member.id !== id));
  };

  const handleSubmit = async () => {
    if (!id) return;

    // Validate group name
    if (!groupName.trim()) {
      setSubmitError('Vui lòng nhập tên nhóm');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    const result = await groupService.updateGroup(id, groupName.trim());

    result.match(
      async () => {
        // Successfully updated group name, now update members
        // Get current members from the group
        const groupResult = await groupService.getGroupById(id);

        if (groupResult.isOk()) {
          const existingMemberIds = new Set(
            groupResult.value.data.group_memberships?.map(m => m.user.id) || []
          );

          const selectedMemberIds = selectedMembers
            .filter(m => m.id !== 'user-me')
            .map(m => m.id as string);

          // Add new members
          const membersToAdd = selectedMemberIds.filter(id => !existingMemberIds.has(id));
          // Remove members
          const membersToRemove = Array.from(existingMemberIds).filter(id => !selectedMemberIds.includes(id));

          // Execute all add/remove operations in parallel
          const addPromises = membersToAdd.map(userId =>
            groupService.addMember(id, userId)
          );
          const removePromises = membersToRemove.map(userId =>
            groupService.removeMember(id, userId)
          );

          await Promise.allSettled([...addPromises, ...removePromises]);
        }

        // Success - navigate back to detail view
        navigate(`/main/family-group/${id}`);
      },
      (error) => {
        console.error('Failed to update group:', error);
        if (error.type === 'unauthorized') {
          setSubmitError('Bạn cần đăng nhập để chỉnh sửa nhóm');
        } else if (error.type === 'not-found') {
          setSubmitError('Không tìm thấy nhóm');
        } else if (error.type === 'validation-error') {
          setSubmitError('Dữ liệu không hợp lệ');
        } else if (error.type === 'network-error') {
          setSubmitError('Lỗi kết nối mạng');
        } else {
          setSubmitError('Không thể cập nhật nhóm');
        }
      }
    );

    setIsSubmitting(false);
  };

  // Loading state
  if (isLoadingGroup) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C3485C]"></div>
        <p className="text-gray-600 mt-4">Đang tải...</p>
      </div>
    );
  }

  // Error state
  if (groupError) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <p className="text-red-500 mb-4">{groupError}</p>
        <Button
          variant="primary"
          size="fit"
          onClick={() => navigate('/main/family-group')}
        >
          Quay lại
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6 pb-24 relative">
      {/* 1. Header */}
      <div className="relative mb-6 flex items-center">
        <BackButton
          text="Quay lại"
          to={`/main/family-group/${id}`}
          className="absolute left-0"
        />
      </div>
      <h1 className="text-xl font-bold text-[#C3485C] text-center">
        Chỉnh Sửa Nhóm
      </h1>

      {/* 2. Group Image Upload */}
      <div className="flex flex-col items-center mb-8">
        <div className="relative">
          <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center">
            {/* Placeholder for avatar */}
          </div>
          <button className="absolute bottom-0 right-0 bg-gray-200 p-2 rounded-full text-gray-600 hover:bg-gray-300 transition-colors border-2 border-white">
            <Camera size={20} />
          </button>
        </div>
        <p className="text-sm font-medium text-gray-700 mt-3">
          Tải ảnh nhóm lên
        </p>
      </div>

      {/* 3. Form Fields */}
      <div className="space-y-6">
        <InputField
          label="Tên nhóm gia đình"
          labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
          placeholder="Ví dụ: Gia đình haha"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
        />

        {/* Member Search Section */}
        <div className="relative">
          <InputField
            label="Thêm thành viên"
            labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
            placeholder="Ví dụ: hungdeptrai@gmail.com"
            icon={<Search size={20} />}
            value={memberSearch}
            onChange={(e) => setMemberSearch(e.target.value)}
          />

          {/* --- UI State: Searching --- */}
          {isSearching && (
            <div className="flex flex-col items-center justify-center py-6 text-gray-400">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
              <p className="text-sm font-medium mt-2">
                Đang tìm kiếm...
              </p>
            </div>
          )}

          {/* --- UI State: Not Found --- */}
          {!isSearching && showNotFound && (
            <div className="flex flex-col items-center justify-center py-6 text-gray-400">
              <Search size={24} className="mb-2 opacity-50" />
              <p className="text-sm font-medium">
                Không tồn tại tài khoản với email trên
              </p>
            </div>
          )}

          {/* --- UI State: Found Result (Add Candidate) --- */}
          {!isSearching && searchResult && (
            <div className="mt-4 animate-in fade-in slide-in-from-top-2">
              <UserCard
                id={searchResult.id}
                name={getDisplayName(searchResult)}
                role="Thành viên"
                email={searchResult.email}
                variant="candidate"
                onAdd={() => handleAddMember(searchResult)}
              />
            </div>
          )}
        </div>
      </div>

      {/* 4. Selected Members List */}
      <div className="mt-8">
        <h2 className="text-sm font-bold text-gray-700 mb-4 uppercase">
          THÀNH VIÊN ĐÃ CHỌN ({selectedMembers.length})
        </h2>
        <div className="flex flex-col gap-3">
          {selectedMembers.map((member) => (
            <UserCard
              key={member.id}
              {...member}
              onRemove={handleRemoveMember}
            />
          ))}
        </div>
      </div>

      {/* 5. Submit Buttons */}
      <div className="mt-10 flex gap-0">
        {submitError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg w-full">
            <p className="text-red-600 text-sm">{submitError}</p>
          </div>
        )}
        <Button
          variant={isSubmitting ? 'disabled' : 'primary'}
          onClick={handleSubmit}
          size="fit"
          icon={Check}
        >
          {isSubmitting ? 'Đang lưu...' : 'Lưu thay đổi'}
        </Button>
        <Button
          variant="secondary"
          onClick={() => navigate(`/main/family-group/${id}`)}
          size="fit"
          icon={X}
        >
          Hủy
        </Button>
      </div>
    </div>
  );
};

export default EditGroup;
