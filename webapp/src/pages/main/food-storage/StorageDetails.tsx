import { Plus, Loader, ArrowDown } from 'lucide-react'
import { Button } from '../../../components/Button'
import { BackButton } from '../../../components/BackButton'
import { Time } from '../../../utils/time'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { storageService, type StorableUnit } from '../../../services/storage'

type StorageItemExpirationLevel = 'no' | 'almost' | 'expired'
type StorageItemProps = {
  unit: StorableUnit
  level: StorageItemExpirationLevel
  quantity: number
  onQuantityChange: (quantity: number) => void
  onConsumeClick?: () => void
  consuming?: boolean
}

function StorageItem({
  unit,
  level,
  quantity,
  onQuantityChange,
  onConsumeClick,
  consuming = false
}: StorageItemProps) {
  const colorStr =
    level === 'no'
      ? 'bg-gray-200'
      : level === 'almost'
        ? 'bg-yellow-100'
        : 'bg-red-400'
  
  const formatAmount = () => {
    if (unit.content_quantity && unit.content_unit) {
      return `${unit.package_quantity} x ${unit.content_quantity}${unit.content_unit}`
    }
    return String(unit.package_quantity)
  }

  return (
    <div
      className={`flex items-center justify-center rounded-xl p-4 ${colorStr}`}
    >
      <div className="flex h-full flex-1 flex-col justify-between gap-3">
        <p className="text-xl font-bold">{unit.unit_name}</p>
        <div className="flex flex-col gap-1 text-sm">
          <p>Số lượng: {formatAmount()}</p>
          <p>Ngày thêm: {Time.DD_MM_YYYY(new Date(unit.added_date))}</p>
          <p>HSD: {unit.expiration_date ? Time.DD_MM_YYYY(new Date(unit.expiration_date)) : 'Không có'}</p>
        </div>
      </div>
      <div className="flex h-full flex-col items-end justify-end gap-4">
        <div className="flex items-center gap-2">
          <input
            type="number"
            min="1"
            step="1"
            inputMode="numeric"
            value={quantity}
            onChange={(e) => {
              const val = Math.max(1, Math.floor(Number(e.target.value)) || 1)
              onQuantityChange(val)
            }}
            disabled={consuming}
            className="w-16 rounded border border-gray-300 px-2 py-1 text-center text-sm focus:border-[#C3485C] focus:outline-none disabled:bg-gray-100 disabled:opacity-50"
          />
          <Button
            type="button"
            variant={consuming ? 'disabled' : 'primary'}
            size="fit"
            icon={ArrowDown}
            onClick={onConsumeClick}
            className="p-2"
          />
        </div>
      </div>
    </div>
  )
}

function calculateExpirationLevel(expirationDate: Date | null): StorageItemExpirationLevel {
  if (!expirationDate) return 'no'
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const expDate = new Date(expirationDate)
  expDate.setHours(0, 0, 0, 0)
  const diffTime = expDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return 'expired'
  if (diffDays <= 3) return 'almost'
  return 'no'
}

export function StorageDetails() {
  const navigate = useNavigate()
  const location = useLocation()
  const { id: groupId } = useParams<{ id: string }>()
  const [items, setItems] = useState<StorableUnit[]>([])
  const [storageName, setStorageName] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [consumingUnitId, setConsumingUnitId] = useState<number | null>(null)
  const [consumeQuantities, setConsumeQuantities] = useState<Record<number, number>>({})

  // Get storage_id from location state
  const storageId = location.state?.storageId || location.state?.storage?.storage_id

  const fetchItems = () => {
    if (!storageId) return
    
    storageService
      .getStorageItems(Number(storageId))
      .map((response) => {
        setItems(response.data)
        setIsLoading(false)
      })
      .mapErr((e) => {
        setError('Không thể tải danh sách thực phẩm')
        setIsLoading(false)
        console.error('Error fetching storage items:', e)
      })
  }

  useEffect(() => {
    if (!storageId) {
      setError('Không tìm thấy thông tin kho')
      setIsLoading(false)
      return
    }

    // Get storage name from location state
    if (location.state?.storage?.storage_name) {
      setStorageName(location.state.storage.storage_name)
    }

    fetchItems()
  }, [storageId, location.state])

  // Refetch when refreshItems is true
  useEffect(() => {
    if (location.state?.refreshItems && storageId) {
      fetchItems()
    }
  }, [location.state?.refreshItems, storageId])

  const handleConsume = async (unit: StorableUnit, quantity: number) => {
    setConsumingUnitId(unit.unit_id)
    
    storageService.consumeStorableUnit(unit.unit_id, quantity).match(
      () => {
        // Successfully consumed, refresh items
        setConsumingUnitId(null)
        fetchItems()
      },
      (err) => {
        console.error('Failed to consume storable unit:', err)
        setConsumingUnitId(null)
        // TODO: Show error message to user
      }
    )
  }

  if (isLoading) {
    return (
      <div className="flex flex-col p-4">
        <BackButton 
          to={groupId ? `/main/family-group/${groupId}/storage` : '../'} 
          text="Quay lại" 
          className="mb-4"
        />
        <div className="mb-4">
          <h1 className="text-2xl font-bold">{storageName || 'Đang tải...'}</h1>
        </div>
        <div className="flex items-center justify-center p-8">
          <Loader className="animate-spin text-gray-400" size={32} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col p-4">
        <BackButton 
          to={groupId ? `/main/family-group/${groupId}/storage` : '../'} 
          text="Quay lại" 
          className="mb-4"
        />
        <div className="mb-4">
          <h1 className="text-2xl font-bold">{storageName || 'Kho thực phẩm'}</h1>
        </div>
        <div className="flex items-center justify-center p-8 text-red-600">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col p-4">
      <BackButton 
        to={groupId ? `/main/family-group/${groupId}/storage` : '../'} 
        text="Quay lại" 
        className="mb-4"
      />
      <div className="mb-4">
        <h1 className="text-2xl font-bold">{storageName || 'Kho thực phẩm'}</h1>
      </div>
      <div className="flex flex-1 flex-col gap-3">
        {items.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            Chưa có thực phẩm nào trong kho
          </div>
        ) : (
          items.map((unit) => {
            const expirationDate = unit.expiration_date ? new Date(unit.expiration_date) : null
            const isConsuming = consumingUnitId === unit.unit_id
            const quantity = consumeQuantities[unit.unit_id] || 1

            return (
              <StorageItem
                key={unit.unit_id}
                unit={unit}
                level={calculateExpirationLevel(expirationDate)}
                quantity={quantity}
                onQuantityChange={(qty) => setConsumeQuantities({ ...consumeQuantities, [unit.unit_id]: qty })}
                onConsumeClick={() => handleConsume(unit, quantity)}
                consuming={isConsuming}
              />
            )
          })
        )}
        <div className="mx-auto">
          <Button
            icon={Plus}
            type="button"
            variant="icon"
            size="fit"
            onClick={() => navigate('add', { 
              state: { 
                storageId, 
                storage: location.state?.storage
              } 
            })}
          />
        </div>
      </div>
    </div>
  )
}