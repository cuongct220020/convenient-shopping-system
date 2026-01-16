import React, { useState, useEffect, useCallback } from 'react'
import {
  Search,
  Plus,
  Filter,
  Check,
  Edit,
  Trash2,
  RotateCw
} from 'lucide-react'
import Item from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
import { DishForm } from '../components/DishForm'
import { IngredientForm } from '../components/IngredientForm'
import garlicImg from '../assets/garlic.png'
import { ingredientService } from '../services/ingredient'
import { useIsMounted } from '../hooks/useIsMounted'
import type { Ingredient } from '../services/schema/ingredientSchema'
import { NotificationCard } from '../components/NotificationCard'
import { INGREDIENT_CATEGORIES } from '../utils/constants'

// Dữ liệu giả lập để hiển thị giống hình ảnh (no longer used, data now fetches from server)

const ITEMS_PER_PAGE = 20

type ItemData = Omit<
  Ingredient,
  'component_id' | 'component_name' | 'c_measurement_unit'
> & {
  id: number
  name: string
  image: string
}

// Map server ingredient to UI item format
const mapIngredientToItem = (ingredient: Ingredient): ItemData => ({
  id: ingredient.component_id,
  name: ingredient.component_name,
  image: garlicImg,
  ...ingredient
})

const IngredientMenu = () => {
  const isMounted = useIsMounted()
  const [ingredients, setIngredients] = useState<
    ReturnType<typeof mapIngredientToItem>[]
  >([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pagesCursors, setPagesCursors] = useState<(number | null)[]>([null])
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilter, setShowFilter] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [searchInputValue, setSearchInputValue] = useState('')
  const [showAddDishForm, setShowAddDishForm] = useState(false)
  const [showAddIngredientForm, setShowAddIngredientForm] = useState(false)
  const [selectedItem, setSelectedItem] = useState<ItemData | null>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)
  const [reportModal, setReportModal] = useState<{
    type: 'success' | 'error'
    title: string
    message: string
  } | null>(null)

  const fetchIngredients = useCallback(
    async (pageNumber: number = 1) => {
      setLoading(true)
      setError(null)
      try {
        const cursor = pagesCursors[pageNumber - 1] ?? undefined
        const result = await ingredientService.getIngredients({
          cursor,
          limit: ITEMS_PER_PAGE,
          search: searchQuery || undefined,
          categories:
            selectedCategories.length > 0 ? selectedCategories : undefined
        })

        if (!isMounted.current) return

        if (result.isOk()) {
          const response = result.value
          setIngredients(response.data.map(mapIngredientToItem))
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
          setError(result.error.desc || 'Failed to fetch ingredients')
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
    // Reset pagination when search changes, then fetch page 1
    setPagesCursors([null])
    setCurrentPage(1)
    // Call fetchIngredients to fetch page 1 with new search
    // Note: selectedCategories is not in dependency array because filter
    // is applied via manual button click in handleApplyFilter
    fetchIngredients(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery])

  const handleToggleFilter = () => {
    setShowFilter((prev) => !prev)
  }

  const handleAddIngredientClick = () => {
    setShowAddIngredientForm(true)
  }

  const handleIngredientFormSubmit = async (formData: Partial<Ingredient>) => {
    setLoading(true)
    try {
      const result = await ingredientService.createIngredient(formData)

      if (result.isOk()) {
        setShowAddIngredientForm(false)
        setReportModal({
          type: 'success',
          title: 'Tạo nguyên liệu thành công',
          message: `Nguyên liệu "${formData.component_name}" đã được tạo.`
        })
        // Reset pagination state and refetch page 1
        setPagesCursors([null])
        setCurrentPage(1)
        // Fetch with fresh state - pass cursor explicitly as undefined for page 1
        try {
          const freshResult = await ingredientService.getIngredients({
            cursor: undefined,
            limit: ITEMS_PER_PAGE,
            search: searchQuery || undefined,
            categories:
              selectedCategories.length > 0 ? selectedCategories : undefined
          })

          if (isMounted.current && freshResult.isOk()) {
            const response = freshResult.value
            setIngredients(response.data.map(mapIngredientToItem))
            // Set pagination cursors - second page cursor is available if next_cursor exists
            if (
              response.next_cursor !== null &&
              response.next_cursor !== undefined
            ) {
              setPagesCursors([null, response.next_cursor])
            } else {
              // No next page available, keep pagination at length 1 (single page)
              setPagesCursors([null])
            }
          }
        } catch (err) {
          if (isMounted.current) {
            setError(String(err))
          }
        }
      } else {
        setReportModal({
          type: 'error',
          title: 'Tạo thất bại',
          message:
            result.error.desc ||
            'Không thể tạo nguyên liệu. Vui lòng thử lại sau.'
        })
      }
    } catch (err) {
      setReportModal({
        type: 'error',
        title: 'Lỗi',
        message: String(err)
      })
    } finally {
      setLoading(false)
    }
  }

  const handleIngredientFormCancel = () => {
    setShowAddIngredientForm(false)
  }

  const handleDishFormSubmit = (dishData: Record<string, unknown>) => {
    setShowAddDishForm(false)
  }

  const handleDishFormCancel = () => {
    setShowAddDishForm(false)
  }

  const handleItemClick = (item: ItemData) => {
    setSelectedItem(item)
    setViewMode('view')
  }

  const handleEditClick = () => {
    setViewMode('edit')
  }

  const handleSaveClick = async (formData: Partial<Ingredient>) => {
    if (!selectedItem) return
    setLoading(true)
    try {
      const result = await ingredientService.updateIngredient(
        `${selectedItem.id}`,
        formData
      )

      if (result.isOk()) {
        setReportModal({
          type: 'success',
          title: 'Cập nhật nguyên liệu thành công',
          message: `Nguyên liệu "${
            formData.component_name || selectedItem.name
          }" đã được cập nhật.`
        })
        setViewMode(null)
        setSelectedItem(null)
        // Refresh current page
        await fetchIngredients(currentPage)
      } else {
        setReportModal({
          type: 'error',
          title: 'Cập nhật thất bại',
          message:
            result.error.desc ||
            'Không thể cập nhật nguyên liệu. Vui lòng thử lại sau.'
        })
      }
    } catch (err) {
      setReportModal({
        type: 'error',
        title: 'Lỗi',
        message: String(err)
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteClick = async () => {
    if (!selectedItem) return
    const result = await ingredientService.deleteIngredient(
      `${selectedItem.id}`
    )
    if (result.isOk()) {
      setIngredients((prev) => prev.filter((i) => i.id !== selectedItem.id))
      setReportModal({
        type: 'success',
        title: 'Xóa nguyên liệu thành công',
        message: `Nguyên liệu ${selectedItem.name} đã được xóa.`
      })
      setSelectedItem(null)
      setViewMode(null)
    } else {
      setReportModal({
        type: 'error',
        title: 'Xóa thất bại',
        message:
          result.error.type === 'ingredient-still-used'
            ? 'Nguyên liệu đang được sử dụng trong công thức nấu ăn.'
            : 'Không thể xóa nguyên liệu này. Vui lòng thử lại sau.'
      })
    }
  }

  const closeModal = () => {
    setSelectedItem(null)
    setViewMode(null)
  }

  // Use predefined categories from constants instead of deriving from API response
  const uniqueCategories = INGREDIENT_CATEGORIES

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInputValue(e.target.value)
  }

  const handleSearch = () => {
    // Clear filters when searching
    setSelectedCategories([])
    setShowFilter(false)
    // Set search query and reset pagination
    setSearchQuery(searchInputValue)
    setPagesCursors([null])
    setCurrentPage(1)
  }

  const handleReload = () => {
    // Clear both search and filter, reset to initial state
    setSearchQuery('')
    setSearchInputValue('')
    setSelectedCategories([])
    setShowFilter(false)
    setPagesCursors([null])
    setCurrentPage(1)
  }

  const handleApplyFilter = async () => {
    // Clear search when filter is applied
    setSearchQuery('')
    setSearchInputValue('')
    setShowFilter(false)
    // Reset pagination
    setPagesCursors([null])
    setCurrentPage(1)
    // Directly fetch with selected categories
    try {
      const result = await ingredientService.getIngredients({
        cursor: undefined,
        limit: ITEMS_PER_PAGE,
        categories:
          selectedCategories.length > 0 ? selectedCategories : undefined
      })

      if (isMounted.current && result.isOk()) {
        const response = result.value
        setIngredients(response.data.map(mapIngredientToItem))
        // Set pagination cursors - second page cursor is available if next_cursor exists
        if (
          response.next_cursor !== null &&
          response.next_cursor !== undefined
        ) {
          setPagesCursors([null, response.next_cursor])
        } else {
          setPagesCursors([null])
        }
      } else if (isMounted.current) {
        setError(
          result.isErr()
            ? result.error.desc || 'Failed to fetch ingredients'
            : 'Failed to fetch ingredients'
        )
      }
    } catch (err) {
      if (isMounted.current) {
        setError(String(err))
      }
    }
  }

  return (
    <div className="flex min-h-screen flex-1 flex-col pt-6">
      {/* Header */}
      <div className="mb-8 flex flex-col space-y-6 px-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-800">
            Danh mục nguyên liệu
          </h2>

          <div className="flex items-center space-x-4">
            <Button
              variant="primary"
              icon={Plus}
              size="fit"
              onClick={handleAddIngredientClick}
            >
              Thêm nguyên liệu
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
                  <h3 className="mb-4 font-semibold text-gray-700">
                    Lọc theo danh mục
                  </h3>
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {uniqueCategories.map((category) => (
                      <label
                        key={category}
                        className="flex items-center space-x-2 text-sm text-gray-600"
                      >
                        <input
                          type="checkbox"
                          checked={selectedCategories.includes(category)}
                          onChange={() =>
                            setSelectedCategories((prev) =>
                              prev.includes(category)
                                ? prev.filter((c) => c !== category)
                                : [...prev, category]
                            )
                          }
                          className="rounded border-gray-300 text-rose-500 focus:ring-rose-500"
                        />
                        <span>{category}</span>
                      </label>
                    ))}
                  </div>
                  <Button
                    variant="primary"
                    size="full"
                    onClick={handleApplyFilter}
                  >
                    Áp dụng lọc
                  </Button>
                </div>
              )}
            </button>

            <div className="flex items-center space-x-2">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Tìm kiếm..."
                  value={searchInputValue}
                  onChange={handleSearchChange}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && searchInputValue.trim()) {
                      handleSearch()
                    }
                  }}
                  className="w-64 rounded-lg border border-gray-300 py-2 pl-4 pr-4 text-sm focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-600"
                />
              </div>
              {searchInputValue.trim() ? (
                <Button
                  variant="icon"
                  size="fit"
                  icon={Search}
                  onClick={handleSearch}
                />
              ) : (
                <Button
                  variant="icon"
                  size="fit"
                  icon={RotateCw}
                  onClick={handleReload}
                />
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end text-sm text-gray-600">
          <span>
            Đang hiển thị{' '}
            <span className="font-bold">{ingredients.length} nguyên liệu</span>
            {' (trang '}
            <span className="font-bold">{currentPage}</span>
            {' trên '}
            <span className="font-bold">{pagesCursors.length}</span>
            {')'}
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
        {!loading && !error && ingredients.length > 0 && (
          <div className="grid grid-cols-2 gap-4 px-6 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {ingredients.map((item) => (
              <Item
                key={item.id}
                name={item.name}
                category={item.category}
                image={item.image}
                onClick={() => handleItemClick(item)}
              />
            ))}
          </div>
        )}
        {!loading && !error && ingredients.length === 0 && (
          <div className="flex h-64 items-center justify-center px-6 text-gray-500">
            Không tìm thấy nguyên liệu nào.
          </div>
        )}
      </div>

      {/* Pagination - Always at Bottom */}
      <div className="sticky bottom-0 bg-white px-6 py-4">
        <div className="flex items-center justify-center">
          <Pagination
            currentPage={currentPage}
            totalPages={pagesCursors.length}
            onPageChange={(page) => fetchIngredients(page)}
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

      {/* Add Ingredient Form Modal */}
      {showAddIngredientForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Background overlay */}
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={handleIngredientFormCancel}
          />

          {/* Form container */}
          <div className="relative z-10 flex items-center justify-center p-4">
            <IngredientForm
              onSubmit={handleIngredientFormSubmit}
              onCancel={handleIngredientFormCancel}
            />
          </div>
        </div>
      )}

      {/* View/Edit Ingredient Modal */}
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
              <IngredientForm
                initialData={selectedItem}
                readOnly={true}
                actions={
                  <>
                    <Button
                      variant="primary"
                      size="fit"
                      icon={Check}
                      onClick={closeModal}
                      className="mx-0"
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
              />
            )}
            {viewMode === 'edit' && (
              <IngredientForm
                initialData={selectedItem}
                onSubmit={handleSaveClick}
                onCancel={() => setViewMode('view')}
                submitLabel="Lưu"
              />
            )}
          </div>
        </div>
      )}

      {/* Action Report Modal */}
      {reportModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <NotificationCard
            title={reportModal.title}
            message={reportModal.message}
            iconBgColor={
              reportModal.type === 'success' ? 'bg-green-500' : 'bg-red-500'
            }
            buttonText="Đóng"
            onButtonClick={() => {
              setReportModal(null)
              closeModal()
            }}
          />
        </div>
      )}
    </div>
  )
}

export default IngredientMenu
