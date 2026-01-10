import { useState, useEffect } from 'react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { NotificationCard } from '../../../components/NotificationCard';
import { HelpCircle, X, Save, Loader2 } from 'lucide-react';
import { userService } from '../../../services/user';

// Define types based on API schema
type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
type CurrCondition = 'normal' | 'pregnant' | 'injured';
type HealthGoal = 'lose_weight' | 'maintain' | 'gain_weight';

interface HealthProfileData {
  height_cm: number | null;
  weight_kg: number | null;
  activity_level: ActivityLevel | null;
  curr_condition: CurrCondition | null;
  health_goal: HealthGoal | null;
}

const HealthProfile = () => {
  // --- State Management ---
  const [height, setHeight] = useState<string>('');
  const [weight, setWeight] = useState<string>('');
  const [activityLevel, setActivityLevel] = useState<ActivityLevel | null>(null);
  const [currCondition, setCurrCondition] = useState<CurrCondition | null>(null);
  const [healthGoal, setHealthGoal] = useState<HealthGoal | null>(null);

  // Edit mode state
  const [isEditMode, setIsEditMode] = useState(false);

  // Loading state
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // State for modal visibility and original values
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [originalValues, setOriginalValues] = useState<HealthProfileData>({
    height_cm: null,
    weight_kg: null,
    activity_level: null,
    curr_condition: null,
    health_goal: null
  });

  // Error state
  const [error, setError] = useState<string | null>(null);

  // --- Fetch Data on Mount ---
  useEffect(() => {
    fetchHealthProfile();
  }, []);

  const fetchHealthProfile = () => {
    setIsLoading(true);
    setError(null);

    userService.getMyHealthProfile()
      .match(
        (response) => {
          const data = response.data;
          setHeight(data.height_cm?.toString() ?? '');
          setWeight(data.weight_kg?.toString() ?? '');
          setActivityLevel(data.activity_level ?? null);
          setCurrCondition(data.curr_condition ?? null);
          setHealthGoal(data.health_goal ?? null);

          setOriginalValues({
            height_cm: data.height_cm ?? null,
            weight_kg: data.weight_kg ?? null,
            activity_level: data.activity_level ?? null,
            curr_condition: data.curr_condition ?? null,
            health_goal: data.health_goal ?? null
          });

          setIsLoading(false);
        },
        (error) => {
          console.error('Failed to fetch health profile:', error);
          setError('Không thể tải thông tin sức khỏe. Vui lòng thử lại.');
          setIsLoading(false);
        }
      );
  };

  // --- Handlers ---
  const handleSave = () => {
    setIsSaving(true);
    setError(null);

    const updateData = {
      height_cm: height ? parseFloat(height) : null,
      weight_kg: weight ? parseFloat(weight) : null,
      activity_level: activityLevel,
      curr_condition: currCondition,
      health_goal: healthGoal
    };

    userService.updateMyHealthProfile(updateData)
      .match(
        (response) => {
          const data = response.data;
          setOriginalValues({
            height_cm: data.height_cm ?? null,
            weight_kg: data.weight_kg ?? null,
            activity_level: data.activity_level ?? null,
            curr_condition: data.curr_condition ?? null,
            health_goal: data.health_goal ?? null
          });
          setShowConfirmModal(false);
          setIsEditMode(false);
          setIsSaving(false);
        },
        (error) => {
          console.error('Failed to update health profile:', error);
          setError('Không thể cập nhật thông tin sức khỏe. Vui lòng thử lại.');
          setIsSaving(false);
          setShowConfirmModal(false);
        }
      );
  };

  const handleCancelEdit = () => {
    // Revert to original values
    setHeight(originalValues.height_cm?.toString() ?? '');
    setWeight(originalValues.weight_kg?.toString() ?? '');
    setActivityLevel(originalValues.activity_level);
    setCurrCondition(originalValues.curr_condition);
    setHealthGoal(originalValues.health_goal);
    setShowConfirmModal(false);
  };

  if (isLoading) {
    return (
      <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full pb-24 flex items-center justify-center">
        <Loader2 className="animate-spin text-[#C3485C]" size={32} />
      </div>
    );
  }

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full pb-24">

      <BackButton to="/main/profile" text="Quay lại" className="mb-4" />

      <h1 className="text-2xl font-bold text-black mb-6">
        Hồ sơ sức khỏe
      </h1>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* --- Vital Stats (Height/Weight) --- */}
      <div className="mb-8 space-y-6">
        <StatInput
          label="Chiều cao"
          value={height}
          unit="cm"
          onChange={setHeight}
          isEditMode={isEditMode}
        />
        <StatInput
          label="Cân nặng"
          value={weight}
          unit="kg"
          onChange={setWeight}
          isEditMode={isEditMode}
        />
      </div>

      {/* --- Activity Level --- */}
      <div className="mb-8">
        <SectionTitle title="Cường độ vận động hàng ngày"/>
        {isEditMode ? (
          <div className="mt-4 space-y-4">
            <RadioItem
              label="Ít vận động"
              checked={activityLevel === 'sedentary'}
              onClick={() => setActivityLevel('sedentary')}
              isEditable={true}
            />
            <RadioItem
              label="Vận động nhẹ"
              checked={activityLevel === 'light'}
              onClick={() => setActivityLevel('light')}
              isEditable={true}
            />
            <RadioItem
              label="Vận động vừa"
              checked={activityLevel === 'moderate'}
              onClick={() => setActivityLevel('moderate')}
              isEditable={true}
            />
            <RadioItem
              label="Vận động tích cực"
              checked={activityLevel === 'active'}
              onClick={() => setActivityLevel('active')}
              isEditable={true}
            />
            <RadioItem
              label="Vận động rất tích cực"
              checked={activityLevel === 'very_active'}
              onClick={() => setActivityLevel('very_active')}
              isEditable={true}
            />
          </div>
        ) : (
          <div className="mt-4">
            <DisplayValue value={activityLevel} />
          </div>
        )}
      </div>

      {/* --- Current Condition --- */}
      <div className="mb-8">
        <SectionTitle title="Tình trạng hiện tại" />
        {isEditMode ? (
          <div className="mt-4 space-y-4">
            <RadioItem
              label="Bình thường"
              checked={currCondition === 'normal'}
              onClick={() => setCurrCondition('normal')}
              isEditable={true}
            />
            <RadioItem
              label="Mang thai"
              checked={currCondition === 'pregnant'}
              onClick={() => setCurrCondition('pregnant')}
              isEditable={true}
            />
            <RadioItem
              label="Chấn thương"
              checked={currCondition === 'injured'}
              onClick={() => setCurrCondition('injured')}
              isEditable={true}
            />
          </div>
        ) : (
          <div className="mt-4">
            <DisplayValue value={currCondition} />
          </div>
        )}
      </div>

      {/* --- Health Goal --- */}
      <div className="mb-8">
        <SectionTitle title="Mục tiêu sức khỏe" />
        {isEditMode ? (
          <div className="mt-4 space-y-4">
            <RadioItem
              label="Giảm cân"
              checked={healthGoal === 'lose_weight'}
              onClick={() => setHealthGoal('lose_weight')}
              isEditable={true}
            />
            <RadioItem
              label="Duy trì"
              checked={healthGoal === 'maintain'}
              onClick={() => setHealthGoal('maintain')}
              isEditable={true}
            />
            <RadioItem
              label="Tăng cân"
              checked={healthGoal === 'gain_weight'}
              onClick={() => setHealthGoal('gain_weight')}
              isEditable={true}
            />
          </div>
        ) : (
          <div className="mt-4">
            <DisplayValue value={healthGoal} />
          </div>
        )}
      </div>

      {/* --- Edit/Save/Cancel Buttons --- */}
      <div className="flex gap-3">
        <Button
          onClick={() => {
            if (isEditMode) {
              // Check if values have changed
              const hasChanges =
                height !== (originalValues.height_cm?.toString() ?? '') ||
                weight !== (originalValues.weight_kg?.toString() ?? '') ||
                activityLevel !== originalValues.activity_level ||
                currCondition !== originalValues.curr_condition ||
                healthGoal !== originalValues.health_goal;

              if (hasChanges) {
                setShowConfirmModal(true);
              } else {
                // No changes, just exit edit mode
                setIsEditMode(false);
              }
            } else {
              // Entering edit mode
              setIsEditMode(true);
            }
          }}
          variant="primary"
          size="fit"
        >
          {isEditMode ? 'Lưu' : 'Chỉnh sửa'}
        </Button>

        {isEditMode && (
          <Button
            onClick={() => {
              // Revert to original values and exit edit mode
              handleCancelEdit();
            }}
            variant="secondary"
            size="fit"
          >
            Hủy
          </Button>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <NotificationCard
            title="Xác nhận thay đổi"
            message="Bạn có chắc chắn muốn lưu thay đổi thông tin sức khỏe không?"
            iconBgColor="bg-yellow-500"
            buttonText={isSaving ? 'Đang lưu...' : 'Xác nhận'}
            buttonIcon={isSaving ? Loader2 : Save}
            onButtonClick={handleSave}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={handleCancelEdit}
          />
        </div>
      )}
    </div>
  );
};

// --- Helper Components ---

// 1. Stat Input (Height/Weight)
const StatInput = ({ label, value, unit, onChange, isEditMode }: {
  label: string,
  value: string,
  unit: string,
  onChange: (val: string) => void,
  isEditMode: boolean
}) => (
  <div className="flex items-center gap-4">
    <span className="font-bold text-black">{label}</span>
    <div className="flex items-center">
      {isEditMode ? (
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-16 font-medium text-gray-800 bg-transparent focus:outline-none border-b border-dashed border-gray-300 focus:border-[#C3485C] text-right"
          placeholder="0"
        />
      ) : (
        <span className="font-medium text-gray-800">
          {value || 'Chưa có thông tin'}
        </span>
      )}
      {value && <span className="text-gray-800 font-medium ml-1">{unit}</span>}
    </div>
  </div>
);

// 2. Section Title with Tooltip Icon
const SectionTitle = ({ title, hasInfo }: { title: string, hasInfo?: boolean }) => (
  <div className="flex items-center gap-1">
    <h3 className="font-bold text-black text-base">{title}</h3>
    {hasInfo && <HelpCircle size={14} className="text-gray-500" />}
  </div>
);

// 3. Radio Button Item
const RadioItem = ({ label, checked, onClick, isEditable }: {
  label: string,
  checked: boolean,
  onClick: () => void,
  isEditable: boolean
}) => (
  <button
    onClick={onClick}
    disabled={!isEditable}
    className={`flex items-center gap-3 w-full group ${
      !isEditable ? 'cursor-default' : ''
    }`}
  >
    <div className={`
      w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors
      ${checked ? 'border-[#C3485C]' : isEditable ? 'border-gray-500 group-hover:border-gray-700' : 'border-gray-300'}
    `}>
      {checked && <div className="w-2.5 h-2.5 rounded-full bg-[#C3485C]" />}
    </div>
    <span className={`text-base font-medium ${
      checked ? 'text-[#C3485C]' : isEditable ? 'text-gray-500 group-hover:text-gray-700' : 'text-gray-400'
    }`}>
      {label}
    </span>
  </button>
);

// 4. Display Value Component
const DisplayValue = ({ value }: { value: string | null }) => {
  const displayMap: Record<string, string> = {
    'sedentary': 'Ít vận động',
    'light': 'Vận động nhẹ',
    'moderate': 'Vận động vừa',
    'active': 'Vận động tích cực',
    'very_active': 'Vận động rất tích cực',
    'normal': 'Bình thường',
    'pregnant': 'Mang thai',
    'injured': 'Chấn thương',
    'lose_weight': 'Giảm cân',
    'maintain': 'Duy trì',
    'gain_weight': 'Tăng cân'
  };

  return (
    <p className="text-gray-800 font-medium">
      {value ? displayMap[value] : 'Chưa có thông tin'}
    </p>
  );
};

export default HealthProfile;
