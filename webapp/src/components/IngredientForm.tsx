import { useState, useRef, useEffect } from 'react'
import { Check, X, Image as ImageIcon, ChevronDown, Trash2 } from 'lucide-react'
import { Button } from './Button'
import { InputField } from './InputField'
import {
  Ingredient,
  IngredientCreate
} from '../services/schema/ingredientSchema'

// Hardcoded measurement units
const C_UNITS = [
  'quả',
  'củ',
  'gói',
  'bó',
  'miếng',
  'nhánh',
  'tép',
  'con',
  'viên',
  'túi',
  'cây',
  'lát',
  'khúc',
  'lá',
  'hộp',
  'cái'
]
const UC_UNITS = ['G', 'ML']

// Mock tags for tag selector
const MOCK_TAGS = [
  { id: 1, name: 'Tag 1' },
  { id: 2, name: 'Tag 2' },
  { id: 3, name: 'Tag 3' },
  { id: 4, name: 'Tag 4' },
  { id: 5, name: 'Tag 5' },
  { id: 6, name: 'Tag 6' },
  { id: 7, name: 'Tag 7' },
  { id: 8, name: 'Tag 8' },
  { id: 9, name: 'Tag 9' },
  { id: 10, name: 'Tag 10' }
]

interface IngredientFormProps {
  initialData?: Partial<IngredientCreate>
  onSubmit?: (formData: Partial<IngredientCreate>) => void
  onCancel?: () => void
  submitLabel?: string
  readOnly?: boolean
  actions?: React.ReactNode
}

export const IngredientForm = ({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Xác nhận',
  readOnly = false,
  actions
}: IngredientFormProps) => {
  // Category dropdown state
  const [isOpen, setIsOpen] = useState(false)

  // Form field states
  const [name, setName] = useState(initialData?.component_name || '')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    initialData?.category || null
  )
  const [isCountable, setIsCountable] = useState(
    initialData?.type === 'countable_ingredient'
  )
  const [unit, setUnit] = useState<string | null>(
    initialData?.c_measurement_unit || initialData?.uc_measurement_unit || null
  )
  const [shelfLife, setShelfLife] = useState<number | null>(
    initialData?.estimated_shelf_life || null
  )
  const [price, setPrice] = useState<number | null>(
    initialData?.estimated_price || null
  )
  const [selectedTags, setSelectedTags] = useState<number[]>(
    initialData?.ingredient_tag_list || []
  )
  const [image, setImage] = useState<string | null>(null)
  const [tagInputValue, setTagInputValue] = useState('')

  const dropdownRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const categories = [
    'Thịt trắng',
    'Thịt đỏ',
    'Hải sản',
    'Rau củ',
    'Trái cây',
    'Gia vị',
    'Đồ khô',
    'Thực phẩm đông lạnh',
    'Đồ hộp',
    'Bơ sữa',
    'Bánh kẹo',
    'Đồ uống'
  ]

  // TagSelector Component
  const TagSelector = () => {
    const availableTags = MOCK_TAGS.filter(
      (tag) => !selectedTags.includes(tag.id)
    )

    const handleAddTag = (tagId: number) => {
      if (!readOnly && !selectedTags.includes(tagId)) {
        setSelectedTags([...selectedTags, tagId])
      }
    }

    const handleDeleteTag = (tagId: number) => {
      if (!readOnly) {
        setSelectedTags(selectedTags.filter((id) => id !== tagId))
      }
    }

    const handleTagInputKeyPress = (
      e: React.KeyboardEvent<HTMLInputElement>
    ) => {
      if (e.key === 'Enter' && tagInputValue.trim()) {
        const tagId = parseInt(tagInputValue.trim())
        if (!isNaN(tagId) && !selectedTags.includes(tagId)) {
          handleAddTag(tagId)
          setTagInputValue('')
        }
      }
    }

    return (
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          Thẻ nguyên liệu
        </label>
        {selectedTags.length > 0 ? (
          <div className="flex flex-wrap gap-2 mb-3">
            {selectedTags.map((tagId) => {
              const tag = MOCK_TAGS.find((t) => t.id === tagId)
              return (
                <div
                  key={tagId}
                  className="inline-flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                >
                  {tag?.name}
                  {!readOnly && (
                    <button
                      type="button"
                      onClick={() => handleDeleteTag(tagId)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-sm mb-3">Không có dữ liệu</p>
        )}

        {!readOnly && (
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="Nhập ID thẻ (1-10)"
              value={tagInputValue}
              onChange={(e) => setTagInputValue(e.target.value)}
              onKeyPress={handleTagInputKeyPress}
              className="flex-1 p-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-400"
            />
            <Button
              variant="secondary"
              size="fit"
              onClick={() => {
                const tagId = parseInt(tagInputValue.trim())
                if (!isNaN(tagId) && !selectedTags.includes(tagId)) {
                  handleAddTag(tagId)
                  setTagInputValue('')
                }
              }}
              className="!mx-0"
            >
              Thêm
            </Button>
          </div>
        )}
      </div>
    )
  }

  const handleImageUploadClick = () => {
    if (!readOnly) {
      fileInputRef.current?.click()
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const imageUrl = URL.createObjectURL(file)
      setImage(imageUrl)
    }
  }

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const getDisplayValue = (value: string | number | undefined) => {
    if (readOnly && (value === undefined || value === null || value === '')) {
      return 'Chưa có thông tin'
    }
    return value
  }

  return (
    <div
      className="bg-white p-8 rounded-xl shadow-md grid grid-cols-1 md:grid-cols-5 gap-8"
      style={{ width: '800px', height: '600px' }}
    >
      {/* Left Column */}
      <div className="md:col-span-2 flex flex-col gap-6">
        {/* Tên nguyên liệu */}
        <InputField
          label="Tên nguyên liệu"
          type="text"
          placeholder="Nhập tên nguyên liệu"
          value={name || (readOnly && !name ? 'Không có dữ liệu' : '')}
          onChange={(e) => !readOnly && setName(e.target.value)}
          readOnly={readOnly}
          inputClassName={readOnly ? 'bg-gray-50 focus:outline-none' : ''}
        />

        {/* Phân loại */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            Phân loại
          </label>
          <div className="relative" ref={dropdownRef}>
            <button
              type="button"
              className={`w-full p-3 border border-gray-300 rounded-lg text-gray-700 flex justify-between items-center ${
                readOnly
                  ? 'bg-gray-50 cursor-default'
                  : 'bg-white focus:outline-none focus:border-gray-400'
              }`}
              onClick={() => !readOnly && setIsOpen(!isOpen)}
            >
              {selectedCategory ? (
                <span>{selectedCategory}</span>
              ) : (
                <span className="text-gray-400">
                  {readOnly ? 'Chưa có thông tin' : 'Chọn loại nguyên liệu'}
                </span>
              )}
              {!readOnly && <ChevronDown size={20} className="text-gray-500" />}
            </button>

            {isOpen && !readOnly && (
              <div className="absolute w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                {categories.map((category, index) => (
                  <div
                    key={index}
                    className="p-3 hover:bg-gray-100 cursor-pointer text-gray-700"
                    onClick={() => {
                      setSelectedCategory(category)
                      setIsOpen(false)
                    }}
                  >
                    {category}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Countable Ingredient Checkbox */}
        <div>
          <label className="flex items-center space-x-2 text-gray-700 font-medium">
            <input
              type="checkbox"
              checked={isCountable}
              onChange={() => !readOnly && setIsCountable(!isCountable)}
              disabled={readOnly}
              className="rounded border-gray-300 text-rose-500 focus:ring-rose-500"
            />
            <span>Nguyên liệu đếm được</span>
          </label>
        </div>

        {/* Thêm hình ảnh */}
        <div className="bg-[#FFD7C1] rounded-lg aspect-square flex items-center justify-center relative overflow-hidden">
          {!readOnly && (
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              accept="image/*"
              onChange={handleFileChange}
            />
          )}
          {image ? (
            <div className="group relative w-full h-full">
              <img
                src={image}
                alt="Selected"
                className="w-full h-full object-cover"
              />
              {!readOnly && (
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center transition-all">
                  <Button
                    variant="primary"
                    size="fit"
                    icon={ImageIcon}
                    onClick={handleImageUploadClick}
                    className="!shadow-none"
                  >
                    Thay đổi hình ảnh
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <Button
              variant={readOnly ? 'text' : 'primary'}
              size="fit"
              icon={ImageIcon}
              onClick={handleImageUploadClick}
              className={readOnly ? '!p-0 !mx-0 !hover:bg-transparent' : ''}
            >
              {readOnly ? 'Chưa có hình ảnh' : 'Thêm hình ảnh'}
            </Button>
          )}
        </div>
      </div>

      {/* Right Column */}
      <div className="md:col-span-3 flex flex-col justify-between overflow-y-auto pr-4">
        <div className="flex flex-col gap-6">
          {/* Measurement Unit */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Đơn vị tính
            </label>
            <div className="relative">
              <select
                value={unit || ''}
                onChange={(e) => !readOnly && setUnit(e.target.value || null)}
                disabled={readOnly}
                className={`w-full p-3 border border-gray-300 rounded-lg text-gray-700 ${
                  readOnly
                    ? 'bg-gray-50 cursor-default'
                    : 'bg-white focus:outline-none focus:border-gray-400'
                }`}
              >
                <option value="">
                  {!unit ? (readOnly ? 'Không có dữ liệu' : 'Chọn đơn vị') : ''}
                </option>
                {(isCountable ? C_UNITS : UC_UNITS).map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Shelf Life */}
          <div>
            <label className="block text-gray-700 font-bold mb-2">
              Thời hạn sử dụng (ngày)
            </label>
            <input
              type="number"
              placeholder={readOnly ? '' : '0'}
              value={shelfLife ?? ''}
              onChange={(e) =>
                !readOnly &&
                setShelfLife(e.target.value ? parseInt(e.target.value) : null)
              }
              disabled={readOnly}
              className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                readOnly
                  ? 'bg-gray-50 focus:outline-none'
                  : 'focus:outline-none focus:border-gray-400'
              }`}
            />
            {readOnly && !shelfLife && (
              <p className="text-gray-500 text-sm">Không có dữ liệu</p>
            )}
          </div>

          {/* Price */}
          <div>
            <label className="block text-gray-700 font-bold mb-2">
              Giá ước tính
            </label>
            <input
              type="number"
              placeholder={readOnly ? '' : '0'}
              value={price ?? ''}
              onChange={(e) =>
                !readOnly &&
                setPrice(e.target.value ? parseInt(e.target.value) : null)
              }
              disabled={readOnly}
              className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                readOnly
                  ? 'bg-gray-50 focus:outline-none'
                  : 'focus:outline-none focus:border-gray-400'
              }`}
            />
            {readOnly && !price && (
              <p className="text-gray-500 text-sm">Không có dữ liệu</p>
            )}
          </div>

          {/* Hàm lượng dinh dưỡng trên */}
          <div>
            <label className="block text-gray-700 font-bold mb-2">
              Lượng dinh dưỡng trên 1 đơn vị
            </label>
            {/* <input
              type="text"
              placeholder={readOnly ? '' : '0 g'}
              defaultValue={''}
              className={`w-full text-gray-700 p-3 border-b border-gray-300 ${
                readOnly
                  ? 'bg-gray-50 focus:outline-none'
                  : 'focus:outline-none focus:border-gray-400'
              }`}
              readOnly={readOnly}
            /> */}
          </div>

          {/* Bao gồm: */}
          <div>
            {/* <label className="block text-gray-700 font-medium mb-4">
              Bao gồm:
            </label> */}
            <div className="grid grid-cols-2 gap-x-8 gap-y-6">
              <div className="col-span-2">
                <label className="block text-gray-700 font-bold mb-1">
                  Calo
                </label>
                <input
                  type={readOnly ? 'text' : 'number'}
                  placeholder={readOnly ? '' : '0'}
                  defaultValue={
                    readOnly &&
                    (initialData?.calories === undefined ||
                      initialData?.calories === null)
                      ? 'Không có dữ liệu'
                      : initialData?.calories ?? ''
                  }
                  className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:outline-none focus:border-gray-400'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Đạm
                </label>
                <input
                  type={readOnly ? 'text' : 'number'}
                  placeholder={readOnly ? '' : '0'}
                  defaultValue={
                    readOnly &&
                    (initialData?.protein === undefined ||
                      initialData?.protein === null)
                      ? 'Không có dữ liệu'
                      : initialData?.protein ?? ''
                  }
                  className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:outline-none focus:border-gray-400'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Chất bột đường
                </label>
                <input
                  type={readOnly ? 'text' : 'number'}
                  placeholder={readOnly ? '' : '0'}
                  defaultValue={
                    readOnly &&
                    (initialData?.carb === undefined ||
                      initialData?.carb === null)
                      ? 'Không có dữ liệu'
                      : initialData?.carb ?? ''
                  }
                  className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:outline-none focus:border-gray-400'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Chất xơ
                </label>
                <input
                  type={readOnly ? 'text' : 'number'}
                  placeholder={readOnly ? '' : '0'}
                  defaultValue={
                    readOnly &&
                    (initialData?.fiber === undefined ||
                      initialData?.fiber === null)
                      ? 'Không có dữ liệu'
                      : initialData?.fiber ?? ''
                  }
                  className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:outline-none focus:border-gray-400'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Chất béo
                </label>
                <input
                  type={readOnly ? 'text' : 'number'}
                  placeholder={readOnly ? '' : '0'}
                  defaultValue={
                    readOnly &&
                    (initialData?.fat === undefined ||
                      initialData?.fat === null)
                      ? 'Không có dữ liệu'
                      : initialData?.fat ?? ''
                  }
                  className={`w-full p-2 border-b border-gray-300 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:outline-none focus:border-gray-400'
                  }`}
                  readOnly={readOnly}
                />
              </div>
            </div>
          </div>

          {/* Tag Selector */}
          <TagSelector />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-6 justify-center mt-8">
          {actions ? (
            actions
          ) : (
            <>
              <Button
                variant="primary"
                size="fit"
                icon={Check}
                onClick={() => {
                  const formData: Partial<Ingredient> = {
                    component_name: name,
                    category: selectedCategory,
                    type: isCountable
                      ? 'countable_ingredient'
                      : 'uncountable_ingredient',
                    c_measurement_unit: isCountable ? unit : null,
                    uc_measurement_unit: !isCountable ? unit : null,
                    estimated_shelf_life: shelfLife,
                    estimated_price: price,
                    ingredient_tag_list:
                      selectedTags.length > 0 ? selectedTags : null
                  }
                  onSubmit?.(formData)
                }}
                className="!mx-0"
              >
                {submitLabel}
              </Button>
              <Button
                variant="secondary"
                size="fit"
                icon={X}
                onClick={onCancel}
                className="!mx-0"
              >
                Hủy
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
