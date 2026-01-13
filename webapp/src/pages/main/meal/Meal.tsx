import { Button } from '../../../components/Button'
import { useState, useEffect, useCallback, useMemo } from 'react'
import { NotificationList } from '../../../components/NotificationList'
import { Calendar, Info, Plus, Trash, ChevronLeft, Users, ChefHat, Settings } from 'lucide-react'
import { DayPicker, getDefaultClassNames } from 'react-day-picker'
import 'react-day-picker/style.css'
import { Time } from '../../../utils/time'
import MealImage from '../../../assets/meal.png'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { groupService } from '../../../services/group'
import { userService } from '../../../services/user'
import type { GroupMembership } from '../../../services/schema/groupSchema'
import { GroupHeader } from '../../../components/GroupHeader'

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

function dayName(index: number) {
  return index === 6 ? 'CN' : `Thứ ${index + 2}`
}

type DateThumbnailProps = {
  dayLabel: string
  date: number
  isToday?: boolean
  isSelected?: boolean
  onClick?: () => void
}

function DateThumbnail({
  dayLabel,
  date,
  isToday,
  isSelected,
  onClick
}: DateThumbnailProps) {
  return (
    <button
      onClick={onClick}
      className={[
        'flex w-11 flex-col items-center rounded-xl transition',
        'p-2 gap-1',
        isSelected && 'bg-red-500 shadow-sm'
      ].join(' ')}
    >
      <span
        className={[
          'text-sm font-medium leading-none text-nowrap',
          isSelected ? 'text-white' : 'invisible'
        ].join(' ')}
      >
        {dayLabel}
      </span>

      <div
        className={[
          'flex h-8 w-8 items-center justify-center rounded-full',
          'text-lg font-semibold',
          isToday || isSelected
            ? 'bg-yellow-100 text-red-500'
            : 'bg-gray-100 text-black'
        ].join(' ')}
      >
        {date}
      </div>
    </button>
  )
}

const calendarClassNames = getDefaultClassNames()
type NotificationPopupProps = {
  onClose?: () => unknown
}
function NotificationPopup({ onClose }: NotificationPopupProps) {
  const [noti, setNoti] = useState([
    {
      title: 'notif 1',
      timestamp: '2h truoc',
      content: 'lorem ipsum 12312313213 sdfljsldf',
      id: 1
    },
    {
      title: 'fff notif 1',
      timestamp: 'f2h truoc',
      content: 'lorem ipsum 12312313213 sdfljsldf',
      id: 2
    },
    {
      title: 'notif f 1',
      timestamp: '2h tfdruoc',
      content: 'lorem ipsum 12312313213 sdfljsldf',
      id: 3
    }
  ])
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <NotificationList
        notifications={noti}
        onClose={onClose}
        onDelete={(id) => setNoti((prev) => prev.filter((e) => e.id !== id))}
      />
    </div>
  )
}

function getWeekDates(d: Date) {
  // mon -> sun: 0 -> 6
  const day = (d.getDay() + 6) % 7
  const monday = new Date(d)
  monday.setHours(0, 0, 0, 0)
  monday.setDate(d.getDate() - day)
  const week: Date[] = []
  for (let i = 0; i < 7; i++) {
    const dt = new Date(monday)
    dt.setDate(monday.getDate() + i)
    week.push(dt)
  }
  return week
}

type MealTabType = 'members' | 'shopping-plan' | 'storage' | 'meal'

export function Meal() {
  const { id: groupId } = useParams<{ id: string }>()
  const location = useLocation()
  const [showNoti, setShowNoti] = useState(false)
  const [date, setDate] = useState(new Date(Date.now()))
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [activeTab, setActiveTab] = useState<MealTabType>('meal')
  const [groupData, setGroupData] = useState<{
    id: string
    name: string
    avatarUrl: string | null
    memberCount: number
    adminName: string
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

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
            onClick={() => {
              // TODO: Navigate to food storage management
            }}
          >
            Quản lý kho thực phẩm
          </button>
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'meal'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('meal')}
          >
            Quản lý bữa ăn
          </button>
        </div>

        {/* Meal Content */}
        {activeTab === 'meal' && (
          <div className="mt-4">
            <div className="relative">
              <button
                className="flex w-fit gap-3 transition-all duration-200 active:scale-95"
                onClick={() => setShowDatePicker((prev) => !prev)}
              >
                <Calendar />
                <p>{Time.DD_MM_YYYY(date)}</p>
              </button>
              {showDatePicker && (
                <div className="absolute z-[60] w-fit rounded-lg bg-white">
                  <DayPicker
                    animate
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    required
                    classNames={{
                      root: `${calendarClassNames.root} shadow-lg p-2`
                    }}
                  />
                </div>
              )}
            </div>
            <div className="no-scrollbar flex gap-2 overflow-x-auto py-2">
              {getWeekDates(date).map((d, i) => {
                return (
                  <DateThumbnail
                    key={d.toISOString()}
                    dayLabel={dayName(i)}
                    date={d.getDate()}
                    isSelected={Time.isSameDay(d, date)}
                    isToday={Time.isSameDay(d, new Date())}
                    onClick={() => setDate(d)}
                  />
                )
              })}
            </div>
            <div className="flex flex-col items-center gap-2 py-4">
              <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
                <img src={MealImage} alt="Meal" className="aspect-square" />
                <div className="flex flex-col justify-between pl-2">
                  <p className="font-bold">Bữa sáng</p>
                  <div className="flex w-full flex-1 flex-col justify-start text-sm">
                    <p>Bánh bao</p>
                    <p>Lạp xưởng</p>
                    <p>...</p>
                  </div>
                  <p>
                    <span className="font-bold">Calo:</span> 1000
                  </p>
                </div>
                <div className="flex flex-1 flex-col items-end justify-center gap-2">
                  <Button icon={Trash} variant="primary" size="fit" />
                  <Button
                    icon={Info}
                    variant="secondary"
                    size="fit"
                    onClick={() =>
                      navigate(`/main/family-group/${groupId}/meal/detail`)
                    }
                  />
                </div>
              </div>

              <div className="mx-auto flex w-full max-w-sm rounded-xl bg-yellow-100 px-6 py-3">
                <img src={MealImage} alt="Meal" className="aspect-square" />
                <div className="flex flex-col justify-between pl-2">
                  <p className="font-bold">Bữa trưa</p>
                  <div className="flex w-full flex-1 flex-col justify-start text-sm">
                    <p>Bánh bao</p>
                    <p>Lạp xưởng</p>
                    <p>...</p>
                  </div>
                  <p>
                    <span className="font-bold">Calo:</span> 1000
                  </p>
                </div>
                <div className="flex flex-1 flex-col items-end justify-center gap-2">
                  <Button icon={Trash} variant="primary" size="fit" />
                  <Button
                    icon={Info}
                    variant="secondary"
                    size="fit"
                    onClick={() =>
                      navigate(`/main/family-group/${groupId}/meal/detail`)
                    }
                  />
                </div>
              </div>
              <div className="mx-auto flex w-full max-w-sm rounded-xl bg-gray-200 px-6 py-3">
                <img src={MealImage} alt="Meal" className="aspect-square" />
                <div className="flex flex-col justify-between pl-2">
                  <p className="font-bold">Bữa tối</p>
                  <div className="flex w-full flex-1 flex-col justify-start text-sm">
                    <p>Chưa có món ăn</p>
                  </div>
                  <p>
                    <span className="font-bold">Calo:</span> 1000
                  </p>
                </div>
                <div className="flex flex-1 flex-col items-end justify-center gap-2">
                  <Button icon={Trash} variant="primary" size="fit" />
                  <Button
                    icon={Info}
                    variant="secondary"
                    size="fit"
                    onClick={() =>
                      navigate(`/main/family-group/${groupId}/meal/detail`)
                    }
                  />
                </div>
              </div>
              <Button
                icon={Plus}
                variant="icon"
                size="fit"
                onClick={() => navigate(`/main/family-group/${groupId}/meal/add`)}
              />
            </div>
          </div>
        )}
      </div>

      {showNoti && <NotificationPopup onClose={() => setShowNoti(false)} />}
    </div>
  )
}
