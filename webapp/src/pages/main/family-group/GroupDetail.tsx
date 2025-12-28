import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Settings,
  Users,
  ChefHat,
  UserPlus,
  MoreVertical,
  Edit2,
  Trash2,
  User,
  Shield,
  LogOut,
  AlertTriangle,
  X, // Added for the cancel button
} from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { UserCard } from '../../../components/UserCard';

// Mock data for the group and its members
const mockGroupData = {
  id: 'g1',
  name: 'Gia đình haha',
  memberCount: 4,
  adminName: 'Bùi Mạnh Hưng',
  members: [
    {
      id: 'u1',
      name: 'Bạn (Tôi)',
      role: 'Trưởng nhóm',
      isCurrentUser: false,
    },
    {
      id: 'u2',
      name: 'Bùi Mạnh Hưng',
      role: 'Thành viên',
      email: 'hungdeeptry@gmail.com',
      isCurrentUser: false,
    },
    // Add more members as needed for testing
  ],
};

type TabType = 'members' | 'shopping-plan';

const GroupDetail = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('members');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [openMemberMenuId, setOpenMemberMenuId] = useState<string | null>(null);
  
  // State for the Delete Confirmation Modal
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // State for the Set Leader Modal
  const [isSetLeaderModalOpen, setIsSetLeaderModalOpen] = useState(false);
  const [selectedMemberForLeader, setSelectedMemberForLeader] = useState<typeof mockGroupData.members[0] | null>(null);

  // State for the Remove Member Modal
  const [isRemoveMemberModalOpen, setIsRemoveMemberModalOpen] = useState(false);
  const [selectedMemberForRemoval, setSelectedMemberForRemoval] = useState<typeof mockGroupData.members[0] | null>(null);

  // State for the Leave Group Modal
  const [isLeaveGroupModalOpen, setIsLeaveGroupModalOpen] = useState(false);

  // Add blur effect to bottom nav when modal is open
  useEffect(() => {
    const bottomNav = document.querySelector('nav.fixed.bottom-0');
    if (bottomNav) {
      if (isDeleteModalOpen || isSetLeaderModalOpen || isRemoveMemberModalOpen || isLeaveGroupModalOpen) {
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
  }, [isDeleteModalOpen, isSetLeaderModalOpen, isRemoveMemberModalOpen, isLeaveGroupModalOpen]);

  // Check if current user is the head chef
  const currentUser = mockGroupData.members.find(m => m.isCurrentUser);
  const isHeadChef = currentUser?.role === 'Trưởng nhóm';

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);
  const toggleMemberMenu = (id: string) => {
    setOpenMemberMenuId(openMemberMenuId === id ? null : id);
  };

  const handleEdit = () => {
    navigate('/main/family-group/add', {
      state: {
        group: {
          id: mockGroupData.id,
          name: mockGroupData.name,
          members: mockGroupData.members.map(m => ({
            id: m.id,
            name: m.name,
            role: m.role,
            email: m.email,
          })),
        },
      },
    });
    setIsSettingsOpen(false);
  };

  const handleDeleteGroup = () => {
    // Perform delete API logic here
    console.log("Deleting group...");
    setIsDeleteModalOpen(false);
    navigate('/main/family-group');
  };

  const handleSetLeader = () => {
    // Perform set leader API logic here
    console.log("Setting member as leader:", selectedMemberForLeader?.name);
    setIsSetLeaderModalOpen(false);
    setSelectedMemberForLeader(null);
    setOpenMemberMenuId(null);
  };

  const handleRemoveMember = () => {
    // Perform remove member API logic here
    console.log("Removing member:", selectedMemberForRemoval?.name);
    setIsRemoveMemberModalOpen(false);
    setSelectedMemberForRemoval(null);
    setOpenMemberMenuId(null);
  };

  const handleLeaveGroup = () => {
    // Perform leave group API logic here
    console.log("Leaving group...");
    setIsLeaveGroupModalOpen(false);
    setIsSettingsOpen(false);
    navigate('/main/family-group');
  };

  // Close popovers when clicking outside
  const handleBackdropClick = () => {
    // Don't close anything if any modal is open
    if (isDeleteModalOpen || isSetLeaderModalOpen || isRemoveMemberModalOpen || isLeaveGroupModalOpen) return;

    if (isSettingsOpen) setIsSettingsOpen(false);
    if (openMemberMenuId) setOpenMemberMenuId(null);
  };

  return (
    <div className="min-h-screen bg-white relative" onClick={handleBackdropClick}>
      {/* Header */}
      <div>
        <div className="flex items-center justify-between px-4 py-2">
          <BackButton to="/main/family-group" text="Quay lại" />
          <div className="relative">
            <button onClick={(e) => { e.stopPropagation(); toggleSettings(); }} className="p-2">
              <Settings size={24} className="text-gray-700" />
            </button>

            {/* Settings Popover */}
            {isSettingsOpen && (
              <div className="absolute right-0 top-full mt-2 w-32 bg-white rounded-lg shadow-lg z-10 border border-gray-200 py-1">
                {isHeadChef ? (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit();
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                    >
                      <Edit2 size={16} className="mr-2" />
                      Chỉnh sửa
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsSettingsOpen(false);
                        setIsDeleteModalOpen(true); // Open the modal
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center"
                    >
                      <Trash2 size={16} className="mr-2" />
                      Xóa nhóm
                    </button>
                  </>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsSettingsOpen(false);
                      setIsLeaveGroupModalOpen(true);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center"
                  >
                    <LogOut size={16} className="mr-2" />
                    Rời nhóm
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <h1 className="text-xl font-bold text-[#C3485C] text-center pb-2">
          Chi Tiết Nhóm
        </h1>
      </div>

      <div className="px-4 pb-4">
        {/* Group Info */}
        <div className="flex flex-col items-center mt-4">
          <div className="w-24 h-24 bg-gray-200 rounded-full mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-900">{mockGroupData.name}</h2>
          <div className="flex items-center text-sm text-gray-600 mt-2 space-x-4">
            <div className="flex items-center">
              <Users size={16} className="mr-1" />
              <span>{mockGroupData.memberCount} thành viên</span>
            </div>
            <div className="flex items-center">
              <ChefHat size={16} className="mr-1" />
              <span>{mockGroupData.adminName}</span>
            </div>
          </div>
          <Button
            variant="primary"
            size="fit"
            className="mt-6"
            icon={UserPlus}
            onClick={handleEdit}
          >
            Thêm thành viên
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex mt-8 border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center font-bold text-sm ${
              activeTab === 'members'
                ? 'text-gray-900 border-b-2 border-[#C3485C]'
                : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('members')}
          >
            Thành viên
          </button>
          <button
            className={`flex-1 py-3 text-center font-bold text-sm ${
              activeTab === 'shopping-plan'
                ? 'text-gray-900 border-b-2 border-[#C3485C]'
                : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('shopping-plan')}
          >
            Kế hoạch mua sắm
          </button>
        </div>

        {/* Tab Content */}
        <div className="mt-4">
          {activeTab === 'members' && (
            <div>
              <h3 className="text-gray-600 text-sm mb-4">
                Danh sách thành viên ({mockGroupData.members.length})
              </h3>
              <div className="space-y-3">
                {mockGroupData.members.map((member) => (
                  <UserCard
                    key={member.id}
                    id={member.id}
                    name={member.name}
                    role={member.role}
                    email={member.email}
                    variant="selected"
                    onClick={() => navigate(`/main/family-group/${mockGroupData.id}/${member.id}`)}
                    actionElement={
                      isHeadChef && !member.isCurrentUser && (
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleMemberMenu(member.id);
                            }}
                            className="p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors"
                          >
                            <MoreVertical size={20} />
                          </button>
                          {/* Member Menu Popover */}
                          {openMemberMenuId === member.id && (
                            <div className="absolute right-0 top-full mt-1 w-52 bg-white rounded-lg shadow-lg z-10 border border-gray-200 py-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/main/family-group/${mockGroupData.id}/${member.id}`);
                                }}
                                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center font-medium"
                              >
                                <User size={16} className="mr-2" />
                                Xem thông tin
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedMemberForLeader(member);
                                  setIsSetLeaderModalOpen(true);
                                }}
                                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center font-medium"
                              >
                                <Shield size={16} className="mr-2" />
                                Đặt làm nhóm trưởng
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedMemberForRemoval(member);
                                  setIsRemoveMemberModalOpen(true);
                                }}
                                className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center font-medium"
                              >
                                <LogOut size={16} className="mr-2" />
                                Xóa khỏi nhóm
                              </button>
                            </div>
                          )}
                        </div>
                      )
                    }
                  />
                ))}
              </div>
            </div>
          )}
          {activeTab === 'shopping-plan' && (
            <div className="text-center text-gray-500 py-8">
              <p>Chưa có kế hoạch mua sắm nào.</p>
            </div>
          )}
        </div>
      </div>

      {/* DELETE CONFIRMATION MODAL */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div
            className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">
              Xóa Nhóm Gia Đình?
            </h3>

            <div className="flex justify-center mb-5">
              {/* Using fill to make the triangle solid red, text-white makes the '!' white */}
              <AlertTriangle
                size={64}
                className="text-white fill-[#C3485C]"
                strokeWidth={1.5}
              />
            </div>

            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">
              Hành động này <span className="text-[#C3485C] font-semibold">không thể hoàn tác</span>.
              Tất cả dữ liệu thành viên và kế hoạch mua sắm sẽ bị xóa vĩnh viễn.
            </p>

            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                 <Button
                  variant="primary"
                  onClick={handleDeleteGroup}
                  icon={Trash2}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  Xóa
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => setIsDeleteModalOpen(false)}
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
                  onClick={() => {
                    setIsSetLeaderModalOpen(false);
                    setSelectedMemberForLeader(null);
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
                  onClick={() => {
                    setIsRemoveMemberModalOpen(false);
                    setSelectedMemberForRemoval(null);
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

      {/* LEAVE GROUP CONFIRMATION MODAL */}
      {isLeaveGroupModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div
            className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">
              Rời Nhóm?
            </h3>

            <div className="flex justify-center mb-5">
              <LogOut
                size={64}
                className="text-[#C3485C]"
                strokeWidth={1.5}
              />
            </div>

            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">
              Bạn có chắc muốn rời khỏi nhóm <span className="text-[#C3485C] font-semibold">{mockGroupData.name}</span>?
            </p>

            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                 <Button
                  variant="primary"
                  onClick={handleLeaveGroup}
                  icon={LogOut}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  Rời nhóm
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => setIsLeaveGroupModalOpen(false)}
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

export default GroupDetail;