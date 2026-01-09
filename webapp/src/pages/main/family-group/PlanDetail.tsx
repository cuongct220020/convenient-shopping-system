import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Check, Clock, User, Calendar, AlertTriangle, X, Settings, Edit2, Trash2, ArrowRight, Loader2 } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { shoppingPlanService } from '../../../services/shopping-plan';
import { groupService } from '../../../services/group';
import { userService } from '../../../services/user';
import type { PlanResponse } from '../../../services/schema/shoppingPlanSchema';
import type { UserCoreInfo } from '../../../services/schema/groupSchema';

export const PlanDetail = () => {
  const { id, planId } = useParams<{ id: string; planId: string }>();
  const navigate = useNavigate();
  const [isApproveModalOpen, setIsApproveModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [planData, setPlanData] = useState<PlanResponse | null>(null);
  const [creatorInfo, setCreatorInfo] = useState<UserCoreInfo | null>(null);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch current user on mount
  useEffect(() => {
    userService.getCurrentUser().match(
      (response) => {
        setCurrentUserId(response.data.id);
      },
      (err) => {
        console.error('Failed to fetch current user:', err);
      }
    );
  }, []);

  // Fetch creator info when plan data is loaded
  useEffect(() => {
    if (!planData?.assigner_id || !id) return;

    groupService
      .getGroupMembers(id)
      .match(
        (response) => {
          const memberships = response.data.members || response.data.group_memberships || [];
          const creator = memberships.find((m) => m.user.id === planData.assigner_id);
          if (creator) {
            setCreatorInfo(creator.user);
          }
        },
        (err) => {
          // Silently fail - we'll show the assigner_id instead of the name
          console.log('Could not fetch creator info:', err);
        }
      );
  }, [planData, id]);

  // Fetch plan data on mount
  useEffect(() => {
    if (!planId) return;

    shoppingPlanService
      .getPlanById(parseInt(planId))
      .match(
        (data) => {
          setPlanData(data);
          setIsLoading(false);
        },
        (err) => {
          console.error('Failed to fetch plan:', err);
          setError(err.desc || 'Failed to load plan');
          setIsLoading(false);
        }
      );
  }, [planId]);

  useEffect(() => {
    const bottomNav = document.querySelector('nav.fixed.bottom-0');
    if (bottomNav) {
      if (isApproveModalOpen || isDeleteModalOpen) {
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
  }, [isApproveModalOpen, isDeleteModalOpen]);

  const handleBack = () => {
    navigate(`/main/family-group/${id}`, { state: { activeTab: 'shopping-plan' } });
  };

  const handleApprovePlan = () => {
    console.log('Approving plan...');
    setIsApproveModalOpen(false);
    navigate(`/main/family-group/${id}/plan/${planId}/implement`);
  };

  const handleEdit = () => {
    if (!planData) return;
    const planForEdit = {
      id: planId,
      planData: planData,
    };
    navigate(`/main/family-group/${id}/plan/${planId}/edit`, {
      state: { plan: planForEdit },
    });
    setIsSettingsOpen(false);
  };

  const handleDeletePlan = () => {
    if (!planId) return;

    setIsDeleting(true);
    setError(null);

    shoppingPlanService
      .deletePlan(parseInt(planId))
      .match(
        () => {
          setIsDeleting(false);
          setIsDeleteModalOpen(false);
          navigate(`/main/family-group/${id}`, { state: { activeTab: 'shopping-plan' } });
        },
        (err) => {
          console.error('Failed to delete plan:', err);
          setError(err.desc || 'Failed to delete plan');
          setIsDeleting(false);
        }
      );
  };

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);

  // Helper functions to map API data to display format
  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'created':
        return 'Chờ duyệt';
      case 'in_progress':
        return 'Đang thực hiện';
      case 'completed':
        return 'Đã xong';
      case 'cancelled':
        return 'Đã hủy';
      case 'expired':
        return 'Đã hết hạn';
      default:
        return status;
    }
  };

  const formatDeadline = (deadline: string) => {
    try {
      const date = new Date(deadline);
      const options: Intl.DateTimeFormatOptions = {
        weekday: 'long',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      return date.toLocaleDateString('vi-VN', options);
    } catch {
      return deadline;
    }
  };

  const getPlanTitle = (plan: PlanResponse) => {
    return plan.others?.name as string || 'Kế hoạch mua sắm';
  };

  const getPlanNote = (plan: PlanResponse) => {
    return plan.others?.notes as string || 'Không có ghi chú';
  };

  const getCreatorDisplayName = (creator: UserCoreInfo | null) => {
    if (!creator) {
      // If we've finished loading but don't have creator info, show a fallback
      if (!isLoading) {
        return planData ? planData.assigner_id.substring(0, 8) + '...' : 'Người dùng';
      }
      return 'Đang tải...';
    }

    const firstName = creator.first_name?.trim();
    const lastName = creator.last_name?.trim();

    if (firstName && lastName) {
      return `${firstName} ${lastName}`;
    } else if (firstName) {
      return firstName;
    } else if (lastName) {
      return lastName;
    } else {
      return creator.username || 'Người dùng';
    }
  };

  return (
    <div className="bg-white min-h-screen relative pb-8" onClick={() => { if (isSettingsOpen) setIsSettingsOpen(false); }}>
      {/* Header Container with padding */}
      <div className="p-4">
        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C3485C]"></div>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <AlertTriangle size={48} className="text-red-500 mb-4" />
            <p className="text-gray-600">{error}</p>
            <Button
              variant="primary"
              onClick={handleBack}
              className="mt-4"
            >
              Quay lại
            </Button>
          </div>
        )}

        {/* Plan Content */}
        {!isLoading && !error && planData && (
          <>
            {/* Header Nav */}
            <div className="flex items-center justify-between mb-2">
              <BackButton text="Quay lại" to={`/main/family-group/${id}`} onClick={handleBack} />
              {/* Only show settings icon to the creator */}
              {currentUserId === planData.assigner_id && (
                <div className="relative">
                  <button onClick={(e) => { e.stopPropagation(); toggleSettings(); }} className="p-2">
                  <Settings size={24} className="text-gray-700" />
                </button>

                {/* Settings Popover */}
                {isSettingsOpen && (
                  <div className="absolute right-0 top-full mt-2 w-36 bg-white rounded-lg shadow-lg z-10 border border-gray-200 py-1">
                    {/* Only show edit button for editable plans (created or in_progress) */}
                    {planData.plan_status === 'created' || planData.plan_status === 'in_progress' ? (
                      <button onClick={(e) => { e.stopPropagation(); handleEdit(); }} className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center">
                        <Edit2 size={16} className="mr-2" />
                        Chỉnh sửa
                      </button>
                    ) : null}
                    <button onClick={(e) => { e.stopPropagation(); setIsSettingsOpen(false); setIsDeleteModalOpen(true); }} className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center">
                      <Trash2 size={16} className="mr-2" />
                      Xóa kế hoạch
                    </button>
                  </div>
                )}
              </div>
                )}
            </div>
            <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">Chi Tiết Kế Hoạch</h1>

            {/* Info Cards - 2 Rows */}
            {/* Row 1: Plan Name | Status */}
            <div className="bg-gray-100 rounded-2xl p-4 flex justify-between items-center mb-3">
              {/* Left: Plan Name */}
              <div className="flex flex-col items-center w-1/2 border-r border-gray-300">
                <span className="font-bold text-sm text-gray-700 mb-1">Tên kế hoạch</span>
                <p className="text-sm font-medium">{getPlanTitle(planData)}</p>
              </div>

              {/* Right: Status */}
              <div className="flex flex-col items-center w-1/2">
                <div className="flex items-center gap-1 mb-1">
                  <Clock size={16} className="text-black" strokeWidth={2.5} />
                  <span className="font-bold text-sm text-gray-700">Trạng thái</span>
                </div>
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-[#FFD7C1] text-[#C3485C] text-xs font-bold">
                  {getStatusDisplay(planData.plan_status)}
                </div>
              </div>
            </div>

            {/* Creator Card (Full Width) */}
            <div className="bg-gray-100 rounded-2xl p-4 flex items-center mb-3">
              <User size={16} className="text-black mr-3" strokeWidth={2.5} />
              <div>
                <span className="font-bold text-sm text-gray-700">Người tạo</span>
                <p className="text-sm font-medium">{getCreatorDisplayName(creatorInfo)}</p>
              </div>
            </div>

            {/* Date Card (Full Width) */}
            <div className="bg-[#F3F4F6] p-4 rounded-[20px] mb-6 flex items-start">
              <Calendar size={20} className="mr-3 mt-0.5 text-gray-800" strokeWidth={2.5} />
              <div>
                <h3 className="font-bold text-sm mb-1">Hạn chót</h3>
                <p className="text-sm font-medium">{formatDeadline(planData.deadline)}</p>
              </div>
            </div>

            {/* Note Section */}
            <div className="mb-8">
              <div className="flex items-center font-bold mb-2 text-sm">
                <FileText size={18} className="mr-2" strokeWidth={2.5} /> Ghi chú
              </div>
              <div className="border border-gray-400 rounded-[20px] p-4 text-sm leading-relaxed font-medium">
                {getPlanNote(planData)}
              </div>
            </div>

            {/* Ingredient List Section */}
            <h2 className="font-bold text-lg mb-4">Danh sách nguyên liệu</h2>
            <div className="mb-10">
              {planData.shopping_list.map((item, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-4 mb-3 border border-gray-200">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{item.component_name}</h3>
                      <p className="text-sm text-gray-600">
                        Số lượng: {item.quantity} {item.unit}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Loại: {item.type === 'countable_ingredient' ? 'Đếm được' : 'Không đếm được'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer Button */}
            {planData.plan_status !== 'completed' && planData.plan_status !== 'cancelled' && (
              <div className="flex justify-center">
                <Button
                  variant="primary"
                  size="fit"
                  icon={planData.plan_status === 'in_progress' ? ArrowRight : Check}
                  className="!px-10 !py-3 text-base rounded-2xl shadow-lg shadow-red-200/50"
                  onClick={() => setIsApproveModalOpen(true)}
                >
                  {planData.plan_status === 'in_progress' ? "Tiếp tục thực hiện kế hoạch" : "Duyệt kế hoạch"}
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* APPROVE PLAN CONFIRMATION MODAL */}
      {isApproveModalOpen && planData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Duyệt Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center"><Check size={36} className="text-white" strokeWidth={3} /></div></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn duyệt kế hoạch <span className="text-[#C3485C] font-semibold">{getPlanTitle(planData)}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleApprovePlan} icon={Check} className="bg-[#C3485C] hover:bg-[#a83648]">Xác nhận</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsApproveModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}

      {/* DELETE PLAN CONFIRMATION MODAL */}
      {isDeleteModalOpen && planData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Xóa Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><AlertTriangle size={64} className="text-white fill-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Hành động này <span className="text-[#C3485C] font-semibold">không thể hoàn tác</span>. Bạn có chắc muốn xóa kế hoạch <span className="text-[#C3485C] font-semibold">{getPlanTitle(planData)}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                <Button
                  variant={isDeleting ? 'disabled' : 'primary'}
                  onClick={isDeleting ? undefined : handleDeletePlan}
                  icon={isDeleting ? Loader2 : Trash2}
                  className={isDeleting ? '' : 'bg-[#C3485C] hover:bg-[#a83648]'}
                >
                  {isDeleting ? 'Đang xóa...' : 'Xóa'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant={isDeleting ? 'disabled' : 'secondary'}
                  onClick={isDeleting ? undefined : () => setIsDeleteModalOpen(false)}
                  icon={X}
                  className={isDeleting ? '' : 'bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]'}
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

export default PlanDetail;