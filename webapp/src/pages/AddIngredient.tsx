import { useState, useRef, useEffect } from 'react'
import { Check, X, Image as ImageIcon, ChevronDown } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/Button'

const AddIngredient = () => {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('Thịt trắng')
  const dropdownRef = useRef<HTMLDivElement>(null)

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

  const handleContinue = () => {
    navigate('/ingredient-list')
  }

  const handleDraft = () => {
    navigate('/ingredient-list')
  }

  return (
    <div
      className="flex items-center justify-center bg-gray-700 p-4"
      style={{ width: '1440px', height: '1024px' }}
    >
      <div
        className="bg-white p-8 rounded-xl shadow-md grid grid-cols-1 md:grid-cols-5 gap-8"
        style={{ width: '800px', height: '600px' }}
      >
        {/* Left Column */}
        <div className="md:col-span-2 flex flex-col gap-6">
          {/* Tên nguyên liệu */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Tên nguyên liệu
            </label>
            <input
              type="text"
              defaultValue="Thịt gà"
              className="w-full p-3 border border-red-500 rounded-lg text-gray-700 focus:outline-none focus:border-red-600"
            />
            <p className="text-red-500 text-sm mt-1">
              Tên không đúng định dạng
            </p>
          </div>

          {/* Phân loại */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Phân loại
            </label>
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                className="w-full p-3 border border-gray-300 rounded-lg text-gray-700 bg-white focus:outline-none focus:border-gray-400 flex justify-between items-center"
                onClick={() => setIsOpen(!isOpen)}
              >
                <span>{selectedCategory}</span>
                <ChevronDown size={20} className="text-gray-500" />
              </button>

              {isOpen && (
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
          <div className="bg-[#fcece9] rounded-lg aspect-square flex items-center justify-center">
            <Button variant="primary" size="fit" icon={ImageIcon}>
              Thêm hình ảnh
            </Button>
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
                defaultValue="100 g"
                className="w-full text-gray-700 p-3 border-b border-gray-300 focus:outline-none focus:border-gray-400"
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
                    type="number"
                    placeholder="0"
                    className="w-full p-2 border-b border-gray-300 text-gray-700 focus:outline-none focus:border-gray-400"
                  />
                </div>
                {/* Đạm */}
                <div>
                  <label className="block text-gray-700 font-bold mb-1">
                    Đạm
                  </label>
                  <input
                    type="number"
                    placeholder="0"
                    className="w-full p-2 border-b border-gray-300 text-gray-700 focus:outline-none focus:border-gray-400"
                  />
                </div>
                {/* Chất bột đường */}
                <div>
                  <label className="block text-gray-700 font-bold mb-1">
                    Chất bột đường
                  </label>
                  <input
                    type="number"
                    placeholder="0"
                    className="w-full p-2 border-b border-gray-300 text-gray-700 focus:outline-none focus:border-gray-400"
                  />
                </div>
                {/* Chất xơ */}
                <div>
                  <label className="block text-gray-700 font-bold mb-1">
                    Chất xơ
                  </label>
                  <input
                    type="number"
                    placeholder="0"
                    className="w-full p-2 border-b border-gray-300 text-gray-700 focus:outline-none focus:border-gray-400"
                  />
                </div>
                {/* Chất béo */}
                <div>
                  <label className="block text-gray-700 font-bold mb-1">
                    Chất béo
                  </label>
                  <input
                    type="number"
                    placeholder="0"
                    className="w-full p-2 border-b border-gray-300 text-gray-700 focus:outline-none focus:border-gray-400"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-4 items-end mt-8">
            <Button variant="primary" size="fit" icon={Check} onClick={handleContinue}>
              Tiếp tục
            </Button>
            <Button variant="secondary" size="fit" icon={X} onClick={handleDraft}>
              Lưu bản nháp
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AddIngredient