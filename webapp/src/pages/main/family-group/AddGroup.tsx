import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Check } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { groupService } from '../../../services/group';

const AddGroup: React.FC = () => {
  const navigate = useNavigate();

  // --- State Management ---
  const [groupName, setGroupName] = useState('');

  // Loading and error states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleSubmit = async () => {
    // Validate group name
    if (!groupName.trim()) {
      setSubmitError('Vui lòng nhập tên nhóm');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    const result = await groupService.createGroup(groupName.trim());

    result.match(
      () => {
        // Success - navigate back to list
        navigate('/main/family-group');
      },
      (error) => {
        console.error('Failed to create group:', error);
        if (error.type === 'unauthorized') {
          setSubmitError('Bạn cần đăng nhập để tạo nhóm');
        } else if (error.type === 'validation-error') {
          setSubmitError('Dữ liệu không hợp lệ');
        } else if (error.type === 'network-error') {
          setSubmitError('Lỗi kết nối mạng');
        } else {
          setSubmitError('Không thể tạo nhóm');
        }
      }
    );

    setIsSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-white p-6 pb-24 relative">
      {/* 1. Header */}
      <div className="relative mb-6 flex items-center">
        <BackButton
          text="Quay lại"
          to="/main/family-group"
          className="absolute left-0"
        />
      </div>
      <h1 className="text-xl font-bold text-[#C3485C] text-center">
        Tạo Nhóm Mới
      </h1>

      {/* 2. Group Image Upload */}
      <div className="flex flex-col items-center mb-8">
        <div className="relative">
          <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center">
            {/* Placeholder for avatar */}
          </div>
          <button className="absolute bottom-0 right-0 bg-gray-200 p-2 rounded-full text-gray-600 hover:bg-gray-300 transition-colors border-2 border-white">
            <Camera size={20} />
          </button>
        </div>
        <p className="text-sm font-medium text-gray-700 mt-3">
          Tải ảnh nhóm lên
        </p>
      </div>

      {/* 3. Form Fields */}
      <div className="space-y-6">
        <InputField
          label="Tên nhóm gia đình"
          labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
          placeholder="Ví dụ: Gia đình haha"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
        />
      </div>

      {/* 4. Submit Button */}
      <div className="mt-10">
        {submitError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{submitError}</p>
          </div>
        )}
        <Button
          variant={isSubmitting ? 'disabled' : 'primary'}
          onClick={handleSubmit}
          size="fit"
          icon={Check}
        >
          {isSubmitting ? 'Đang tạo...' : 'Tạo nhóm'}
        </Button>
      </div>
    </div>
  );
};

export default AddGroup;
