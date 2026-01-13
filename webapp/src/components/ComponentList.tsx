import { useState, useEffect, useCallback, useRef } from 'react'
import { Search, Plus, Trash2, X, Loader } from 'lucide-react'
import { Button } from './Button'
import { dishService } from '../services/dish'
import { ingredientService } from '../services/ingredient'
import { Dish } from '../services/schema/dishSchema'
import { Ingredient } from '../services/schema/ingredientSchema'
import {
  formatDishQuantity,
  formatIngredientQuantity
} from '../utils/componentFormatter'

interface ComponentItem {
  component_id: number
  quantity: number
  type: 'dish' | 'ingredient'
}

interface ComponentListProps {
  initialData?: ComponentItem[]
  onSubmit: (list: ComponentItem[]) => void
  onCancel: () => void
  readOnly?: boolean
}

type ComponentType = 'ingredient' | 'dish'
type SearchResult = (Dish | Ingredient) & { component_type?: ComponentType }

export const ComponentList: React.FC<ComponentListProps> = ({
  initialData = [],
  onSubmit,
  onCancel,
  readOnly = false
}) => {
  const [componentList, setComponentList] =
    useState<ComponentItem[]>(initialData)
  const [showModal, setShowModal] = useState(false)
  const [activeTab, setActiveTab] = useState<ComponentType>('ingredient')
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [resolving, setResolving] = useState<Set<number>>(new Set())
  const [componentData, setComponentData] = useState<
    Map<number, { name: string; unit?: string | null }>
  >(new Map())
  const [ingredientCursor, setIngredientCursor] = useState<number | null>(null)
  const [dishCursor, setDishCursor] = useState<number | null>(null)
  const resultsContainerRef = useRef<HTMLDivElement>(null)

  // Lazy-resolve component names and units
  const resolveComponent = useCallback(
    async (componentId: number) => {
      if (componentData.has(componentId)) return

      setResolving((prev) => new Set([...prev, componentId]))
      try {
        // Try ingredient first
        const ingredientResult =
          await ingredientService.getIngredientById(componentId)
        if (ingredientResult.isOk()) {
          setComponentData((prev) =>
            new Map(prev).set(componentId, {
              name: ingredientResult.value.component_name,
              unit:
                ingredientResult.value.uc_measurement_unit ||
                ingredientResult.value.c_measurement_unit ||
                null
            })
          )
          return
        }

        // If ingredient fails, try dish
        const dishResult = await dishService.getDishById(componentId)
        if (dishResult.isOk()) {
          setComponentData((prev) =>
            new Map(prev).set(componentId, {
              name: dishResult.value.component_name
            })
          )
          return
        }
      } catch (err) {
        console.error(`Failed to resolve component ${componentId}:`, err)
      } finally {
        setResolving((prev) => {
          const next = new Set(prev)
          next.delete(componentId)
          return next
        })
      }
    },
    [componentData]
  )

  // Resolve names for initial data
  useEffect(() => {
    componentList.forEach((item) => {
      if (!componentData.has(item.component_id)) {
        resolveComponent(item.component_id)
      }
    })
  }, [componentList, componentData, resolveComponent])

  const handleSearch = useCallback(
    async (query: string, cursor?: number) => {
      if (!query.trim()) {
        setResults([])
        return
      }

      setLoading(true)
      try {
        if (activeTab === 'ingredient') {
          const result = await ingredientService.searchIngredients(query, {
            cursor,
            limit: 20
          })
          if (result.isOk()) {
            const data = result.value.data.map((item) => ({
              ...item,
              component_type: 'ingredient' as const
            }))
            setResults((prevResults) =>
              cursor ? [...prevResults, ...data] : data
            )
            setIngredientCursor(result.value.next_cursor)
          }
        } else {
          const result = await dishService.searchDishes({
            keyword: query,
            cursor,
            limit: 20
          })
          if (result.isOk()) {
            const data = result.value.data.map((item) => ({
              ...item,
              component_type: 'dish' as const
            }))
            setResults((prevResults) =>
              cursor ? [...prevResults, ...data] : data
            )
            setDishCursor(result.value.next_cursor)
          }
        }
      } catch (err) {
        console.error('Search failed:', err)
      } finally {
        setLoading(false)
      }
    },
    [activeTab]
  )

  useEffect(() => {
    const debounce = setTimeout(() => {
      handleSearch(searchQuery)
    }, 300)
    return () => clearTimeout(debounce)
  }, [searchQuery, activeTab, handleSearch])

  const handleLoadMore = () => {
    const cursor = activeTab === 'ingredient' ? ingredientCursor : dishCursor
    if (cursor !== null) {
      handleSearch(searchQuery, cursor)
    }
  }

  const handleAddComponent = (component: SearchResult) => {
    if (
      !componentList.find(
        (item) => item.component_id === component.component_id
      )
    ) {
      const newItem: ComponentItem = {
        component_id: component.component_id,
        quantity: 1,
        type: component.component_type || 'ingredient'
      }
      setComponentList([...componentList, newItem])
      resolveComponent(component.component_id)
    }
  }

  const handleQuantityChange = (componentId: number, quantity: number) => {
    setComponentList(
      componentList.map((item) =>
        item.component_id === componentId ? { ...item, quantity } : item
      )
    )
  }

  const handleRemoveComponent = (componentId: number) => {
    setComponentList(
      componentList.filter((item) => item.component_id !== componentId)
    )
  }

  const handleSave = () => {
    onSubmit(componentList)
    setShowModal(false)
  }

  const getComponentName = (componentId: number): string | null => {
    const data = componentData.get(componentId)
    return data?.name || null
  }

  const getFormattedQuantity = (item: ComponentItem): string => {
    const data = componentData.get(item.component_id)
    if (item.type === 'dish') {
      return formatDishQuantity(item.quantity)
    } else {
      return formatIngredientQuantity(item.quantity, data?.unit)
    }
  }

  const isResolving = (componentId: number): boolean => {
    return resolving.has(componentId)
  }

  return (
    <>
      {/* Always render the component list display */}
      <div className="rounded-lg bg-white p-4">
        <h3 className="mb-4 text-lg font-bold text-gray-800">
          Thành phần ({componentList.length})
        </h3>
        {componentList.length === 0 ? (
          <div className="rounded-lg bg-gray-50 p-4 text-center italic text-gray-500">
            Chưa có thành phần
          </div>
        ) : (
          <div className="space-y-2">
            {componentList.map((item) => (
              <div
                key={item.component_id}
                className="flex items-center justify-between rounded border border-gray-300 bg-gray-50 p-3"
              >
                <div className="flex items-center space-x-2">
                  {isResolving(item.component_id) ? (
                    <Loader size={16} className="animate-spin text-gray-400" />
                  ) : (
                    <span className="text-gray-700">
                      {getComponentName(item.component_id) ||
                        `Component ${item.component_id}`}
                    </span>
                  )}
                </div>
                <span className="text-sm text-gray-600">
                  {getFormattedQuantity(item)}
                </span>
              </div>
            ))}
          </div>
        )}
        {!readOnly && (
          <div className="mt-4">
            <Button
              variant="secondary"
              size="fit"
              icon={Plus}
              onClick={() => setShowModal(true)}
              className="!mx-0"
            >
              Quản lý thành phần
            </Button>
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={() => setShowModal(false)}
          />
          <div className="relative z-10 w-full max-w-2xl p-4">
            <div className="flex flex-col space-y-4 rounded-lg bg-white p-4">
              {/* Tabs */}
              <div className="flex border-b border-gray-300">
                {(['ingredient', 'dish'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => {
                      setActiveTab(tab)
                      setResults([])
                      setSearchQuery('')
                    }}
                    className={`px-4 py-2 font-medium ${
                      activeTab === tab
                        ? 'border-b-2 border-rose-500 text-rose-500'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    {tab === 'ingredient' ? 'Nguyên liệu' : 'Món ăn'}
                  </button>
                ))}
              </div>

              {/* Search */}
              <div className="relative">
                <input
                  type="text"
                  placeholder={`Tìm kiếm ${
                    activeTab === 'ingredient' ? 'nguyên liệu' : 'món ăn'
                  }...`}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 py-2 pl-4 pr-10 focus:border-rose-500 focus:outline-none"
                />
                <Search
                  className="absolute right-3 top-2.5 text-gray-400"
                  size={18}
                />
              </div>

              {/* Results */}
              <div
                ref={resultsContainerRef}
                className="max-h-64 space-y-2 overflow-y-auto rounded-lg border border-gray-200 p-3"
              >
                {loading && (
                  <div className="text-center text-sm text-gray-500">
                    Đang tải...
                  </div>
                )}
                {!loading && results.length === 0 && searchQuery && (
                  <div className="text-center text-sm text-gray-500">
                    Không tìm thấy kết quả
                  </div>
                )}
                {!loading && results.length === 0 && !searchQuery && (
                  <div className="text-center text-sm text-gray-500">
                    Nhập từ khóa để tìm kiếm
                  </div>
                )}
                {results.map((result) => (
                  <div
                    key={result.component_id}
                    className="flex items-center justify-between rounded border border-gray-300 bg-gray-50 p-2"
                  >
                    <span className="flex-1 text-sm text-gray-700">
                      {result.component_name}
                    </span>
                    <Button
                      variant="icon"
                      icon={Plus}
                      onClick={() => handleAddComponent(result)}
                      className="!h-fit !w-fit !p-1"
                    />
                  </div>
                ))}
                {!loading &&
                  results.length > 0 &&
                  (activeTab === 'ingredient'
                    ? ingredientCursor
                    : dishCursor) !== null && (
                    <button
                      onClick={handleLoadMore}
                      className="w-full rounded py-2 text-center text-sm text-rose-500 hover:bg-gray-50"
                    >
                      Tải thêm
                    </button>
                  )}
              </div>

              {/* Component List */}
              <div className="space-y-2">
                <h3 className="font-bold text-gray-800">
                  Thành phần ({componentList.length})
                </h3>
                {componentList.length === 0 ? (
                  <div className="rounded-lg bg-gray-50 p-4 text-center italic text-gray-500">
                    Chưa có thành phần
                  </div>
                ) : (
                  <div className="space-y-2">
                    {componentList.map((item) => (
                      <div
                        key={item.component_id}
                        className="flex items-center justify-between rounded border border-gray-300 p-3"
                      >
                        <div className="flex flex-1 items-center space-x-2">
                          {isResolving(item.component_id) ? (
                            <Loader
                              size={16}
                              className="animate-spin text-gray-400"
                            />
                          ) : (
                            <span className="flex-1 text-gray-700">
                              {getComponentName(item.component_id) ||
                                `Component ${item.component_id}`}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="number"
                            value={item.quantity}
                            onChange={(e) =>
                              handleQuantityChange(
                                item.component_id,
                                Number(e.target.value)
                              )
                            }
                            className="w-20 rounded border border-gray-300 px-2 py-1 text-center text-sm focus:outline-none focus:ring-2 focus:ring-rose-500"
                            min="0"
                            step="0.1"
                          />
                          <span className="w-12 text-right text-sm text-gray-600">
                            {getFormattedQuantity(item)}
                          </span>
                          <Button
                            variant="icon"
                            icon={Trash2}
                            onClick={() =>
                              handleRemoveComponent(item.component_id)
                            }
                            className="!h-fit !w-fit !p-2"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-center gap-4">
                <Button
                  variant="primary"
                  size="fit"
                  onClick={handleSave}
                  className="!mx-0"
                >
                  Xác nhận
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
