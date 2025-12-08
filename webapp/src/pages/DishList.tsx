import React, { useState, useMemo } from 'react'
import { Search, Plus, Filter, LayoutGrid } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Item from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
// Assuming the uploaded image is placed in assets
import hamburgerImg from '../assets/hamburger.png'

// Dữ liệu giả lập cho Món ăn
const possibleNames = [
  'Hamburger',
  'Pizza Hải Sản',
  'Phở Bò',
  'Bún Chả',
  'Cơm Tấm',
  'Mì Ý Sốt Kem',
  'Gà Rán',
  'Khoai Tây Chiên',
  'Bánh Mì',
  'Sushi',
  'Sashimi',
  'Lẩu Thái',
  'Bò Bít Tết',
  'Salad Nga',
  'Nem Rán',
  'Bánh Xèo',
  'Trà Sữa',
  'Cà Phê Sữa',
  'Sinh Tố Bơ',
  'Nước Ép Cam'
]

const possibleCategories = [
  'Món ăn vặt',
  'Món chính',
  'Món khai vị',
  'Tráng miệng',
  'Đồ uống',
  'Đồ chay',
  'Bánh ngọt'
]

// Tạo 200 món ăn giả lập
const allDishesData = Array(200)
  .fill(null)
  .map((_, index) => {
    // Để giống screenshot, ta ưu tiên hiển thị Hamburger nhiều hơn một chút trong random
    const isHamburger = Math.random() > 0.7
    const randomNameIndex = Math.floor(Math.random() * possibleNames.length)
    const randomCategoryIndex = Math.floor(
      Math.random() * possibleCategories.length
    )

    return {
      id: index,
      name: isHamburger ? 'Hamburger' : possibleNames[randomNameIndex],
      category: isHamburger ? 'Món ăn vặt' : possibleCategories[randomCategoryIndex],
      image: hamburgerImg
    }
  })

const ITEMS_PER_PAGE = 20

const DishList = () => {
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilter, setShowFilter] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()

  const handleToggleFilter = () => {
    setShowFilter((prev) => !prev)
  }

  const handleAddDishClick = () => {
    navigate('/add-dish')
  }

  const handleItemClick = (item: any) => {
    // Convert the dish item to match ViewDish expected format
    const dishData = {
      id: item.id,
      name: item.name,
      category: item.category,
      image: item.image,
      // Add empty/dummy values for optional fields
      difficulty: '',
      servings: 0,
      cookTime: '',
      prepTime: '',
      ingredients: [],
      instructions: []
    }
    navigate('/view-dish', { state: { item: dishData } })
  }

  const uniqueCategories = useMemo(() => {
    const categories = new Set(allDishesData.map((item) => item.category))
    return Array.from(categories)
  }, [])

  const handleCategoryChange = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    )
    setCurrentPage(1)
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    setCurrentPage(1)
  }

  const { totalPages, currentItems, startIndex, endIndex, totalItems } =
    useMemo(() => {
      let filteredData = allDishesData

      if (selectedCategories.length > 0) {
        filteredData = filteredData.filter((item) =>
          selectedCategories.includes(item.category)
        )
      }

      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        filteredData = filteredData.filter((item) =>
          item.name.toLowerCase().includes(query)
        )
      }

      const totalItems = filteredData.length
      const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE) || 1
      const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
      const endIndex = startIndex + ITEMS_PER_PAGE
      const currentItems = filteredData.slice(startIndex, endIndex)

      return {
        totalPages,
        currentItems,
        startIndex: totalItems === 0 ? 0 : startIndex + 1,
        endIndex: Math.min(endIndex, totalItems),
        totalItems
      }
    }, [currentPage, selectedCategories, searchQuery])

  return (
        <main
          className="flex flex-1 flex-col overflow-y-auto p-8"
        >      {/* Header */}
      <div className="mb-8 flex flex-col space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-800">
            Danh mục món ăn
          </h2>

          <div className="flex items-center space-x-4">
            <Button variant="primary" icon={Plus} size="fit" onClick={handleAddDishClick}>
              Thêm món ăn
            </Button>

            <button
              className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100"
              onClick={handleToggleFilter}
            >
              <Filter size={20} />
              {selectedCategories.length > 0 && (
                <span className="absolute bottom-2 right-2 block size-2 rounded-full bg-red-500 ring-2 ring-white" />
              )}
              {showFilter && (
                <div
                  className="absolute right-0 top-full z-10 mt-2 w-[550px] rounded-md border border-gray-200 bg-white p-4 shadow-lg"
                  onClick={(e) => e.stopPropagation()}
                >
                  <h3 className="mb-2 font-semibold text-gray-700">
                    Lọc theo danh mục
                  </h3>
                  <div className="grid grid-cols-3 gap-3">
                    {uniqueCategories.map((category) => (
                      <label
                        key={category}
                        className="flex items-center space-x-2 text-sm text-gray-600"
                      >
                        <input
                          type="checkbox"
                          checked={selectedCategories.includes(category)}
                          onChange={() => handleCategoryChange(category)}
                          className="rounded border-gray-300 text-rose-500 focus:ring-rose-500"
                        />
                        <span>{category}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </button>

            <div className="relative">
              <input
                type="text"
                placeholder="Tìm kiếm..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-64 rounded-lg border border-gray-300 py-2 pl-4 pr-10 text-sm focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-600"
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
            / {totalItems} món ăn
          </span>
        </div>
      </div>

      {/* Grid Container */}
      {currentItems.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {currentItems.map((item) => (
            <Item
              key={item.id}
              name={item.name}
              category={item.category}
              image={item.image}
              onClick={() => handleItemClick(item)}
            />
          ))}
        </div>
      ) : (
        <div className="flex h-64 items-center justify-center text-gray-500">
          Không tìm thấy món ăn nào.
        </div>
      )}

      {/* Pagination */}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
        className="mt-auto pt-8"
      />
    </main>
  )
}

export default DishList