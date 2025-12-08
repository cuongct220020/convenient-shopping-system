import { useState, useRef, useEffect } from 'react'
import { Check, X, Image as ImageIcon, ChevronDown } from 'lucide-react'
import { Button } from './Button'
import { InputField } from './InputField'

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
  
  const getInputType = (value: string | number | undefined, defaultType: string) => {
    if (readOnly && (value === undefined || value === null || value === '')) {
      return 'text'
    }
    return defaultType
  }

  const inputReadOnlyClass = readOnly
    ? 'bg-gray-50 focus:outline-none'
    : 'bg-white focus:outline-none focus:border-gray-400'

  const numberInputClass = `w-full p-2 border-b border-gray-300 text-gray-700 ${
    readOnly ? 'bg-gray-50 focus:outline-none' : 'focus:outline-none focus:border-gray-400'
  }`

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
        <div className="bg-[#fcece9] rounded-lg aspect-square flex items-center justify-center relative overflow-hidden">
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
              variant="primary"
              size="fit"
              icon={ImageIcon}
              onClick={handleImageUploadClick}
              disabled={readOnly}
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
              {/* Calo */}
              <div className="col-span-2">
                <label className="block text-gray-700 font-bold mb-1">
                  Calo
                </label>
                <input
                  type={getInputType(initialData?.calories, 'number')}
                  placeholder={readOnly ? '' : '0'}
                  className={numberInputClass}
                  readOnly={readOnly}
                  defaultValue={getDisplayValue(initialData?.calories)}
                />
              </div>
              {/* Đạm */}
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Đạm
                </label>
                <input
                  type={getInputType(initialData?.protein, 'number')}
                  placeholder={readOnly ? '' : '0'}
                  className={numberInputClass}
                  readOnly={readOnly}
                  defaultValue={getDisplayValue(initialData?.protein)}
                />
              </div>
              {/* Chất bột đường */}
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Chất bột đường
                </label>
                <input
                  type={getInputType(initialData?.carbs, 'number')}
                  placeholder={readOnly ? '' : '0'}
                  className={numberInputClass}
                  readOnly={readOnly}
                  defaultValue={getDisplayValue(initialData?.carbs)}
                />
              </div>
              {/* Chất xơ */}
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Chất xơ
                </label>
                <input
                  type={getInputType(initialData?.fiber, 'number')}
                  placeholder={readOnly ? '' : '0'}
                  className={numberInputClass}
                  readOnly={readOnly}
                  defaultValue={getDisplayValue(initialData?.fiber)}
                />
              </div>
              {/* Chất béo */}
              <div>
                <label className="block text-gray-700 font-bold mb-1">
                  Chất béo
                </label>
                <input
                  type={getInputType(initialData?.fat, 'number')}
                  placeholder={readOnly ? '' : '0'}
                  className={numberInputClass}
                  readOnly={readOnly}
                  defaultValue={getDisplayValue(initialData?.fat)}
                />
              </div>
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
