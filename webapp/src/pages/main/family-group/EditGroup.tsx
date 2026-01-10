import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Camera, Check, X } from 'lucide-react';
import { BackButton } from '../../../components/BackButton';
import { InputField } from '../../../components/InputField';
import { Button } from '../../../components/Button';
import { groupService } from '../../../services/group';

const EditGroup: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const [groupName, setGroupName] = useState('');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [groupError, setGroupError] = useState<string | null>(null);

  // Fetch group detail
  useEffect(() => {
    if (!id) return;

    const fetchGroup = async () => {
      setIsLoading(true);
      setGroupError(null);

      const groupResult = await groupService.getGroupById(id);

      groupResult.match(
        (response) => {
          setGroupName(response.data.group_name);
          setAvatarUrl(response.data.group_avatar_url);
        },
        (err) => {
          console.error('Failed to fetch group detail:', err);
          if (err.type === 'unauthorized') {
            setGroupError('Bạn cần đăng nhập để xem nhóm');
          } else if (err.type === 'not-found') {
            setGroupError('Không tìm thấy nhóm');
          } else {
            setGroupError('Không thể tải thông tin nhóm');
          }
        }
      );

      setIsLoading(false);
    };

    fetchGroup();
  }, [id]);

  const handleSubmit = async () => {
    if (!id) return;

    // Validate group name
    if (!groupName.trim()) {
      setSubmitError('Vui lòng nhập tên nhóm');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    const result = await groupService.updateGroup(id, groupName.trim(), avatarUrl ?? undefined);

    result.match(
      () => {
        // Success - navigate back to detail view with refresh state
        navigate(`/main/family-group/${id}`, { state: { refresh: true, returningFromEdit: true } });
      },
      (error) => {
        console.error('Failed to update group:', error);
        if (error.type === 'unauthorized') {
          setSubmitError('Bạn cần đăng nhập để chỉnh sửa nhóm');
        } else if (error.type === 'not-found') {
          setSubmitError('Không tìm thấy nhóm');
        } else if (error.type === 'validation-error') {
          setSubmitError('Dữ liệu không hợp lệ');
        } else if (error.type === 'network-error') {
          setSubmitError('Lỗi kết nối mạng');
        } else {
          setSubmitError('Không thể cập nhật nhóm');
        }
      }
    );

    setIsSubmitting(false);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C3485C]"></div>
        <p className="text-gray-600 mt-4">Đang tải...</p>
      </div>
    );
  }

  // Error state
  if (groupError) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <p className="text-red-500 mb-4">{groupError}</p>
        <Button
          variant="primary"
          size="fit"
          onClick={() => navigate('/main/family-group')}
        >
          Quay lại
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6 pb-24 relative">
      {/* 1. Header */}
      <div className="relative mb-6 flex items-center">
        <BackButton
          text="Quay lại"
          to={`/main/family-group/${id}`}
          className="absolute left-0"
        />
      </div>
      <h1 className="text-xl font-bold text-[#C3485C] text-center">
        Chỉnh Sửa Nhóm
      </h1>

      {/* 2. Group Image Upload */}
      <div className="flex flex-col items-center mb-8">
        <div className="relative">
          <img
            src={avatarUrl || new URL('../../../assets/family.png', import.meta.url).href}
            alt="Group avatar"
            className="w-32 h-32 rounded-full object-cover"
          />
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

      {/* 4. Submit Buttons */}
      <div className="mt-10 flex gap-0">
        {submitError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg w-full">
            <p className="text-red-600 text-sm">{submitError}</p>
          </div>
        )}
        <Button
          variant={isSubmitting ? 'disabled' : 'primary'}
          onClick={handleSubmit}
          size="fit"
          icon={Check}
        >
          {isSubmitting ? 'Đang lưu...' : 'Lưu thay đổi'}
        </Button>
        <Button
          variant="secondary"
          onClick={() => navigate(`/main/family-group/${id}`)}
          size="fit"
          icon={X}
        >
          Hủy
        </Button>
      </div>
    </div>
  );
};

export default EditGroup;
