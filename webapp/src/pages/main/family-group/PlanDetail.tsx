import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Check, Clock, User, DollarSign, Calendar } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { IngredientCard } from '../../../components/IngredientCard';

// Define interface for dummy data
interface IngredientReadonly {
  id: number;
  name: string;
  category: string;
  quantity: string;
  image: string;
}

// Hardcoded data to match the screenshot
const planData = {
  title: "Mua đồ ăn tối",
  status: "Đang chờ",
  creator: "Bùi Mạnh Hưng",
  budget: "500.000 VND",
  deadline: "21:00 - Thứ 4, 24/12/2025",
  note: "Nhớ mua ở đồ ở siêu thị, đừng mua đồ ở chợ để đảm bảo vệ sinh an toàn thực phẩm. Mua xong nhớ nhắn tin cho Hưng để thông báo. Về nhà nhớ cất đồ dễ hỏng vào tủ lạnh để bảo quản. Sau đó nhớ cập nhật trạng thái tủ lạnh trong app.",
};

// Using a placeholder image URL. In a real app, this would be a local asset or URL.
const placeholderImage = "https://placehold.co/100x80/4CAF50/FFFFFF?text=Broccoli";

const ingredientsList: IngredientReadonly[] = [
  { id: 1, name: 'Bông cải', category: 'Rau', quantity: '100g', image: placeholderImage },
  { id: 2, name: 'Bông cải', category: 'Rau', quantity: '100g', image: placeholderImage },
  { id: 3, name: 'Bông cải', category: 'Rau', quantity: '100g', image: placeholderImage },
];

export const PlanDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const handleBack = () => {
    navigate(`/main/family-group/${id}`, { state: { activeTab: 'shopping-plan' } });
  };

  return (
    <div className="bg-white min-h-screen relative pb-8">
      {/* Header Container with padding */}
      <div className="p-4">
        {/* Header Nav */}
        <div className="mb-2">
          <BackButton text="Quay lại" to={`/main/family-group/${id}`} onClick={handleBack} />
        </div>
        <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">Chi Tiết Kế Hoạch</h1>

        {/* Info Cards Grid */}
        <div className="grid grid-cols-2 gap-3 mb-3">
          {/* Card 1: Plan Name */}
          <div className="bg-[#F3F4F6] p-4 rounded-[20px]">
            <h3 className="font-bold text-sm mb-1">Tên kế hoạch</h3>
            <p className="text-sm font-medium">{planData.title}</p>
          </div>

          {/* Card 2: Status */}
          <div className="bg-[#F3F4F6] p-4 rounded-[20px]">
            <h3 className="font-bold text-sm mb-1">Trạng thái</h3>
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-[#FFD7C1] text-[#C3485C] text-xs font-bold">
              <Clock size={14} className="mr-1" strokeWidth={3} /> {planData.status}
            </div>
          </div>

          {/* Card 3: Creator */}
          <div className="bg-[#F3F4F6] p-4 rounded-[20px]">
            <div className="flex items-center font-bold text-sm mb-1">
              <User size={18} className="mr-2" strokeWidth={2.5} /> Người tạo
            </div>
            <p className="text-sm font-medium">{planData.creator}</p>
          </div>

          {/* Card 4: Budget */}
          <div className="bg-[#F3F4F6] p-4 rounded-[20px]">
            <div className="flex items-center font-bold text-sm mb-1">
              <DollarSign size={18} className="mr-2" strokeWidth={2.5} /> Ngân sách
            </div>
            <p className="text-sm font-medium">{planData.budget}</p>
          </div>
        </div>

        {/* Date Card (Full Width) */}
        <div className="bg-[#F3F4F6] p-4 rounded-[20px] mb-6 flex items-start">
          <Calendar size={20} className="mr-3 mt-0.5 text-gray-800" strokeWidth={2.5} />
          <div>
            <h3 className="font-bold text-sm mb-1">Hạn chót</h3>
            <p className="text-sm font-medium">{planData.deadline}</p>
          </div>
        </div>

        {/* Note Section */}
        <div className="mb-8">
          <div className="flex items-center font-bold mb-2 text-sm">
            <FileText size={18} className="mr-2" strokeWidth={2.5} /> Ghi chú
          </div>
          <div className="border border-gray-400 rounded-[20px] p-4 text-sm leading-relaxed font-medium">
            {planData.note}
          </div>
        </div>

        {/* Ingredient List Section */}
        <h2 className="font-bold text-lg mb-4">Danh sách nguyên liệu</h2>
        <div className="mb-10">
          {ingredientsList.map((ingredient) => (
            <IngredientCard
              key={ingredient.id}
              ingredient={ingredient}
              onDelete={() => {}}
              readonly
            />
          ))}
        </div>

        {/* Footer Button */}
        <div className="flex justify-center">
          <Button
            variant="primary"
            size="fit"
            icon={Check}
            className="!px-10 !py-3 text-base rounded-2xl shadow-lg shadow-red-200/50"
          >
            Duyệt kế hoạch
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PlanDetail;