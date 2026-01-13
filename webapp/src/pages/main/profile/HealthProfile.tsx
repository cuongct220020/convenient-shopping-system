import { useState, useEffect } from 'react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { NotificationCard } from '../../../components/NotificationCard';
import { HelpCircle, X, Save, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { userService } from '../../../services/user';
import {
  UserTagsData,
  TagCategory,
  getTagByValue,
  TAG_CATEGORY_NAMES,
  AGE_TAGS,
  MEDICAL_TAGS,
  ALLERGY_TAGS,
  DIET_TAGS,
  TASTE_TAGS,
  type TagValue
} from '../../../services/tags';

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
  const [originalTags, setOriginalTags] = useState<Set<TagValue>>(new Set());

  // Error state
  const [error, setError] = useState<string | null>(null);

  // Tags state
  const [tags, setTags] = useState<UserTagsData>({
    age: [],
    medical: [],
    allergy: [],
    diet: [],
    taste: []
  });
  const [selectedTags, setSelectedTags] = useState<Set<TagValue>>(new Set());
  const [expandedCategory, setExpandedCategory] = useState<TagCategory | null>(null);
  const [isTagsLoading, setIsTagsLoading] = useState(true);

  // --- Fetch Data on Mount ---
  useEffect(() => {
    fetchHealthProfile();
    fetchTags();
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

  const fetchTags = () => {
    setIsTagsLoading(true);
    setError(null);

    userService.getMyTags()
      .match(
        (response) => {
          const data = response.data;
          setTags(data);
          const tagValues = new Set(
            [...data.age, ...data.medical, ...data.allergy, ...data.diet, ...data.taste]
              .map(tag => tag.tag_value as TagValue)
          );
          setSelectedTags(tagValues);
          setOriginalTags(tagValues);
          setIsTagsLoading(false);
        },
        (error) => {
          console.error('Failed to fetch tags:', error);
          setError('Không thể tải thông tin tags. Vui lòng thử lại.');
          setIsTagsLoading(false);
        }
      );
  };

  // --- Handlers ---
  const handleSave = () => {
    setIsSaving(true);
    setError(null);

    const currentTagValues = new Set(
      [...tags.age, ...tags.medical, ...tags.allergy, ...tags.diet, ...tags.taste]
        .map(tag => tag.tag_value as TagValue)
    );

    const tagsToAdd = Array.from(selectedTags).filter(tag => !currentTagValues.has(tag));
    const tagsToRemove = Array.from(currentTagValues).filter(tag => !selectedTags.has(tag));

    // Prepare health profile update data
    const updateData = {
      height_cm: height ? parseFloat(height) : null,
      weight_kg: weight ? parseFloat(weight) : null,
      activity_level: activityLevel,
      curr_condition: currCondition,
      health_goal: healthGoal
    };

    // Build the operation chain - only include API calls that have actual changes
    let saveOperation: ResultAsync<any, any> = userService.updateMyHealthProfile(updateData);

    if (tagsToAdd.length > 0) {
      saveOperation = saveOperation.andThen(() => userService.addMyTags(tagsToAdd));
    }
    if (tagsToRemove.length > 0) {
      saveOperation = saveOperation.andThen(() => userService.removeMyTags(tagsToRemove));
    }

    saveOperation.match(
      () => {
        // Update original values
        setOriginalValues({
          height_cm: height ? parseFloat(height) : null,
          weight_kg: weight ? parseFloat(weight) : null,
          activity_level: activityLevel,
          curr_condition: currCondition,
          health_goal: healthGoal
        });
        setOriginalTags(new Set(selectedTags));
        fetchTags();
        setShowConfirmModal(false);
        setIsEditMode(false);
        setIsSaving(false);
      },
      (error) => {
        console.error('Failed to save:', error);
        setError('Không thể cập nhật thông tin. Vui lòng thử lại.');
        setIsSaving(false);
        setShowConfirmModal(false);
      }
    );
  };

  const handleCancelEdit = () => {
    // Revert health profile to original values
    setHeight(originalValues.height_cm?.toString() ?? '');
    setWeight(originalValues.weight_kg?.toString() ?? '');
    setActivityLevel(originalValues.activity_level);
    setCurrCondition(originalValues.curr_condition);
    setHealthGoal(originalValues.health_goal);

    // Revert tags to original values
    setSelectedTags(new Set(originalTags));

    // Close modal and exit edit mode
    setShowConfirmModal(false);
    setIsEditMode(false);
  };

  const handleCancelModalOnly = () => {
    setShowConfirmModal(false);
  };

  const handleTagToggle = (tagValue: TagValue) => {
    if (!isEditMode) return;
    setSelectedTags(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tagValue)) {
        newSet.delete(tagValue);
      } else {
        newSet.add(tagValue);
      }
      return newSet;
    });
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

      {/* --- Tags Section --- */}
      <div className="mb-8">
        <SectionTitle title="Thông tin bổ sung" />
        {isTagsLoading ? (
          <div className="mt-4 flex items-center justify-center">
            <Loader2 className="animate-spin text-[#C3485C]" size={24} />
          </div>
        ) : !isEditMode ? (
          <div className="mt-4 space-y-3">
            {(['age', 'medical', 'allergy', 'diet', 'taste'] as TagCategory[]).map((category) => (
              <TagCategorySectionReadOnly
                key={category}
                category={category}
                selectedTags={selectedTags}
              />
            ))}
          </div>
        ) : (
          <div className="mt-4 space-y-3">
            {(['age', 'medical', 'allergy', 'diet', 'taste'] as TagCategory[]).map((category) => (
              <TagCategorySection
                key={category}
                category={category}
                tags={tags[category]}
                selectedTags={selectedTags}
                onToggle={handleTagToggle}
                isExpanded={expandedCategory === category}
                onToggleExpand={() => setExpandedCategory(expandedCategory === category ? null : category)}
              />
            ))}
          </div>
        )}
      </div>

      {/* --- Edit/Save/Cancel Buttons --- */}
      <div className="flex gap-3">
        <Button
          onClick={() => {
            if (isEditMode) {
              // Show confirmation modal to save
              setShowConfirmModal(true);
            } else {
              // Entering edit mode - store original tags
              setOriginalTags(new Set(selectedTags));
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
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
          <NotificationCard
            title="Xác nhận thay đổi"
            message="Bạn có chắc chắn muốn lưu thay đổi thông tin không?"
            iconBgColor="bg-yellow-500"
            buttonText={isSaving ? 'Đang lưu...' : 'Xác nhận'}
            buttonIcon={isSaving ? Loader2 : Save}
            onButtonClick={handleSave}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={handleCancelModalOnly}
          />
        </div>
      )}
    </div>
  );
};

// --- Helper Components ---

// Read-only Tag Category Section Component (display mode)
const TagCategorySectionReadOnly = ({
  category,
  selectedTags
}: {
  category: TagCategory;
  selectedTags: Set<TagValue>;
}) => {
  const allTagsByCategory: Record<TagCategory, Record<string, { value: TagValue; name: string }>> = {
    age: AGE_TAGS,
    medical: MEDICAL_TAGS,
    allergy: ALLERGY_TAGS,
    diet: DIET_TAGS,
    taste: TASTE_TAGS
  };

  const categoryTags = allTagsByCategory[category];
  const selectedTagsInCategory = Object.values(categoryTags).filter(t => selectedTags.has(t.value));

  return (
    <div className="border border-gray-200 rounded-lg p-3">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-black">{TAG_CATEGORY_NAMES[category]}</span>
        <span className="text-sm text-gray-500">
          {selectedTagsInCategory.length > 0 && (
            <span className="bg-[#C3485C] text-white text-xs px-2 py-0.5 rounded-full">
              {selectedTagsInCategory.length}
            </span>
          )}
        </span>
      </div>
      {selectedTagsInCategory.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {selectedTagsInCategory.map(({ value, name }) => (
            <span
              key={value}
              className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
            >
              {name}
            </span>
          ))}
        </div>
      )}
      {selectedTagsInCategory.length === 0 && (
        <p className="mt-2 text-sm text-gray-400">Chưa có thông tin</p>
      )}
    </div>
  );
};

// Tag Category Section Component (edit mode)
const TagCategorySection = ({
  category,
  tags,
  selectedTags,
  onToggle,
  isExpanded,
  onToggleExpand
}: {
  category: TagCategory;
  tags: Array<{ id: number; tag_value: TagValue; tag_name: string; description: string }>;
  selectedTags: Set<TagValue>;
  onToggle: (tagValue: TagValue) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}) => {
  const allTagsByCategory: Record<TagCategory, Record<string, { value: TagValue; name: string }>> = {
    age: AGE_TAGS,
    medical: MEDICAL_TAGS,
    allergy: ALLERGY_TAGS,
    diet: DIET_TAGS,
    taste: TASTE_TAGS
  };

  const categoryTags = allTagsByCategory[category];

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggleExpand}
        className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="font-semibold text-black">{TAG_CATEGORY_NAMES[category]}</span>
          <span className="text-sm text-gray-500">
            {selectedTags.size > 0 && Array.from(selectedTags).some(tag =>
              Object.values(categoryTags).some(t => t.value === tag)
            ) && (
              <span className="bg-[#C3485C] text-white text-xs px-2 py-0.5 rounded-full">
                {Array.from(selectedTags).filter(tag =>
                  Object.values(categoryTags).some(t => t.value === tag)
                ).length}
              </span>
            )}
          </span>
        </div>
        {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>
      {isExpanded && (
        <div className="p-3 bg-white max-h-60 overflow-y-auto">
          <div className="space-y-2">
            {Object.entries(categoryTags).map(([key, { value, name }]) => (
              <TagItem
                key={key}
                label={name}
                checked={selectedTags.has(value)}
                onToggle={() => onToggle(value)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Tag Item Component
const TagItem = ({ label, checked, onToggle }: {
  label: string;
  checked: boolean;
  onToggle: () => void;
}) => (
  <button
    onClick={onToggle}
    className="flex items-center gap-3 w-full group"
  >
    <div className={`
      w-5 h-5 rounded border-2 flex items-center justify-center transition-colors
      ${checked ? 'border-[#C3485C] bg-[#C3485C]' : 'border-gray-300 group-hover:border-gray-500'}
    `}>
      {checked && (
        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      )}
    </div>
    <span className={`text-sm ${checked ? 'text-[#C3485C] font-medium' : 'text-gray-500 group-hover:text-gray-700'}`}>
      {label}
    </span>
  </button>
);

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
