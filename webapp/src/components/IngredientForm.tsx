import { useState, useRef, useEffect } from 'react'
import { Check, X, Image as ImageIcon, ChevronDown } from 'lucide-react'
import { Button } from './Button'
import { InputField } from './InputField'
import { DropdownInputField } from './DropDownInputField'
import {
  Ingredient,
  IngredientCreate
} from '../services/schema/ingredientSchema'
import {
  COUNTABLE_UNITS,
  UNCOUNTABLE_UNITS,
  INGREDIENT_CATEGORIES,
  INGREDIENT_TAGS_MAP
} from '../utils/constants'

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

  const dropdownRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // TagSelector Component
  const TagSelector = () => {
    const [selectedTagForAdd, setSelectedTagForAdd] = useState('')

    const availableTags = Object.entries(INGREDIENT_TAGS_MAP)
      .filter(([id]) => !selectedTags.includes(Number(id)))
      .sort((a, b) => Number(a[0]) - Number(b[0]))

    const tagOptions = availableTags.map(([id, name]) => ({
      value: id,
      label: name
    }))

    const handleAddTag = (tagIdStr: string) => {
      const tagId = Number(tagIdStr)
      if (!readOnly && !selectedTags.includes(tagId)) {
        setSelectedTags([...selectedTags, tagId])
        setSelectedTagForAdd('')
      }
    }

    const handleDeleteTag = (tagId: number) => {
      if (!readOnly) {
        setSelectedTags(selectedTags.filter((id) => id !== tagId))
      }
    }

    return (
      <div>
        <label className="mb-2 block font-medium text-gray-700">
          Thẻ nguyên liệu
        </label>
        {selectedTags.length > 0 ? (
          <div className="mb-3 flex flex-wrap gap-2">
            {selectedTags.map((tagId) => {
              const tagName =
                INGREDIENT_TAGS_MAP[tagId as keyof typeof INGREDIENT_TAGS_MAP]
              return (
                <div
                  key={tagId}
                  className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
                >
                  {tagName || `Tag ${tagId}`}
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
          <p className="mb-3 text-sm text-gray-500">Không có dữ liệu</p>
        )}

        {!readOnly && (
          <div>
            {tagOptions.length > 0 ? (
              <DropdownInputField
                options={tagOptions}
                value={selectedTagForAdd}
                onChange={handleAddTag}
                placeholder="Chọn thẻ để thêm"
                disabled={readOnly}
              />
            ) : (
              <div className="rounded-lg border border-gray-300 bg-gray-50 p-3 text-sm text-gray-500">
                Tất cả thẻ đã được chọn
              </div>
            )}
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

  return (
    <div
      className="grid grid-cols-1 gap-8 rounded-xl bg-white p-8 shadow-md md:grid-cols-5"
      style={{ width: '800px', height: '600px' }}
    >
      {/* Left Column */}
      <div className="flex flex-col gap-6 md:col-span-2">
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
          <label className="mb-2 block font-medium text-gray-700">
            Phân loại
          </label>
          <div className="relative" ref={dropdownRef}>
            <button
              type="button"
              className={`flex w-full items-center justify-between rounded-lg border border-gray-300 p-3 text-gray-700 ${
                readOnly
                  ? 'cursor-default bg-gray-50'
                  : 'bg-white focus:border-gray-400 focus:outline-none'
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
              <div className="absolute z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-lg border border-gray-300 bg-white shadow-lg">
                {INGREDIENT_CATEGORIES.map((category, index) => (
                  <div
                    key={index}
                    className="cursor-pointer p-3 text-gray-700 hover:bg-gray-100"
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
          <label className="flex items-center space-x-2 font-medium text-gray-700">
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
        <div className="relative flex aspect-square items-center justify-center overflow-hidden rounded-lg bg-[#FFD7C1]">
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
            <div className="group relative size-full">
              <img
                src={image}
                alt="Selected"
                className="size-full object-cover"
              />
              {!readOnly && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/40 transition-all">
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
              className={readOnly ? '!hover:bg-transparent !mx-0 !p-0' : ''}
            >
              {readOnly ? 'Chưa có hình ảnh' : 'Thêm hình ảnh'}
            </Button>
          )}
        </div>
      </div>

      {/* Right Column */}
      <div className="flex flex-col justify-between overflow-y-auto pr-4 md:col-span-3">
        <div className="flex flex-col gap-6">
          {/* Measurement Unit */}
          <div>
            <label className="mb-2 block font-medium text-gray-700">
              Đơn vị tính
            </label>
            <div className="relative">
              <select
                value={unit || ''}
                onChange={(e) => !readOnly && setUnit(e.target.value || null)}
                disabled={readOnly}
                className={`w-full rounded-lg border border-gray-300 p-3 text-gray-700 ${
                  readOnly
                    ? 'cursor-default bg-gray-50'
                    : 'bg-white focus:border-gray-400 focus:outline-none'
                }`}
              >
                <option value="">
                  {!unit ? (readOnly ? 'Không có dữ liệu' : 'Chọn đơn vị') : ''}
                </option>
                {(isCountable ? COUNTABLE_UNITS : UNCOUNTABLE_UNITS).map(
                  (u) => (
                    <option key={u} value={u}>
                      {u}
                    </option>
                  )
                )}
              </select>
            </div>
          </div>

          {/* Shelf Life */}
          <div>
            <label className="mb-2 block font-bold text-gray-700">
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
              className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                readOnly
                  ? 'bg-gray-50 focus:outline-none'
                  : 'focus:border-gray-400 focus:outline-none'
              }`}
            />
            {readOnly && !shelfLife && (
              <p className="text-sm text-gray-500">Không có dữ liệu</p>
            )}
          </div>

          {/* Price */}
          <div>
            <label className="mb-2 block font-bold text-gray-700">
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
              className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                readOnly
                  ? 'bg-gray-50 focus:outline-none'
                  : 'focus:border-gray-400 focus:outline-none'
              }`}
            />
            {readOnly && !price && (
              <p className="text-sm text-gray-500">Không có dữ liệu</p>
            )}
          </div>

          {/* Hàm lượng dinh dưỡng trên */}
          <div>
            <label className="mb-2 block font-bold text-gray-700">
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
                <label className="mb-1 block font-bold text-gray-700">
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
                  className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:border-gray-400 focus:outline-none'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="mb-1 block font-bold text-gray-700">
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
                  className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:border-gray-400 focus:outline-none'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="mb-1 block font-bold text-gray-700">
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
                  className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:border-gray-400 focus:outline-none'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="mb-1 block font-bold text-gray-700">
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
                  className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:border-gray-400 focus:outline-none'
                  }`}
                  readOnly={readOnly}
                />
              </div>
              <div>
                <label className="mb-1 block font-bold text-gray-700">
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
                  className={`w-full border-b border-gray-300 p-2 text-gray-700 ${
                    readOnly
                      ? 'bg-gray-50 focus:outline-none'
                      : 'focus:border-gray-400 focus:outline-none'
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
        <div className="mt-8 flex justify-center gap-6">
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
