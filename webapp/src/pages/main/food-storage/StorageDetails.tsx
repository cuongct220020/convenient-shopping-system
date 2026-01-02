import { Info, Plus } from 'lucide-react'
import { BackButton } from '../../../components/BackButton'
import { Time } from '../../../utils/time'
import { Button } from '../../../components/Button'

type StorageItemExpirationLevel = 'no' | 'almost' | 'expired'
type StorageItemProps = {
  name: string
  amount: string
  expirationDate: Date
  level: StorageItemExpirationLevel
}

function StorageItem({
  name,
  amount,
  expirationDate,
  level
}: StorageItemProps) {
  const colorStr =
    level === 'no'
      ? 'bg-gray-200'
      : level === 'almost'
        ? 'bg-yellow-100'
        : 'bg-red-400'
  return (
    <div
      className={`flex items-center justify-center rounded-xl p-2 ${colorStr}`}
    >
      <div className="flex h-full flex-1 flex-col justify-between gap-4">
        <p className="text-xl font-bold">{name}</p>
        <p>Số lượng: {amount}</p>
      </div>
      <div className="flex h-full flex-col items-end justify-between gap-4">
        <button
          type="button"
          className="transition-all duration-200 active:scale-95"
        >
          <Info />
        </button>
        <p>HSD: {Time.DD_MM_YYYY(expirationDate)}</p>
      </div>
    </div>
  )
}

export function StorageDetails() {
  const exampleStorageDetails = {
    name: 'Tủ lạnh',
    items: [
      {
        name: 'Sữa tươi',
        amount: '2',
        expirationDate: new Date(2026, 10, 4),
        level: 'expired',
        key: 0
      },
      {
        name: 'Thịt bò',
        amount: '700g',
        expirationDate: new Date(2026, 1, 6),
        level: 'almost',
        key: 1
      },
      {
        name: 'Sữa tươi',
        amount: '2',
        expirationDate: new Date(2026, 10, 4),
        level: 'almost',
        key: 2
      },
      {
        name: 'Lúa mạch',
        amount: '1kg',
        expirationDate: new Date(2026, 10, 4),
        level: 'no',
        key: 3
      },
      {
        name: 'Bia',
        amount: '2 lon',
        expirationDate: new Date(2036, 10, 4),
        level: 'no',
        key: 4
      }
    ] as (StorageItemProps & { key: number })[]
  }

  return (
    <div className="flex flex-col p-4">
      <BackButton to="../" text="Quay lại" className="mb-4" />
      <div className="mb-4">
        <h1 className="text-2xl font-bold">{exampleStorageDetails.name}</h1>
      </div>
      <div className="flex flex-1 flex-col gap-3">
        {exampleStorageDetails.items.map((item) => (
          <StorageItem {...item} key={item.key} />
        ))}
        <div className="mx-auto">
          <Button icon={Plus} type="button" variant="icon" size="fit" />
        </div>
      </div>
    </div>
  )
}
