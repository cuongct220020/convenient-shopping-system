import React, { useState, useMemo } from 'react'
import { Search, Plus, Settings2, LayoutGrid } from 'lucide-react'
import Item from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
import { Sidebar } from '../components/Sidebar'

// Dữ liệu giả lập để hiển thị giống hình ảnh
const allIngredientsData = Array(200)
  .fill(null)
  .map((_, index) => {
    // Tạo sự đa dạng nhẹ cho dữ liệu
    if (index === 3)
      return {
        id: index,
        name: 'Trứng gà',
        category: 'Trứng',
        image: '/src/assets/garlic.png'
      }
    if (index === 9)
      return {
        id: index,
        name: 'Sữa bò',
        category: 'Sữa',
        image: '/src/assets/garlic.png'
      }
    if (index === 11)
      return {
        id: index,
        name: 'Thịt bò',
        category: 'Thịt đỏ',
        image: '/src/assets/garlic.png'
      }
    if (index === 13)
      return {
        id: index,
        name: 'Củ cải ta',
        category: 'Rau củ',
        image: '/src/assets/garlic.png'
      }

    // Mặc định là Tỏi
    return {
      id: index,
      name: 'Tỏi',
      category: 'Gia vị',
      image: '/src/assets/garlic.png'
    }
  })

const ITEMS_PER_PAGE = 20

const IngredientDashboard = () => {
  const [currentPage, setCurrentPage] = useState(1)

  // Calculate pagination data
  const { totalPages, currentItems, startIndex, endIndex } = useMemo(() => {
    const totalPages = Math.ceil(allIngredientsData.length / ITEMS_PER_PAGE)
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
    const endIndex = startIndex + ITEMS_PER_PAGE
    const currentItems = allIngredientsData.slice(startIndex, endIndex)

    return {
      totalPages,
      currentItems,
      startIndex: startIndex + 1,
      endIndex: Math.min(endIndex, allIngredientsData.length)
    }
  }, [currentPage])
  return (
    <div
      className="flex bg-white font-sans text-gray-800"
      style={{ width: '1440px', height: '1024px' }}
    >
      {/* --- SIDEBAR --- */}
      <Sidebar />

      {/* --- MAIN CONTENT --- */}
      <main
        className="flex flex-1 flex-col overflow-y-auto p-8"
        style={{ width: 'calc(1440px - 330px)' }}
      >
        {/* Header */}
        <div className="mb-8 flex flex-col space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">
              Danh mục nguyên liệu
            </h2>

            <div className="flex items-center space-x-4">
              <Button variant="primary" icon={Plus} size="fit">
                Thêm nguyên liệu
              </Button>

              <button className="rounded-lg p-2 text-gray-500 hover:bg-gray-100">
                <Settings2 size={20} />
              </button>

              <div className="relative">
                <input
                  type="text"
                  placeholder="Tìm kiếm..."
                  className="w-64 rounded-lg border border-gray-300 py-2 pl-4 pr-10 text-sm focus:outline-none focus:ring-1 focus:ring-rose-500"
                />
                <Search
                  className="absolute right-3 top-2.5 text-gray-400"
                  size={18}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end text-sm text-gray-600">
            <LayoutGrid size={16} className="mr-2" />
            <span>
              Đang hiển thị{' '}
              <span className="font-bold">
                {startIndex} - {endIndex}
              </span>{' '}
              / {allIngredientsData.length} nguyên liệu
            </span>
          </div>
        </div>

        {/* Grid Container */}
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {currentItems.map((item) => (
            <Item
              key={item.id}
              name={item.name}
              category={item.category}
              image={item.image}
            />
          ))}
        </div>

        {/* Pagination */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          className="mt-auto pt-8"
        />
      </main>
    </div>
  )
}

export default IngredientDashboard
