import React, { useState, useMemo, useCallback, useEffect } from 'react'
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
import { dishService } from '../services/dish'
import { useIsMounted } from '../hooks/useIsMounted'
import hamburgerImg from '../assets/hamburger.png'
import {
  DishLevelTypeSchema,
  type Dish,
  type DishLevelType
} from '../services/schema/dishSchema'

const ITEMS_PER_PAGE = 20

const DishMenu = () => {
  const isMounted = useIsMounted()
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilter, setShowFilter] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState<DishLevelType[]>(
    []
  )
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddDishForm, setShowAddDishForm] = useState(false)
  const [selectedItem, setSelectedItem] = useState<Dish | null>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)
  const [dishes, setDishes] = useState<Dish[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pagesCursors, setPagesCursors] = useState<(number | null)[]>([null])

  const fetchDishes = useCallback(
    async (pageNumber: number = 1) => {
      setLoading(true)
      setError(null)
      try {
        const cursor = pagesCursors[pageNumber - 1] ?? undefined
        const result = await dishService.getDishes({
          cursor,
          limit: ITEMS_PER_PAGE,
          search: searchQuery || undefined,
          level: selectedCategories.length > 0 ? selectedCategories : undefined
        })

        if (!isMounted.current) return

        if (result.isOk()) {
          const response = result.value
          setDishes(response.data)
          setCurrentPage(pageNumber)

          // Add next page cursor if it doesn't exist yet
          if (response.next_cursor !== null && !pagesCursors[pageNumber]) {
            setPagesCursors((prev) => {
              const updated = [...prev]
              updated[pageNumber] = response.next_cursor
              return updated
            })
          }
        } else {
          setError(result.error.desc || 'Failed to fetch dishes')
        }
      } catch (err) {
        if (isMounted.current) {
          setError(String(err))
        }
      } finally {
        if (isMounted.current) {
          setLoading(false)
        }
      }
    },
    [pagesCursors, searchQuery, selectedCategories, isMounted]
  )

  useEffect(() => {
    // Reset pagination when filters change, then fetch page 1
    setPagesCursors([null])
    setCurrentPage(1)
    // Call fetchDishes to fetch page 1 with new filters
    // Intentionally not in dependency array to avoid circular dependency
    // with pagesCursors (which gets updated during fetch)
    fetchDishes(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, selectedCategories])

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
    const categories = new Set<string>()
    dishes.forEach((item) => {
      if (item.level) categories.add(item.level)
    })
    return Array.from(categories).sort()
  }, [dishes])

  const handleCategoryChange = (category: string) => {
    if (DishLevelTypeSchema.safeParse(category).success === false) {
      return
    }
    const typedCategory = category as DishLevelType
    setSelectedCategories((prev) =>
      prev.includes(typedCategory)
        ? prev.filter((c) => c !== category)
        : [...prev, typedCategory]
    )
    setPagesCursors([null])
    setCurrentPage(1)
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    setPagesCursors([null])
    setCurrentPage(1)
  }

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
                    Lọc theo độ khó
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
            <span className="font-bold">{dishes.length} món ăn</span>
            {' (trang '}
            <span className="font-bold">{currentPage}</span>
            {' trên '}
            <span className="font-bold">{pagesCursors.length}</span>
            {')'}.
          </span>
        </div>
      </div>

      {/* Grid Container - Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex h-64 items-center justify-center px-6 text-gray-500">
            <p>Đang tải...</p>
          </div>
        )}
        {error && (
          <div className="flex h-64 items-center justify-center px-6 text-red-500">
            <p>Lỗi: {error}</p>
          </div>
        )}
        {!loading && !error && dishes.length > 0 && (
          <div className="grid grid-cols-2 gap-4 px-6 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {dishes.map((item) => (
              <Item
                key={item.component_id}
                name={item.component_name}
                category={item.level || 'N/A'}
                image={item.image_url || hamburgerImg}
                onClick={() => handleItemClick(item)}
              />
            ))}
          </div>
        )}
        {!loading && !error && dishes.length === 0 && (
          <div className="flex h-64 items-center justify-center px-6 text-gray-500">
            Không tìm thấy món ăn nào.
          </div>
        )}
      </div>

      {/* Pagination - Always at Bottom */}
      <div className="sticky bottom-0 bg-white px-6 py-4">
        <div className="flex items-center justify-center">
          <Pagination
            currentPage={currentPage}
            totalPages={pagesCursors.length}
            onPageChange={(page) => fetchDishes(page)}
          />
        </div>
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
                  dishName: selectedItem.component_name || 'Chưa có thông tin',
                  category: selectedItem.level || 'Chưa có thông tin',
                  difficulty: selectedItem.level || 'Chưa có thông tin',
                  image: selectedItem.image_url || hamburgerImg,
                  servings: selectedItem.default_servings || 0,
                  cookTime: String(selectedItem.cook_time || '0'),
                  prepTime: String(selectedItem.prep_time || '0'),
                  ingredients: [],
                  instructions: []
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
                  dishName: selectedItem.component_name || '',
                  category: selectedItem.level || '',
                  difficulty: selectedItem.level || '',
                  image: selectedItem.image_url || hamburgerImg,
                  servings: selectedItem.default_servings || 0,
                  cookTime: String(selectedItem.cook_time || ''),
                  prepTime: String(selectedItem.prep_time || ''),
                  ingredients: [],
                  instructions: []
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
