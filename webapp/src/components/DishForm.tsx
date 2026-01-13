import { useState, useRef } from 'react'
import { Trash2, Plus, Check, X, Image as ImageIcon } from 'lucide-react'
import { Button } from './Button'
import { InputField } from './InputField'
import { DropdownInputField } from './DropDownInputField'
import {
  DishLevelTypeSchema,
  DishLevelType,
  Dish
} from '../services/schema/dishSchema'

const DISH_LEVELS = DishLevelTypeSchema.options as readonly DishLevelType[]

interface DishFormProps {
  onSubmit: (dishData: Partial<Dish>) => void
  onCancel: () => void
  submitLabel?: string
  readOnly?: boolean
  actions?: React.ReactNode
  initialData?: Partial<Dish>
}

export const DishForm: React.FC<DishFormProps> = ({
  onSubmit,
  onCancel,
  submitLabel = 'Xác nhận',
  readOnly = false,
  actions,
  initialData
}) => {
  const [componentName, setComponentName] = useState(
    initialData?.component_name || ''
  )
  const [level, setLevel] = useState<DishLevelType | undefined>(
    initialData?.level
  )
  const [imageUrl, setImageUrl] = useState<string | null>(
    initialData?.image_url || null
  )
  const [servings, setServings] = useState<number | ''>(
    initialData?.default_servings || ''
  )
  const [cookTime, setCookTime] = useState<number | null | ''>(
    initialData?.cook_time ?? ''
  )
  const [prepTime, setPrepTime] = useState<number | null | ''>(
    initialData?.prep_time ?? ''
  )
  const [keywords, setKeywords] = useState<string[]>(
    initialData?.keywords || []
  )
  const [instructions, setInstructions] = useState<string[]>(
    initialData?.instructions || []
  )

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUploadClick = () => {
    if (!readOnly) {
      fileInputRef.current?.click()
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setImageUrl(url)
    }
  }

  const handleAddKeyword = () => {
    setKeywords([...keywords, ''])
  }

  const handleRemoveKeyword = (index: number) => {
    setKeywords(keywords.filter((_, i) => i !== index))
  }

  const handleKeywordChange = (index: number, value: string) => {
    setKeywords(keywords.map((kw, i) => (i === index ? value : kw)))
  }

  const handleAddInstruction = () => {
    setInstructions([...instructions, ''])
  }

  const handleRemoveInstruction = (index: number) => {
    setInstructions(instructions.filter((_, i) => i !== index))
  }

  const handleInstructionChange = (index: number, value: string) => {
    setInstructions(instructions.map((inst, i) => (i === index ? value : inst)))
  }

  const handleSave = () => {
    onSubmit({
      component_name: componentName || undefined,
      level,
      image_url: imageUrl,
      default_servings: servings ? Number(servings) : undefined,
      cook_time: cookTime ? Number(cookTime) : null,
      prep_time: prepTime ? Number(prepTime) : null,
      keywords: keywords.filter(Boolean),
      instructions: instructions.filter(Boolean),
      component_list: []
    })
  }

  return (
    <div
      className="bg-white p-8 rounded-xl shadow-md grid grid-cols-1 md:grid-cols-5 gap-8 overflow-y-auto"
      style={{ width: '950px', height: '850px' }}
    >
      {/* Left Column */}
      <div className="md:col-span-2 space-y-6">
        <div>
          <InputField
            label="Tên món ăn"
            placeholder="Nhập tên món ăn"
            type="text"
            id="componentName"
            value={componentName}
            onChange={(e) => setComponentName(e.target.value)}
            readOnly={readOnly}
          />
        </div>

        <DropdownInputField
          label="Độ khó"
          id="level"
          options={DISH_LEVELS.map((lv) => ({
            value: lv,
            label: lv
          }))}
          value={level}
          onChange={(value) => setLevel(value as DishLevelType)}
          placeholder="Chọn độ khó"
          readOnly={readOnly}
        />

        <div className="bg-[#FFD7C1] rounded-lg aspect-square flex items-center justify-center relative overflow-hidden">
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
          />
          {imageUrl ? (
            <div className="group relative w-full h-full">
              <img
                src={imageUrl}
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
          ) : readOnly ? (
            <div className="text-gray-500">Không có hình ảnh</div>
          ) : (
            <Button
              variant="primary"
              size="fit"
              icon={ImageIcon}
              onClick={handleImageUploadClick}
            >
              Thêm hình ảnh
            </Button>
          )}
        </div>

        <div>
          <label
            htmlFor="servings"
            className="block text-sm font-bold text-gray-700"
          >
            Số người ăn
          </label>
          <input
            type="number"
            id="servings"
            value={servings}
            placeholder="0"
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setServings(e.target.value ? parseInt(e.target.value) : '')
            }
            readOnly={readOnly}
            className={`mt-1 block w-full border-b border-gray-300 p-2 text-lg focus:border-rose-500 focus:outline-none ${
              readOnly ? 'bg-gray-50' : ''
            }`}
          />
        </div>

        <div className="flex space-x-4">
          <div className="w-1/2">
            <label
              htmlFor="cookTime"
              className="block text-sm font-bold text-gray-700"
            >
              Thời gian nấu (phút)
            </label>
            <input
              type="number"
              id="cookTime"
              value={cookTime === null || cookTime === '' ? '' : cookTime}
              placeholder="0"
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setCookTime(e.target.value ? parseInt(e.target.value) : null)
              }
              readOnly={readOnly}
              className={`mt-1 block w-full border-b border-gray-300 p-2 text-lg focus:border-rose-500 focus:outline-none ${
                readOnly ? 'bg-gray-50' : ''
              }`}
            />
          </div>
          <div className="w-1/2">
            <label
              htmlFor="prepTime"
              className="block text-sm font-bold text-gray-700"
            >
              Thời gian chuẩn bị (phút)
            </label>
            <input
              type="number"
              id="prepTime"
              value={prepTime === null || prepTime === '' ? '' : prepTime}
              placeholder="0"
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setPrepTime(e.target.value ? parseInt(e.target.value) : null)
              }
              readOnly={readOnly}
              className={`mt-1 block w-full border-b border-gray-300 p-2 text-lg focus:border-rose-500 focus:outline-none ${
                readOnly ? 'bg-gray-50' : ''
              }`}
            />
          </div>
        </div>
      </div>

      {/* Right Column */}
      <div className="md:col-span-3 flex flex-col space-y-8">
        {/* Keywords */}
        <div>
          <h3 className="mb-4 text-lg font-bold text-gray-800">Từ khóa</h3>
          <div className="space-y-4">
            {keywords.length === 0 && readOnly ? (
              <div className="text-gray-500 italic p-4 text-center bg-gray-50 rounded-lg">
                Chưa có thông tin từ khóa
              </div>
            ) : (
              keywords.map((keyword, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <span className="text-gray-600 w-8">{index + 1}.</span>
                  {readOnly ? (
                    <div className="flex-1 p-2 border border-gray-300 rounded-lg bg-gray-50">
                      <span className="text-gray-700">
                        {keyword || 'Chưa có thông tin'}
                      </span>
                    </div>
                  ) : (
                    <>
                      <InputField
                        type="text"
                        value={keyword}
                        onChange={(e) =>
                          handleKeywordChange(index, e.target.value)
                        }
                        placeholder="Nhập từ khóa"
                        containerClassName="flex-1"
                      />
                      <Button
                        onClick={() => handleRemoveKeyword(index)}
                        variant="icon"
                        icon={Trash2}
                        className="!py-2 !px-2 !w-fit !h-fit"
                      />
                    </>
                  )}
                </div>
              ))
            )}
          </div>
          {!readOnly && (
            <div className="mt-4">
              <Button
                onClick={handleAddKeyword}
                variant="secondary"
                size="fit"
                icon={Plus}
                className="!mx-0"
              />
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="flex-1">
          <h3 className="mb-4 text-lg font-bold text-gray-800">
            Hướng dẫn nấu
          </h3>

          <div className="mb-6">
            <div className="space-y-4">
              {instructions.length === 0 && readOnly ? (
                <div className="text-gray-500 italic p-4 text-center bg-gray-50 rounded-lg">
                  Chưa có thông tin hướng dẫn nấu
                </div>
              ) : (
                instructions.map((instruction, index) => (
                  <div key={index} className="flex items-start space-x-4">
                    <span className="text-gray-600 w-8 flex-shrink-0 pt-2">
                      {index + 1}.
                    </span>
                    <div className="flex-1">
                      {readOnly ? (
                        <div className="text-gray-700 px-2 py-1 whitespace-pre-wrap">
                          {instruction || 'Chưa có thông tin'}
                        </div>
                      ) : (
                        <textarea
                          value={instruction}
                          onChange={(e) =>
                            handleInstructionChange(index, e.target.value)
                          }
                          placeholder="Nhập hướng dẫn..."
                          className="text-gray-700 w-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-rose-500 rounded px-2 py-1 min-h-[2.5rem] resize-none overflow-hidden"
                          rows={1}
                          style={{
                            height: 'auto'
                          }}
                          onInput={(e) => {
                            const target = e.target as HTMLTextAreaElement
                            target.style.height = 'auto'
                            target.style.height = target.scrollHeight + 'px'
                          }}
                        />
                      )}
                    </div>
                    {!readOnly && (
                      <Button
                        onClick={() => handleRemoveInstruction(index)}
                        variant="icon"
                        icon={Trash2}
                        className="!py-2 !px-2 !w-fit !h-fit flex-shrink-0"
                      />
                    )}
                  </div>
                ))
              )}
            </div>
            {!readOnly && (
              <div className="mt-4">
                <Button
                  onClick={handleAddInstruction}
                  variant="secondary"
                  size="fit"
                  icon={Plus}
                  className="!mx-0"
                />
              </div>
            )}
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
                onClick={handleSave}
                className="!mx-0 -mr-2"
              >
                {submitLabel}
              </Button>
              <Button
                variant="secondary"
                size="fit"
                icon={X}
                onClick={onCancel}
                className="!mx-0 -ml-2"
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
