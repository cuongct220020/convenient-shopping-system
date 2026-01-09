import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { Plus, FileText, Check, Search, X } from 'lucide-react';
import { IngredientCard, Ingredient } from '../../../components/IngredientCard';

// Dummy image for ingredients
const BROCCOLI_IMAGE_URL = 'https://i.imgur.com/0Zl3xYm.png';

// Mock database of available ingredients
const MOCK_INGREDIENTS = [
  { id: 'ing-1', name: 'Bông cải', category: 'Rau', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-2', name: 'Cà rốt', category: 'Rau', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-3', name: 'Thịt gà', category: 'Thịt', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-4', name: 'Cà chua', category: 'Rau', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-5', name: 'Trứng', category: 'Đồ tươi', image: BROCCOLI_IMAGE_URL },
];

type PlanData = {
  id: string;
  title: string;
  status: string;
  creator: string;
  deadline: string;
  note: string;
  ingredients: Ingredient[];
};

const EditPlan: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { id, planId } = useParams<{ id: string; planId: string }>();
  const planToEdit = location.state?.plan as PlanData;

  if (!planToEdit || !id || !planId) {
    navigate(`/main/family-group/${id}`);
    return null;
  }

  // --- State Management ---
  // Parse deadline to datetime-local format
  const parseDeadlineToLocal = (deadlineStr: string): string => {
    // Assuming format like "21:00 - Thứ 4, 24/12/2025"
    // For edit, we'll use a simple date format or return empty
    // In a real app, you'd parse this properly
    return '';
  };

  const [planName, setPlanName] = useState(planToEdit.title);
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [ingredientQuantity, setIngredientQuantity] = useState('');
  const [ingredients, setIngredients] = useState<Ingredient[]>(planToEdit.ingredients);

  // Search states
  const [searchResult, setSearchResult] = useState<typeof MOCK_INGREDIENTS[0] | null>(null);
  const [showNotFound, setShowNotFound] = useState(false);
  const [showQuantityInput, setShowQuantityInput] = useState(false);

  const [deadline, setDeadline] = useState(parseDeadlineToLocal(planToEdit.deadline));
  const [notes, setNotes] = useState(planToEdit.note);

  // --- Search Logic (Debounced) ---
  useEffect(() => {
    // 300ms delay to simulate network request and avoid flickering
    const delayDebounceFn = setTimeout(() => {
      if (!ingredientSearch.trim()) {
        setSearchResult(null);
        setShowNotFound(false);
        setShowQuantityInput(false);
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
        return;
      }

      // Simulate finding the ingredient from mock database
      const found = MOCK_INGREDIENTS.find(
        (ing) => ing.name.toLowerCase() === ingredientSearch.toLowerCase()
      );

      if (found) {
        setSearchResult(found);
        setShowNotFound(false);
        setShowQuantityInput(true);
      } else {
        setSearchResult(null);
        setShowNotFound(true);
        setShowQuantityInput(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [ingredientSearch, ingredients]);

  // --- Handlers ---
  const handleAddIngredient = () => {
    if (searchResult && ingredientQuantity) {
      const newIngredient: Ingredient = {
        id: Date.now(),
        name: searchResult.name,
        category: searchResult.category,
        quantity: ingredientQuantity,
        image: searchResult.image,
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
    console.log({
      planName,
      ingredients,
      deadline,
      notes,
    });
    navigate(`/main/family-group/${id}/plan/${planId}`);
  };

  const handleBack = () => {
    navigate(`/main/family-group/${id}/plan/${planId}`);
  };

  return (
    <div className="p-4 max-w-sm mx-auto pb-20">
      <BackButton text="Quay lại" to={`/main/family-group/${id}/plan/${planId}`} onClick={handleBack} className="mb-2" />
      <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">
        Chỉnh Sửa Kế Hoạch
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

          {/* --- UI State: Not Found --- */}
          {showNotFound && (
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
                placeholder="Ví dụ: 100g"
                containerClassName="flex-1"
                value={ingredientQuantity}
                onChange={(e) => setIngredientQuantity(e.target.value)}
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
          variant="primary"
          onClick={handleSubmit}
          size="fit"
          icon={Check}
        >
          Lưu thay đổi
        </Button>
        <Button
          variant="secondary"
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
