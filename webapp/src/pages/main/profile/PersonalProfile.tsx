import React, { useState } from 'react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { NotificationCard } from '../../../components/NotificationCard';
import { Save, X } from 'lucide-react';

const PersonalProfile = () => {
  // State for gender selection to mimic the radio button behavior in the image
  const [gender, setGender] = useState<'nam' | 'nu' | 'khac'>('nam');

  // State for edit mode
  const [isEditMode, setIsEditMode] = useState(false);

  // State for form values
  const [formData, setFormData] = useState({
    fullName: '',
    address: 'Số 12A đường Ngô Quyền, quận Hoàn Kiếm',
    job: 'Huấn luyện viên thể hình',
    phoneNumber: '',
    dateOfBirth: '28/10/2000'
  });

  // State for modal visibility and original values
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [originalValues, setOriginalValues] = useState({
    fullName: '',
    address: 'Số 12A đường Ngô Quyền, quận Hoàn Kiếm',
    job: 'Huấn luyện viên thể hình',
    phoneNumber: '',
    dateOfBirth: '28/10/2000',
    gender: 'nam' as 'nam' | 'nu' | 'khac'
  });

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full pb-24">
      
      {/* Back Navigation */}
      <BackButton to="/main/profile" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-6">
        Hồ sơ cá nhân
      </h1>

      <div className="flex flex-col gap-6">
        
        {/* Full Name */}
        <InfoSection
          label="Họ và tên"
          value={formData.fullName}
          isPlaceholder={!formData.fullName}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, fullName: value})}
        />

        {/* Address */}
        <InfoSection
          label="Địa chỉ"
          value={formData.address}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, address: value})}
        />

        {/* Job */}
        <InfoSection
          label="Nghề nghiệp"
          value={formData.job}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, job: value})}
        />

        {/* Phone Number */}
        <InfoSection
          label="Số điện thoại"
          value={formData.phoneNumber}
          isPlaceholder={!formData.phoneNumber}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, phoneNumber: value})}
        />

        {/* Date of Birth */}
        <InfoSection
          label="Ngày sinh"
          value={formData.dateOfBirth}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, dateOfBirth: value})}
        />

        {/* Gender Selection */}
        <div>
          <h3 className="font-bold text-black mb-3 text-base">Giới tính</h3>
          {isEditMode ? (
            <div className="flex items-center gap-8">
              <RadioButton
                label="Nam"
                selected={gender === 'nam'}
                onClick={() => setGender('nam')}
              />
              <RadioButton
                label="Nữ"
                selected={gender === 'nu'}
                onClick={() => setGender('nu')}
              />
              <RadioButton
                label="Khác"
                selected={gender === 'khac'}
                onClick={() => setGender('khac')}
              />
            </div>
          ) : (
            <span className="text-base text-gray-800">
              {gender === 'nam' ? 'Nam' : gender === 'nu' ? 'Nữ' : 'Khác'}
            </span>
          )}
        </div>

        {/* Edit/Save Button */}
        <Button
          onClick={() => {
            if (isEditMode) {
              // Check if values have changed
              const hasChanges =
                formData.fullName !== originalValues.fullName ||
                formData.address !== originalValues.address ||
                formData.job !== originalValues.job ||
                formData.phoneNumber !== originalValues.phoneNumber ||
                formData.dateOfBirth !== originalValues.dateOfBirth ||
                gender !== originalValues.gender;

              if (hasChanges) {
                setShowConfirmModal(true);
              } else {
                // No changes, just exit edit mode
                setIsEditMode(false);
              }
            } else {
              // Entering edit mode, store current values
              setOriginalValues({
                ...formData,
                gender
              });
              setIsEditMode(true);
            }
          }}
          variant="secondary"
          size="fit"
        >
          {isEditMode ? 'Lưu' : 'Chỉnh sửa'}
        </Button>

      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <NotificationCard
            title="Xác nhận thay đổi"
            message="Bạn có chắc chắn muốn lưu thay đổi thông tin cá nhân không?"
            iconBgColor="bg-yellow-500"
            buttonText="Xác nhận"
            buttonIcon={Save}
            onButtonClick={() => {
              // Save the changes
              console.log('Saving:', { formData, gender });
              setOriginalValues({
                ...formData,
                gender
              });
              setShowConfirmModal(false);
              setIsEditMode(false);
            }}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={() => {
              // Revert changes
              setFormData({
                fullName: originalValues.fullName,
                address: originalValues.address,
                job: originalValues.job,
                phoneNumber: originalValues.phoneNumber,
                dateOfBirth: originalValues.dateOfBirth
              });
              setGender(originalValues.gender);
              setShowConfirmModal(false);
            }}
          />
        </div>
      )}
    </div>
  );
};

// --- Helper Components ---

interface InfoSectionProps {
  label: string;
  value: string;
  isPlaceholder?: boolean;
  isEditMode?: boolean;
  onChange?: (value: string) => void;
}

const InfoSection = ({ label, value, isPlaceholder = false, isEditMode = false, onChange }: InfoSectionProps) => {
  return (
    <div>
      <h3 className="font-bold text-black mb-2 text-base">{label}</h3>
      {isEditMode ? (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={isPlaceholder ? "Chưa có thông tin" : ""}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      ) : (
        <span className={`text-base ${isPlaceholder ? 'text-gray-400' : 'text-gray-800'}`}>
          {value || (isPlaceholder ? "Chưa có thông tin" : "")}
        </span>
      )}
    </div>
  );
};

interface RadioButtonProps {
  label: string;
  selected: boolean;
  onClick: () => void;
}

const RadioButton = ({ label, selected, onClick }: RadioButtonProps) => {
  return (
    <button 
      onClick={onClick}
      className="flex items-center gap-2 focus:outline-none"
    >
      <div className={`
        w-5 h-5 rounded-full border-2 flex items-center justify-center
        ${selected ? 'border-black' : 'border-gray-500'}
      `}>
        {selected && <div className="w-2.5 h-2.5 rounded-full bg-black" />}
      </div>
      <span className={`text-base font-bold ${selected ? 'text-black' : 'text-gray-500'}`}>
        {label}
      </span>
    </button>
  );
};

export default PersonalProfile;