import { Users, ChefHat, ChevronLeft } from 'lucide-react'
import { ReactNode, memo } from 'react'
import { useNavigate } from 'react-router-dom'

type ActiveNav = 'members' | 'meal' | 'shopping' | 'storage'

export interface GroupHeaderProps {
  groupName: string
  avatarUrl: string | null
  groupId: string
  memberCount?: number
  adminName?: string
  isCompact: boolean
  activeNav: ActiveNav
  onBack?: () => void
  settingsButton?: ReactNode
}

export const GroupHeader = memo(
  function GroupHeader({
    groupName,
    avatarUrl,
    groupId,
    memberCount,
    adminName,
    isCompact,
    activeNav,
    onBack,
    settingsButton
  }: GroupHeaderProps) {
    const navigate = useNavigate()
    const defaultAvatar = new URL('../assets/family.png', import.meta.url).href

    const navigationItems = [
      {
        id: 'members' as const,
        label: 'Thành viên',
        onClick: () =>
          navigate(`/main/family-group/${groupId}`, {
            state: { activeTab: 'members' }
          })
      },
      {
        id: 'meal' as const,
        label: 'Bữa ăn',
        onClick: () =>
          navigate(`/main/family-group/${groupId}`, {
            state: { activeTab: 'meal' }
          })
      },
      {
        id: 'shopping' as const,
        label: 'Kế hoạch mua sắm',
        onClick: () =>
          navigate(`/main/family-group/${groupId}`, {
            state: { activeTab: 'shopping-plan' }
          })
      },
      {
        id: 'storage' as const,
        label: 'Quản lý kho',
        onClick: () => navigate(`/main/family-group/${groupId}/storage`)
      }
    ]

    return (
      <>
        {/* Top Header Bar */}
        <div className="flex items-center justify-between px-4 py-2">
          {onBack ? (
            <button
              onClick={onBack}
              className="flex items-center text-sm font-bold text-[#C3485C] hover:opacity-80"
            >
              <ChevronLeft size={20} strokeWidth={3} />
              <span className="ml-1">Quay lại</span>
            </button>
          ) : (
            <div></div>
          )}
          {settingsButton ? (
            <div className="relative">{settingsButton}</div>
          ) : (
            <div></div>
          )}
        </div>

        {/* Title - Always shown */}
        <h1 className="pb-2 text-center text-xl font-bold text-[#C3485C]">
          Chi Tiết Nhóm
        </h1>

        {/* Group Info */}
        <div className="px-4 pb-4">
          <div className="relative mt-4 overflow-hidden">
            {isCompact ? (
              <div
                className="flex items-center"
                style={{
                  animation: 'slideInLeft 0.3s ease-in-out'
                }}
              >
                <img
                  src={avatarUrl || defaultAvatar}
                  alt={groupName}
                  className="mr-3 size-12 rounded-full object-cover transition-all duration-300 ease-in-out"
                />
                <h2 className="text-xl font-bold text-gray-900 transition-all duration-300 ease-in-out">
                  {groupName}
                </h2>
              </div>
            ) : (
              <div
                className="flex flex-col items-center"
                style={{
                  animation: 'fadeInScale 0.3s ease-in-out'
                }}
              >
                <img
                  src={avatarUrl || defaultAvatar}
                  alt={groupName}
                  className="mb-4 size-24 rounded-full object-cover transition-all duration-300 ease-in-out"
                />
                <h2 className="text-2xl font-bold text-gray-900 transition-all duration-300 ease-in-out">
                  {groupName}
                </h2>
                {memberCount !== undefined && adminName && (
                  <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600 transition-all duration-300 ease-in-out">
                    <div className="flex items-center">
                      <Users size={16} className="mr-1" />
                      <span>{memberCount} thành viên</span>
                    </div>
                    <div className="flex items-center">
                      <ChefHat size={16} className="mr-1" />
                      <span>{adminName}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="grid grid-cols-2 gap-2 px-4 pb-4">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              onClick={item.onClick}
              className={`rounded-lg px-2 py-3 text-center text-sm font-bold transition-colors ${
                activeNav === item.id
                  ? 'bg-[#C3485C] text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </>
    )
  },
  (prevProps, nextProps) => {
    // Custom comparison to prevent re-render when only isCompact changes during tab navigation
    // Only re-render if actual data changes
    return (
      prevProps.groupName === nextProps.groupName &&
      prevProps.avatarUrl === nextProps.avatarUrl &&
      prevProps.groupId === nextProps.groupId &&
      prevProps.memberCount === nextProps.memberCount &&
      prevProps.adminName === nextProps.adminName &&
      prevProps.isCompact === nextProps.isCompact &&
      prevProps.activeNav === nextProps.activeNav &&
      prevProps.onBack === nextProps.onBack &&
      prevProps.settingsButton === nextProps.settingsButton
    )
  }
)
