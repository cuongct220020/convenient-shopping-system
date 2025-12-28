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

// Mock data based on the image
const mockMemberData = {
  id: 'u2',
  name: 'Bùi Mạnh Hưng',
  avatarUrl: null, // Placeholder
  gender: 'Nam',
  age: 21,
  dob: '01/01/2000',
  phone: '0123456789',
  email: 'hungdeptrai@gmail.com',
  address: 'Số xx, Ngõ xx, Phường xx xx, Hà Nội',
  occupation: 'Sinh viên',
};

// Mock group data to check current user's role
const mockGroupData = {
  currentUserRole: 'Trưởng nhóm', // Change to 'Thành viên' to test non-leader view
};

type TabType = 'personal-info' | 'health-profile' | 'favorite-dishes';

const MemberDetail = () => {
  const navigate = useNavigate();
  const { id, userId } = useParams();
  const [activeTab, setActiveTab] = useState<TabType>('personal-info');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Check if current user is the leader
  const isHeadChef = mockGroupData.currentUserRole === 'Trưởng nhóm';

  // State for the Set Leader Modal
  const [isSetLeaderModalOpen, setIsSetLeaderModalOpen] = useState(false);

  // State for the Remove Member Modal
  const [isRemoveMemberModalOpen, setIsRemoveMemberModalOpen] = useState(false);

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

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);

  // Close popover when clicking outside
  const handleBackdropClick = () => {
    // Don't close anything if any modal is open
    if (isSetLeaderModalOpen || isRemoveMemberModalOpen) return;

    if (isSettingsOpen) setIsSettingsOpen(false);
  };

  const handleSetLeader = () => {
    // Perform set leader API logic here
    console.log('Setting member as leader:', mockMemberData.name);
    setIsSetLeaderModalOpen(false);
    setIsSettingsOpen(false);
  };

  const handleRemoveMember = () => {
    // Perform remove member API logic here
    console.log('Removing member:', mockMemberData.name);
    setIsRemoveMemberModalOpen(false);
    setIsSettingsOpen(false);
    navigate(`/main/family-group/${id}`);
  };

  // Placeholder actions for settings menu
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSettingsOpen(false);
    setIsSetLeaderModalOpen(true);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSettingsOpen(false);
    setIsRemoveMemberModalOpen(true);
  };

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
        <div className="w-24 h-24 bg-gray-200 rounded-full mb-4"></div>
        <h2 className="text-2xl font-bold">{mockMemberData.name}</h2>
        <div className="flex items-center text-sm text-gray-600 mt-2">
          <User size={16} className="mr-1" />
          <span>{mockMemberData.gender} • {mockMemberData.age} tuổi</span>
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
        <button
          className={`px-6 py-3 text-center font-bold text-sm whitespace-nowrap ${
            activeTab === 'favorite-dishes'
              ? 'text-gray-900 border-b-2 border-[#C3485C]'
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('favorite-dishes')}
        >
          Món ăn yêu thích
        </button>
      </div>

      {/* Tab Content */}
      <div className="px-4 py-4">
        {activeTab === 'personal-info' && (
          <div className="space-y-4 text-sm">
            <InfoRow label="Ngày sinh" value={mockMemberData.dob} />
            <InfoRow label="Số điện thoại" value={mockMemberData.phone} />
            <InfoRow label="Email" value={mockMemberData.email} />
            <InfoRow label="Địa chỉ" value={mockMemberData.address} />
            <InfoRow label="Nghề nghiệp" value={mockMemberData.occupation} />
          </div>
        )}
        {activeTab === 'health-profile' && (
          <div className="text-center text-gray-500 py-8">
            <p>Chưa có thông tin sức khỏe.</p>
          </div>
        )}
        {activeTab === 'favorite-dishes' && (
          <div className="text-center text-gray-500 py-8">
            <p>Chưa có món ăn yêu thích.</p>
          </div>
        )}
      </div>

      {/* SET LEADER CONFIRMATION MODAL */}
      {isSetLeaderModalOpen && (
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
              Bạn có chắc muốn chuyển quyền trưởng nhóm cho <span className="text-[#C3485C] font-semibold">{mockMemberData.name}</span>?
            </p>

            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                 <Button
                  variant="primary"
                  onClick={handleSetLeader}
                  icon={Shield}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  Xác nhận
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => setIsSetLeaderModalOpen(false)}
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
      {isRemoveMemberModalOpen && (
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
              Bạn có chắc muốn xóa <span className="text-[#C3485C] font-semibold">{mockMemberData.name}</span> khỏi nhóm?
            </p>

            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                 <Button
                  variant="primary"
                  onClick={handleRemoveMember}
                  icon={LogOut}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  Xóa
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => setIsRemoveMemberModalOpen(false)}
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

export default MemberDetail;