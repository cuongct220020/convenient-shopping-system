import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import { Settings, Edit2, Trash2, LogOut } from 'lucide-react'
import { Button } from '../../../components/Button'
import { GroupHeader } from '../../../components/GroupHeader'
import GroupDetailMembers from './GroupDetailMembers'
import GroupDetailShoppingPlans from './GroupDetailShoppingPlans'
import { groupService } from '../../../services/group'
import { userService } from '../../../services/user'
import type {
  UserCoreInfo,
  GroupMembership
} from '../../../services/schema/groupSchema'
import { Meal } from '../meal/Meal'

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

type TabType = 'members' | 'shopping-plan' | 'meal'

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

  const [activeTab, setActiveTab] = useState<TabType>('members')
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  // Update activeTab when location.state changes
  useEffect(() => {
    const stateActiveTab = (location.state as { activeTab?: TabType })
      ?.activeTab
    if (stateActiveTab) {
      setActiveTab(stateActiveTab)
    }
  }, [location.state])

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

      // Check if groupData was passed via navigation state
      const stateGroupData = (
        location.state as { groupData?: typeof groupData }
      )?.groupData
      if (stateGroupData) {
        // Set groupData immediately from state to avoid loading/reload
        // We still need to fetch full data for members list and current user role
        // But we can use stateGroupData for basic info to avoid layout reload
        setError(null)

        // Set groupData immediately with basic info to prevent reload
        setGroupData({
          id: stateGroupData.id,
          name: stateGroupData.name,
          avatarUrl: stateGroupData.avatarUrl,
          memberCount: stateGroupData.memberCount,
          adminName: stateGroupData.adminName,
          members: [], // Will be updated after fetch
          currentUserRole: 'member', // Will be updated after fetch
          currentUserId: null // Will be updated after fetch
        })

        setIsLoading(false) // Set loading to false immediately

        // Fetch full data in background
        const fetchFullData = async () => {
          const userResult = await userService.getCurrentUser()
          const currentUserId = userResult.isOk()
            ? userResult.value.data.id
            : null

          const membersResult = await groupService.getGroupMembers(id)

          membersResult.match(
            (response) => {
              const group = response.data
              const memberships = group.members || group.group_memberships || []

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

              // Update groupData with full info
              setGroupData((prev) => {
                if (!prev) return prev
                return {
                  ...prev,
                  members,
                  currentUserRole,
                  currentUserId
                }
              })
            },
            (err) => {
              console.error('Failed to fetch group members:', err)
              // Don't set error state to avoid disrupting the UI
            }
          )
        }

        fetchFullData()
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

  const toggleSettings = useCallback(() => {
    setIsSettingsOpen((prev) => !prev)
  }, [])

  const handleEdit = useCallback(() => {
    if (!id || !groupData) return
    navigate(`/main/family-group/${id}/edit`, {
      state: { group: groupData, returningFromEdit: true }
    })
    setIsSettingsOpen(false)
  }, [id, groupData, navigate])

  const handleBackdropClick = useCallback(() => {
    setIsSettingsOpen(false)
  }, [])

  const handleRefresh = useCallback(() => {
    setRefreshKey((prev) => prev + 1)
  }, [])

  const handleBack = useCallback(() => {
    navigate('/main/family-group', {
      state: returningFromEdit ? { refresh: true } : undefined
    })
  }, [navigate, returningFromEdit])

  const settingsButton = useMemo(
    () => (
      <button
        onClick={(e) => {
          e.stopPropagation()
          toggleSettings()
        }}
        className="p-2"
      >
        <Settings size={24} className="text-gray-700" />
      </button>
    ),
    [toggleSettings]
  )

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
      {/* Header with Group Info */}
      <GroupHeader
        groupName={groupData.name}
        avatarUrl={groupData.avatarUrl}
        groupId={groupData.id}
        memberCount={groupData.memberCount}
        adminName={groupData.adminName}
        isCompact={activeTab !== 'members'}
        activeNav={
          activeTab === 'members'
            ? 'members'
            : activeTab === 'meal'
              ? 'meal'
              : 'shopping'
        }
        onBack={handleBack}
        settingsButton={settingsButton}
      />

      {/* Settings Popover */}
      {isSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-end px-4 pt-16">
          <div
            className="absolute right-4 top-16 z-10 w-32 rounded-lg border border-gray-200 bg-white py-1 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
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
        </div>
      )}

      <div className="px-4 pb-4">
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

          {activeTab === 'meal' && <Meal />}
        </div>
      </div>
    </div>
  )
}

export default GroupDetail
