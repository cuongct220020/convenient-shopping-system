import React, { useState, useCallback, useEffect } from 'react'
import {
  Search,
  Plus,
  LayoutGrid,
  Check,
  Edit,
  Trash2,
  RotateCw
} from 'lucide-react'
import Item from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
import { DishForm } from '../components/DishForm'
import { dishService } from '../services/dish'
import { useIsMounted } from '../hooks/useIsMounted'
import hamburgerImg from '../assets/hamburger.png'
import { DishCreateSchema, type Dish } from '../services/schema/dishSchema'
import { parseZodObject } from '../utils/zod-result'
import { NotificationCard } from '../components/NotificationCard'

const ITEMS_PER_PAGE = 20

const DishMenu = () => {
  const isMounted = useIsMounted()
  const [currentPage, setCurrentPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchInputValue, setSearchInputValue] = useState('')
  const [showAddDishForm, setShowAddDishForm] = useState(false)
  const [selectedItem, setSelectedItem] = useState<Dish | null>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)
  const [dishes, setDishes] = useState<Dish[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pagesCursors, setPagesCursors] = useState<(number | null)[]>([null])
  const [reportModal, setReportModal] = useState<{
    type: 'success' | 'error'
    title: string
    message: string
  } | null>(null)

  const fetchDishes = useCallback(
    async (pageNumber: number = 1) => {
      setLoading(true)
      setError(null)
      try {
        const cursor = pagesCursors[pageNumber - 1] ?? undefined
        const result = await dishService.getDishes({
          cursor,
          limit: ITEMS_PER_PAGE,
          search: searchQuery || undefined
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
    [pagesCursors, searchQuery, isMounted]
  )

  useEffect(() => {
    // Reset pagination when search changes, then fetch page 1
    setPagesCursors([null])
    setCurrentPage(1)
    // Call fetchDishes to fetch page 1 with new search
    fetchDishes(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery])

  const handleAddDishClick = () => {
    setShowAddDishForm(true)
  }

  const handleDishFormSubmit = async (dishData: Partial<Dish>) => {
    setLoading(true)
    try {
      const parseData = parseZodObject(DishCreateSchema, dishData)
      // Validate that dishData is a complete Dish object
      if (parseData.isErr()) {
        throw new Error(
          'Developer Error: DishForm must return a complete Dish object' +
            parseData.error
        )
      }

      const result = await dishService.createDish(dishData as Dish)

      if (result.isOk()) {
        setShowAddDishForm(false)
        setReportModal({
          type: 'success',
          title: 'Tạo món ăn thành công',
          message: `Món ăn "${dishData.component_name}" đã được tạo.`
        })
        // Reset pagination state and refetch page 1
        setPagesCursors([null])
        setCurrentPage(1)
        // Fetch with fresh state - pass cursor explicitly as undefined for page 1
        try {
          const freshResult = await dishService.getDishes({
            cursor: undefined,
            limit: ITEMS_PER_PAGE,
            search: searchQuery || undefined
          })

          if (isMounted.current && freshResult.isOk()) {
            const response = freshResult.value
            setDishes(response.data)
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
            result.error.desc || 'Không thể tạo món ăn. Vui lòng thử lại sau.'
        })
      }
    } catch (err) {
      setReportModal({
        type: 'error',
        title: 'Lỗi',
        message: String(err)
      })
    } finally {
      if (isMounted.current) {
        setLoading(false)
      }
    }
  }

  const handleDishFormCancel = () => {
    setShowAddDishForm(false)
  }

  const handleItemClick = (item: Dish) => {
    setSelectedItem(item)
    setViewMode('view')
  }

  const handleEditClick = () => {
    setViewMode('edit')
  }

  const handleSaveClick = async (formData: Partial<Dish>) => {
    if (!selectedItem) return
    setLoading(true)
    setError(null)
    try {
      const result = await dishService.updateDish(
        selectedItem.component_id,
        formData
      )
      if (!isMounted.current) return
      if (result.isOk()) {
        await fetchDishes(currentPage)
        closeModal()
      } else {
        setError(result.error.desc || 'Failed to update dish')
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
  }
  const handleDeleteClick = async () => {
    if (!selectedItem) return
    setLoading(true)
    try {
      const result = await dishService.deleteDish(selectedItem.component_id)
      if (!isMounted.current) return
      if (result.isOk()) {
        closeModal()

        // Invalidate cursor chain after deletion
        // Trim cursors from current page onwards since dataset has changed
        setPagesCursors((prev) => prev.slice(0, currentPage))

        // Refetch current page to rebuild cursor chain and refresh displayed data
        const freshResult = await dishService.getDishes({
          cursor: pagesCursors[currentPage - 1] ?? undefined,
          limit: ITEMS_PER_PAGE,
          search: searchQuery || undefined
        })

        if (!isMounted.current) return

        if (freshResult.isOk()) {
          const response = freshResult.value
          setDishes(response.data)

          // Handle edge case: current page is now empty
          if (response.data.length === 0 && currentPage > 1) {
            // Redirect to previous page and reset pagination
            setCurrentPage(currentPage - 1)
            setPagesCursors([null])
            // Refetch previous page
            const prevPageResult = await dishService.getDishes({
              cursor: undefined,
              limit: ITEMS_PER_PAGE,
              search: searchQuery || undefined
            })
            if (isMounted.current && prevPageResult.isOk()) {
              const prevResponse = prevPageResult.value
              setDishes(prevResponse.data)
              if (prevResponse.next_cursor !== null) {
                setPagesCursors([null, prevResponse.next_cursor])
              }
            }
          } else if (response.data.length > 0) {
            // Update pagination cursors if next page exists
            if (response.next_cursor !== null) {
              setPagesCursors((prev) => {
                const updated = [...prev]
                updated[currentPage] = response.next_cursor
                return updated
              })
            }
          }
        }

        setReportModal({
          type: 'success',
          title: 'Xóa thành công',
          message: `Món ăn "${selectedItem.component_name}" đã được xóa.`
        })
      } else {
        setError(result.error.desc || 'Failed to delete dish')
        setReportModal({
          type: 'error',
          title: 'Xóa thất bại',
          message:
            result.error.desc || 'Không thể xóa món ăn. Vui lòng thử lại sau.'
        })
      }
    } catch (err) {
      if (isMounted.current) {
        setError(String(err))
        setReportModal({
          type: 'error',
          title: 'Lỗi',
          message: String(err)
        })
      }
    } finally {
      if (isMounted.current) {
        setLoading(false)
      }
    }
  }

  const closeModal = () => {
    setSelectedItem(null)
    setViewMode(null)
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInputValue(e.target.value)
  }

  const handleSearch = async () => {
    setSearchQuery(searchInputValue)
    // Reset pagination when search is triggered
    setPagesCursors([null])
    setCurrentPage(1)
    // Note: useEffect will handle fetching with new searchQuery
  }

  const handleReload = () => {
    setSearchQuery('')
    setSearchInputValue('')
    setPagesCursors([null])
    setCurrentPage(1)
    // Note: useEffect will handle fetching with cleared searchQuery
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

            <div className="flex items-center space-x-2">
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
                className="w-48 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-600"
              />
              {searchInputValue.trim() ? (
                <Button
                  variant="icon"
                  icon={Search}
                  size="fit"
                  onClick={handleSearch}
                >
                  Tìm kiếm
                </Button>
              ) : (
                <Button
                  variant="icon"
                  icon={RotateCw}
                  size="fit"
                  onClick={handleReload}
                />
              )}
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
              loading={loading}
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
                  component_name: selectedItem.component_name,
                  level: selectedItem.level,
                  image_url: selectedItem.image_url || hamburgerImg,
                  default_servings: selectedItem.default_servings,
                  cook_time: selectedItem.cook_time,
                  prep_time: selectedItem.prep_time,
                  keywords: selectedItem.keywords,
                  instructions: selectedItem.instructions,
                  component_list: selectedItem.component_list
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
                  component_name: selectedItem.component_name,
                  level: selectedItem.level,
                  image_url: selectedItem.image_url || hamburgerImg,
                  default_servings: selectedItem.default_servings,
                  cook_time: selectedItem.cook_time,
                  prep_time: selectedItem.prep_time,
                  keywords: selectedItem.keywords,
                  instructions: selectedItem.instructions,
                  component_list: selectedItem.component_list
                }}
                onSubmit={handleSaveClick}
                onCancel={() => setViewMode('view')}
                loading={loading}
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

export default DishMenu
