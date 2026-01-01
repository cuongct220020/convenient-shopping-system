import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Check, Clock, User, DollarSign, Calendar, AlertTriangle, X, Settings, Edit2, Trash2, ArrowRight } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { IngredientCard } from '../../../components/IngredientCard';

// Define interface for dummy data
interface IngredientReadonly {
  id: number
  name: string
  category: string
  quantity: string
  image: string
  price?: number
}

// Hardcoded data to match the screenshot
const planData = {
  title: "Mua đồ ăn tối",
  status: "Đã xong",
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

const boughtIngredientsList: IngredientReadonly[] = [
  { id: 4, name: 'Cà rốt', category: 'Rau', quantity: '200g', image: placeholderImage, price: 15000 },
  { id: 5, name: 'Khoai lang', category: 'Củ', quantity: '300g', image: placeholderImage, price: 25000 },
];

export const PlanDetail = () => {
  const { id, planId } = useParams<{ id: string; planId: string }>();
  const navigate = useNavigate();
  const [isApproveModalOpen, setIsApproveModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

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
    const planForEdit = {
      id: planId,
      title: planData.title,
      status: planData.status,
      creator: planData.creator,
      budget: planData.budget,
      deadline: planData.deadline,
      note: planData.note,
      ingredients: ingredientsList.map(ing => ({
        id: ing.id,
        name: ing.name,
        category: ing.category,
        quantity: ing.quantity,
        image: ing.image,
      })),
    };
    navigate(`/main/family-group/${id}/plan/${planId}/edit`, {
      state: { plan: planForEdit },
    });
    setIsSettingsOpen(false);
  };

  const handleDeletePlan = () => {
    console.log('Deleting plan...');
    setIsDeleteModalOpen(false);
    navigate(`/main/family-group/${id}`, { state: { activeTab: 'shopping-plan' } });
  };

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      minimumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="bg-white min-h-screen relative pb-8" onClick={() => { if (isSettingsOpen) setIsSettingsOpen(false); }}>
      {/* Header Container with padding */}
      <div className="p-4">
        {/* Header Nav */}
        <div className="flex items-center justify-between mb-2">
          <BackButton text="Quay lại" to={`/main/family-group/${id}`} onClick={handleBack} />
          <div className="relative">
            <button onClick={(e) => { e.stopPropagation(); toggleSettings(); }} className="p-2">
              <Settings size={24} className="text-gray-700" />
            </button>

            {/* Settings Popover */}
            {isSettingsOpen && (
              <div className="absolute right-0 top-full mt-2 w-36 bg-white rounded-lg shadow-lg z-10 border border-gray-200 py-1">
                <button onClick={(e) => { e.stopPropagation(); handleEdit(); }} className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center">
                  <Edit2 size={16} className="mr-2" />
                  Chỉnh sửa
                </button>
                <button onClick={(e) => { e.stopPropagation(); setIsSettingsOpen(false); setIsDeleteModalOpen(true); }} className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 flex items-center">
                  <Trash2 size={16} className="mr-2" />
                  Xóa kế hoạch
                </button>
              </div>
            )}
          </div>
        </div>
        <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">Chi Tiết Kế Hoạch</h1>

        {/* Info Cards - 2 Rows */}
        {/* Row 1: Plan Name | Status */}
        <div className="bg-gray-100 rounded-2xl p-4 flex justify-between items-center mb-3">
          {/* Left: Plan Name */}
          <div className="flex flex-col items-center w-1/2 border-r border-gray-300">
            <span className="font-bold text-sm text-gray-700 mb-1">Tên kế hoạch</span>
            <p className="text-sm font-medium">{planData.title}</p>
          </div>

          {/* Right: Status */}
          <div className="flex flex-col items-center w-1/2">
            <div className="flex items-center gap-1 mb-1">
              <Clock size={16} className="text-black" strokeWidth={2.5} />
              <span className="font-bold text-sm text-gray-700">Trạng thái</span>
            </div>
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-[#FFD7C1] text-[#C3485C] text-xs font-bold">
              {planData.status}
            </div>
          </div>
        </div>

        {/* Row 2: Creator | Budget */}
        <div className="bg-gray-100 rounded-2xl p-4 flex justify-between items-center mb-3">
          {/* Left: Creator */}
          <div className="flex flex-col items-center w-1/2 border-r border-gray-300">
            <div className="flex items-center gap-1 mb-1">
              <User size={16} className="text-black" strokeWidth={2.5} />
              <span className="font-bold text-sm text-gray-700">Người tạo</span>
            </div>
            <p className="text-sm font-medium">{planData.creator}</p>
          </div>

          {/* Right: Budget */}
          <div className="flex flex-col items-center w-1/2">
            <div className="flex items-center gap-1 mb-1">
              <DollarSign size={16} className="text-black" strokeWidth={2.5} />
              <span className="font-bold text-sm text-gray-700">Ngân sách</span>
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
        {planData.status === "Đã xong" ? (
          <>
            {/* Nguyên liệu đã mua */}
            <h2 className="font-bold text-lg mb-4">Nguyên liệu đã mua</h2>
            <div className="mb-10">
              {boughtIngredientsList.map((ingredient) => (
                <IngredientCard
                  key={ingredient.id}
                  ingredient={ingredient}
                  onDelete={() => {}}
                  readonly
                  showPrice
                  formatCurrency={formatCurrency}
                />
              ))}
            </div>

            {/* Nguyên liệu chưa mua */}
            <h2 className="font-bold text-lg mb-4">Nguyên liệu chưa mua</h2>
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
          </>
        ) : (
          <>
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
          </>
        )}

        {/* Footer Button */}
        {planData.status !== "Đã xong" && (
          <div className="flex justify-center">
            <Button
              variant="primary"
              size="fit"
              icon={planData.status === "Đang thực hiện" ? ArrowRight : Check}
              className="!px-10 !py-3 text-base rounded-2xl shadow-lg shadow-red-200/50"
              onClick={() => setIsApproveModalOpen(true)}
            >
              {planData.status === "Đang thực hiện" ? "Tiếp tục thực hiện kế hoạch" : "Duyệt kế hoạch"}
            </Button>
          </div>
        )}
      </div>

      {/* APPROVE PLAN CONFIRMATION MODAL */}
      {isApproveModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Duyệt Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center"><Check size={36} className="text-white" strokeWidth={3} /></div></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn duyệt kế hoạch <span className="text-[#C3485C] font-semibold">{planData.title}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleApprovePlan} icon={Check} className="bg-[#C3485C] hover:bg-[#a83648]">Xác nhận</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsApproveModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}

      {/* DELETE PLAN CONFIRMATION MODAL */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Xóa Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><AlertTriangle size={64} className="text-white fill-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Hành động này <span className="text-[#C3485C] font-semibold">không thể hoàn tác</span>. Bạn có chắc muốn xóa kế hoạch <span className="text-[#C3485C] font-semibold">{planData.title}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleDeletePlan} icon={Trash2} className="bg-[#C3485C] hover:bg-[#a83648]">Xóa</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsDeleteModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanDetail;