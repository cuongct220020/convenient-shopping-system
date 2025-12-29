import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { Plus, DollarSign, FileText, Check, Search } from 'lucide-react';
import { IngredientCard, Ingredient } from '../../../components/IngredientCard';

// Dummy image for broccoli
const BROCCOLI_IMAGE_URL = 'https://i.imgur.com/0Zl3xYm.png';

// Mock database of available ingredients
const MOCK_INGREDIENTS = [
  { id: 'ing-1', name: 'Bông cải', category: 'Rau', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-2', name: 'Cà rốt', category: 'Rau', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-3', name: 'Thịt gà', category: 'Thịt', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-4', name: 'Cà chua', category: 'Rau', image: BROCCOLI_IMAGE_URL },
  { id: 'ing-5', name: 'Trứng', category: 'Đồ tươi', image: BROCCOLI_IMAGE_URL },
];

const AddPlan = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [planName, setPlanName] = useState('');
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [ingredientQuantity, setIngredientQuantity] = useState('');
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);

  // Search states
  const [searchResult, setSearchResult] = useState<typeof MOCK_INGREDIENTS[0] | null>(null);
  const [showNotFound, setShowNotFound] = useState(false);
  const [showQuantityInput, setShowQuantityInput] = useState(false);

  const [deadline, setDeadline] = useState('');
  const [budget, setBudget] = useState('');
  const [notes, setNotes] = useState('');

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
        setShowNotFound(true); // Treat already added as "not found" for adding purposes
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

  const handleCreatePlan = () => {
    console.log({
      planName,
      ingredients,
      deadline,
      budget,
      notes,
    });
    navigate(`/main/family-group/${id}`); // Navigate back to group detail after creation
  };

  return (
    <div className="p-4 max-w-sm mx-auto pb-20">
      <BackButton text="Quay lại" to={`/main/family-group/${id}`} className="mb-2" />
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
            label="Ngân sách"
            placeholder="0 VND"
            icon={<DollarSign size={18} />}
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
          />
          <InputField
            label="Ghi chú"
            placeholder="Nhập ghi chú cho kế hoạch..."
            icon={<FileText size={18} />}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>
      </div>

      <Button
        variant="primary"
        size="fit"
        onClick={handleCreatePlan}
        icon={Check}
      >
        Tạo kế hoạch
      </Button>
    </div>
  );
};

export default AddPlan;