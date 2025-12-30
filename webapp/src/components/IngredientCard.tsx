import { X, Check } from 'lucide-react';

export interface Ingredient {
  id: number;
  name: string;
  category: string;
  quantity: string;
  image: string;
  isChecked?: boolean;
  price?: number;
}

interface IngredientCardProps {
  ingredient: Ingredient;
  onDelete?: (id: number) => void;
  readonly?: boolean;
  onToggle?: () => void;
  onPriceChange?: (value: string) => void;
  formatCurrency?: (val: number) => string;
}

export const IngredientCard = ({
  ingredient,
  onDelete,
  readonly = false,
  onToggle,
  onPriceChange,
  formatCurrency
}: IngredientCardProps) => {
  const hasShoppingFeatures = onToggle !== undefined || onPriceChange !== undefined;

  if (hasShoppingFeatures) {
    // Shopping list mode (for ImplementPlan)
    return (
      <div className="bg-gray-100 rounded-2xl overflow-hidden">
        {/* Top part: Image and Info */}
        <div className="flex p-3 relative">
          <img
            src={ingredient.image}
            alt={ingredient.name}
            className="w-24 h-16 object-cover rounded-xl mr-3 flex-shrink-0"
          />
          <div className="flex flex-col justify-center">
            <h3 className="font-bold text-base">{ingredient.name}</h3>
            <p className="text-gray-500 text-xs">{ingredient.category}</p>
          </div>
          <div className="absolute top-3 right-3 bg-white px-2 py-1 rounded-full text-xs font-medium text-gray-600 shadow-sm">
            {ingredient.quantity}
          </div>
        </div>

        {/* Divider */}
        <div className="h-px bg-gray-200 mx-3"></div>

        {/* Bottom part: Checkbox and Price Input */}
        <div className="flex items-center justify-between p-3 bg-gray-50">
          <div className="flex items-center">
            {/* Custom styled checkbox */}
            <label className="relative flex items-center p-1 rounded-full cursor-pointer mr-4">
              <input
                type="checkbox"
                className="peer hidden"
                checked={ingredient.isChecked}
                onChange={onToggle}
              />
              <span className="w-6 h-6 border-2 border-gray-700 rounded-md peer-checked:bg-black peer-checked:border-black flex items-center justify-center transition-colors">
                {ingredient.isChecked && <Check size={16} color="white" strokeWidth={3} />}
              </span>
            </label>
          </div>

          {onPriceChange && formatCurrency && (
            <div className="flex items-center gap-2 flex-1 justify-end">
              <span className="text-gray-700 font-medium">Chi:</span>
              <div className="flex items-center bg-white rounded-lg px-3 py-1.5 border border-gray-200 w-36 justify-end">
                <input
                  type="text"
                  inputMode="numeric"
                  value={ingredient.isChecked ? formatCurrency(ingredient.price || 0) : '0'}
                  onChange={(e) => ingredient.isChecked && onPriceChange(e.target.value)}
                  className="w-full text-right font-medium outline-none bg-transparent"
                  readOnly={!ingredient.isChecked}
                />
                <span className="text-gray-500 ml-1 text-sm">VND</span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Simple mode (for existing uses)
  return (
    <div className="flex items-center justify-between p-3 bg-gray-100 rounded-xl mb-2">
      <div className="flex items-center space-x-3">
        <img
          src={ingredient.image}
          alt={ingredient.name}
          className="w-12 h-12 object-cover rounded-lg"
        />
        <div>
          <h4 className="font-bold text-sm text-gray-800">{ingredient.name}</h4>
          <p className="text-xs text-gray-500">{ingredient.category}</p>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-600">{ingredient.quantity}</span>
        {!readonly && onDelete && (
          <button onClick={() => onDelete(ingredient.id)} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        )}
      </div>
    </div>
  );
};
