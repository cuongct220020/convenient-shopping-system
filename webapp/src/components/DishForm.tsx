import React, { useState, useRef, useEffect } from 'react'
import { Trash2, Plus, Check, X, Image as ImageIcon, ChevronDown } from 'lucide-react'
import { Button } from './Button' // Assuming Button component exists
import { InputField } from './InputField'
import { FormInput } from './FormInput'

// Mock data for dropdowns
const categories = ['Đồ ăn vặt', 'Món chính', 'Món khai vị', 'Tráng miệng', 'Đồ uống']
const difficulties = ['Dễ', 'Trung bình', 'Khó']
const ingredientOptions = ['Hành tím', 'Tỏi', 'Ớt', 'Gừng', 'Thịt gà', 'Thịt bò']

interface DishFormProps {
  onSubmit: (dishData: any) => void
  onCancel: () => void
  submitLabel?: string
  readOnly?: boolean
  actions?: React.ReactNode
  initialData?: {
    dishName: string
    category: string
    difficulty: string
    image: string | null
    servings: number
    cookTime: string
    prepTime: string
    ingredients: { id: number; name: string; quantity: string }[]
    instructions: { id: number; title: string; description: string }[]
  }
}

export const DishForm: React.FC<DishFormProps> = ({
  onSubmit,
  onCancel,
  submitLabel = 'Xác nhận',
  readOnly = false,
  actions,
  initialData
}) => {
  const [dishName, setDishName] = useState('')
  const [dishNameError, setDishNameError] = useState('')
  const [category, setCategory] = useState('Chọn loại món ăn')
  const [difficulty, setDifficulty] = useState('Chọn độ khó')
  const [image, setImage] = useState<string | null>(null)
  const [servings, setServings] = useState<string | number>('')
  const [cookTime, setCookTime] = useState('')
  const [prepTime, setPrepTime] = useState('')

  const [isCategoryOpen, setIsCategoryOpen] = useState(false)
  const [isDifficultyOpen, setIsDifficultyOpen] = useState(false)
  const [openIngredientDropdowns, setOpenIngredientDropdowns] = useState<Set<number>>(new Set())

  const categoryDropdownRef = useRef<HTMLDivElement>(null)
  const difficultyDropdownRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [ingredients, setIngredients] = useState<{ id: number; name: string; quantity: string }[]>([])

  const [instructions, setInstructions] = useState<{ id: number; title: string; description: string }[]>([])

  // Initialize form with initialData when provided
  useEffect(() => {
    if (initialData) {
      setDishName(initialData.dishName || '')
      setCategory(initialData.category || 'Chọn loại món ăn')
      setDifficulty(initialData.difficulty || 'Chọn độ khó')
      setImage(initialData.image || null)
      setServings(initialData.servings || 0)
      setCookTime(initialData.cookTime || '')
      setPrepTime(initialData.prepTime || '')
      setIngredients(initialData.ingredients || [])
      setInstructions(initialData.instructions || [])
    }
  }, [initialData])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        categoryDropdownRef.current &&
        !categoryDropdownRef.current.contains(event.target as Node)
      ) {
        setIsCategoryOpen(false)
      }
      if (
        difficultyDropdownRef.current &&
        !difficultyDropdownRef.current.contains(event.target as Node)
      ) {
        setIsDifficultyOpen(false)
      }
      // Close all ingredient dropdowns when clicking outside
      const ingredientDropdownElements = document.querySelectorAll('[data-ingredient-dropdown]')
      let clickedOutsideAll = true
      ingredientDropdownElements.forEach((element) => {
        if (element.contains(event.target as Node)) {
          clickedOutsideAll = false
        }
      })
      if (clickedOutsideAll) {
        setOpenIngredientDropdowns(new Set())
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleImageUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const imageUrl = URL.createObjectURL(file)
      setImage(imageUrl)
    }
  }

  const handleAddIngredient = () => {
    const newId = ingredients.length > 0 ? Math.max(...ingredients.map(i => i.id)) + 1 : 1
    setIngredients([...ingredients, { id: newId, name: 'Chọn nguyên liệu', quantity: '' }])
  }

  const handleRemoveIngredient = (id: number) => {
    setIngredients(ingredients.filter((item) => item.id !== id))
    // Close dropdown if this ingredient was open
    const newOpenSet = new Set(openIngredientDropdowns)
    newOpenSet.delete(id)
    setOpenIngredientDropdowns(newOpenSet)
  }

  const handleIngredientChange = (id: number, field: 'name' | 'quantity', value: string) => {
    setIngredients(
      ingredients.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    )
  }

  const toggleIngredientDropdown = (id: number) => {
    const newOpenSet = new Set(openIngredientDropdowns)
    if (newOpenSet.has(id)) {
      newOpenSet.delete(id)
    } else {
      // Close all other dropdowns and open this one
      newOpenSet.clear()
      newOpenSet.add(id)
    }
    setOpenIngredientDropdowns(newOpenSet)
  }

  const selectIngredient = (ingredientId: number, value: string) => {
    handleIngredientChange(ingredientId, 'name', value)
    // Close dropdown after selection
    const newOpenSet = new Set(openIngredientDropdowns)
    newOpenSet.delete(ingredientId)
    setOpenIngredientDropdowns(newOpenSet)
  }

  const handleAddInstruction = () => {
    const newId = instructions.length > 0 ? Math.max(...instructions.map(i => i.id)) + 1 : 1
    setInstructions([
      ...instructions,
      { id: newId, title: 'Bước mới', description: '' },
    ])
  }


  const handleAddCookInstruction = () => {
    const newId = instructions.length > 0 ? Math.max(...instructions.map(i => i.id)) + 1 : 1
    setInstructions([
      ...instructions,
      { id: newId, title: '', description: '' },
    ])
  }

  const handleRemoveInstruction = (id: number) => {
    setInstructions(instructions.filter((item) => item.id !== id))
  }

  const handleInstructionChange = (id: number, field: 'title' | 'description', value: string) => {
    setInstructions(
      instructions.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    )
  }

  const handleSave = () => {
    onSubmit({
      dishName,
      category,
      difficulty,
      image,
      servings,
      cookTime,
      prepTime,
      ingredients,
      instructions,
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
            id="dishName"
            value={dishName}
            onChange={(e) => setDishName(e.target.value)}
            error={dishNameError}
            readOnly={readOnly}
          />
        </div>

        <div className="flex flex-col gap-4">
          <div className="flex gap-2 w-full">
            <div className="w-1/2">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                Phân loại
              </label>
              <div className="relative" ref={categoryDropdownRef}>
                <button
                  type="button"
                  className={`w-full p-2 border border-gray-300 rounded-lg text-gray-700 flex justify-between items-center ${
                    readOnly
                      ? 'bg-gray-50 cursor-default'
                      : 'bg-white focus:outline-none focus:border-gray-400'
                  }`}
                  onClick={() => !readOnly && setIsCategoryOpen(!isCategoryOpen)}
                >
                  <span className={category === 'Chưa có thông tin' ? 'text-gray-400 italic' : ''}>{category}</span>
                  {!readOnly && <ChevronDown size={20} className="text-gray-500" />}
                </button>

                {isCategoryOpen && !readOnly && (
                  <div className="absolute w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                    {categories.map((c, index) => (
                      <div
                        key={index}
                        className="p-3 hover:bg-gray-100 cursor-pointer text-gray-700"
                        onClick={() => {
                          setCategory(c)
                          setIsCategoryOpen(false)
                        }}
                      >
                        {c}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="w-1/2">
              <label htmlFor="difficulty" className="block text-sm font-medium text-gray-700">
                Độ khó
              </label>
              <div className="relative" ref={difficultyDropdownRef}>
                <button
                  type="button"
                  className={`w-full p-2 border border-gray-300 rounded-lg text-gray-700 flex justify-between items-center ${
                    readOnly
                      ? 'bg-gray-50 cursor-default'
                      : 'bg-white focus:outline-none focus:border-gray-400'
                  }`}
                  onClick={() => !readOnly && setIsDifficultyOpen(!isDifficultyOpen)}
                >
                  <span className={difficulty === 'Chưa có thông tin' ? 'text-gray-400 italic' : ''}>{difficulty}</span>
                  {!readOnly && <ChevronDown size={20} className="text-gray-500" />}
                </button>

                {isDifficultyOpen && !readOnly && (
                  <div className="absolute w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                    {difficulties.map((d, index) => (
                      <div
                        key={index}
                        className="p-3 hover:bg-gray-100 cursor-pointer text-gray-700"
                        onClick={() => {
                          setDifficulty(d)
                          setIsDifficultyOpen(false)
                        }}
                      >
                        {d}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-[#FFD7C1] rounded-lg aspect-square flex items-center justify-center relative overflow-hidden">
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
          />
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

        <FormInput
          label="Số người ăn"
          id="servings"
          type="text"
          value={servings}
          placeholder="0"
          onChange={(e) => setServings(e.target.value)}
          readOnly={readOnly}
          showEmptyState={false}
        />

        <div className="flex space-x-4">
          <div className="w-1/2">
            <FormInput
              label="Thời gian nấu"
              id="cookTime"
              type="text"
              value={cookTime}
              placeholder="VD: 1 giờ"
              onChange={(e) => setCookTime(e.target.value)}
              readOnly={readOnly}
              showEmptyState={false}
            />
          </div>
          <div className="w-1/2">
            <FormInput
              label="Thời gian chuẩn bị"
              id="prepTime"
              type="text"
              value={prepTime}
              placeholder="VD: 30 phút"
              onChange={(e) => setPrepTime(e.target.value)}
              readOnly={readOnly}
              showEmptyState={false}
            />
          </div>
        </div>
      </div>

      {/* Right Column */}
      <div className="md:col-span-3 flex flex-col space-y-8">
        {/* Ingredients */}
        <div>
          <h3 className="mb-4 text-lg font-bold text-gray-800">Nguyên liệu</h3>
          <div className="space-y-4">
            {ingredients.length === 0 && readOnly ? (
              <div className="text-gray-500 italic p-4 text-center bg-gray-50 rounded-lg">
                Chưa có thông tin nguyên liệu
              </div>
            ) : (
              ingredients.map((ingredient, index) => (
                <div key={ingredient.id} className="flex items-center space-x-4">
                  <span className="text-gray-600 w-8">{index + 1}.</span>
                  {readOnly ? (
                    <>
                      <div className="flex-1 p-2 border border-gray-300 rounded-lg bg-gray-50">
                        <span className="text-gray-700">{ingredient.name}</span>
                      </div>
                      <div className="flex-1">
                        <div className="p-2 border border-gray-300 rounded-lg bg-gray-50">
                          <span className="text-gray-700">{ingredient.quantity || 'Chưa có thông tin'}</span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex-1 relative" data-ingredient-dropdown>
                        <button
                          type="button"
                          className="w-full p-2 border border-gray-300 rounded-lg text-gray-700 flex justify-between items-center bg-white focus:outline-none focus:border-gray-400 text-left"
                          onClick={() => toggleIngredientDropdown(ingredient.id)}
                        >
                          <span className="truncate">{ingredient.name}</span>
                          <ChevronDown size={20} className="text-gray-500 flex-shrink-0" />
                        </button>

                        {openIngredientDropdowns.has(ingredient.id) && (
                          <div className="absolute w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                            {ingredientOptions.map((option) => (
                              <div
                                key={option}
                                className="p-3 hover:bg-gray-100 cursor-pointer text-gray-700"
                                onClick={() => selectIngredient(ingredient.id, option)}
                              >
                                {option}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <InputField
                        type="text"
                        value={ingredient.quantity}
                        onChange={(e) =>
                          handleIngredientChange(ingredient.id, 'quantity', e.target.value)
                        }
                        placeholder="Số lượng (VD: 100g)"
                        containerClassName="flex-1"
                      />
                      <Button
                        onClick={() => handleRemoveIngredient(ingredient.id)}
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
                onClick={handleAddIngredient}
                variant="secondary"
                size="fit"
                icon={Plus}
                className="!mx-0"
              />
            </div>
          )}
        </div>

        {/* Cooking Instructions */}
        <div className="flex-1">
          <h3 className="mb-4 text-lg font-bold text-gray-800">Hướng dẫn nấu</h3>

          <div className="mb-6">
            <div className="space-y-2">
              {instructions.length === 0 && readOnly ? (
                <div className="text-gray-500 italic p-4 text-center bg-gray-50 rounded-lg">
                  Chưa có thông tin hướng dẫn nấu
                </div>
              ) : (
                instructions.map((instruction) => (
                  <div key={instruction.id} className="flex items-start space-x-4">
                    <div className="flex-1">
                      {readOnly ? (
                        <>
                          <div className="font-bold text-gray-800 px-2 py-1">
                            {instruction.title || 'Chưa có thông tin'}
                          </div>
                          <div className="text-gray-600 px-2 py-1 mt-1 whitespace-pre-wrap">
                            {instruction.description || 'Chưa có thông tin'}
                          </div>
                        </>
                      ) : (
                        <>
                          <input
                            type="text"
                            value={instruction.title}
                            onChange={(e) => handleInstructionChange(instruction.id, 'title', e.target.value)}
                            placeholder="Nhập tên bước"
                            className="font-bold text-gray-800 w-full border-0 focus:outline-none focus:ring-2 focus:ring-rose-500 rounded px-2 py-1 placeholder:font-normal"
                          />
                          <textarea
                            value={instruction.description}
                            onChange={(e) => handleInstructionChange(instruction.id, 'description', e.target.value)}
                            placeholder="Nhập mô tả chi tiết..."
                            className="text-gray-600 w-full border-0 focus:outline-none focus:ring-2 focus:ring-rose-500 rounded px-2 py-1 mt-1 min-h-[2.5rem] resize-none overflow-hidden"
                            rows={1}
                            style={{
                              height: 'auto'
                            }}
                            onInput={(e) => {
                              const target = e.target as HTMLTextAreaElement;
                              target.style.height = 'auto';
                              target.style.height = target.scrollHeight + 'px';
                            }}
                          />
                        </>
                      )}
                    </div>
                    {!readOnly && (
                      <Button
                        onClick={() => handleRemoveInstruction(instruction.id)}
                        variant="icon"
                        icon={Trash2}
                        className="!py-2 !px-2 !w-fit !h-fit"
                      />
                    )}
                  </div>
                ))
              )}
            </div>
            {!readOnly && (
              <div className="mt-4">
                <Button
                  onClick={handleAddCookInstruction}
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