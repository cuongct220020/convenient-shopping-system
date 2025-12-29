import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { Camera, Search, Check, X } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { UserCardProps, UserCard } from '../../../components/UserCard';

// 1. Define a Mock User to simulate the database found result
const MOCK_DB_USER = {
  id: 'user-hung-123',
  name: 'Bùi Mạnh Hưng',
  role: 'Thành viên',
  email: 'hungdeptrai@gmail.com',
};

type GroupData = {
  id: string;
  name: string;
  members: Array<{ id: string; name: string; role: string; email?: string }>;
};

const EditGroup: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const groupToEdit = location.state?.group as GroupData;

  if (!groupToEdit || !id) {
    navigate('/main/family-group');
    return null;
  }

  // --- State Management ---
  const [groupName, setGroupName] = useState(groupToEdit.name);
  const [memberSearch, setMemberSearch] = useState('');

  // Search states
  const [searchResult, setSearchResult] = useState<typeof MOCK_DB_USER | null>(null);
  const [showNotFound, setShowNotFound] = useState(false);

  // Selected members list (Initialized with existing members)
  const [selectedMembers, setSelectedMembers] = useState<UserCardProps[]>(
    groupToEdit.members.map(m => ({
      id: m.id,
      name: m.name,
      role: m.role,
      email: m.email,
      isRemovable: m.role !== 'Trưởng nhóm',
    }))
  );

  // --- Search Logic (Debounced) ---
  useEffect(() => {
    // 300ms delay to simulate network request and avoid flickering
    const delayDebounceFn = setTimeout(() => {
      if (!memberSearch.trim()) {
        setSearchResult(null);
        setShowNotFound(false);
        return;
      }

      // Check if this user is already added to the list
      const isAlreadyAdded = selectedMembers.some(
        (m) => m.email === memberSearch || (memberSearch === MOCK_DB_USER.email && m.email === MOCK_DB_USER.email)
      );

      if (isAlreadyAdded) {
        setSearchResult(null);
        setShowNotFound(true); // Treat already added as "not found" for adding purposes
        return;
      }

      // Simulate finding the specific user from the screenshot
      if (memberSearch === 'hungdeptrai@gmail.com') {
        setSearchResult(MOCK_DB_USER);
        setShowNotFound(false);
      } else {
        setSearchResult(null);
        setShowNotFound(true);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [memberSearch, selectedMembers]);

  // --- Handlers ---
  const handleAddMember = (user: typeof MOCK_DB_USER) => {
    const newUser: UserCardProps = {
      id: user.id,
      name: user.name,
      role: user.role,
      email: user.email,
      isRemovable: true,
    };

    setSelectedMembers((prev) => [...prev, newUser]);
    setMemberSearch(''); // Clear search input
    setSearchResult(null); // Clear result
  };

  const handleRemoveMember = (id: string | number) => {
    setSelectedMembers((prev) => prev.filter((member) => member.id !== id));
  };

  const handleSubmit = () => {
    navigate(`/main/family-group/${id}`);
  };

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

          {/* --- UI State: Not Found --- */}
          {showNotFound && (
            <div className="flex flex-col items-center justify-center py-6 text-gray-400">
              <Search size={24} className="mb-2 opacity-50" />
              <p className="text-sm font-medium">
                Không tồn tại tài khoản với email trên
              </p>
            </div>
          )}

          {/* --- UI State: Found Result (Add Candidate) --- */}
          {searchResult && (
            <div className="mt-4 animate-in fade-in slide-in-from-top-2">
              <UserCard
                id={searchResult.id}
                name={searchResult.name}
                role={searchResult.role}
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
        <Button
          variant="primary"
          onClick={handleSubmit}
          size="fit"
          icon={Check}
        >
          Lưu thay đổi
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
