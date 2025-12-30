import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
  X,
  Plus,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Clock,
  Circle
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
      isCurrentUser: true,
    },
    {
      id: 'u2',
      name: 'Bùi Mạnh Hưng',
      role: 'Thành viên',
      email: 'hungdeeptry@gmail.com',
      isCurrentUser: false,
    },
  ],
};

// Mock data for Shopping Plans (matching the image)
const mockShoppingPlans = [
  {
    id: 'p1',
    title: 'Mua đồ ăn tối',
    creator: 'Bùi Mạnh Hưng',
    ingredients: 3,
    cost: '500.000 VND',
    status: 'completed', // Đã xong
  },
  {
    id: 'p2',
    title: 'Mua đồ ăn tối',
    creator: 'Bùi Mạnh Hưng',
    ingredients: 3,
    cost: '500.000 VND',
    status: 'pending', // Đang chờ
  },
  {
    id: 'p3',
    title: 'Mua đồ ăn tối',
    creator: 'Bùi Mạnh Hưng',
    ingredients: 3,
    cost: '500.000 VND',
    status: 'in_progress', // Đang thực hiện
  },
  {
    id: 'p4',
    title: 'Mua đồ ăn tối',
    creator: 'Bùi Mạnh Hưng',
    ingredients: 3,
    cost: '500.000 VND',
    status: 'completed', // Đã xong
  },
];

type TabType = 'members' | 'shopping-plan';
type TimeFilterType = 'today' | 'week' | 'month';

const GroupDetail = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<TabType>(() => {
    // Check if navigation state specifies which tab to show
    return (location.state as { activeTab?: TabType })?.activeTab || 'members';
  });
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [openMemberMenuId, setOpenMemberMenuId] = useState<string | null>(null);
  
  // Shopping Plan State
  const [timeFilter, setTimeFilter] = useState<TimeFilterType>('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const calendarScrollRef = useRef<HTMLDivElement>(null);

  // Scroll to selected date when filter or selected date changes
  useEffect(() => {
    const scrollToSelected = () => {
      if (calendarScrollRef.current) {
        const activeButton = calendarScrollRef.current.querySelector('[data-selected="true"]') as HTMLElement;
        if (activeButton) {
          activeButton.scrollIntoView({ behavior: 'auto', block: 'nearest', inline: 'center' });
        }
      }
    };

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        scrollToSelected();
      });
    });
  }, [timeFilter, selectedDate]);

  // Generate dates based on selected filter
  const getWeekDates = () => {
    const today = new Date();
    const dates = [];
    const dayLabels = ['CN', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
    let startDate = new Date(selectedDate);
    let daysToShow = 30; 
    let centerOffset = 7; 

    if (timeFilter === 'today') {
      centerOffset = 7;
      daysToShow = 15;
    } else if (timeFilter === 'week') {
      centerOffset = 7;
      daysToShow = 14;
    } else if (timeFilter === 'month') {
      centerOffset = 15;
      daysToShow = 31;
    }

    startDate.setDate(selectedDate.getDate() - centerOffset);

    for (let i = 0; i < daysToShow; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      dates.push({
        date: date.getDate(),
        fullDate: date,
        label: dayLabels[date.getDay()],
        active: date.toDateString() === selectedDate.toDateString(),
        isToday: date.toDateString() === today.toDateString(),
      });
    }
    return dates;
  };

  const weekDates = useMemo(getWeekDates, [timeFilter, selectedDate]);

  const handleTimeFilterChange = (filter: TimeFilterType) => {
    setTimeFilter(filter);
    const today = new Date();

    if (filter === 'today') {
      setSelectedDate(new Date(today));
    } else if (filter === 'week') {
      setSelectedDate(new Date(today));
    } else if (filter === 'month') {
      setSelectedDate(new Date(today));
    }
  };

  const today = new Date();
  const isFilterInRange = (filter: TimeFilterType): boolean => {
    if (filter === 'today') {
      return selectedDate.toDateString() === today.toDateString();
    } else if (filter === 'week') {
      const dayOfWeek = today.getDay();
      const weekStart = new Date(today);
      const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
      weekStart.setDate(today.getDate() + diff);
      weekStart.setHours(0, 0, 0, 0);

      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      weekEnd.setHours(23, 59, 59, 999);

      return selectedDate >= weekStart && selectedDate <= weekEnd;
    } else if (filter === 'month') {
      return selectedDate.getMonth() === today.getMonth() &&
             selectedDate.getFullYear() === today.getFullYear();
    }
    return true;
  };

  // Modal States
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isSetLeaderModalOpen, setIsSetLeaderModalOpen] = useState(false);
  const [selectedMemberForLeader, setSelectedMemberForLeader] = useState<typeof mockGroupData.members[0] | null>(null);
  const [isRemoveMemberModalOpen, setIsRemoveMemberModalOpen] = useState(false);
  const [selectedMemberForRemoval, setSelectedMemberForRemoval] = useState<typeof mockGroupData.members[0] | null>(null);
  const [isLeaveGroupModalOpen, setIsLeaveGroupModalOpen] = useState(false);

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

  const currentUser = mockGroupData.members.find(m => m.isCurrentUser);
  const isHeadChef = currentUser?.role === 'Trưởng nhóm';

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);
  const toggleMemberMenu = (id: string) => {
    setOpenMemberMenuId(openMemberMenuId === id ? null : id);
  };

  const handleEdit = () => {
    navigate(`/main/family-group/${mockGroupData.id}/edit`, {
      state: { group: mockGroupData },
    });
    setIsSettingsOpen(false);
  };

  const handleDeleteGroup = () => {
    console.log("Deleting group...");
    setIsDeleteModalOpen(false);
    navigate('/main/family-group');
  };

  const handleSetLeader = () => {
    console.log("Setting member as leader:", selectedMemberForLeader?.name);
    setIsSetLeaderModalOpen(false);
    setSelectedMemberForLeader(null);
    setOpenMemberMenuId(null);
  };

  const handleRemoveMember = () => {
    console.log("Removing member:", selectedMemberForRemoval?.name);
    setIsRemoveMemberModalOpen(false);
    setSelectedMemberForRemoval(null);
    setOpenMemberMenuId(null);
  };

  const handleLeaveGroup = () => {
    console.log("Leaving group...");
    setIsLeaveGroupModalOpen(false);
    setIsSettingsOpen(false);
    navigate('/main/family-group');
  };

  const handleCreatePlan = () => {
    console.log("Create new shopping plan");
    navigate(`/main/family-group/${mockGroupData.id}/add-plan`);
  };

  const handleBackdropClick = () => {
    if (isDeleteModalOpen || isSetLeaderModalOpen || isRemoveMemberModalOpen || isLeaveGroupModalOpen) return;
    if (isSettingsOpen) setIsSettingsOpen(false);
    if (openMemberMenuId) setOpenMemberMenuId(null);
  };

  // Helper to render plan status badge
  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full border border-green-300 bg-white">
            <CheckCircle2 size={12} className="text-green-500" />
            <span className="text-[10px] font-medium text-green-500">Đã xong</span>
          </div>
        );
      case 'pending':
        return (
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full border border-orange-300 bg-white">
            <Clock size={12} className="text-orange-400" />
            <span className="text-[10px] font-medium text-orange-400">Đang chờ</span>
          </div>
        );
      case 'in_progress':
        return (
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full border border-[#C3485C] bg-white">
            <Circle size={8} fill="#C3485C" className="text-[#C3485C]" />
            <span className="text-[10px] font-medium text-[#C3485C]">Đang thực hiện</span>
          </div>
        );
      default:
        return null;
    }
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
                    <button onClick={(e) => { e.stopPropagation(); handleEdit(); }} className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center">
                      <Edit2 size={16} className="mr-2" />
                      Chỉnh sửa
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); setIsSettingsOpen(false); setIsDeleteModalOpen(true); }} className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center">
                      <Trash2 size={16} className="mr-2" />
                      Xóa nhóm
                    </button>
                  </>
                ) : (
                  <button onClick={(e) => { e.stopPropagation(); setIsSettingsOpen(false); setIsLeaveGroupModalOpen(true); }} className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center">
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
          {activeTab === 'members' && (
             <Button variant="primary" size="fit" className="mt-6" icon={UserPlus} onClick={handleEdit}>
               Thêm thành viên
             </Button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex mt-8 border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center font-bold text-sm ${
              activeTab === 'members' ? 'text-gray-900 border-b-2 border-[#C3485C]' : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('members')}
          >
            Thành viên
          </button>
          <button
            className={`flex-1 py-3 text-center font-bold text-sm ${
              activeTab === 'shopping-plan' ? 'text-gray-900 border-b-2 border-[#C3485C]' : 'text-gray-500'
            }`}
            onClick={() => {
              setActiveTab('shopping-plan');
              setTimeFilter('today');
              setSelectedDate(new Date());
            }}
          >
            Kế hoạch mua sắm
          </button>
        </div>

        {/* Tab Content */}
        <div className="mt-4">
          {activeTab === 'members' && (
            <div>
              <h3 className="text-gray-600 text-sm mb-4">Danh sách thành viên ({mockGroupData.members.length})</h3>
              <div className="space-y-3">
                {mockGroupData.members.map((member) => (
                  <UserCard
                    key={member.id}
                    id={member.id}
                    name={member.name}
                    role={member.role}
                    email={member.email}
                    variant="selected"
                    onClick={() => navigate(`/main/family-group/${mockGroupData.id}/user/${member.id}`)}
                    actionElement={
                      isHeadChef && !member.isCurrentUser && (
                        <div className="relative">
                          <button onClick={(e) => { e.stopPropagation(); toggleMemberMenu(member.id); }} className="p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors">
                            <MoreVertical size={20} />
                          </button>
                          {openMemberMenuId === member.id && (
                            <div className="absolute right-0 top-full mt-1 w-52 bg-white rounded-lg shadow-lg z-10 border border-gray-200 py-1">
                              <button onClick={(e) => { e.stopPropagation(); navigate(`/main/family-group/${mockGroupData.id}/user/${member.id}`); }} className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center font-medium">
                                <User size={16} className="mr-2" /> Xem thông tin
                              </button>
                              <button onClick={(e) => { e.stopPropagation(); setSelectedMemberForLeader(member); setIsSetLeaderModalOpen(true); }} className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center font-medium">
                                <Shield size={16} className="mr-2" /> Đặt làm nhóm trưởng
                              </button>
                              <button onClick={(e) => { e.stopPropagation(); setSelectedMemberForRemoval(member); setIsRemoveMemberModalOpen(true); }} className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center font-medium">
                                <LogOut size={16} className="mr-2" /> Xóa khỏi nhóm
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
            <div className="flex flex-col items-center pt-2 pb-24 relative min-h-[400px]">
              {/* Filter Buttons */}
              <div className="flex w-full justify-between gap-2 mb-6 px-1">
                {[
                  { id: 'today', label: 'Hôm nay' },
                  { id: 'week', label: 'Tuần này' },
                  { id: 'month', label: 'Tháng này' }
                ].map((filter) => {
                  const inRange = isFilterInRange(filter.id as TimeFilterType);
                  const isActive = timeFilter === filter.id && inRange;
                  return (
                    <button
                      key={filter.id}
                      onClick={() => handleTimeFilterChange(filter.id as TimeFilterType)}
                      className={`
                        flex-1 py-1.5 px-2 rounded-lg text-sm font-semibold transition-colors
                        ${isActive ? 'bg-[#C3485C] text-white shadow-md' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}
                      `}
                    >
                      {filter.label}
                    </button>
                  );
                })}
              </div>

              {/* Calendar Strip */}
              <div className="w-full mb-6">
                <div className="flex items-center gap-2">
                  <button onClick={() => { const newDate = new Date(selectedDate); newDate.setDate(newDate.getDate() - 1); setSelectedDate(newDate); }} className="p-2 rounded-full hover:bg-gray-100 transition-colors flex-shrink-0">
                    <ChevronLeft size={24} className="text-gray-600" />
                  </button>

                  <div ref={calendarScrollRef} className="flex items-center gap-2 overflow-x-auto scrollbar-hide snap-x snap-center flex-1">
                    {weekDates.map((day, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedDate(day.fullDate)}
                        data-selected={day.active ? 'true' : 'false'}
                        className="flex flex-col items-center transition-transform active:scale-95 flex-shrink-0 snap-center"
                      >
                      {day.active ? (
                        <div className="bg-[#C3485C] rounded-xl w-14 h-[5.0rem] flex flex-col items-center justify-between py-2 shadow-lg shadow-red-100 cursor-pointer">
                          <span className="text-[10px] text-white font-medium">{day.label}</span>
                          <div className="w-8 h-8 rounded-full bg-[#F8EFCE] flex items-center justify-center">
                            <span className="text-[#C3485C] font-bold text-sm">{day.date}</span>
                          </div>
                          <span className="text-[10px] text-white font-medium mt-1">Tháng {day.fullDate.getMonth() + 1}</span>
                        </div>
                      ) : day.isToday ? (
                        <div className="w-10 h-10 rounded-full bg-[#F8EFCE] border border-[#F8EFCE] shadow-sm flex items-center justify-center mt-6 cursor-pointer hover:bg-[#ffdcc4] hover:border-[#ffdcc4] transition-colors">
                          <span className="text-[#C3485C] font-bold text-sm">{day.date}</span>
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-white border border-gray-100 shadow-sm flex items-center justify-center mt-6 cursor-pointer hover:bg-gray-50 hover:border-gray-200 transition-colors">
                          <span className="text-gray-900 font-bold text-sm">{day.date}</span>
                        </div>
                      )}
                    </button>
                  ))}
                  </div>

                  <button onClick={() => { const newDate = new Date(selectedDate); newDate.setDate(newDate.getDate() + 1); setSelectedDate(newDate); }} className="p-2 rounded-full hover:bg-gray-100 transition-colors flex-shrink-0">
                    <ChevronRight size={24} className="text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Plans List */}
              <div className="w-full space-y-3">
                {mockShoppingPlans.length > 0 ? (
                  mockShoppingPlans.map((plan) => (
                    <div
                      key={plan.id}
                      onClick={() => navigate(`/main/family-group/${mockGroupData.id}/plan/${plan.id}`)}
                      className="bg-gray-50 rounded-xl p-4 flex justify-between items-start shadow-sm border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors"
                    >
                      <div>
                        <h4 className="font-bold text-gray-900 text-sm">{plan.title}</h4>
                        <p className="text-xs text-gray-500 mt-1">
                          {plan.creator} • {plan.ingredients} nguyên liệu
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{plan.cost}</p>
                      </div>
                      <div>
                        {renderStatusBadge(plan.status)}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-gray-800 text-sm px-6 leading-relaxed">
                    Nhóm chưa có kế hoạch mua sắm nào cả. Hãy tạo kế hoạch mua sắm mới!
                  </p>
                )}
              </div>

              {/* Floating Action Button for Create Plan */}
              <div className="mt-4">
                <Button
                  variant="primary"
                  size="fit"
                  icon={Plus}
                  onClick={handleCreatePlan}
                >
                  Tạo kế hoạch mới
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* DELETE CONFIRMATION MODAL */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Xóa Nhóm Gia Đình?</h3>
            <div className="flex justify-center mb-5"><AlertTriangle size={64} className="text-white fill-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Hành động này <span className="text-[#C3485C] font-semibold">không thể hoàn tác</span>. Tất cả dữ liệu sẽ bị xóa.</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleDeleteGroup} icon={Trash2} className="bg-[#C3485C] hover:bg-[#a83648]">Xóa</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsDeleteModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}

      {/* SET LEADER MODAL */}
      {isSetLeaderModalOpen && selectedMemberForLeader && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Đặt Làm Trưởng Nhóm?</h3>
            <div className="flex justify-center mb-5"><Shield size={64} className="text-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn chuyển quyền trưởng nhóm cho <span className="text-[#C3485C] font-semibold">{selectedMemberForLeader.name}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleSetLeader} icon={Shield} className="bg-[#C3485C] hover:bg-[#a83648]">Xác nhận</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => { setIsSetLeaderModalOpen(false); setSelectedMemberForLeader(null); }} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}

      {/* REMOVE MEMBER MODAL */}
      {isRemoveMemberModalOpen && selectedMemberForRemoval && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
           <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Xóa Thành Viên?</h3>
            <div className="flex justify-center mb-5"><AlertTriangle size={64} className="text-white fill-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn xóa <span className="text-[#C3485C] font-semibold">{selectedMemberForRemoval.name}</span> khỏi nhóm?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleRemoveMember} icon={LogOut} className="bg-[#C3485C] hover:bg-[#a83648]">Xóa</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => { setIsRemoveMemberModalOpen(false); setSelectedMemberForRemoval(null); }} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}

      {/* LEAVE GROUP MODAL */}
      {isLeaveGroupModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Rời Nhóm?</h3>
            <div className="flex justify-center mb-5"><LogOut size={64} className="text-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn rời khỏi nhóm <span className="text-[#C3485C] font-semibold">{mockGroupData.name}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleLeaveGroup} icon={LogOut} className="bg-[#C3485C] hover:bg-[#a83648]">Rời nhóm</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsLeaveGroupModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GroupDetail;