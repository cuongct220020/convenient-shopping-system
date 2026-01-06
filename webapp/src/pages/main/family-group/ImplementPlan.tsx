import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ClipboardList,
  DollarSign,
  Check,
  X,
  AlertTriangle
} from 'lucide-react';
import { Button } from '../../../components/Button';
import { BackButton } from '../../../components/BackButton';
import { IngredientCard, Ingredient } from '../../../components/IngredientCard';

// Define interface for an ingredient item data structure
interface IngredientItemData extends Ingredient {
  isChecked: boolean;
  price: number;
}

const planTitle = "Mua Đồ Ăn Tối";

// Mock data based on the image content
const initialData: IngredientItemData[] = [
  { id: 1, name: 'Bông cải', category: 'Rau', quantity: '100g', image: 'https://placehold.co/80x60/green/white?text=Broccoli', isChecked: false, price: 0 },
  { id: 2, name: 'Bông cải', category: 'Rau', quantity: '100g', image: 'https://placehold.co/80x60/green/white?text=Broccoli', isChecked: false, price: 0 },
  { id: 3, name: 'Bông cải', category: 'Rau', quantity: '100g', image: 'https://placehold.co/80x60/green/white?text=Broccoli', isChecked: true, price: 30000 },
  { id: 4, name: 'Bông cải', category: 'Rau', quantity: '100g', image: 'https://placehold.co/80x60/green/white?text=Broccoli', isChecked: true, price: 30000 },
  { id: 5, name: 'Bông cải', category: 'Rau', quantity: '100g', image: 'https://placehold.co/80x60/green/white?text=Broccoli', isChecked: true, price: 30000 },
  { id: 6, name: 'Bông cải', category: 'Rau', quantity: '100g', image: 'https://placehold.co/80x60/green/white?text=Broccoli', isChecked: false, price: 0 },
];

export default function ImplementPlan() {
  const navigate = useNavigate();
  const { id, plan_id } = useParams<{ id: string; plan_id: string }>();
  const [items, setItems] = useState<IngredientItemData[]>(initialData);
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);

  useEffect(() => {
    const bottomNav = document.querySelector('nav.fixed.bottom-0');
    if (bottomNav) {
      if (isCompleteModalOpen || isCancelModalOpen) {
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
  }, [isCompleteModalOpen, isCancelModalOpen]);

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
        item.id === id ? { ...item, isChecked: !item.isChecked } : item
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

  const handleCompletePlan = () => {
    console.log('Completing plan...');
    setIsCompleteModalOpen(false);
    navigate(`/main/family-group/${id}/plan/${plan_id}`);
  };

  const handleCancelPlan = () => {
    console.log('Canceling plan...');
    setIsCancelModalOpen(false);
    navigate(`/main/family-group/${id}/plan/${plan_id}`);
  };

  return (
    <div className="min-h-screen bg-white pb-6">
      {/* Header */}
      <div className="pt-4 px-4 mb-4">
        <BackButton onClick={() => navigate(-1)} text="Quay lại" />
      </div>

      <h1 className="text-xl font-bold text-[#D3314D] text-center mb-4">
        Mua Đồ Ăn Tối
      </h1>

      <div className="px-4">
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
          {items.map((item) => (
            <IngredientCard
              key={item.id}
              ingredient={item}
              onToggle={() => handleToggle(item.id)}
              onPriceChange={(val) => handlePriceChange(item.id, val)}
              formatCurrency={formatCurrency}
            />
          ))}
        </div>

        {/* Bottom Action Buttons */}
        <div className="flex gap-4 mt-6">
          <Button
            variant="primary"
            icon={Check}
            size="fit"
            className="rounded-2xl"
            onClick={() => setIsCompleteModalOpen(true)}
          >
            Hoàn thành
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
      </div>

      {/* COMPLETE PLAN CONFIRMATION MODAL */}
      {isCompleteModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Hoàn Thành Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center"><Check size={36} className="text-white" strokeWidth={3} /></div></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn hoàn thành kế hoạch <span className="text-[#C3485C] font-semibold">{planTitle}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleCompletePlan} icon={Check} className="bg-[#C3485C] hover:bg-[#a83648]">Xác nhận</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsCompleteModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}

      {/* CANCEL PLAN CONFIRMATION MODAL */}
      {isCancelModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-5 text-center">Hủy Kế Hoạch?</h3>
            <div className="flex justify-center mb-5"><AlertTriangle size={64} className="text-white fill-[#C3485C]" strokeWidth={1.5} /></div>
            <p className="text-sm text-center text-gray-600 mb-6 leading-relaxed">Bạn có chắc muốn hủy kế hoạch <span className="text-[#C3485C] font-semibold">{planTitle}</span>?</p>
            <div className="flex gap-3 justify-center">
              <div className="w-1/2"><Button variant="primary" onClick={handleCancelPlan} icon={Check} className="bg-[#C3485C] hover:bg-[#a83648]">Xác nhận</Button></div>
              <div className="w-1/2"><Button variant="secondary" onClick={() => setIsCancelModalOpen(false)} icon={X} className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]">Hủy</Button></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}