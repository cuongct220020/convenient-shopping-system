import { AlertTriangle, Loader, Plus, Trash, X } from 'lucide-react'
import { Button } from '../../../components/Button'
import fridge from '../../../assets/fridge.png'
import { useNavigate } from 'react-router-dom'
import { NotificationCard } from '../../../components/NotificationCard'
import { i18n } from '../../../utils/i18n/i18n'
import { MouseEvent, useState } from 'react'

function FridgeCardSkeleton() {
  return (
    <div className="animate-pulse rounded-lg bg-white p-3 shadow">
      <div className="aspect-square w-full rounded bg-gray-200" />

      <div className="mt-3 space-y-2">
        <div className="h-4 w-3/4 rounded bg-gray-200" />
        <div className="h-3 w-1/2 rounded bg-gray-200" />
      </div>

      <div className="absolute bottom-3 right-3 size-9 rounded-full bg-gray-200" />
    </div>
  )
}

type FridgeCardProps = {
  name: string
  count: number
  imageUrl?: string
  isLoading?: boolean
  deleting?: boolean
  onDelete?: () => unknown
  onClick?: () => unknown
}

export function FridgeCard({
  name,
  count,
  imageUrl,
  isLoading = false,
  deleting = false,
  onClick,
  onDelete
}: FridgeCardProps) {
  if (isLoading) {
    return <FridgeCardSkeleton />
  }

  return (
    <div
      role="button"
      onClick={onClick}
      className="relative rounded-lg bg-white p-3 shadow"
    >
      <div className="aspect-square w-full rounded bg-gray-100">
        {imageUrl && (
          <img src={imageUrl} alt={name} className="size-full object-cover" />
        )}
      </div>
      <div className="mt-2">
        <p className="font-semibold">{name}</p>
        <p className="text-sm text-gray-500">{count} thực phẩm</p>
      </div>
      <div className="absolute bottom-3 right-3 flex items-center justify-center">
        <Button
          icon={Trash}
          size="fit"
          variant={deleting ? 'disabled' : 'secondary'}
          onClick={(e: MouseEvent) => {
            e.stopPropagation()
            onDelete?.()
          }}
        />
      </div>
    </div>
  )
}

type DeleteStoragePopupProps = {
  name: string
  foodCount: number
  deleting: boolean
  onCancel?: () => unknown
  onDelete?: () => unknown
}

function DeleteStoragePopup({
  name,
  foodCount,
  deleting,
  onCancel,
  onDelete
}: DeleteStoragePopupProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <NotificationCard
        title={`Xóa ${name}`}
        message={`Trong ${name} còn ${foodCount} thực phẩm. Bạn có chắc chắn muốn xóa?`}
        icon={AlertTriangle}
        iconBgColor="bg-red-500"
        buttonIcon={deleting ? Loader : Trash}
        buttonText={i18n.t(deleting ? 'deleting' : 'delete')}
        buttonVariant={deleting ? 'disabled' : 'primary'}
        onButtonClick={onDelete}
        button2Icon={X}
        button2Text={i18n.t('decline')}
        button2Variant={deleting ? 'disabled' : 'secondary'}
        onButton2Click={onCancel}
      />
    </div>
  )
}

type DeleteState = {
  show: boolean
  deleting: boolean
  name: string
  foodCount: number
}

export function Storage() {
  const navigate = useNavigate()
  const [deleteSt, setDeleteSt] = useState<DeleteState>({
    show: false,
    deleting: false,
    foodCount: 0,
    name: ''
  })
  const onDeleteStorageRequested = () =>
    setDeleteSt({
      show: true,
      name: 'Tủ lạnh 1',
      foodCount: 8,
      deleting: false
    })

  const onDeleteStorageConfirmed = () => {
    setDeleteSt((prev) => ({ ...prev, deleting: true }))
    // Send API here
  }

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-4">
        <p className="whitespace-nowrap text-xl font-bold text-red-600">
          Kho thực phẩm
        </p>
        <Button
          icon={Plus}
          type="button"
          size="fit"
          variant="primary"
          onClick={() => navigate('storage/add')}
        />
      </div>

      {/* Grid container */}
      <div className="px-4">
        <div className="mx-auto grid max-w-6xl grid-cols-[repeat(auto-fill,minmax(150px,1fr))] gap-4">
          <FridgeCard
            name="Tủ lạnh 1"
            count={8}
            imageUrl={fridge}
            onClick={() => navigate('storage/items')}
            onDelete={onDeleteStorageRequested}
          />
          <FridgeCard name="Tủ lạnh 2" count={12} imageUrl={fridge} />
          <FridgeCard name="Tủ lạnh 3" count={5} imageUrl={fridge} />
          <FridgeCard name="Tủ lạnh 4" count={9} isLoading />
          <FridgeCard name="Tủ lạnh 5" count={3} isLoading />
        </div>
      </div>

      {deleteSt.show && (
        <DeleteStoragePopup
          {...deleteSt}
          onCancel={() => setDeleteSt((prev) => ({ ...prev, show: false }))}
          onDelete={onDeleteStorageConfirmed}
        />
      )}
    </div>
  )
}
