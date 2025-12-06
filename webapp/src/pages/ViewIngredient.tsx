import { Check, Image as ImageIcon, Edit } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../components/Button'

const ViewIngredient = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const item = location.state?.item

  const handleBack = () => {
    navigate('/ingredient-list')
  }

  if (!item) {
    return <div>Loading...</div>
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
              defaultValue={item.name}
              readOnly
              className="w-full p-3 border border-gray-300 rounded-lg text-gray-700 bg-gray-50 focus:outline-none"
            />
          </div>

          {/* Phân loại */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Phân loại
            </label>
            <div className="relative">
              <div className="w-full p-3 border border-gray-300 rounded-lg text-gray-700 bg-gray-50 flex justify-between items-center">
                <span>{item.category}</span>
              </div>
            </div>
          </div>

          {/* Hình ảnh */}
          <div className="bg-[#fcece9] rounded-lg aspect-square flex items-center justify-center overflow-hidden">
            {item.image ? (
              <img
                src={item.image}
                alt={item.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <Button variant="primary" size="fit" icon={ImageIcon} disabled>
                Hình ảnh
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
                defaultValue="100 g"
                readOnly
                className="w-full text-gray-700 p-3 border-b border-gray-300 bg-transparent focus:outline-none"
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
                    readOnly
                    className="w-full p-2 border-b border-gray-300 text-gray-700 bg-transparent focus:outline-none"
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
                    readOnly
                    className="w-full p-2 border-b border-gray-300 text-gray-700 bg-transparent focus:outline-none"
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
                    readOnly
                    className="w-full p-2 border-b border-gray-300 text-gray-700 bg-transparent focus:outline-none"
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
                    readOnly
                    className="w-full p-2 border-b border-gray-300 text-gray-700 bg-transparent focus:outline-none"
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
                    readOnly
                    className="w-full p-2 border-b border-gray-300 text-gray-700 bg-transparent focus:outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-4 items-end mt-8">
            <Button variant="primary" size="fit" icon={Check} onClick={handleBack}>
              Quay lại
            </Button>
            <Button variant="secondary" size="fit" icon={Edit}>
              Chỉnh sửa
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ViewIngredient