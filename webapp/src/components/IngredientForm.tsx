import { useState, useRef, useEffect } from 'react'
import { Check, X, Image as ImageIcon, ChevronDown } from 'lucide-react'
import { Button } from './Button'
import { InputField } from './InputField'
import { FormInput } from './FormInput'

interface IngredientFormProps {
  initialData?: {
    name?: string
    category?: string
    image?: string
    nutritionPer?: string
    calories?: number
    protein?: number
    carbs?: number
    fiber?: number
    fat?: number
  }
  onSubmit?: () => void
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
  const [isOpen, setIsOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    initialData?.category || null
  )
  const [image, setImage] = useState<string | null>(initialData?.image || null)
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
    'Đồ uống',
  ]

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
          defaultValue={getDisplayValue(initialData?.name)}
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
      <div className="md:col-span-3 flex flex-col justify-between">
        <div className="flex flex-col gap-6">
          {/* Hàm lượng dinh dưỡng trên */}
          <div>
            <label className="block text-gray-700 font-bold text-lg mb-2">
              Hàm lượng dinh dưỡng trên
            </label>
            <input
              type="text"
              placeholder={readOnly ? '' : '0 g'}
              className={`w-full text-gray-700 p-3 border-b border-gray-300 ${
                readOnly
                  ? 'bg-gray-50 focus:outline-none'
                  : 'focus:outline-none focus:border-gray-400'
              }`}
              defaultValue={getDisplayValue(initialData?.nutritionPer)}
              readOnly={readOnly}
            />
          </div>

          {/* Bao gồm: */}
          <div>
            <label className="block text-gray-700 font-medium mb-4">
              Bao gồm:
            </label>
            <div className="grid grid-cols-2 gap-x-8 gap-y-6">
              <FormInput
                variant="nutrition"
                label="Calo"
                value={initialData?.calories}
                readOnly={readOnly}
                containerClassName="col-span-2"
              />
              <FormInput
                variant="nutrition"
                label="Đạm"
                value={initialData?.protein}
                readOnly={readOnly}
              />
              <FormInput
                variant="nutrition"
                label="Chất bột đường"
                value={initialData?.carbs}
                readOnly={readOnly}
              />
              <FormInput
                variant="nutrition"
                label="Chất xơ"
                value={initialData?.fiber}
                readOnly={readOnly}
              />
              <FormInput
                variant="nutrition"
                label="Chất béo"
                value={initialData?.fat}
                readOnly={readOnly}
              />
            </div>
          </div>
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
                onClick={onSubmit}
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
