import { BackButton } from '../../../components/BackButton'
import { useParams, useLocation } from 'react-router-dom'
import { Time } from '../../../utils/time'
import { storageService, type StorableUnit } from '../../../services/storage'

function ReadonlyTextField({ title, value }: { title: string; value: string }) {
  return (
    <div>
      <p className="pb-1 font-bold">{title}</p>
      <p>{value}</p>
    </div>
  )
}

function formatAmount(item: StorableUnit): string {
  if (item.content_quantity && item.content_unit) {
    return `${item.package_quantity} x ${item.content_quantity}${item.content_unit}`
  }
  return String(item.package_quantity)
}

export function StorageItemDetail() {
  const { id: groupId } = useParams<{ id: string }>()
  const location = useLocation()
  
  // Get storageId, storage, and item from location state
  const storageId = location.state?.storageId
  const storage = location.state?.storage
  const item = location.state?.item as StorableUnit | undefined
  
  const formatAmountText = item ? formatAmount(item) : ''

  if (!item) {
    return (
      <div className="flex flex-col p-4">
        <BackButton
          to={groupId ? `/main/family-group/${groupId}/storage/items` : '../'}
          text="Quay lại"
          className="mb-4"
          state={{
            storageId,
            storage
          }}
        />
        <div className="flex items-center justify-center p-8 text-red-600">
          Không tìm thấy thông tin thực phẩm
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col p-4">
      <BackButton
        to={groupId ? `/main/family-group/${groupId}/storage/items` : '../'}
        text="Quay lại"
        className="mb-4"
        state={{
          storageId,
          storage
        }}
      />
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{item.unit_name}</h1>
      </div>
      <div className="flex flex-1 flex-col gap-3">
        <ReadonlyTextField
          title="Số lượng"
          value={formatAmountText}
        />
        <ReadonlyTextField
          title="Tổng số lượng"
          value={String(item.package_quantity)}
        />
        {item.content_quantity && item.content_unit && (
          <ReadonlyTextField
            title="Định lượng bao bì"
            value={`${item.content_quantity}${item.content_unit}`}
          />
        )}
        <ReadonlyTextField
          title="Ngày thêm"
          value={Time.DD_MM_YYYY(new Date(item.added_date))}
        />
        <ReadonlyTextField
          title="Hạn sử dụng"
          value={item.expiration_date ? Time.DD_MM_YYYY(new Date(item.expiration_date)) : 'Không có'}
        />
      </div>
    </div>
  )
}