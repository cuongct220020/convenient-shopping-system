import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Settings,
  User,
  Shield,
  LogOut,
  AlertTriangle,
  X,
} from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { groupService } from '../../../services/group';
import { userService } from '../../../services/user';
import type { UserCoreInfo, UserIdentityProfile, UserHealthProfile } from '../../../services/schema/groupSchema';

// Default user avatar
const DEFAULT_USER_AVATAR = new URL('../../../assets/user.png', import.meta.url).href;

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

// Helper function to get gender display
function getGenderDisplay(gender: 'male' | 'female' | 'other' | null | undefined): string {
  if (!gender) return 'Chưa cập nhật';
  switch (gender) {
    case 'male': return 'Nam';
    case 'female': return 'Nữ';
    case 'other': return 'Khác';
    default: return 'Chưa cập nhật';
  }
}

// Helper function to calculate age from date of birth
function calculateAge(dateOfBirth: string | null | undefined): number | null {
  if (!dateOfBirth) return null;
  const dob = new Date(dateOfBirth);
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const monthDiff = today.getMonth() - dob.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  return age;
}

type TabType = 'personal-info' | 'health-profile' | 'favorite-dishes'; // 'favorite-dishes' is commented out

const UserDetail = () => {
  const navigate = useNavigate();
  const { id, userId } = useParams();
  const [activeTab, setActiveTab] = useState<TabType>('personal-info');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Data states
  const [userData, setUserData] = useState<{
    user: UserCoreInfo | null;
    identityProfile: UserIdentityProfile | null;
    healthProfile: UserHealthProfile | null;
    currentUserRole: 'head_chef' | 'member';
    currentUserId: string | null;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Set leader loading and error states
  const [isSettingLeader, setIsSettingLeader] = useState(false);
  const [setLeaderError, setSetLeaderError] = useState<string | null>(null);

  // Remove member loading and error states
  const [isRemovingMember, setIsRemovingMember] = useState(false);
  const [removeMemberError, setRemoveMemberError] = useState<string | null>(null);

  // Modal States
  const [isSetLeaderModalOpen, setIsSetLeaderModalOpen] = useState(false);
  const [isRemoveMemberModalOpen, setIsRemoveMemberModalOpen] = useState(false);

  // Selected member state for set leader
  type MemberType = {
    id: string;
    name: string;
  };
  const [selectedMemberForLeader, setSelectedMemberForLeader] = useState<MemberType | null>(null);
  const [selectedMemberForRemoval, setSelectedMemberForRemoval] = useState<MemberType | null>(null);

  // Fetch user data on mount
  useEffect(() => {
    const fetchData = async () => {
      if (!id || !userId) {
        setError('Không tìm thấy ID nhóm hoặc người dùng');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Fetch current user to check role
        const currentUserResult = await userService.getCurrentUser();

        // Fetch group members to get membership data
        const groupResult = await groupService.getGroupMembers(id);

        if (groupResult.isErr()) {
          throw groupResult.error;
        }

        const groupData = groupResult.value.data;
        // Check members first since group_memberships might be empty array (truthy in ||)
        const memberships = groupData.members || groupData.group_memberships || [];
        const creator = groupData.creator;

        const currentUserRole = memberships.find(
          (m) => m.user.id === (currentUserResult.isOk() ? currentUserResult.value.data.id : null)
        )?.role || 'member';

        // Get user info from group memberships or creator (for newly created groups)
        let user: UserCoreInfo | null = null;
        const member = memberships.find((m) => m.user.id === userId || m.user.user_id === userId);
        if (member) {
          // User is in group memberships
          user = member.user;
        } else if (creator && (creator.id === userId || creator.user_id === userId)) {
          // User is the creator/leader but not in memberships (newly created group)
          user = creator;
        } else {
          console.log('User not found in group. userId:', userId, 'Available members:', memberships.map(m => ({ id: m.user.id, user_id: m.user.user_id })), 'Creator:', creator?.id || creator?.user_id);
          const notFoundError = { type: 'not-found' } as const;
          throw notFoundError;
        }

        // Fetch identity profile using group-specific endpoint
        const identityResult = await groupService.getMemberIdentityProfile(id, userId);
        const identityProfile = identityResult.isOk() ? identityResult.value.data : null;

        // Fetch health profile using group-specific endpoint
        const healthResult = await groupService.getMemberHealthProfile(id, userId);
        const healthProfile = healthResult.isOk() ? healthResult.value.data : null;

        setUserData({
          user,
          identityProfile,
          healthProfile,
          currentUserRole,
          currentUserId: currentUserResult.isOk() ? currentUserResult.value.data.id : null
        });
      } catch (err) {
        console.error('Failed to fetch user data:', err);
        if (err && typeof err === 'object' && 'type' in err) {
          const error = err as { type: string };
          if (error.type === 'unauthorized') {
            setError('Bạn cần đăng nhập để xem thông tin');
          } else if (error.type === 'not-found') {
            setError('Không tìm thấy người dùng trong nhóm');
          } else {
            setError('Không thể tải thông tin người dùng');
          }
        } else {
          setError('Không thể tải thông tin người dùng');
        }
      }

      setIsLoading(false);
    };

    fetchData();
  }, [id, userId]);

  // Add blur effect to bottom nav when modal is open
  useEffect(() => {
    const bottomNav = document.querySelector('nav.fixed.bottom-0');
    if (bottomNav) {
      if (isSetLeaderModalOpen || isRemoveMemberModalOpen) {
        bottomNav.classList.add('blur-sm', 'pointer-events-none');
      } else {
        bottomNav.classList.remove('blur-sm', 'pointer-events-none');
      }
    }
    return () => {
      const nav = document.querySelector('nav.fixed.bottom-0');
      if (nav) {
        nav.classList.remove('blur-sm', 'pointer-events-none');
      }
    };
  }, [isSetLeaderModalOpen, isRemoveMemberModalOpen]);

  const isHeadChef = userData?.currentUserRole === 'head_chef';

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);

  // Close popover when clicking outside
  const handleBackdropClick = () => {
    // Don't close anything if any modal is open
    if (isSetLeaderModalOpen || isRemoveMemberModalOpen) return;

    if (isSettingsOpen) setIsSettingsOpen(false);
  };

  const handleSetLeader = async () => {
    if (!id || !selectedMemberForLeader || !userData?.currentUserId) return;

    setIsSettingLeader(true);
    setSetLeaderError(null);

    // Transfer leadership by making requests sequentially
    // (not in parallel to avoid race conditions)
    const currentLeaderId = userData.currentUserId;
    const targetMemberId = selectedMemberForLeader.id;

    // First, set the target member as head_chef
    const firstResult = await groupService.updateMemberRole(
      id,
      targetMemberId,
      'head_chef'
    );

    firstResult.match(
      async () => {
        // Then, set the current leader as member
        const secondResult = await groupService.updateMemberRole(
          id,
          currentLeaderId,
          'member'
        );

        secondResult.match(
          () => {
            setIsSetLeaderModalOpen(false);
            setSelectedMemberForLeader(null);
            setIsSettingsOpen(false);
            // Navigate back to group detail
            navigate(`/main/family-group/${id}`);
          },
          (error) => {
            console.error('Failed to demote current leader:', error);
            if (error.type === 'unauthorized') {
              setSetLeaderError('Bạn cần đăng nhập để thực hiện thao tác này');
            } else if (error.type === 'not-found') {
              setSetLeaderError('Không tìm thấy nhóm');
            } else if (error.type === 'forbidden') {
              setSetLeaderError('Bạn không có quyền thực hiện thao tác này');
            } else {
              setSetLeaderError('Không thể đặt làm trưởng nhóm');
            }
          }
        );
      },
      (error) => {
        console.error('Failed to set leader:', error);
        if (error.type === 'unauthorized') {
          setSetLeaderError('Bạn cần đăng nhập để thực hiện thao tác này');
        } else if (error.type === 'not-found') {
          setSetLeaderError('Không tìm thấy nhóm');
        } else if (error.type === 'forbidden') {
          setSetLeaderError('Bạn không có quyền thực hiện thao tác này');
        } else {
          setSetLeaderError('Không thể đặt làm trưởng nhóm');
        }
      }
    );

    setIsSettingLeader(false);
  };

  const handleRemoveMember = async () => {
    if (!id || !selectedMemberForRemoval || !userData) return;

    // Only head_chef can remove members
    if (userData?.currentUserRole !== 'head_chef') {
      setRemoveMemberError('Chỉ trưởng nhóm mới có quyền xóa thành viên');
      return;
    }

    setIsRemovingMember(true);
    setRemoveMemberError(null);

    const result = await groupService.removeMember(id, selectedMemberForRemoval.id);

    result.match(
      () => {
        setIsRemoveMemberModalOpen(false);
        setSelectedMemberForRemoval(null);
        setIsSettingsOpen(false);
        navigate(`/main/family-group/${id}`);
      },
      (error) => {
        console.error('Failed to remove member:', error);
        if (error.type === 'unauthorized') {
          setRemoveMemberError('Bạn cần đăng nhập để thực hiện thao tác này');
        } else if (error.type === 'not-found') {
          setRemoveMemberError('Không tìm thấy nhóm');
        } else if (error.type === 'forbidden') {
          setRemoveMemberError('Bạn không có quyền thực hiện thao tác này');
        } else {
          setRemoveMemberError('Không thể xóa thành viên');
        }
      }
    );

    setIsRemovingMember(false);
  };

  // Placeholder actions for settings menu
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSettingsOpen(false);
    setSelectedMemberForLeader({ id: userId!, name: displayName });
    setIsSetLeaderModalOpen(true);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSettingsOpen(false);
    setSelectedMemberForRemoval({ id: userId!, name: displayName });
    setIsRemoveMemberModalOpen(true);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C3485C]"></div>
        <p className="text-gray-600 mt-4">Đang tải...</p>
      </div>
    );
  }

  // Error state
  if (error || !userData) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <p className="text-red-500 mb-4">{error || 'Không thể tải thông tin người dùng'}</p>
        <Button
          variant="primary"
          size="fit"
          onClick={() => navigate(`/main/family-group/${id}`)}
        >
          Quay lại
        </Button>
      </div>
    );
  }

  const { user, identityProfile, healthProfile } = userData;
  const displayName = getDisplayName(user);
  const gender = getGenderDisplay(identityProfile?.gender);
  const age = calculateAge(identityProfile?.date_of_birth);
  const dob = identityProfile?.date_of_birth
    ? new Date(identityProfile.date_of_birth).toLocaleDateString('vi-VN')
    : 'Chưa cập nhật';

  return (
    <div className="min-h-screen bg-white text-gray-900" onClick={handleBackdropClick}>
      {/* Header */}
      <div>
        <div className="flex items-center justify-between px-4 py-2">
          <BackButton to={`/main/family-group/${id}`} text="Quay lại" />
          {isHeadChef && (
            <div className="relative">
              <button onClick={(e) => { e.stopPropagation(); toggleSettings(); }} className="p-2">
                <Settings size={24} className="text-gray-700" />
              </button>

              {/* Settings Popover */}
              {isSettingsOpen && (
                <div className="absolute right-0 top-full mt-2 w-52 bg-white rounded-lg shadow-lg z-10 border border-gray-200 py-1">
                  <button
                    onClick={handleEdit}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <Shield size={16} className="mr-2" />
                    Đặt làm nhóm trưởng
                  </button>
                  <button
                    onClick={handleDelete}
                    className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center"
                  >
                    <LogOut size={16} className="mr-2" />
                    Xóa khỏi nhóm
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <h1 className="text-xl font-bold text-[#C3485C] text-center pb-4">
          Thông tin thành viên
        </h1>
      </div>

      {/* Profile Summary */}
      <div className="flex flex-col items-center mt-4 px-4">
        <img
          src={user?.avatar_url || DEFAULT_USER_AVATAR}
          alt={displayName}
          className="w-24 h-24 rounded-full object-cover mb-4"
        />
        <h2 className="text-2xl font-bold">{displayName}</h2>
        <div className="flex items-center text-sm text-gray-600 mt-2">
          <User size={16} className="mr-1" />
          <span>{gender} • {age !== null ? `${age} tuổi` : 'Chưa cập nhật'}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex mt-8 border-b border-gray-200 px-4 overflow-x-auto flex-nowrap">
        <button
          className={`px-6 py-3 text-center font-bold text-sm whitespace-nowrap ${
            activeTab === 'personal-info'
              ? 'text-gray-900 border-b-2 border-[#C3485C]'
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('personal-info')}
        >
          Thông tin cá nhân
        </button>
        <button
          className={`px-6 py-3 text-center font-bold text-sm whitespace-nowrap ${
            activeTab === 'health-profile'
              ? 'text-gray-900 border-b-2 border-[#C3485C]'
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('health-profile')}
        >
          Hồ sơ sức khỏe
        </button>
        {/* <button
          className={`px-6 py-3 text-center font-bold text-sm whitespace-nowrap ${
            activeTab === 'favorite-dishes'
              ? 'text-gray-900 border-b-2 border-[#C3485C]'
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('favorite-dishes')}
        >
          Món ăn yêu thích
        </button> */}
      </div>

      {/* Tab Content */}
      <div className="px-4 py-4">
        {activeTab === 'personal-info' && (
          <div className="space-y-4 text-sm">
            <InfoRow label="Ngày sinh" value={dob} />
            <InfoRow label="Số điện thoại" value={user?.phone_num || 'Chưa cập nhật'} />
            <InfoRow label="Email" value={user?.email || 'Chưa cập nhật'} />
            <InfoRow
              label="Địa chỉ"
              value={
                identityProfile?.address
                  ? `${identityProfile.address.ward || ''}, ${identityProfile.address.district || ''}, ${identityProfile.address.city || ''}, ${identityProfile.address.province || ''}`.replace(/^,\s*,\s*/g, '').replace(/,\s*,/g, ',') || 'Chưa cập nhật'
                  : 'Chưa cập nhật'
              }
            />
            <InfoRow label="Nghề nghiệp" value={identityProfile?.occupation || 'Chưa cập nhật'} />
          </div>
        )}
        {activeTab === 'health-profile' && (
          <div className="space-y-4 text-sm">
            <InfoRow label="Chiều cao" value={healthProfile?.height_cm ? `${healthProfile.height_cm} cm` : 'Chưa cập nhật'} />
            <InfoRow label="Cân nặng" value={healthProfile?.weight_kg ? `${healthProfile.weight_kg} kg` : 'Chưa cập nhật'} />
            <InfoRow label="Mức độ hoạt động" value={
              healthProfile?.activity_level
                ? {
                    sedentary: 'Ít vận động',
                    light: 'Nhẹ nhàng',
                    moderate: 'Vừa phải',
                    active: 'Năng động',
                    very_active: 'Rất năng động'
                  }[healthProfile.activity_level]
                : 'Chưa cập nhật'
            } />
            <InfoRow label="Tình trạng hiện tại" value={
              healthProfile?.curr_condition
                ? {
                    normal: 'Bình thường',
                    pregnant: 'Mang thai',
                    injured: 'Chấn thương'
                  }[healthProfile.curr_condition]
                : 'Chưa cập nhật'
            } />
            <InfoRow label="Mục tiêu sức khỏe" value={
              healthProfile?.health_goal
                ? {
                    lose_weight: 'Giảm cân',
                    maintain: 'Duy trì',
                    gain_weight: 'Tăng cân'
                  }[healthProfile.health_goal]
                : 'Chưa cập nhật'
            } />
          </div>
        )}
        {/* {activeTab === 'favorite-dishes' && (
          <div className="text-center text-gray-500 py-8">
            <p>Chưa cập nhật</p>
          </div>
        )} */}
      </div>

      {/* SET LEADER CONFIRMATION MODAL */}
      {isSetLeaderModalOpen && selectedMemberForLeader && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div
            className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">
              Đặt Làm Trưởng Nhóm?
            </h3>

            <div className="flex justify-center mb-5">
              <Shield
                size={64}
                className="text-[#C3485C]"
                strokeWidth={1.5}
              />
            </div>

            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">
              Bạn có chắc muốn chuyển quyền trưởng nhóm cho <span className="text-[#C3485C] font-semibold">{selectedMemberForLeader.name}</span>?
            </p>

            {setLeaderError && (
              <p className="text-sm text-center text-red-600 mb-4">{setLeaderError}</p>
            )}

            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                 <Button
                  variant={isSettingLeader ? 'disabled' : 'primary'}
                  onClick={handleSetLeader}
                  icon={Shield}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  {isSettingLeader ? 'Đang lưu...' : 'Xác nhận'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant={isSettingLeader ? 'disabled' : 'secondary'}
                  onClick={() => {
                    setIsSetLeaderModalOpen(false);
                    setSelectedMemberForLeader(null);
                    setSetLeaderError(null);
                  }}
                  icon={X}
                  className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* REMOVE MEMBER CONFIRMATION MODAL */}
      {isRemoveMemberModalOpen && selectedMemberForRemoval && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div
            className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">
              Xóa Thành Viên?
            </h3>

            <div className="flex justify-center mb-5">
              <AlertTriangle
                size={64}
                className="text-white fill-[#C3485C]"
                strokeWidth={1.5}
              />
            </div>

            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">
              Bạn có chắc muốn xóa <span className="text-[#C3485C] font-semibold">{selectedMemberForRemoval.name}</span> khỏi nhóm?
            </p>

            {removeMemberError && (
              <p className="text-sm text-center text-red-600 mb-4">{removeMemberError}</p>
            )}

            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                 <Button
                  variant={isRemovingMember ? 'disabled' : 'primary'}
                  onClick={handleRemoveMember}
                  icon={LogOut}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  {isRemovingMember ? 'Đang xóa...' : 'Xóa'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant={isRemovingMember ? 'disabled' : 'secondary'}
                  onClick={() => {
                    setIsRemoveMemberModalOpen(false);
                    setSelectedMemberForRemoval(null);
                    setRemoveMemberError(null);
                  }}
                  icon={X}
                  className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper component for displaying information rows
const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex">
    <span className="font-bold w-1/3 flex-shrink-0">{label}</span>
    <span className="text-gray-700">{value}</span>
  </div>
);

export default UserDetail;
