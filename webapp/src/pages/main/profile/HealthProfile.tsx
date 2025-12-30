import React, { useState, useEffect } from 'react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { NotificationCard } from '../../../components/NotificationCard';
import { Pencil, HelpCircle, X, Check, Save } from 'lucide-react';

// Define types for the selection data
type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'heavy' | 'very_heavy';

const HealthProfile = () => {
  // --- State Management ---
  const [height, setHeight] = useState<string>('165');
  const [weight, setWeight] = useState<string>('65');
  const [age, setAge] = useState<string>('--'); // Assuming age is derived or fetched

  const [bmi, setBmi] = useState<number>(0);
  const [activityLevel, setActivityLevel] = useState<ActivityLevel>('sedentary');

  // Tag Selections
  const [selectedConditions, setSelectedConditions] = useState<string[]>(['Tim mạch']);
  const [selectedAllergies, setSelectedAllergies] = useState<string[]>(['Hải sản']);
  const [selectedDiets, setSelectedDiets] = useState<string[]>(['Gym']);
  const [selectedTastes, setSelectedTastes] = useState<string[]>(['Tim mạch']); // Using dummy data from image

  // Edit mode state
  const [isEditMode, setIsEditMode] = useState(false);

  // State for modal visibility and original values
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [originalValues, setOriginalValues] = useState({
    height: '165',
    weight: '65',
    activityLevel: 'sedentary' as ActivityLevel,
    selectedConditions: ['Tim mạch'],
    selectedAllergies: ['Hải sản'],
    selectedDiets: ['Gym'],
    selectedTastes: ['Tim mạch']
  });

  // --- Calculations ---
  useEffect(() => {
    // Simple BMI Calculation: weight (kg) / height (m)^2
    const h = parseFloat(height);
    const w = parseFloat(weight);
    if (h > 0 && w > 0) {
      const calculatedBmi = w / ((h / 100) * (h / 100));
      setBmi(parseFloat(calculatedBmi.toFixed(2)));
    }
  }, [height, weight]);

  // --- Handlers ---
  const toggleTag = (item: string, currentList: string[], setList: (l: string[]) => void) => {
    if (currentList.includes(item)) {
      setList(currentList.filter(i => i !== item));
    } else {
      setList([...currentList, item]);
    }
  };

  const handleSave = () => {
    console.log('Saving Health Profile:', {
      height, weight, activityLevel, selectedConditions, selectedAllergies, selectedDiets, selectedTastes
    });
    // Add navigation or API call here
  };

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full pb-24">
      
      <BackButton to="/main/profile" text="Quay lại" className="mb-4" />

      <h1 className="text-2xl font-bold text-black mb-6">
        Hồ sơ sức khỏe
      </h1>

      {/* --- Vital Stats (Height/Weight/Age) --- */}
      <div className="flex justify-between mb-8">
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
        <div className="flex flex-col">
          <span className="font-bold text-black mb-1">Tuổi</span>
          <span className="text-gray-500 font-medium py-1">{age}</span>
        </div>
      </div>

      {/* --- Indices (BMI, BMR, TDEE) --- */}
      <div className="space-y-6 mb-8">
        {/* BMI */}
        <div>
          <SectionTitle title="Chỉ số BMI" hasInfo />
          <div className="flex justify-between items-end mt-1 text-sm">
            <div className="text-center text-gray-400">
              <p>Thiếu cân</p>
              <p>&lt; 18.5</p>
            </div>
            <div className="text-center">
              <p className="text-[#C3485C] font-medium">Bình thường</p>
              <p className="text-[#C3485C] font-bold text-xl">{bmi}</p>
            </div>
            <div className="text-center text-gray-400">
              <p>Tiền béo phì</p>
              <p>&gt;22.5</p>
            </div>
          </div>
        </div>

        {/* BMR */}
        <div>
          <SectionTitle title="Chỉ số BMR" hasInfo />
          <p className="text-gray-800 font-medium mt-1">1300 kcal / ngày</p>
        </div>
      </div>

      {/* --- Activity Level --- */}
      <div className="mb-8">
        <SectionTitle title="Cường độ vận động hàng ngày" hasInfo />
        <div className="mt-4 space-y-4">
          <RadioItem
            label="Ít vận động"
            checked={activityLevel === 'sedentary'}
            onClick={() => isEditMode && setActivityLevel('sedentary')}
            isEditable={isEditMode}
          />
          <RadioItem
            label="Vận động nhẹ"
            checked={activityLevel === 'light'}
            onClick={() => isEditMode && setActivityLevel('light')}
            isEditable={isEditMode}
          />
          <RadioItem
            label="Vận động vừa"
            checked={activityLevel === 'moderate'}
            onClick={() => isEditMode && setActivityLevel('moderate')}
            isEditable={isEditMode}
          />
          <RadioItem
            label="Tập nặng"
            checked={activityLevel === 'heavy'}
            onClick={() => isEditMode && setActivityLevel('heavy')}
            isEditable={isEditMode}
          />
          <RadioItem
            label="Tập rất nặng"
            checked={activityLevel === 'very_heavy'}
            onClick={() => isEditMode && setActivityLevel('very_heavy')}
            isEditable={isEditMode}
          />
        </div>
        
        {/* Calculated TDEE */}
        <div className="mt-6">
          <SectionTitle title="Chỉ số TDEE" hasInfo />
          <p className="text-[#C3485C] font-medium mt-1">1900 kcal / ngày</p>
        </div>
      </div>

      {/* --- Tags Sections --- */}
      <div className="space-y-8">
        
        {/* Pathology / Medical Conditions */}
        <TagSection
          title="Bệnh lý"
          options={['Tim mạch', 'Sỏi thận', 'Xơ gan', 'Máu nhiễm mỡ', 'Hen suyễn', 'Máu khó đông', 'Gout']}
          selected={selectedConditions}
          onToggle={(item) => isEditMode && toggleTag(item, selectedConditions, setSelectedConditions)}
          isEditMode={isEditMode}
        />

        {/* Allergies */}
        <TagSection
          title="Dị ứng"
          options={['Hải sản', 'Thịt mỡ', 'Da động vật', 'Sự tử tế', 'Thịt sống', 'Rau muống']}
          selected={selectedAllergies}
          onToggle={(item) => isEditMode && toggleTag(item, selectedAllergies, setSelectedAllergies)}
          isEditMode={isEditMode}
        />

        {/* Nutrition Mode */}
        <TagSection
          title="Chế độ dinh dưỡng"
          options={['Gym', 'Ăn chay trường', 'Giảm béo', 'Tăng cân', 'Eat Clean', 'Keto']}
          selected={selectedDiets}
          onToggle={(item) => isEditMode && toggleTag(item, selectedDiets, setSelectedDiets)}
          isEditMode={isEditMode}
        />

        {/* Taste */}
        <TagSection
          title="Khẩu vị"
          options={['Chua', 'Cay', 'Mặn', 'Ngọt', 'Nhạt', 'Đắng']}
          selected={selectedTastes}
          onToggle={(item) => isEditMode && toggleTag(item, selectedTastes, setSelectedTastes)}
          isEditMode={isEditMode}
        />

        {/* Edit/Save Button */}
        <Button
          onClick={() => {
            if (isEditMode) {
              // Check if values have changed
              const hasChanges =
                height !== originalValues.height ||
                weight !== originalValues.weight ||
                activityLevel !== originalValues.activityLevel ||
                JSON.stringify(selectedConditions) !== JSON.stringify(originalValues.selectedConditions) ||
                JSON.stringify(selectedAllergies) !== JSON.stringify(originalValues.selectedAllergies) ||
                JSON.stringify(selectedDiets) !== JSON.stringify(originalValues.selectedDiets) ||
                JSON.stringify(selectedTastes) !== JSON.stringify(originalValues.selectedTastes);

              if (hasChanges) {
                setShowConfirmModal(true);
              } else {
                // No changes, just exit edit mode
                setIsEditMode(false);
              }
            } else {
              // Entering edit mode, store current values
              setOriginalValues({
                height,
                weight,
                activityLevel,
                selectedConditions: [...selectedConditions],
                selectedAllergies: [...selectedAllergies],
                selectedDiets: [...selectedDiets],
                selectedTastes: [...selectedTastes]
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
            message="Bạn có chắc chắn muốn lưu thay đổi thông tin sức khỏe không?"
            iconBgColor="bg-yellow-500"
            buttonText="Xác nhận"
            buttonIcon={Save}
            onButtonClick={() => {
              // Save the changes
              console.log('Saving Health Profile:', {
                height,
                weight,
                activityLevel,
                selectedConditions,
                selectedAllergies,
                selectedDiets,
                selectedTastes
              });
              setOriginalValues({
                height,
                weight,
                activityLevel,
                selectedConditions: [...selectedConditions],
                selectedAllergies: [...selectedAllergies],
                selectedDiets: [...selectedDiets],
                selectedTastes: [...selectedTastes]
              });
              setShowConfirmModal(false);
              setIsEditMode(false);
            }}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={() => {
              // Revert changes
              setHeight(originalValues.height);
              setWeight(originalValues.weight);
              setActivityLevel(originalValues.activityLevel);
              setSelectedConditions([...originalValues.selectedConditions]);
              setSelectedAllergies([...originalValues.selectedAllergies]);
              setSelectedDiets([...originalValues.selectedDiets]);
              setSelectedTastes([...originalValues.selectedTastes]);
              setShowConfirmModal(false);
            }}
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
  <div className="flex flex-col">
    <span className="font-bold text-black mb-1">{label}</span>
    <div className="flex items-center">
      <Pencil size={16} className={`${isEditMode ? 'text-black fill-black' : 'text-gray-500 fill-gray-500'} mr-2`} />
      {isEditMode ? (
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-12 font-medium text-gray-800 bg-transparent focus:outline-none border-b border-dashed border-gray-300 focus:border-[#C3485C]"
        />
      ) : (
        <span className="w-12 font-medium text-gray-800">{value}</span>
      )}
      <span className="text-gray-800 font-medium ml-1">{unit}</span>
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

// 4. Tag/Chip Section
const TagSection = ({ title, options, selected, onToggle, isEditMode }: {
  title: string,
  options: string[],
  selected: string[],
  onToggle: (item: string) => void,
  isEditMode: boolean
}) => {
  return (
    <div>
      <SectionTitle title={title} />
      <div className="flex flex-wrap gap-2 mt-3">
        {options.map((option) => {
          const isSelected = selected.includes(option);
          return (
            <button
              key={option}
              onClick={() => onToggle(option)}
              disabled={!isEditMode}
              className={`
                px-3 py-1.5 rounded-full text-xs font-medium border transition-all
                ${isSelected
                  ? 'bg-[#FFEFEF] text-[#C3485C] border-[#C3485C]'
                  : isEditMode
                    ? 'bg-transparent text-gray-500 border-[#C3485C] hover:bg-red-50'
                    : 'bg-transparent text-gray-400 border-gray-300'
                }
                ${!isEditMode ? 'cursor-default' : ''}
              `}
            >
              #{option}
            </button>
          );
        })}
      </div>
      <button className={`font-bold text-sm mt-2 ${
        isEditMode ? 'text-gray-400 hover:text-gray-600' : 'text-gray-300 cursor-default'
      }`}>
        Xem thêm
      </button>
    </div>
  );
};

export default HealthProfile;