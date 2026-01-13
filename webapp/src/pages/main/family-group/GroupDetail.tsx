import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import {
  Settings,
  Users,
  ChefHat,
  Edit2,
  Trash2,
  LogOut,
  ChevronLeft
} from 'lucide-react'
import { Button } from '../../../components/Button'
import GroupDetailMembers from './GroupDetailMembers'
import GroupDetailShoppingPlans from './GroupDetailShoppingPlans'
import { groupService } from '../../../services/group'
import { userService } from '../../../services/user'
import type {
  UserCoreInfo,
  GroupMembership
} from '../../../services/schema/groupSchema'

// Helper function to map backend role to UI role
function mapRoleToUI(
  role: 'head_chef' | 'member'
): 'Trưởng nhóm' | 'Thành viên' {
  return role === 'head_chef' ? 'Trưởng nhóm' : 'Thành viên'
}

// Helper function to get display name from user
function getDisplayName(user: UserCoreInfo | null): string {
  if (!user) return 'Người dùng'
  if (user.first_name && user.last_name) {
    return `${user.last_name} ${user.first_name}`
  }
  if (user.first_name) return user.first_name
  if (user.last_name) return user.last_name
  return user.username || 'Người dùng'
}

type TabType = 'members' | 'shopping-plan'

const GroupDetail = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { id } = useParams<{ id: string }>()

  // Check if navigation state has refresh flag
  const needsRefresh = location.state?.refresh || false
  const returningFromEdit = location.state?.returningFromEdit || false
  const [refreshKey, setRefreshKey] = useState(0)

  // State for group data
  const [groupData, setGroupData] = useState<{
    id: string
    name: string
    avatarUrl: string | null
    memberCount: number
    adminName: string
    members: Array<{
      id: string
      name: string
      role: string
      email?: string
      avatar?: string | null
      isCurrentUser: boolean
    }>
    currentUserRole: 'head_chef' | 'member'
    currentUserId: string | null
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [activeTab, setActiveTab] = useState<TabType>(() => {
    return (location.state as { activeTab?: TabType })?.activeTab || 'members'
  })
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  // Trigger refresh when navigation state has refresh flag
  useEffect(() => {
    if (needsRefresh) {
      setRefreshKey((prev) => prev + 1)
      // Clear the refresh flag but preserve returningFromEdit
      navigate(location.pathname, {
        replace: true,
        state: { returningFromEdit }
      })
    }
  }, [needsRefresh, location.pathname, navigate, returningFromEdit])

  // Fetch current user and group data on mount and when refreshKey changes
  useEffect(() => {
    const fetchData = async () => {
      if (!id) {
        setError('Không tìm thấy ID nhóm')
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      setError(null)

      // Fetch current user info
      const userResult = await userService.getCurrentUser()
      const currentUserId = userResult.isOk() ? userResult.value.data.id : null

      // Fetch group info using the members endpoint (accessible to all members)
      const membersResult = await groupService.getGroupMembers(id)

      membersResult.match(
        (response) => {
          const group = response.data
          // API returns 'members' field, not 'group_memberships'
          const memberships = group.members || group.group_memberships || []

          // Map members to display format
          const members = memberships.map((membership: GroupMembership) => {
            const role = membership.role as 'head_chef' | 'member'
            return {
              id: membership.user.id,
              name: getDisplayName(membership.user),
              role: mapRoleToUI(role),
              email: membership.user.email,
              avatar: membership.user.avatar_url,
              isCurrentUser: membership.user.id === currentUserId
            }
          })

          // Find current user's role from memberships
          const currentUserMembership = memberships.find(
            (m: GroupMembership) => m.user.id === currentUserId
          )
          let currentUserRole: 'head_chef' | 'member' = 'member'

          if (
            currentUserMembership?.role === 'head_chef' ||
            currentUserMembership?.role === 'member'
          ) {
            currentUserRole = currentUserMembership.role
          }

          setGroupData({
            id: group.id,
            name: group.group_name,
            avatarUrl: group.group_avatar_url,
            memberCount: memberships.length,
            adminName: getDisplayName(group.creator),
            members,
            currentUserRole,
            currentUserId
          })
        },
        (err) => {
          console.error('Failed to fetch group members:', err)
          if (err.type === 'unauthorized') {
            setError('Bạn cần đăng nhập để xem nhóm')
          } else if (err.type === 'not-found') {
            setError('Không tìm thấy nhóm')
          } else {
            setError('Không thể tải thông tin nhóm')
          }
        }
      )

      setIsLoading(false)
    }

    fetchData()
  }, [id, refreshKey])

  const isHeadChef = groupData?.currentUserRole === 'head_chef'

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen)

  const handleEdit = () => {
    navigate(`/main/family-group/${id}/edit`, {
      state: { group: groupData, returningFromEdit: true }
    })
    setIsSettingsOpen(false)
  }

  const handleBackdropClick = () => {
    if (isSettingsOpen) setIsSettingsOpen(false)
  }

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1)
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center px-6 pt-20 text-center">
        <div className="size-12 animate-spin rounded-full border-b-2 border-[#C3485C]"></div>
        <p className="mt-4 text-gray-600">Đang tải...</p>
      </div>
    )
  }

  // Error state
  if (error || !groupData) {
    return (
      <div className="flex flex-col items-center justify-center px-6 pt-20 text-center">
        <p className="mb-4 text-red-500">
          {error || 'Không thể tải thông tin nhóm'}
        </p>
        <Button
          variant="primary"
          size="fit"
          onClick={() => navigate('/main/family-group')}
        >
          Quay lại
        </Button>
      </div>
    )
  }

  return (
    <div
      className="relative min-h-screen bg-white"
      onClick={handleBackdropClick}
    >
      {/* Header */}
      <div>
        <div className="flex items-center justify-between px-4 py-2">
          <button
            onClick={() =>
              navigate('/main/family-group', {
                state: returningFromEdit ? { refresh: true } : undefined
              })
            }
            className="flex items-center text-sm font-bold text-[#C3485C] hover:opacity-80"
          >
            <ChevronLeft size={20} strokeWidth={3} />
            <span className="ml-1">Quay lại</span>
          </button>
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleSettings()
              }}
              className="p-2"
            >
              <Settings size={24} className="text-gray-700" />
            </button>

            {/* Settings Popover */}
            {isSettingsOpen && (
              <div className="absolute right-0 top-full z-10 mt-2 w-32 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                {isHeadChef ? (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleEdit()
                      }}
                      className="flex w-full items-center px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <Edit2 size={16} className="mr-2" />
                      Chỉnh sửa
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setIsSettingsOpen(false)
                      }}
                      className="flex w-full items-center px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100"
                    >
                      <Trash2 size={16} className="mr-2" />
                      Xóa nhóm
                    </button>
                  </>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setIsSettingsOpen(false)
                    }}
                    className="flex w-full items-center px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100"
                  >
                    <LogOut size={16} className="mr-2" />
                    Rời nhóm
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <h1 className="pb-2 text-center text-xl font-bold text-[#C3485C]">
          Chi Tiết Nhóm
        </h1>
      </div>

      <div className="px-4 pb-4">
        {/* Group Info */}
        <div className="mt-4 flex flex-col items-center">
          <img
            src={
              groupData.avatarUrl ||
              new URL('../../../assets/family.png', import.meta.url).href
            }
            alt={groupData.name}
            className="mb-4 size-24 rounded-full object-cover"
          />
          <h2 className="text-2xl font-bold text-gray-900">{groupData.name}</h2>
          <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center">
              <Users size={16} className="mr-1" />
              <span>{groupData.memberCount} thành viên</span>
            </div>
            <div className="flex items-center">
              <ChefHat size={16} className="mr-1" />
              <span>{groupData.adminName}</span>
            </div>
          </div>
        </div>

        {/* Quick Access Buttons */}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <Button
            variant="secondary"
            size="fit"
            onClick={() => {
              // TODO: Navigate to food storage management
            }}
          >
            Quản lý kho thực phẩm
          </Button>
          <Button
            variant="secondary"
            size="fit"
            onClick={() => {
              navigate(`/main/family-group/${groupData.id}/meal`)
            }}
          >
            Quản lý bữa ăn
          </Button>
        </div>

        {/* Tabs */}
        <div className="mt-8 flex border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'members'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('members')}
          >
            Thành viên
          </button>
          <button
            className={`flex-1 py-3 text-center text-sm font-bold ${
              activeTab === 'shopping-plan'
                ? 'border-b-2 border-[#C3485C] text-gray-900'
                : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('shopping-plan')}
          >
            Kế hoạch mua sắm
          </button>
        </div>

        {/* Tab Content */}
        <div className="mt-4">
          {activeTab === 'members' && (
            <GroupDetailMembers
              groupData={groupData}
              isHeadChef={isHeadChef}
              onRefresh={handleRefresh}
            />
          )}

          {activeTab === 'shopping-plan' && (
            <GroupDetailShoppingPlans
              groupId={groupData.id}
              members={groupData.members.map((m) => ({
                id: m.id,
                name: m.name
              }))}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default GroupDetail
