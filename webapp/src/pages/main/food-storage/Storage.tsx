import { AlertTriangle, Loader, Plus, Trash, X, Settings } from 'lucide-react'
import { Button } from '../../../components/Button'
import fridge from '../../../assets/fridge.png'
import freezer from '../../../assets/freezer.png'
import pantry from '../../../assets/pantry.png'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { NotificationCard } from '../../../components/NotificationCard'
import { i18n } from '../../../utils/i18n/i18n'
import { MouseEvent, useState, useEffect, useCallback, useMemo } from 'react'
import { groupService } from '../../../services/group'
import { GroupHeader } from '../../../components/GroupHeader'
import { storageService } from '../../../services/storage'

// Helper function to get display name from user
function getDisplayName(user: { first_name?: string | null; last_name?: string | null; username?: string } | null): string {
  if (!user) return 'Người dùng'
  if (user.first_name && user.last_name) {
    return `${user.last_name} ${user.first_name}`
  }
  if (user.first_name) return user.first_name
  if (user.last_name) return user.last_name
  return user.username || 'Người dùng'
}

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
        <button
          onClick={(e: MouseEvent) => {
            e.stopPropagation()
            onDelete?.()
          }}
          disabled={deleting}
          className={`
            flex items-center justify-center
            ${deleting ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-100'}
            rounded-lg p-2 transition-colors
          `}
        >
          <Trash size={18} className="text-gray-600" />
        </button>
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
  storageId: number | null
  name: string
  foodCount: number
}

type StorageTabType = 'members' | 'shopping-plan' | 'storage' | 'meal'

type StorageItem = {
  storage_id: number
  storage_name: string
  storage_type: 'fridge' | 'freezer' | 'pantry'
  item_count: number
}

// Map storage type to image
function getStorageImage(storageType: 'fridge' | 'freezer' | 'pantry'): string {
  switch (storageType) {
    case 'fridge':
      return fridge
    case 'freezer':
      return freezer
    case 'pantry':
      return pantry
    default:
      return fridge
  }
}

export function Storage() {
  const { id: groupId } = useParams<{ id: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const [deleteSt, setDeleteSt] = useState<DeleteState>({
    show: false,
    deleting: false,
    storageId: null,
    foodCount: 0,
    name: ''
  })
  const [activeTab, setActiveTab] = useState<StorageTabType>('storage')
  const [groupData, setGroupData] = useState<{
    id: string
    name: string
    avatarUrl: string | null
    memberCount: number
    adminName: string
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [storages, setStorages] = useState<StorageItem[]>([])
  const [isLoadingStorages, setIsLoadingStorages] = useState(true)

  // Debug: Log storages state changes
  useEffect(() => {
    console.log('Storages state updated:', storages)
    console.log('isLoadingStorages:', isLoadingStorages)
    console.log('activeTab:', activeTab)
  }, [storages, isLoadingStorages, activeTab])

  // Fetch group data - use state from navigation if available
  useEffect(() => {
    const fetchGroupData = async () => {
      if (!groupId) return

      // Check if groupData was passed via navigation state
      const stateGroupData = (location.state as { groupData?: typeof groupData })?.groupData
      if (stateGroupData) {
        setGroupData(stateGroupData)
        setIsLoading(false)
        return
      }

      // Otherwise, fetch from API
      setIsLoading(true)
      const membersResult = await groupService.getGroupMembers(groupId)

      membersResult.match(
        (response) => {
          const group = response.data
          const memberships = group.members || group.group_memberships || []

          setGroupData({
            id: group.id,
            name: group.group_name,
            avatarUrl: group.group_avatar_url,
            memberCount: memberships.length,
            adminName: getDisplayName(group.creator)
          })
        },
        (err) => {
          console.error('Failed to fetch group:', err)
        }
      )

      setIsLoading(false)
    }

    fetchGroupData()
  }, [groupId, location.state])

  // Fetch storages for the group
  const fetchStorages = useCallback(async () => {
    if (!groupId) return

    setIsLoadingStorages(true)
    storageService.getStorages(groupId).match(
      (storagesList) => {
        console.log('Fetched storages:', storagesList)
        // Check if storagesList is an array or wrapped in an object
        const storagesArray = Array.isArray(storagesList) 
          ? storagesList 
          : (storagesList as any)?.data || (storagesList as any)?.results || []
        
        console.log('Storages array:', storagesArray)
        setStorages(storagesArray.map((s: any) => ({
          storage_id: s.storage_id,
          storage_name: s.storage_name,
          storage_type: s.storage_type,
          item_count: Array.isArray(s.storage_unit_list) ? s.storage_unit_list.length : 0
        })))
        setIsLoadingStorages(false)
      },
      (err) => {
        console.error('Failed to fetch storages:', err)
        setIsLoadingStorages(false)
      }
    )
  }, [groupId])

  useEffect(() => {
    fetchStorages()
  }, [fetchStorages])

  // Refresh storages when navigating back from add page
  useEffect(() => {
    if (location.state?.refreshStorages) {
      fetchStorages()
      // Clear the refresh flag
      navigate(location.pathname, { replace: true, state: {} })
    }
  }, [location.state, location.pathname, navigate, fetchStorages])

  const handleBack = useCallback(() => {
    if (!groupId || !groupData) return
    navigate(`/main/family-group/${groupId}`, {
      state: {
        groupData: {
          id: groupData.id,
          name: groupData.name,
          avatarUrl: groupData.avatarUrl,
          memberCount: groupData.memberCount,
          adminName: groupData.adminName
        },
        activeTab: 'members' // Default to members tab when going back
      }
    })
  }, [navigate, groupId, groupData])

  const settingsButton = useMemo(
    () => (
      <button
        onClick={(e) => {
          e.stopPropagation()
          // TODO: Add settings functionality if needed
        }}
        className="p-2"
      >
        <Settings size={24} className="text-gray-700" />
      </button>
    ),
    []
  )

  const onDeleteStorageConfirmed = () => {
    if (!deleteSt.storageId) return

    setDeleteSt((prev) => ({ ...prev, deleting: true }))
    
    storageService.deleteStorage(deleteSt.storageId).match(
      () => {
        // Successfully deleted, refresh storages list
        fetchStorages()
        setDeleteSt({
          show: false,
          deleting: false,
          storageId: null,
          foodCount: 0,
          name: ''
        })
      },
      (err) => {
        console.error('Failed to delete storage:', err)
        setDeleteSt((prev) => ({ ...prev, deleting: false }))
        // TODO: Show error message to user
      }
    )
  }

  if (isLoading || !groupData) {
    return (
      <div className="flex flex-col items-center justify-center px-6 pt-20 text-center">
        <div className="size-12 animate-spin rounded-full border-b-2 border-[#C3485C]"></div>
        <p className="mt-4 text-gray-600">Đang tải...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col bg-white">
      {/* Header with Group Info */}
      <GroupHeader
        groupName={groupData.name}
        avatarUrl={groupData.avatarUrl}
        isCompact={true}
        onBack={handleBack}
        settingsButton={settingsButton}
      />

      <div className="px-4 pb-4">
        {/* Tabs */}
        <div className="mt-8 flex border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'members'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500'
            }`}
            onClick={() => {
              if (activeTab !== 'members') {
                navigate(`/main/family-group/${groupId}`, {
                  state: {
                    groupData: groupData ? {
                      id: groupData.id,
                      name: groupData.name,
                      avatarUrl: groupData.avatarUrl,
                      memberCount: groupData.memberCount,
                      adminName: groupData.adminName
                    } : undefined,
                    activeTab: 'members'
                  }
                })
              }
            }}
          >
            Thành viên
          </button>
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'shopping-plan'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500'
            }`}
            onClick={() => {
              if (activeTab !== 'shopping-plan') {
                navigate(`/main/family-group/${groupId}`, {
                  state: {
                    groupData: groupData ? {
                      id: groupData.id,
                      name: groupData.name,
                      avatarUrl: groupData.avatarUrl,
                      memberCount: groupData.memberCount,
                      adminName: groupData.adminName
                    } : undefined,
                    activeTab: 'shopping-plan'
                  }
                })
              }
            }}
          >
            Kế hoạch mua sắm
          </button>
        </div>

        {/* Quick Access Buttons */}
        <div className="mt-4 flex border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'storage'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('storage')}
          >
            Quản lý kho thực phẩm
          </button>
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'meal'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500 hover:text-gray-900'
            }`}
            onClick={() => {
              if (activeTab !== 'meal') {
                // Get today's date in YYYY-MM-DD format
                const today = new Date()
                const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
                navigate(`/main/family-group/${groupId}/meal?date=${encodeURIComponent(todayStr)}`, {
                  state: {
                    groupData: groupData ? {
                      id: groupData.id,
                      name: groupData.name,
                      avatarUrl: groupData.avatarUrl,
                      memberCount: groupData.memberCount,
                      adminName: groupData.adminName
                    } : undefined
                  }
                })
              }
            }}
          >
            Quản lý bữa ăn
          </button>
        </div>

        {/* Storage Content */}
        {activeTab === 'storage' && (
          <div className="mt-4">
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
                onClick={() => navigate(`/main/family-group/${groupId}/storage/add`, {
                  state: { groupData }
                })}
              />
            </div>

            {/* Grid container */}
            <div className="px-4">
              {isLoadingStorages ? (
                <div className="mx-auto grid max-w-6xl grid-cols-[repeat(auto-fill,minmax(150px,1fr))] gap-4">
                  <FridgeCard name="" count={0} isLoading />
                  <FridgeCard name="" count={0} isLoading />
                  <FridgeCard name="" count={0} isLoading />
                </div>
              ) : storages.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8">
                  <p className="text-gray-500">Chưa có kho thực phẩm nào</p>
                </div>
              ) : (
                <div className="mx-auto grid max-w-6xl grid-cols-[repeat(auto-fill,minmax(150px,1fr))] gap-4">
                  {storages.map((storage) => {
                    console.log('Rendering storage:', storage)
                    return (
                      <FridgeCard
                        key={storage.storage_id}
                        name={storage.storage_name}
                        count={storage.item_count}
                        imageUrl={getStorageImage(storage.storage_type)}
                        onClick={() => navigate(`/main/family-group/${groupId}/storage/items`, {
                          state: {
                            storageId: storage.storage_id,
                            storage: storage,
                            groupData
                          }
                        })}
                        onDelete={() => {
                          setDeleteSt({
                            show: true,
                            storageId: storage.storage_id,
                            name: storage.storage_name,
                            foodCount: storage.item_count,
                            deleting: false
                          })
                        }}
                      />
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        )}
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
