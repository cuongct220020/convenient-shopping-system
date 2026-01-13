import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { Plus, FileText, Check, Search, X, Loader2 } from 'lucide-react';
import { IngredientCard, Ingredient } from '../../../components/IngredientCard';
import { shoppingPlanService } from '../../../services/shopping-plan';
import { ingredientService } from '../../../services/ingredient';
import type { PlanResponse, PlanItemBase } from '../../../services/schema/shoppingPlanSchema';
import type { Ingredient as IngredientSearchResult } from '../../../services/schema/ingredientSchema';

// Extended ingredient type to include original shopping list data and search result
type ExtendedIngredient = Ingredient & {
  originalItem?: PlanItemBase;
  searchResult?: IngredientSearchResult;
  numericQuantity?: number;  // Store the numeric value entered by user
  measurementUnit?: string;  // Store the unit from API (e.g., "g", "ml")
};

// Default ingredient image
const DEFAULT_INGREDIENT_IMAGE = new URL('../../../assets/ingredient.png', import.meta.url).href;

// Helper function to parse ISO date to datetime-local format
const parseISOToDateTimeLocal = (isoString: string): string => {
  try {
    const date = new Date(isoString);
    // Format: YYYY-MM-DDTHH:mm
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  } catch {
    return '';
  }
};

// Helper function to format datetime-local to ISO string
const formatDateTimeLocalToISO = (dateTimeLocal: string): string => {
  try {
    const date = new Date(dateTimeLocal);
    return date.toISOString();
  } catch {
    return new Date().toISOString();
  }
};

const EditPlan: React.FC = () => {
  const navigate = useNavigate();
  const { id, planId } = useParams<{ id: string; planId: string }>();

  // --- State Management ---
  const [planData, setPlanData] = useState<PlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [planName, setPlanName] = useState('');
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [ingredientQuantity, setIngredientQuantity] = useState('');
  const [ingredients, setIngredients] = useState<ExtendedIngredient[]>([]);

  // Search states
  const [searchResult, setSearchResult] = useState<IngredientSearchResult | null>(null);
  const [showNotFound, setShowNotFound] = useState(false);
  const [showQuantityInput, setShowQuantityInput] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const [deadline, setDeadline] = useState('');
  const [notes, setNotes] = useState('');

  // Fetch plan data on mount
  useEffect(() => {
    if (!planId) return;

    shoppingPlanService
      .getPlanById(parseInt(planId))
      .match(
        (data) => {
          // Check if plan can be edited (only created or in_progress can be edited)
          if (data.plan_status !== 'created' && data.plan_status !== 'in_progress') {
            const statusMap: Record<string, string> = {
              completed: 'Đã hoàn thành',
              cancelled: 'Đã hủy',
              expired: 'Đã hết hạn',
            };
            setError(`Kế hoạch này đã ${statusMap[data.plan_status] || data.plan_status} và không thể chỉnh sửa`);
            setIsLoading(false);
            return;
          }

          setPlanData(data);
          // Initialize form fields
          setPlanName((data.others?.name as string) || '');
          setNotes((data.others?.notes as string) || '');
          setDeadline(parseISOToDateTimeLocal(data.deadline));

          // Map shopping list to ingredients, preserving original data
          const mappedIngredients: ExtendedIngredient[] = data.shopping_list.map((item, index) => ({
            id: index,
            name: item.component_name,
            category: item.type === 'countable_ingredient' ? 'Đếm được' : 'Không đếm được',
            quantity: `${item.quantity} ${item.unit}`,
            image: DEFAULT_INGREDIENT_IMAGE,
            originalItem: item, // Store original item data
          }));
          setIngredients(mappedIngredients);
          setIsLoading(false);
        },
        (err) => {
          console.error('Failed to fetch plan:', err);
          setError(err.desc || 'Failed to load plan');
          setIsLoading(false);
        }
      );
  }, [planId]);

  // --- Search Logic (Debounced) ---
  useEffect(() => {
    // 300ms delay to avoid flickering
    const delayDebounceFn = setTimeout(async () => {
      if (!ingredientSearch.trim()) {
        setSearchResult(null);
        setShowNotFound(false);
        setShowQuantityInput(false);
        setIsSearching(false);
        return;
      }

      // Check if this ingredient is already added to the list
      const isAlreadyAdded = ingredients.some(
        (ing) => ing.name.toLowerCase() === ingredientSearch.toLowerCase()
      );

      if (isAlreadyAdded) {
        setSearchResult(null);
        setShowNotFound(true);
        setShowQuantityInput(false);
        setIsSearching(false);
        console.log('Ingredient already added:', ingredientSearch);
        return;
      }

      setIsSearching(true);
      setShowNotFound(false); // Reset not found when starting a new search

      // Search ingredients from API
      const result = await ingredientService.searchIngredients(ingredientSearch);

      result.match(
        (response) => {
          console.log('Search response for:', ingredientSearch, response);
          if (response.data && response.data.length > 0) {
            // Use the first result
            console.log('Found ingredient:', response.data[0]);
            setSearchResult(response.data[0]);
            setShowNotFound(false);
            setShowQuantityInput(true);
          } else {
            console.log('No ingredients found for:', ingredientSearch);
            setSearchResult(null);
            setShowNotFound(true);
            setShowQuantityInput(false);
          }
          setIsSearching(false);
        },
        (error) => {
          console.error('Failed to search ingredients:', error);
          setSearchResult(null);
          setShowNotFound(true);
          setShowQuantityInput(false);
          setIsSearching(false);
        }
      );
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [ingredientSearch, ingredients]);

  // --- Handlers ---
  const handleAddIngredient = () => {
    if (searchResult && ingredientQuantity) {
      // Parse numeric value from user input
      const numericValue = parseFloat(ingredientQuantity.trim()) || 0;
      // Get the measurement unit from API (e.g., "g", "ml", "củ")
      const unit = searchResult.measurementUnit || '';
      // For display, combine them (e.g., "100g")
      const displayQuantity = numericValue > 0 ? `${numericValue} ${unit}` : unit;

      const newIngredient: ExtendedIngredient = {
        id: Date.now(),
        name: searchResult.component_name,
        category: searchResult.category || 'Khác',
        quantity: displayQuantity,
        numericQuantity: numericValue,
        measurementUnit: unit,
        image: DEFAULT_INGREDIENT_IMAGE,
        searchResult: searchResult,
      };
      setIngredients([...ingredients, newIngredient]);
      setIngredientSearch('');
      setIngredientQuantity('');
      setSearchResult(null);
      setShowQuantityInput(false);
    }
  };

  const handleDeleteIngredient = (id: number) => {
    setIngredients(ingredients.filter((ing) => ing.id !== id));
  };

  const handleSubmit = () => {
    if (!planId || !deadline) {
      setError('Vui lòng chọn hạn chót cho kế hoạch');
      return;
    }

    setIsSaving(true);
    setError(null);

    // Build shopping list from ingredients
    const shoppingList = ingredients.map((ing) => {
      // For new ingredients with numeric quantity and measurement unit
      if (ing.numericQuantity !== undefined && ing.measurementUnit) {
        return {
          type: ing.searchResult?.type || 'countable_ingredient',
          unit: ing.measurementUnit,
          quantity: ing.numericQuantity,
          component_id: ing.searchResult?.component_id || 0,
          component_name: ing.name,
        };
      }

      // For existing ingredients from the plan, use original data
      if (ing.originalItem) {
        return {
          type: ing.originalItem.type,
          unit: ing.originalItem.unit,
          quantity: ing.originalItem.quantity,
          component_id: ing.originalItem.component_id,
          component_name: ing.name,
        };
      }

      // Fallback for ingredients without proper data
      return {
        type: 'countable_ingredient' as const,
        unit: ing.quantity,
        quantity: 1,
        component_id: 0,
        component_name: ing.name,
      };
    });

    const others: Record<string, unknown> = {};
    if (planName) others.name = planName;
    if (notes) others.notes = notes;

    // Debug logging
    console.log('Update plan shopping list:', JSON.stringify(shoppingList, null, 2));

    shoppingPlanService
      .updatePlan(parseInt(planId), {
        deadline: formatDateTimeLocalToISO(deadline),
        shoppingList,
        others: Object.keys(others).length > 0 ? others : null,
      })
      .match(
        () => {
          setIsSaving(false);
          navigate(`/main/family-group/${id}/plan/${planId}`);
        },
        (err) => {
          console.error('Failed to update plan:', err);
          setError(err.desc || 'Failed to update plan');
          setIsSaving(false);
        }
      );
  };

  const handleBack = () => {
    navigate(`/main/family-group/${id}/plan/${planId}`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="animate-spin text-[#C3485C]" size={48} />
      </div>
    );
  }

  if (error && !planData) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen p-4">
        <p className="text-red-500 mb-4">{error}</p>
        <Button variant="primary" onClick={handleBack}>
          Quay lại
        </Button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-sm mx-auto pb-20">
      <BackButton text="Quay lại" to={`/main/family-group/${id}/plan/${planId}`} onClick={handleBack} className="mb-2" />
      <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">
        Chỉnh Sửa Kế Hoạch
      </h1>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="mb-6">
        <InputField
          label="Tên kế hoạch mua sắm"
          labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
          placeholder="Ví dụ: Mua đồ ăn tối"
          value={planName}
          onChange={(e) => setPlanName(e.target.value)}
        />
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-bold text-gray-800 mb-3">
          Danh sách nguyên liệu
        </h2>
        <div className="relative">
          <InputField
            label="Tìm kiếm nguyên liệu"
            placeholder="Ví dụ: Bông cải"
            icon={<Search size={20} />}
            value={ingredientSearch}
            onChange={(e) => setIngredientSearch(e.target.value)}
          />

          {/* --- UI State: Loading --- */}
          {isSearching && (
            <div className="flex flex-col items-center justify-center py-6 text-gray-400">
              <Loader2 className="animate-spin mb-2" size={24} />
              <p className="text-sm font-medium">Đang tìm kiếm...</p>
            </div>
          )}

          {/* --- UI State: Not Found --- */}
          {showNotFound && !isSearching && (
            <div className="flex flex-col items-center justify-center py-6 text-gray-400">
              <Search size={24} className="mb-2 opacity-50" />
              <p className="text-sm font-medium">
                Không tìm thấy nguyên liệu này
              </p>
            </div>
          )}

          {/* --- UI State: Found Result (Show Quantity Input + Add Button) --- */}
          {searchResult && showQuantityInput && (
            <div className="mt-4 flex items-end space-x-2 animate-in fade-in slide-in-from-top-2">
              <InputField
                label="Số lượng"
                placeholder="Ví dụ: 100"
                containerClassName="flex-1"
                value={ingredientQuantity}
                onChange={(e) => setIngredientQuantity(e.target.value)}
                rightLabel={searchResult.measurementUnit || undefined}
              />
              <Button
                variant="secondary"
                size="fit"
                className="h-[42px] w-[42px] px-0 border-none"
                onClick={handleAddIngredient}
                icon={Plus}
              />
            </div>
          )}
        </div>

        {/* Selected Ingredients List */}
        {ingredients.length > 0 && (
          <div className="mt-6">
            <h2 className="text-sm font-bold text-gray-700 mb-4 uppercase">
              NGUYÊN LIỆU ĐÃ CHỌN ({ingredients.length})
            </h2>
            <div className="space-y-3">
              {ingredients.map((ingredient) => (
                <IngredientCard
                  key={ingredient.id}
                  ingredient={ingredient}
                  onDelete={handleDeleteIngredient}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-bold text-gray-800 mb-3">
          Chi tiết bổ sung
        </h2>
        <div className="space-y-4">
          <InputField
            label="Hạn chót"
            type="datetime-local"
            placeholder="Chọn thời gian"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />
          <InputField
            label="Ghi chú"
            placeholder="Nhập ghi chú cho kế hoạch..."
            icon={<FileText size={18} />}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            textarea
            textareaRows={3}
          />
        </div>
      </div>

      {/* Submit Buttons */}
      <div className="flex gap-0">
        <Button
          variant={isSaving ? 'disabled' : 'primary'}
          onClick={handleSubmit}
          size="fit"
          icon={isSaving ? Loader2 : Check}
        >
          {isSaving ? 'Đang lưu...' : 'Lưu thay đổi'}
        </Button>
        <Button
          variant={isSaving ? 'disabled' : 'secondary'}
          onClick={handleBack}
          size="fit"
          icon={X}
        >
          Hủy
        </Button>
      </div>
    </div>
  );
};

export default EditPlan;
