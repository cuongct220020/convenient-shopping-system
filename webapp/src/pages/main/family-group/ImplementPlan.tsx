import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ClipboardList,
  DollarSign,
  Check,
  X,
  AlertTriangle,
  Loader2,
  ChevronLeft,
  Plus,
  Trash2
} from 'lucide-react';
import { Button } from '../../../components/Button';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { shoppingPlanService } from '../../../services/shopping-plan';
import { userService } from '../../../services/user';
import { storageService, type StorageListItem } from '../../../services/storage';
import type { PlanResponse } from '../../../services/schema/shoppingPlanSchema';

// Default ingredient image
const DEFAULT_INGREDIENT_IMAGE = new URL('../../../assets/ingredient.png', import.meta.url).href;

type ReportUnitDraft = {
  id: string
  storageId: number | null
  quantity: number // package_quantity (int)
  expirationDate: string // YYYY-MM-DD or ''
  packageMeasurement?: number // content_quantity for uncountable
}

// Define interface for an ingredient item data structure
interface IngredientItemData {
  id: number;
  name: string;
  category: string;
  quantity: string;
  image: string;
  isChecked: boolean;
  price: number;
  numericQuantity: number;
  unit: string;
  componentId: number;
  contentType: 'countable_ingredient' | 'uncountable_ingredient';
  reportUnits: ReportUnitDraft[];
  originalIndex: number;
}

export default function ImplementPlan() {
  const navigate = useNavigate();
  const { id, planId } = useParams<{ id: string; planId: string }>();
  const [items, setItems] = useState<IngredientItemData[]>([]);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [planData, setPlanData] = useState<PlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isUnassigning, setIsUnassigning] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [currentUserUsername, setCurrentUserUsername] = useState<string | null>(null);
  const [storages, setStorages] = useState<StorageListItem[]>([]);
  const [storagesError, setStoragesError] = useState<string | null>(null);
  const [missingItemsModal, setMissingItemsModal] = useState<{
    isOpen: boolean;
    missingItems: Array<{ component_id: number; component_name: string; missing_quantity: number }>;
  }>({
    isOpen: false,
    missingItems: []
  });

  // Fetch current user on mount
  useEffect(() => {
    userService.getCurrentUser().match(
      (response) => {
        setCurrentUserId(response.data.id);
        setCurrentUserUsername(response.data.username);
      },
      (err) => {
        console.error('Failed to fetch current user:', err);
      }
    );
  }, []);

  // Fetch plan data on mount
  useEffect(() => {
    if (!planId) return;

    shoppingPlanService
      .getPlanById(parseInt(planId))
      .match(
        (data) => {
          setPlanData(data);
          // Initialize items from shopping list
          const initialItems: IngredientItemData[] = data.shopping_list.map((item, index) => ({
            id: index,
            name: item.component_name,
            category: item.type === 'countable_ingredient' ? 'Đếm được' : 'Không đếm được',
            quantity: `${item.quantity} ${item.unit}`,
            image: DEFAULT_INGREDIENT_IMAGE,
            isChecked: false,
            price: 0,
            numericQuantity: item.quantity,
            unit: item.unit,
            componentId: item.component_id,
            contentType: item.type,
            reportUnits: [],
            originalIndex: index
          }));
          setItems(initialItems);
          setIsLoading(false);
        },
        (err) => {
          console.error('Failed to fetch plan:', err);
          setError(err.desc || 'Failed to load plan');
          setIsLoading(false);
        }
      );
  }, [planId]);

  // Fetch storages for reporting (each reported unit must belong to a storage)
  useEffect(() => {
    if (!planData?.group_id) return;
    storageService.filterStorages(String(planData.group_id)).match(
      (list) => {
        setStorages(list);
        setStoragesError(null);
      },
      (e) => {
        console.error('Failed to fetch storages:', e);
        setStorages([]);
        setStoragesError('Không thể tải danh sách kho thực phẩm');
      }
    );
  }, [planData?.group_id]);

  useEffect(() => {
    const bottomNav = document.querySelector('nav.fixed.bottom-0');
    if (bottomNav) {
      if (isCancelModalOpen || missingItemsModal.isOpen) {
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
  }, [isCancelModalOpen, missingItemsModal.isOpen]);

  // Calculate summary data
  const totalItems = items.length;
  const boughtItems = items.filter(item => item.isChecked).length;
  const totalSpent = items.reduce((sum, item) => sum + (item.isChecked ? item.price : 0), 0);

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('vi-VN').format(amount);
  };

  // Handle checkbox toggle
  const handleToggle = (id: number) => {
    setItems(prevItems =>
      prevItems.map(item =>
        item.id === id
          ? (() => {
              const nextChecked = !item.isChecked;
              if (nextChecked && item.reportUnits.length === 0) {
                const defaultStorageId =
                  storages.length > 0 ? storages[0].storage_id : null;
                const newUnit: ReportUnitDraft = {
                  id: `${Date.now()}-${Math.random()}`,
                  storageId: defaultStorageId,
                  quantity: 1,
                  expirationDate: '',
                  ...(item.contentType === 'uncountable_ingredient'
                    ? { packageMeasurement: 1 }
                    : {})
                };
                return { ...item, isChecked: nextChecked, reportUnits: [newUnit] };
              }
              return { ...item, isChecked: nextChecked };
            })()
          : item
      )
    );
  };

  // Handle price input change (simplified for this UI demonstration)
  const handlePriceChange = (id: number, newPriceStr: string) => {
    // Remove non-numeric characters for simple parsing
    const numericValue = parseInt(newPriceStr.replace(/\D/g, '')) || 0;
    setItems(prevItems =>
      prevItems.map(item =>
        item.id === id ? { ...item, price: numericValue } : item
      )
    );
  };

  // Handle quantity input change
  const handleQuantityChange = (id: number, newQuantityStr: string) => {
    // Only accept integer values
    const numericValue = Math.max(1, Math.floor(parseFloat(newQuantityStr) || 1));
    setItems(prevItems =>
      prevItems.map(item => {
        if (item.id === id) {
          return {
            ...item,
            numericQuantity: numericValue,
            quantity: `${numericValue} ${item.unit}`
          };
        }
        return item;
      })
    );
  };

  const addReportUnit = (itemId: number) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.id !== itemId) return item;
        const defaultStorageId = storages.length > 0 ? storages[0].storage_id : null;
        const newUnit: ReportUnitDraft = {
          id: `${Date.now()}-${Math.random()}`,
          storageId: defaultStorageId,
          quantity: 1,
          expirationDate: '',
          ...(item.contentType === 'uncountable_ingredient'
            ? { packageMeasurement: 1 }
            : {})
        };
        return { ...item, reportUnits: [...item.reportUnits, newUnit] };
      })
    );
  };

  const removeReportUnit = (itemId: number, unitId: string) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.id !== itemId) return item;
        return { ...item, reportUnits: item.reportUnits.filter((u) => u.id !== unitId) };
      })
    );
  };

  const updateReportUnit = (
    itemId: number,
    unitId: string,
    patch: Partial<ReportUnitDraft>
  ) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.id !== itemId) return item;
        return {
          ...item,
          reportUnits: item.reportUnits.map((u) => (u.id === unitId ? { ...u, ...patch } : u))
        };
      })
    );
  };

  const getPlanTitle = (plan: PlanResponse | null) => {
    if (!plan) return 'Kế hoạch';
    return plan.others?.name as string || 'Kế hoạch mua sắm';
  };

  const handleCompletePlan = (withConfirm: boolean = false) => {
    if (!planId || !planData || !currentUserId || !currentUserUsername) return;

    setIsCompleting(true);
    setError(null);

    if (storages.length === 0) {
      setError(storagesError || 'Vui lòng tạo ít nhất một kho thực phẩm trước khi báo cáo');
      setIsCompleting(false);
      return;
    }

    const report_content: Array<{
      storage_id: number
      package_quantity: number
      unit_name: string
      component_id: number
      content_type: 'countable_ingredient' | 'uncountable_ingredient'
      content_quantity?: number
      content_unit?: string
      expiration_date?: string | null
    }> = [];

    for (const item of items) {
      if (!item.isChecked) continue;
      for (const u of item.reportUnits) {
        if (!u.storageId) {
          setError('Vui lòng chọn kho cho tất cả các unit đã mua');
          setIsCompleting(false);
          return;
        }
        const packageQty = Math.max(1, Math.floor(Number(u.quantity)) || 1);
        const expiration = u.expirationDate ? u.expirationDate : null;

        if (item.contentType === 'uncountable_ingredient') {
          const contentQty = Math.max(
            1,
            Math.floor(Number(u.packageMeasurement)) || 1
          );
          report_content.push({
            storage_id: u.storageId,
            package_quantity: packageQty,
            unit_name: item.name,
            component_id: item.componentId,
            content_type: 'uncountable_ingredient',
            content_quantity: contentQty,
            content_unit: item.unit,
            expiration_date: expiration
          });
        } else {
          report_content.push({
            storage_id: u.storageId,
            package_quantity: packageQty,
            unit_name: item.name,
            component_id: item.componentId,
            content_type: 'countable_ingredient',
            expiration_date: expiration
          });
        }
      }
    }

    if (report_content.length === 0) {
      setError('Vui lòng báo cáo ít nhất một unit nguyên liệu đã mua');
      setIsCompleting(false);
      return;
    }

    const reportPayload = {
      plan_id: parseInt(planId),
      report_content,
      spent_amount: Math.max(0, Math.floor(Number(totalSpent)) || 0)
    };

    shoppingPlanService
      // Report the plan - first time with confirm=false, retry with confirm=true if needed
      .reportPlan(parseInt(planId), currentUserId, currentUserUsername, reportPayload, withConfirm)
      .match(
        (response) => {
          // Check if response has missing_items
          if (response.missing_items && response.missing_items.length > 0) {
            // Show missing items modal
            setMissingItemsModal({
              isOpen: true,
              missingItems: response.missing_items
            });
            setIsCompleting(false);
          } else {
            // Success - no missing items
            setIsCompleting(false);
            navigate(`/main/family-group/${id}/plan/${planId}`);
          }
        },
        (err) => {
          console.error('Failed to complete plan:', err);
          setError(err.desc || 'Failed to complete plan');
          setIsCompleting(false);
        }
      );
  };

  const handleConfirmWithMissingItems = () => {
    setMissingItemsModal({ isOpen: false, missingItems: [] });
    // Retry with confirm=true
    handleCompletePlan(true);
  };

  const handleCancelPlan = () => {
    if (!planId || !currentUserId || !currentUserUsername) return;

    setIsUnassigning(true);
    setIsCancelModalOpen(false);
    setError(null);

    shoppingPlanService
      .unassignPlan(parseInt(planId), currentUserId, currentUserUsername)
      .match(
        () => {
          setIsUnassigning(false);
          navigate(`/main/family-group/${id}/plan/${planId}`);
        },
        (err) => {
          console.error('Failed to unassign plan:', err);
          setError(err.desc || 'Failed to unassign plan');
          setIsUnassigning(false);
        }
      );
  };

  const handleBack = () => {
    navigate(`/main/family-group/${id}/plan/${planId}`);
  };

  return (
    <div className="min-h-screen bg-white pb-6">
      {/* Header */}
      <div className="pt-4 px-4 mb-4">
        <button
          onClick={handleBack}
          className="flex items-center text-sm font-bold text-[#C3485C] hover:opacity-80"
        >
          <ChevronLeft size={20} strokeWidth={3} />
          <span className="ml-1">Quay lại</span>
        </button>
      </div>

      <h1 className="text-xl font-bold text-[#D3314D] text-center mb-4">
        {getPlanTitle(planData)}
      </h1>

      <div className="px-4">
        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-20">
            <LoadingSpinner size="lg" showText text="Đang tải..." />
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <AlertTriangle size={48} className="text-red-500 mb-4" />
            <p className="text-gray-600 mb-4">{error}</p>
            <Button
              variant="primary"
              onClick={handleBack}
            >
              Quay lại
            </Button>
          </div>
        )}

        {/* Content */}
        {!isLoading && !error && planData && (
          <>
            {/* Summary Card */}
            <div className="bg-gray-100 rounded-2xl p-4 flex justify-between items-center mb-6">
              {/* Left: Results */}
              <div className="flex flex-col items-center w-1/2 border-r border-gray-300">
                <div className="flex items-center gap-2 mb-1">
                  <ClipboardList size={20} className="text-black" />
                  <span className="font-bold text-lg">Kết quả</span>
                </div>
                <div className="text-2xl font-black mb-1">
                  {boughtItems}/{totalItems}
                </div>
                <div className="text-gray-600 text-sm">Đã mua</div>
              </div>

              {/* Right: Total Spending */}
              <div className="flex flex-col items-center w-1/2">
                <div className="flex items-center gap-1 mb-1">
                  <DollarSign size={20} className="text-black" />
                  <span className="font-bold text-lg">Tổng chi tiêu</span>
                </div>
                <div className="text-xl font-bold mb-1">
                  {formatCurrency(totalSpent)}
                </div>
                <div className="text-gray-600 text-sm">VND</div>
              </div>
            </div>

            {/* List Title */}
            <h2 className="text-lg font-bold mb-4">Danh sách nguyên liệu cần mua</h2>

            {/* Ingredient List */}
            <div className="space-y-3">
              {storagesError && (
                <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">
                  {storagesError}
                </div>
              )}

              {items.map((item) => {
                const isUncountable = item.contentType === 'uncountable_ingredient';

                // helpful preview for user
                const reportedPreview = item.reportUnits.reduce((sum, u) => {
                  const pkgQty = Math.max(1, Math.floor(Number(u.quantity)) || 1);
                  if (isUncountable) {
                    const contentQty = Math.max(
                      1,
                      Math.floor(Number(u.packageMeasurement)) || 1
                    );
                    return sum + pkgQty * contentQty;
                  }
                  return sum + pkgQty;
                }, 0);

                return (
                  <div key={item.id} className="bg-gray-100 rounded-2xl overflow-hidden">
                    {/* Top: info */}
                    <div className="flex p-3 relative">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-24 h-16 object-cover rounded-xl mr-3 flex-shrink-0"
                      />
                      <div className="flex flex-col justify-center gap-1">
                        <h3 className="font-bold text-base">{item.name}</h3>
                        <p className="text-xs text-gray-600">
                          Cần mua: <span className="font-semibold">{item.quantity}</span>
                          {item.isChecked && item.reportUnits.length > 0 && (
                            <>
                              {'  '}• Đã báo cáo:{' '}
                              <span className="font-semibold text-[#C3485C]">
                                {reportedPreview} {isUncountable ? item.unit : item.unit}
                              </span>
                            </>
                          )}
                        </p>
                      </div>
                      <div className="absolute top-3 right-3">
                        <label className="relative flex items-center p-1 rounded-full cursor-pointer">
                          <input
                            type="checkbox"
                            className="peer hidden"
                            checked={item.isChecked}
                            onChange={() => handleToggle(item.id)}
                          />
                          <span className="w-6 h-6 border-2 border-gray-700 rounded-md peer-checked:bg-black peer-checked:border-black flex items-center justify-center transition-colors">
                            {item.isChecked && <Check size={16} color="white" strokeWidth={3} />}
                          </span>
                        </label>
                      </div>
                    </div>

                    {/* Divider */}
                    <div className="h-px bg-gray-200 mx-3"></div>

                    {/* Bottom: price + report units */}
                    <div className="p-3 bg-gray-50">
                      {/* Price */}
                      <div className="flex items-center justify-between gap-3 mb-3">
                        <span className="text-gray-700 font-medium">Chi:</span>
                        <div className="flex items-center bg-white rounded-lg px-3 py-1.5 border border-gray-200 w-40 justify-end">
                          <input
                            type="text"
                            inputMode="numeric"
                            value={item.isChecked ? formatCurrency(item.price || 0) : '0'}
                            onChange={(e) => item.isChecked && handlePriceChange(item.id, e.target.value)}
                            className="w-full text-right font-medium outline-none bg-transparent"
                            readOnly={!item.isChecked}
                          />
                          <span className="text-gray-500 ml-1 text-sm">VND</span>
                        </div>
                      </div>

                      {/* Units */}
                      {item.isChecked && (
                        <div className="space-y-3">
                          {item.reportUnits.map((u, idx) => (
                            <div key={u.id} className="rounded-xl bg-white border border-gray-200 p-3">
                              <div className="mb-2 flex items-center justify-between">
                                <p className="text-sm font-bold text-gray-800">
                                  Unit {idx + 1}
                                </p>
                                <button
                                  type="button"
                                  className="text-gray-500 hover:text-[#C3485C]"
                                  onClick={() => removeReportUnit(item.id, u.id)}
                                >
                                  <Trash2 size={18} />
                                </button>
                              </div>

                              <div className="grid grid-cols-2 gap-2">
                                {/* Storage */}
                                <div className="col-span-2">
                                  <label className="block text-xs font-semibold text-gray-600 mb-1">Kho</label>
                                  <select
                                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-[#C3485C] focus:outline-none"
                                    value={u.storageId ?? ''}
                                    onChange={(e) => {
                                      const val = e.target.value ? Number(e.target.value) : null;
                                      updateReportUnit(item.id, u.id, { storageId: val });
                                    }}
                                  >
                                    <option value="">Chọn kho</option>
                                    {storages.map((s) => (
                                      <option key={s.storage_id} value={s.storage_id}>
                                        {s.storage_name}
                                      </option>
                                    ))}
                                  </select>
                                </div>

                                {/* Quantity */}
                                <div>
                                  <label className="block text-xs font-semibold text-gray-600 mb-1">Số lượng</label>
                                  <input
                                    type="number"
                                    min="1"
                                    step="1"
                                    inputMode="numeric"
                                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-[#C3485C] focus:outline-none"
                                    value={u.quantity}
                                    onChange={(e) => {
                                      const v = Math.max(1, Math.floor(Number(e.target.value)) || 1);
                                      updateReportUnit(item.id, u.id, { quantity: v });
                                    }}
                                  />
                                </div>

                                {/* Expiration */}
                                <div>
                                  <label className="block text-xs font-semibold text-gray-600 mb-1">Ngày hết hạn</label>
                                  <input
                                    type="date"
                                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-[#C3485C] focus:outline-none"
                                    value={u.expirationDate}
                                    onChange={(e) =>
                                      updateReportUnit(item.id, u.id, { expirationDate: e.target.value })
                                    }
                                  />
                                </div>

                                {/* Uncountable extra */}
                                {isUncountable && (
                                  <div className="col-span-2">
                                    <label className="block text-xs font-semibold text-gray-600 mb-1">
                                      Định lượng bao bì <span className="text-gray-500">({item.unit})</span>
                                    </label>
                                    <input
                                      type="number"
                                      min="1"
                                      step="1"
                                      inputMode="numeric"
                                      className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-[#C3485C] focus:outline-none"
                                      value={u.packageMeasurement ?? 1}
                                      onChange={(e) => {
                                        const v = Math.max(1, Math.floor(Number(e.target.value)) || 1);
                                        updateReportUnit(item.id, u.id, { packageMeasurement: v });
                                      }}
                                    />
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}

                          <div className="flex justify-center">
                            <Button
                              type="button"
                              variant="secondary"
                              size="fit"
                              icon={Plus}
                              onClick={() => addReportUnit(item.id)}
                              className="rounded-xl"
                            >
                              Thêm unit
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Bottom Action Buttons */}
            <div className="flex gap-4 mt-6">
              <Button
                variant={isCompleting ? 'disabled' : 'primary'}
                icon={isCompleting ? Loader2 : Check}
                size="fit"
                className="rounded-2xl"
                onClick={isCompleting ? undefined : () => handleCompletePlan(false)}
              >
                {isCompleting ? 'Đang báo cáo...' : 'Báo cáo'}
              </Button>
              <Button
                variant="secondary"
                icon={X}
                size="fit"
                className="rounded-2xl"
                onClick={() => setIsCancelModalOpen(true)}
              >
                Hủy
              </Button>
            </div>
          </>
        )}
      </div>

      {/* CANCEL PLAN CONFIRMATION MODAL */}
      {isCancelModalOpen && planData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Hủy Làm Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><AlertTriangle size={64} className="text-white fill-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn hủy làm kế hoạch <span className="text-[#C3485C] font-semibold">{getPlanTitle(planData)}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                <Button
                  variant={isUnassigning ? 'disabled' : 'primary'}
                  onClick={isUnassigning ? undefined : handleCancelPlan}
                  icon={isUnassigning ? Loader2 : Check}
                  className={isUnassigning ? '' : 'bg-[#C3485C] hover:bg-[#a83648]'}
                >
                  {isUnassigning ? 'Đang hủy...' : 'Xác nhận'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant={isUnassigning ? 'disabled' : 'secondary'}
                  onClick={isUnassigning ? undefined : () => setIsCancelModalOpen(false)}
                  icon={X}
                  className={isUnassigning ? '' : 'bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]'}
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MISSING ITEMS CONFIRMATION MODAL */}
      {missingItemsModal.isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[400px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-4 text-center">Báo cáo chưa đầy đủ</h3>
            <div className="flex justify-center mb-4">
              <AlertTriangle size={48} className="text-[#C3485C]" strokeWidth={2} />
            </div>
            <p className="text-sm text-center text-gray-600 mb-4">
              Báo cáo của bạn còn thiếu:
            </p>
            <div className="bg-gray-50 rounded-lg p-3 mb-4 max-h-48 overflow-y-auto">
              <ul className="space-y-2">
                {missingItemsModal.missingItems.map((item, index) => (
                  <li key={index} className="text-sm text-gray-700">
                    <span className="font-semibold">{item.component_name}</span>
                    {':  '}còn thiếu{'  '}
                    <span className="font-semibold text-[#C3485C]">{item.missing_quantity}</span>
                  </li>
                ))}
              </ul>
            </div>
            <p className="text-sm text-center text-gray-600 mb-6">
              Bạn có chắc muốn báo cáo không?
            </p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2">
                <Button
                  variant={isCompleting ? 'disabled' : 'primary'}
                  onClick={isCompleting ? undefined : handleConfirmWithMissingItems}
                  icon={isCompleting ? Loader2 : Check}
                  className={isCompleting ? '' : 'bg-[#C3485C] hover:bg-[#a83648]'}
                >
                  {isCompleting ? 'Đang xử lý...' : 'Có'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant={isCompleting ? 'disabled' : 'secondary'}
                  onClick={isCompleting ? undefined : () => setMissingItemsModal({ isOpen: false, missingItems: [] })}
                  icon={X}
                  className={isCompleting ? '' : 'bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]'}
                >
                  Không
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
