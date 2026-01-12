import React, { useState, useMemo } from 'react'
import {
  Search,
  Plus,
  Filter,
  LayoutGrid,
  Check,
  Edit,
  Trash2
} from 'lucide-react'
import Item from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
import { DishForm } from '../components/DishForm'
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
      category: isHamburger
        ? 'Món ăn vặt'
        : possibleCategories[randomCategoryIndex],
      image: hamburgerImg
    }
  })

const ITEMS_PER_PAGE = 20

const DishMenu = () => {
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilter, setShowFilter] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddDishForm, setShowAddDishForm] = useState(false)
  const [selectedItem, setSelectedItem] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)

  const handleToggleFilter = () => {
    setShowFilter((prev) => !prev)
  }

  const handleAddDishClick = () => {
    setShowAddDishForm(true)
  }

  const handleDishFormSubmit = (dishData: any) => {
    console.log('Saving dish:', dishData)
    setShowAddDishForm(false)
  }

  const handleDishFormCancel = () => {
    setShowAddDishForm(false)
  }

  const handleItemClick = (item: any) => {
    setSelectedItem(item)
    setViewMode('view')
  }

  const handleEditClick = () => {
    setViewMode('edit')
  }

  const handleSaveClick = () => {
    // Here you would typically save the changes
    closeModal()
  }

  const handleDeleteClick = () => {
    // Here you would typically delete the item
    closeModal()
  }

  const closeModal = () => {
    setSelectedItem(null)
    setViewMode(null)
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
    <div className="flex min-h-screen flex-1 flex-col pt-6">
      {/* Header */}
      <div className="mb-8 flex flex-col space-y-6 px-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-800">Danh mục món ăn</h2>

          <div className="flex items-center space-x-4">
            <Button
              variant="primary"
              icon={Plus}
              size="fit"
              onClick={handleAddDishClick}
            >
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

      {/* Grid Container - Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {currentItems.length > 0 ? (
          <div className="grid grid-cols-2 gap-4 px-6 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
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
          <div className="flex h-64 items-center justify-center px-6 text-gray-500">
            Không tìm thấy món ăn nào.
          </div>
        )}
      </div>

      {/* Pagination - Always at Bottom */}
      <div className="sticky bottom-0 bg-white px-6 py-4">
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          className=""
        />
      </div>

      {/* Add Dish Form Modal */}
      {showAddDishForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Background overlay */}
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={handleDishFormCancel}
          />

          {/* Form container */}
          <div className="relative z-10 flex items-center justify-center p-4">
            <DishForm
              onSubmit={handleDishFormSubmit}
              onCancel={handleDishFormCancel}
            />
          </div>
        </div>
      )}

      {/* View/Edit Dish Modal */}
      {selectedItem && viewMode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Background overlay */}
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={closeModal}
          />

          {/* Form container */}
          <div className="relative z-10 flex items-center justify-center p-4">
            {viewMode === 'view' && (
              <DishForm
                initialData={{
                  dishName: selectedItem.name || 'Chưa có thông tin',
                  category: selectedItem.category || 'Chưa có thông tin',
                  difficulty: selectedItem.difficulty || 'Chưa có thông tin',
                  image: selectedItem.image || null,
                  servings: selectedItem.servings || 'Chưa có thông tin',
                  cookTime: selectedItem.cookTime || 'Chưa có thông tin',
                  prepTime: selectedItem.prepTime || 'Chưa có thông tin',
                  ingredients:
                    selectedItem.ingredients &&
                    selectedItem.ingredients.length > 0
                      ? selectedItem.ingredients
                      : [],
                  instructions:
                    selectedItem.instructions &&
                    selectedItem.instructions.length > 0
                      ? selectedItem.instructions
                      : []
                }}
                readOnly={true}
                actions={
                  <>
                    <Button
                      variant="primary"
                      size="fit"
                      icon={Check}
                      onClick={closeModal}
                      className="mx-0 -mr-1"
                    >
                      Quay lại
                    </Button>
                    <Button
                      variant="secondary"
                      size="fit"
                      icon={Edit}
                      className="mx-0"
                      onClick={handleEditClick}
                    >
                      Chỉnh sửa
                    </Button>
                    <Button
                      variant="secondary"
                      size="fit"
                      icon={Trash2}
                      className="mx-0"
                      onClick={handleDeleteClick}
                    >
                      Xóa
                    </Button>
                  </>
                }
                onSubmit={() => {}} // Empty function since form is read-only
                onCancel={closeModal}
              />
            )}
            {viewMode === 'edit' && (
              <DishForm
                initialData={{
                  dishName: selectedItem.name || '',
                  category: selectedItem.category || '',
                  difficulty: selectedItem.difficulty || '',
                  image: selectedItem.image || null,
                  servings: selectedItem.servings || 0,
                  cookTime: selectedItem.cookTime || '',
                  prepTime: selectedItem.prepTime || '',
                  ingredients: selectedItem.ingredients || [],
                  instructions: selectedItem.instructions || []
                }}
                onSubmit={handleSaveClick}
                onCancel={() => setViewMode('view')}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default DishMenu
