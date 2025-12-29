import { X } from 'lucide-react';

export interface Ingredient {
  id: number;
  name: string;
  category: string;
  quantity: string;
  image: string;
}

interface IngredientCardProps {
  ingredient: Ingredient;
  onDelete: (id: number) => void;
}

export const IngredientCard = ({ ingredient, onDelete }: IngredientCardProps) => {
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
        <button onClick={() => onDelete(ingredient.id)} className="text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>
      </div>
    </div>
  );
};
