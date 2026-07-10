import { Check, Loader2, Search } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Button } from '../../../components/Button'
import { InputField } from '../../../components/InputField'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ingredientService } from '../../../services/ingredient'
import type { Ingredient } from '../../../services/schema/ingredientSchema'
import { storageService } from '../../../services/storage'

type InputMode = 'direct' | 'search'

export function AddStorageItem() {
  const navigate = useNavigate()
  const location = useLocation()
  const { id: groupId } = useParams<{ id: string }>()
  
  const [inputMode, setInputMode] = useState<InputMode>('direct')
  
  // Direct input fields
  const [directName, setDirectName] = useState('')
  const [directQuantity, setDirectQuantity] = useState('')
  const [directExpirationDate, setDirectExpirationDate] = useState('')
  
  // Search fields
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Ingredient[]>([])
  const [selectedSearchResult, setSelectedSearchResult] = useState<Ingredient | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [showSearchResults, setShowSearchResults] = useState(false)
  
  // Uncountable ingredient fields
  const [contentQuantity, setContentQuantity] = useState('')
  
  // Common fields
  const [expirationDate, setExpirationDate] = useState('')
  const [quantity, setQuantity] = useState('')
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Get storage_id from location state
  const storageId = location.state?.storageId

  // Debounced search
  useEffect(() => {
    if (inputMode !== 'search' || !searchQuery.trim()) {
      setSearchResults([])
      setSelectedSearchResult(null)
      setShowSearchResults(false)
      setIsSearching(false)
      return
    }

    const delayDebounceFn = setTimeout(async () => {
      setIsSearching(true)
      const result = await ingredientService.searchIngredients(searchQuery.trim(), {
        limit: 10
      })

      result.match(
        (response) => {
          if (response.data && response.data.length > 0) {
            setSearchResults(response.data)
            setShowSearchResults(true)
          } else {
            setSearchResults([])
            setShowSearchResults(false)
          }
          setSelectedSearchResult(null)
          setIsSearching(false)
        },
        (error) => {
          console.error('Failed to search ingredients:', error)
          setSearchResults([])
          setSelectedSearchResult(null)
          setShowSearchResults(false)
          setIsSearching(false)
        }
      )
    }, 300)

    return () => clearTimeout(delayDebounceFn)
  }, [searchQuery, inputMode])

  const handleSelectIngredient = (ingredient: Ingredient) => {
    setSelectedSearchResult(ingredient)
    setShowSearchResults(false)
    setSearchQuery(ingredient.component_name)
  }

  const isUncountable = selectedSearchResult?.type === 'uncountable_ingredient'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!storageId) {
      setError('Không tìm thấy thông tin kho')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      let unitName: string
      let packageQty: number
      let componentId: number | null = null
      let contentType: string | null = null
      let contentQty: number | null = null
      let contentUnitValue: 'G' | 'ML' | null = null
      let expirationDateValue: string | null = null

      if (inputMode === 'direct') {
        // Direct input mode
        if (!directName.trim()) {
          setError('Vui lòng nhập tên thực phẩm')
          setIsSubmitting(false)
          return
        }
        if (!directQuantity.trim() || parseInt(directQuantity) < 1) {
          setError('Vui lòng nhập số lượng hợp lệ (ít nhất 1)')
          setIsSubmitting(false)
          return
        }

        unitName = directName.trim()
        packageQty = parseInt(directQuantity)
        if (directExpirationDate) {
          expirationDateValue = new Date(directExpirationDate).toISOString().split('T')[0]
        }
      } else {
        // Search mode
        if (!selectedSearchResult) {
          setError('Vui lòng chọn một nguyên liệu từ kết quả tìm kiếm')
          setIsSubmitting(false)
          return
        }

        if (!quantity.trim() || parseInt(quantity) < 1) {
          setError('Vui lòng nhập số lượng hợp lệ (ít nhất 1)')
          setIsSubmitting(false)
          return
        }

        unitName = selectedSearchResult.component_name
        componentId = selectedSearchResult.component_id

        if (isUncountable) {
          // For uncountable ingredients, require content quantity
          if (!contentQuantity.trim() || parseFloat(contentQuantity) <= 0) {
            setError('Vui lòng nhập định lượng bao bì hợp lệ')
            setIsSubmitting(false)
            return
          }

          // Get unit from selected ingredient
          const unit = selectedSearchResult.measurementUnit || selectedSearchResult.uc_measurement_unit || selectedSearchResult.c_measurement_unit
          if (!unit || (unit !== 'G' && unit !== 'ML')) {
            setError('Nguyên liệu không có đơn vị hợp lệ')
            setIsSubmitting(false)
            return
          }

          packageQty = parseInt(quantity) // Number of packages
          contentType = 'uncountable_ingredient'
          contentQty = parseFloat(contentQuantity) // Quantity per package (định lượng bao bì)
          contentUnitValue = unit as 'G' | 'ML'
        } else {
          // For countable ingredients, quantity is the package quantity
          packageQty = parseInt(quantity)
          contentType = 'countable_ingredient'
        }

        if (expirationDate) {
          expirationDateValue = new Date(expirationDate).toISOString().split('T')[0]
        }
      }

      // Create storable unit
      const createData: any = {
        unit_name: unitName,
        storage_id: Number(storageId),
        package_quantity: packageQty,
        expiration_date: expirationDateValue
      }

      if (componentId) {
        createData.component_id = componentId
      }
      if (contentType) {
        createData.content_type = contentType
      }
      if (contentQty !== null) {
        createData.content_quantity = contentQty
      }
      if (contentUnitValue) {
        createData.content_unit = contentUnitValue
      }

      // Call API to create storable unit
      const result = await storageService.createStorageItem(createData)
      
      result.match(
        () => {
          // Navigate back to StorageDetails page (items)
          navigate(`/main/family-group/${groupId}/storage/items`, { 
            state: { 
              storageId,
              storage: location.state?.storage,
              refreshItems: true
            } 
          })
        },
        (err) => {
          console.error('Failed to create storage item:', err)
          if (err.type === 'unauthorized') {
            setError('Bạn cần đăng nhập để thêm thực phẩm')
          } else {
            setError('Không thể thêm thực phẩm vào kho')
          }
          setIsSubmitting(false)
        }
      )
    } catch (err) {
      console.error('Error creating storage item:', err)
      setError('Không thể thêm thực phẩm vào kho')
      setIsSubmitting(false)
    }
  }

  const inputModeOptions = [
    { value: 'direct', label: 'Điền tên trực tiếp' },
    { value: 'search', label: 'Tìm kiếm nguyên liệu' }
  ]

  return (
    <div className="p-4 max-w-sm mx-auto pb-20">
      <BackButton 
        to={groupId ? `/main/family-group/${groupId}/storage` : '../'} 
        text="Quay lại" 
        className="mb-2"
      />
      <h1 className="text-xl font-bold text-[#C3485C] text-center mb-6">
        Thêm thực phẩm vào kho
      </h1>
      <form className="flex flex-1 flex-col gap-3" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Thực phẩm
          </label>
          <div className="flex flex-col gap-3">
            {inputModeOptions.map((option) => (
              <label
                key={option.value}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <input
                  type="radio"
                  name="inputMode"
                  value={option.value}
                  checked={inputMode === option.value}
                  onChange={(e) => {
                    setInputMode(e.target.value as InputMode)
                    setSelectedSearchResult(null)
                    setSearchQuery('')
                    setError(null)
                  }}
                  className="h-4 w-4 text-[#C3485C] focus:ring-[#C3485C] focus:ring-2"
                />
                <span className="text-gray-900">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        {inputMode === 'direct' ? (
          <div className="mb-6 space-y-4">
            <InputField
              label="Tên thực phẩm"
              placeholder="Ví dụ: Sữa tươi"
              value={directName}
              onChange={(e) => setDirectName(e.target.value)}
              required
            />
            <InputField
              label="Số lượng"
              placeholder="Ví dụ: 2"
              type="number"
              inputMode="numeric"
              min="1"
              step="1"
              value={directQuantity}
              onChange={(e) => setDirectQuantity(e.target.value)}
              required
            />
            <InputField
              label="Ngày hết hạn (tùy chọn)"
              type="date"
              value={directExpirationDate}
              onChange={(e) => setDirectExpirationDate(e.target.value)}
            />
          </div>
        ) : (
          <>
            <div className="mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-3">
                Tìm kiếm nguyên liệu
              </h2>
              <div className="relative">
                <InputField
                  label="Tìm kiếm nguyên liệu"
                  placeholder="Ví dụ: Bông cải"
                  icon={<Search size={20} />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />

                {/* --- UI State: Loading --- */}
                {isSearching && (
                  <div className="flex flex-col items-center justify-center py-6 text-gray-400">
                    <Loader2 className="animate-spin mb-2" size={24} />
                    <p className="text-sm font-medium">Đang tìm kiếm...</p>
                  </div>
                )}

                {/* --- UI State: Not Found --- */}
                {!isSearching && searchQuery.trim() && searchResults.length === 0 && !selectedSearchResult && (
                  <div className="flex flex-col items-center justify-center py-6 text-gray-400">
                    <Search size={24} className="mb-2 opacity-50" />
                    <p className="text-sm font-medium">
                      Không tìm thấy nguyên liệu này
                    </p>
                  </div>
                )}

                {/* --- UI State: Search Results Dropdown --- */}
                {showSearchResults && searchResults.length > 0 && !selectedSearchResult && (
                  <div className="absolute z-10 mt-1 w-full rounded-lg border border-gray-300 bg-white shadow-lg max-h-60 overflow-auto">
                    {searchResults.map((ingredient, index) => {
                      const unit = ingredient.measurementUnit || ingredient.uc_measurement_unit || ingredient.c_measurement_unit || ''
                      return (
                        <button
                          key={ingredient.component_id || index}
                          type="button"
                          onClick={() => handleSelectIngredient(ingredient)}
                          className="w-full px-3 py-2 text-left hover:bg-gray-100 first:rounded-t-lg last:rounded-b-lg flex items-center justify-between"
                        >
                          <div className="flex-1">
                            <div className="font-medium">{ingredient.component_name}</div>
                            {ingredient.category && (
                              <div className="text-sm text-gray-500">{ingredient.category}</div>
                            )}
                          </div>
                          {unit && (
                            <div className="ml-2 text-sm font-medium text-gray-600">
                              {unit}
                            </div>
                          )}
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* --- UI State: Found Result (Show Form Fields) --- */}
            {selectedSearchResult && (
              <div className="mb-6 space-y-3 animate-in fade-in slide-in-from-top-2">
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                  <div className="font-medium">{selectedSearchResult.component_name}</div>
                  {selectedSearchResult.category && (
                    <div className="text-sm text-gray-500">{selectedSearchResult.category}</div>
                  )}
                </div>

                {!isUncountable ? (
                  <InputField
                    label="Số lượng"
                    placeholder="Ví dụ: 100"
                    type="number"
                    inputMode="numeric"
                    min="1"
                    step="1"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    rightLabel={selectedSearchResult.measurementUnit || undefined}
                    required
                  />
                ) : (
                  <>
                    <InputField
                      label="Số lượng"
                      placeholder="Ví dụ: 2"
                      type="number"
                      inputMode="numeric"
                      min="1"
                      step="1"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                      required
                    />
                    <InputField
                      label="Định lượng bao bì"
                      placeholder="Ví dụ: 500"
                      type="number"
                      inputMode="decimal"
                      min="0.01"
                      step="0.01"
                      value={contentQuantity}
                      onChange={(e) => setContentQuantity(e.target.value)}
                      rightLabel={selectedSearchResult.measurementUnit || selectedSearchResult.uc_measurement_unit || selectedSearchResult.c_measurement_unit || undefined}
                      required
                    />
                  </>
                )}

                <InputField
                  label="Ngày hết hạn (tùy chọn)"
                  type="date"
                  value={expirationDate}
                  onChange={(e) => setExpirationDate(e.target.value)}
                />
              </div>
            )}
          </>
        )}

        {error && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 mb-4">
            {error}
          </div>
        )}

        <div className="mt-6">
          <Button
            icon={isSubmitting ? Loader2 : Check}
            type="submit"
            size="fit"
            variant={isSubmitting ? 'disabled' : 'primary'}
            className="w-full"
          >
            {isSubmitting ? 'Đang thêm...' : 'Thêm'}
          </Button>
        </div>
      </form>
    </div>
  )
}
