import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { Plus, FileText, Check, Search, Loader2 } from 'lucide-react';
import { IngredientCard, Ingredient } from '../../../components/IngredientCard';
import { shoppingPlanService } from '../../../services/shopping-plan';
import { userService } from '../../../services/user';
import { ingredientService } from '../../../services/ingredient';
import { groupService } from '../../../services/group';
import type { PlanItemBase } from '../../../services/schema/shoppingPlanSchema';
import type { Ingredient as IngredientSearchResult } from '../../../services/schema/ingredientSchema';

// Default ingredient image
const DEFAULT_INGREDIENT_IMAGE = new URL('../../../assets/ingredient.png', import.meta.url).href;
// Default group avatar
const DEFAULT_GROUP_AVATAR = new URL('../../../assets/family.png', import.meta.url).href;

// Extended ingredient type to include original search result data
type ExtendedIngredient = Ingredient & {
  originalItem?: IngredientSearchResult;
  numericQuantity?: number;  // Store the numeric value entered by user
  measurementUnit?: string;  // Store the unit from API (e.g., "g", "ml")
};

const AddPlan = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [planName, setPlanName] = useState('');
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [ingredientQuantity, setIngredientQuantity] = useState('');
  const [ingredients, setIngredients] = useState<ExtendedIngredient[]>([]);

  // Group data state
  const [groupName, setGroupName] = useState<string>('');
  const [groupAvatar, setGroupAvatar] = useState<string>(DEFAULT_GROUP_AVATAR);

  // Search states
  const [searchResult, setSearchResult] = useState<IngredientSearchResult | null>(null);
  const [showNotFound, setShowNotFound] = useState(false);
  const [showQuantityInput, setShowQuantityInput] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const [deadline, setDeadline] = useState('');
  const [notes, setNotes] = useState('');

  // Loading and error states
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Fetch group data on mount
  useEffect(() => {
    if (!id) return;

    const fetchGroup = async () => {
      const result = await groupService.getGroupById(id);
      result.match(
        (response) => {
          setGroupName(response.data.group_name);
          setGroupAvatar(response.data.group_avatar_url || DEFAULT_GROUP_AVATAR);
        },
        (error) => {
          console.error('Failed to fetch group:', error);
        }
      );
    };

    fetchGroup();
  }, [id]);

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
        setShowNotFound(true); // Treat already added as "not found" for adding purposes
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
        originalItem: searchResult,
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

  const handleCreatePlan = async () => {
    if (!id) return;

    setIsCreating(true);
    setCreateError(null);

    // Fetch current user to get assigner_id
    const userResult = await userService.getCurrentUser();

    userResult.match(
      async (userResponse) => {
        const assignerId = userResponse.data.id;

        // Convert deadline to ISO format if provided
        let deadlineISO = '';
        if (deadline) {
          deadlineISO = new Date(deadline).toISOString();
        }

        // Map ingredients to shopping list format
        const shoppingList: PlanItemBase[] = ingredients.map((ing) => {
          // For new ingredients with numeric quantity and measurement unit
          if (ing.numericQuantity !== undefined && ing.measurementUnit) {
            return {
              type: ing.originalItem?.type || 'countable_ingredient',
              unit: ing.measurementUnit,
              quantity: ing.numericQuantity,
              component_id: ing.originalItem?.component_id || 0,
              component_name: ing.name
            };
          }

          // Fallback for ingredients without separate numeric/unit
          return {
            type: ing.originalItem?.type || 'countable_ingredient',
            unit: ing.quantity,
            quantity: 1,
            component_id: ing.originalItem?.component_id || 0,
            component_name: ing.name
          };
        });

        // Build others object from plan name and notes
        const others: Record<string, unknown> = {};
        if (planName) others.name = planName;
        if (notes) others.notes = notes;

        // Debug logging
        console.log('Creating plan with shopping list:', JSON.stringify(shoppingList, null, 2));
        console.log('Others:', others);

        const result = await shoppingPlanService.createPlan({
          groupId: id,
          deadline: deadlineISO,
          assignerId: assignerId,
          shoppingList,
          others: Object.keys(others).length > 0 ? others : undefined
        });

        result.match(
          () => {
            navigate(`/main/family-group/${id}`, { state: { activeTab: 'shopping-plan' } });
          },
          (error) => {
            console.error('Failed to create plan:', error);
            if (error.type === 'unauthorized') {
              setCreateError('Bạn cần đăng nhập để tạo kế hoạch');
            } else {
              setCreateError('Không thể tạo kế hoạch mua sắm');
            }
            setIsCreating(false);
          }
        );
      },
      (error) => {
        console.error('Failed to get current user:', error);
        setCreateError('Không thể lấy thông tin người dùng');
        setIsCreating(false);
      }
    );
  };

  const handleBack = () => {
    navigate(`/main/family-group/${id}`, { state: { activeTab: 'shopping-plan' } });
  };

  return (
    <div className="p-4 max-w-sm mx-auto pb-20">
      <BackButton text="Quay lại" to={`/main/family-group/${id}`} state={{ activeTab: 'shopping-plan' }} className="mb-2" />

      {/* Group Avatar Display */}
      <div className="flex flex-col items-center mb-4">
        <img
          src={groupAvatar}
          alt={groupName || 'Group'}
          className="w-16 h-16 rounded-full object-cover"
        />
        {groupName && (
          <p className="text-sm text-gray-600 mt-1">{groupName}</p>
        )}
      </div>

      <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">
        Tạo Kế Hoạch Mới
      </h1>

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

      {createError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <p className="text-sm text-red-600">{createError}</p>
        </div>
      )}

      <Button
        variant={isCreating ? 'disabled' : 'primary'}
        size="fit"
        onClick={handleCreatePlan}
        icon={Check}
      >
        {isCreating ? 'Đang tạo...' : 'Tạo kế hoạch'}
      </Button>
    </div>
  );
};

export default AddPlan;