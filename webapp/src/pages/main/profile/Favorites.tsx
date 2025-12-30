import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Heart } from 'lucide-react';

// Mock data based on the image content
const favoriteMeals = [
  {
    id: 1,
    title: "Gà chiên mắm rang sả ớt",
    description: "Món ngon đưa cơm trong những ngày hè nóng...",
    // Using a placeholder image to represent the food item
    image: "https://placehold.co/200x200/e2e8f0/64748b?text=G%C3%A0+Chi%C3%AAn"
  },
  {
    id: 2,
    title: "Gà chiên mắm rang sả ớt",
    description: "Món ngon đưa cơm trong những ngày hè nóng...",
    image: "https://placehold.co/200x200/e2e8f0/64748b?text=G%C3%A0+Chi%C3%AAn"
  },
  {
    id: 3,
    title: "Gà chiên mắm rang sả ớt",
    description: "Món ngon đưa cơm trong những ngày hè nóng...",
    image: "https://placehold.co/200x200/e2e8f0/64748b?text=G%C3%A0+Chi%C3%AAn"
  },
  {
    id: 4,
    title: "Gà chiên mắm rang sả ớt",
    description: "Món ngon đưa cơm trong những ngày hè nóng...",
    image: "https://placehold.co/200x200/e2e8f0/64748b?text=G%C3%A0+Chi%C3%AAn"
  },
];

const Favorites = () => {
  const navigate = useNavigate();

  return (
    // Container follows the same style as Profile.tsx and LoginInformation.tsx
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full pb-24">
      
      {/* Header / Back Navigation */}
      <button
        onClick={() => navigate(-1)} // Go back to the previous screen
        className="flex items-center text-red-600 mb-6"
      >
        <ChevronLeft size={24} />
        <span className="ml-1 text-lg font-bold">Quay lại</span>
      </button>

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-6">
        Danh mục yêu thích
      </h1>

      {/* List of Favorite Meals */}
      <div className="flex flex-col gap-4">
        {favoriteMeals.map((meal) => (
          <div key={meal.id} className="flex bg-gray-100 p-2 rounded-2xl">
            
            {/* Meal Image */}
            <img
              src={meal.image}
              alt={meal.title}
              className="w-24 h-24 rounded-xl object-cover shrink-0"
            />
            
            {/* Meal Information */}
            <div className="ml-3 flex-1 flex flex-col justify-center">
              <div className="flex justify-between items-start">
                <h3 className="font-bold text-base text-gray-900 line-clamp-2">
                  {meal.title}
                </h3>
                {/* Heart Icon indicating favorite status */}
                <Heart className="text-red-500 fill-red-500 ml-2 shrink-0" size={20} />
              </div>
              <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                {meal.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Favorites;