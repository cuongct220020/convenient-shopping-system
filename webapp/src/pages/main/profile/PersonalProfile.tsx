import { useState, useEffect } from 'react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { NotificationCard } from '../../../components/NotificationCard';
import { Save, X } from 'lucide-react';
import { userService } from '../../../services/user';
import type { UserIdentityProfile } from '../../../services/schema/groupSchema';

const PersonalProfile = () => {
  // State for gender selection
  const [gender, setGender] = useState<'male' | 'female' | 'other' | null>(null);

  // State for edit mode
  const [isEditMode, setIsEditMode] = useState(false);

  // State for loading
  const [isLoading, setIsLoading] = useState(true);

  // State for save operation
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // State for form values
  const [formData, setFormData] = useState({
    fullName: '',
    address: '',
    occupation: '',
    phoneNumber: '',
    dateOfBirth: ''
  });

  // State for modal visibility and original values
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [originalValues, setOriginalValues] = useState({
    fullName: '',
    address: '',
    occupation: '',
    phoneNumber: '',
    dateOfBirth: '',
    gender: null as 'male' | 'female' | 'other' | null
  });

  // Fetch user profile data on mount
  useEffect(() => {
    const fetchProfile = async () => {
      // Fetch both current user info and identity profile in parallel
      const [userResult, identityResult] = await Promise.all([
        userService.getCurrentUser(),
        userService.getMyIdentityProfile()
      ]);

      let fullName = '';
      let phoneNumber = '';
      let address = '';
      let occupation = '';
      let dateOfBirth = '';
      let genderValue: 'male' | 'female' | 'other' | null = null;

      // Process current user data
      if (userResult.isOk()) {
        const userData = userResult.value.data;
        fullName = `${userData.first_name || ''} ${userData.last_name || ''}`.trim();
        phoneNumber = userData.phone_num || '';
      }

      // Process identity profile data
      if (identityResult.isOk()) {
        const profile = identityResult.value.data;
        genderValue = profile.gender;
        address = formatAddress(profile.address);
        occupation = profile.occupation || '';
        dateOfBirth = profile.date_of_birth || '';
      }

      // Update state with fetched data
      setGender(genderValue);
      setFormData({
        fullName,
        address,
        occupation,
        phoneNumber,
        dateOfBirth
      });
      setOriginalValues({
        fullName,
        address,
        occupation,
        phoneNumber,
        dateOfBirth,
        gender: genderValue
      });

      setIsLoading(false);
    };
    fetchProfile();
  }, []);

  const formatAddress = (address: UserIdentityProfile['address']): string => {
    if (!address) return '';
    const parts = [address.ward, address.district, address.city, address.province].filter(Boolean);
    return parts.join(', ');
  };

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full pb-24">

      {/* Back Navigation */}
      <BackButton to="/main/profile" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-6">
        Hồ sơ cá nhân
      </h1>

      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
        </div>
      ) : (
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
          isPlaceholder={!formData.address}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, address: value})}
        />

        {/* Occupation */}
        <InfoSection
          label="Nghề nghiệp"
          value={formData.occupation}
          isPlaceholder={!formData.occupation}
          isEditMode={isEditMode}
          onChange={(value) => setFormData({...formData, occupation: value})}
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
          isPlaceholder={!formData.dateOfBirth}
          isEditMode={isEditMode}
          type="date"
          onChange={(value) => setFormData({...formData, dateOfBirth: value})}
        />

          {/* Gender Selection */}
          <div>
            <h3 className="font-bold text-black mb-3 text-base">Giới tính</h3>
            {isEditMode ? (
              <div className="flex items-center gap-8">
                <RadioButton
                  label="Nam"
                  selected={gender === 'male'}
                  onClick={() => setGender('male')}
                />
                <RadioButton
                  label="Nữ"
                  selected={gender === 'female'}
                  onClick={() => setGender('female')}
                />
                <RadioButton
                  label="Khác"
                  selected={gender === 'other'}
                  onClick={() => setGender('other')}
                />
              </div>
            ) : (
              <span className={`text-base ${!gender ? 'text-gray-400' : 'text-gray-800'}`}>
                {!gender ? 'Chưa có thông tin' : gender === 'male' ? 'Nam' : gender === 'female' ? 'Nữ' : 'Khác'}
              </span>
            )}
          </div>

          {/* Edit/Save/Cancel Buttons */}
          {isEditMode ? (
            <div className="flex gap-3">
              <Button
                onClick={() => {
                  // Check if values have changed
                  const hasChanges =
                    formData.fullName !== originalValues.fullName ||
                    formData.address !== originalValues.address ||
                    formData.occupation !== originalValues.occupation ||
                    formData.phoneNumber !== originalValues.phoneNumber ||
                    formData.dateOfBirth !== originalValues.dateOfBirth ||
                    gender !== originalValues.gender;

                  if (hasChanges) {
                    setShowConfirmModal(true);
                  } else {
                    // No changes, just exit edit mode
                    setIsEditMode(false);
                  }
                }}
                variant="primary"
                size="fit"
              >
                Lưu
              </Button>
              <Button
                onClick={() => {
                  // Revert changes and exit edit mode
                  setFormData({
                    fullName: originalValues.fullName,
                    address: originalValues.address,
                    occupation: originalValues.occupation,
                    phoneNumber: originalValues.phoneNumber,
                    dateOfBirth: originalValues.dateOfBirth
                  });
                  setGender(originalValues.gender);
                  setIsEditMode(false);
                }}
                variant="secondary"
                size="fit"
              >
                Hủy
              </Button>
            </div>
          ) : (
            <Button
              onClick={() => {
                // Entering edit mode, store current values
                setOriginalValues({
                  ...formData,
                  gender
                });
                setIsEditMode(true);
              }}
              variant="primary"
              size="fit"
            >
              Chỉnh sửa
            </Button>
          )}
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
          <NotificationCard
            title="Xác nhận thay đổi"
            message="Bạn có chắc chắn muốn lưu thay đổi thông tin cá nhân không?"
            iconBgColor="bg-yellow-500"
            buttonText={isSaving ? "Đang lưu..." : "Xác nhận"}
            buttonIcon={Save}
            onButtonClick={async () => {
              setIsSaving(true);
              setSaveError(null);

              // Prepare user profile update data
              const userUpdateData: {
                first_name?: string | null;
                last_name?: string | null;
                phone_num?: string | null;
              } = {};

              if (formData.fullName !== originalValues.fullName) {
                // Parse full name into first and last name
                // First word is first_name, rest is last_name
                const parts = formData.fullName.trim().split(' ');
                userUpdateData.first_name = parts[0] || null;
                userUpdateData.last_name = parts.slice(1).join(' ') || null;
              }
              if (formData.phoneNumber !== originalValues.phoneNumber) {
                userUpdateData.phone_num = formData.phoneNumber || null;
              }

              // Prepare identity profile update data
              const identityUpdateData: {
                gender?: 'male' | 'female' | 'other';
                date_of_birth?: string | null;
                occupation?: string | null;
                address?: UserIdentityProfile['address'];
              } = {};

              if (gender !== originalValues.gender && gender) {
                identityUpdateData.gender = gender;
              }
              if (formData.dateOfBirth !== originalValues.dateOfBirth) {
                identityUpdateData.date_of_birth = formData.dateOfBirth || null;
              }
              if (formData.occupation !== originalValues.occupation) {
                identityUpdateData.occupation = formData.occupation || null;
              }
              if (formData.address !== originalValues.address) {
                // Parse address string back to object format
                // Address format: "ward, district, city, province"
                const parts = formData.address.split(',').map(s => s.trim());
                identityUpdateData.address = {
                  ward: parts[0] || null,
                  district: parts[1] || null,
                  city: parts[2] || null,
                  province: parts[3] || null
                };
              }

              // Call APIs for both user and identity profile updates in parallel
              const updatePromises: Promise<unknown>[] = [];

              if (Object.keys(userUpdateData).length > 0) {
                updatePromises.push(
                  userService.updateCurrentUser(userUpdateData).match(
                    (value) => value,
                    (error) => Promise.reject(error)
                  )
                );
              }
              if (Object.keys(identityUpdateData).length > 0) {
                updatePromises.push(
                  userService.updateMyIdentityProfile(identityUpdateData).match(
                    (value) => value,
                    (error) => Promise.reject(error)
                  )
                );
              }

              // If nothing changed, just exit edit mode
              if (updatePromises.length === 0) {
                setIsEditMode(false);
                setShowConfirmModal(false);
                setIsSaving(false);
                return;
              }

              const results = await Promise.allSettled(updatePromises);
              const hasError = results.some(r => r.status === 'rejected');

              if (hasError) {
                setSaveError('Không thể lưu thay đổi. Vui lòng thử lại.');
              } else {
                // Update successful
                setOriginalValues({
                  ...formData,
                  gender
                });
                setShowConfirmModal(false);
                setIsEditMode(false);
              }

              setIsSaving(false);
            }}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={() => {
              // Revert changes
              setFormData({
                fullName: originalValues.fullName,
                address: originalValues.address,
                occupation: originalValues.occupation,
                phoneNumber: originalValues.phoneNumber,
                dateOfBirth: originalValues.dateOfBirth
              });
              setGender(originalValues.gender);
              setShowConfirmModal(false);
              setSaveError(null);
            }}
          />
        </div>
      )}

      {/* Error Modal */}
      {saveError && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
          <NotificationCard
            title="Lỗi"
            message={saveError}
            iconBgColor="bg-red-500"
            buttonText="Đóng"
            onButtonClick={() => setSaveError(null)}
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
  type?: 'text' | 'date';
}

const InfoSection = ({ label, value, isPlaceholder = false, isEditMode = false, onChange, type = 'text' }: InfoSectionProps) => {
  return (
    <div>
      <h3 className="font-bold text-black mb-2 text-base">{label}</h3>
      {isEditMode ? (
        <input
          type={type}
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