import React, { useState, useEffect, useMemo, useRef } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import { ResultAsync } from 'neverthrow'
import {
  Settings,
  Users,
  ChefHat,
  UserPlus,
  MoreVertical,
  Edit2,
  Trash2,
  User,
  Shield,
  LogOut,
  AlertTriangle,
  X,
  Plus,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Clock,
  Circle
} from 'lucide-react'
import { Button } from '../../../components/Button'
import { UserCard } from '../../../components/UserCard'
import AddMember from './AddMember'
import { groupService } from '../../../services/group'
import { userService } from '../../../services/user'
import { shoppingPlanService } from '../../../services/shopping-plan'
import type {
  UserCoreInfo,
  GroupMembership
} from '../../../services/schema/groupSchema'
import type { PlanResponse } from '../../../services/schema/shoppingPlanSchema'

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
type TimeFilterType = 'today' | 'week' | 'month'

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
  const [openMemberMenuId, setOpenMemberMenuId] = useState<string | null>(null)

  // Delete loading and error states
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  // Set leader loading and error states
  const [isSettingLeader, setIsSettingLeader] = useState(false)
  const [setLeaderError, setSetLeaderError] = useState<string | null>(null)

  // Remove member loading and error states
  const [isRemovingMember, setIsRemovingMember] = useState(false)
  const [removeMemberError, setRemoveMemberError] = useState<string | null>(
    null
  )

  // Leave group loading and error states
  const [isLeavingGroup, setIsLeavingGroup] = useState(false)
  const [leaveGroupError, setLeaveGroupError] = useState<string | null>(null)

  // Shopping Plan State
  const [timeFilter, setTimeFilter] = useState<TimeFilterType>('week')
  const [selectedDate, setSelectedDate] = useState(new Date())
  const calendarScrollRef = useRef<HTMLDivElement>(null)

  // Shopping Plans Data State
  const [shoppingPlans, setShoppingPlans] = useState<PlanResponse[]>([])
  const [isPlansLoading, setIsPlansLoading] = useState(false)
  const [plansError, setPlansError] = useState<string | null>(null)

  // Helper function to get user name by ID from group members
  const getUserNameById = (userId: string): string => {
    const member = groupData?.members.find(m => m.id === userId)
    if (member) return member.name

    // Also check creator
    if (groupData?.currentUserId === userId) {
      // Could be the current user who is the creator
      return groupData.adminName
    }

    return userId // Fallback to ID if not found
  }

  // Trigger refresh when navigation state has refresh flag
  useEffect(() => {
    if (needsRefresh) {
      setRefreshKey(prev => prev + 1)
      // Clear the refresh flag but preserve returningFromEdit
      navigate(location.pathname, { replace: true, state: { returningFromEdit } })
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

  // Scroll to selected date when filter or selected date changes
  useEffect(() => {
    const scrollToSelected = () => {
      if (calendarScrollRef.current) {
        const activeButton = calendarScrollRef.current.querySelector(
          '[data-selected="true"]'
        ) as HTMLElement
        if (activeButton) {
          activeButton.scrollIntoView({
            behavior: 'auto',
            block: 'nearest',
            inline: 'center'
          })
        }
      }
    }

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        scrollToSelected()
      })
    })
  }, [timeFilter, selectedDate])

  // Fetch shopping plans when shopping-plan tab is active
  useEffect(() => {
    const fetchShoppingPlans = async () => {
      if (!id) return

      setIsPlansLoading(true)
      setPlansError(null)

      const result = await shoppingPlanService.filterPlans(id, {
        sortBy: 'deadline',
        order: 'asc'
      })

      result.match(
        (response) => {
          setShoppingPlans(response.data)
        },
        (error) => {
          console.error('Failed to fetch shopping plans:', error)
          setPlansError('Không thể tải kế hoạch mua sắm')
        }
      )

      setIsPlansLoading(false)
    }

    if (activeTab === 'shopping-plan') {
      fetchShoppingPlans()
    }
  }, [activeTab, id])

  // Generate dates based on selected filter
  const getWeekDates = () => {
    const today = new Date()
    const dates = []
    const dayLabels = [
      'CN',
      'Thứ 2',
      'Thứ 3',
      'Thứ 4',
      'Thứ 5',
      'Thứ 6',
      'Thứ 7'
    ]
    const startDate = new Date(selectedDate)
    let daysToShow = 30
    let centerOffset = 7

    if (timeFilter === 'today') {
      centerOffset = 7
      daysToShow = 15
    } else if (timeFilter === 'week') {
      centerOffset = 7
      daysToShow = 14
    } else if (timeFilter === 'month') {
      centerOffset = 15
      daysToShow = 31
    }

    startDate.setDate(selectedDate.getDate() - centerOffset)

    for (let i = 0; i < daysToShow; i++) {
      const date = new Date(startDate)
      date.setDate(startDate.getDate() + i)
      dates.push({
        date: date.getDate(),
        fullDate: date,
        label: dayLabels[date.getDay()],
        active: date.toDateString() === selectedDate.toDateString(),
        isToday: date.toDateString() === today.toDateString()
      })
    }
    return dates
  }

  const weekDates = useMemo(getWeekDates, [timeFilter, selectedDate])

  const handleTimeFilterChange = (filter: TimeFilterType) => {
    setTimeFilter(filter)
    const today = new Date()

    if (filter === 'today') {
      setSelectedDate(new Date(today))
    } else if (filter === 'week') {
      setSelectedDate(new Date(today))
    } else if (filter === 'month') {
      setSelectedDate(new Date(today))
    }
  }

  const today = new Date()
  const isFilterInRange = (filter: TimeFilterType): boolean => {
    if (filter === 'today') {
      return selectedDate.toDateString() === today.toDateString()
    } else if (filter === 'week') {
      const dayOfWeek = today.getDay()
      const weekStart = new Date(today)
      const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
      weekStart.setDate(today.getDate() + diff)
      weekStart.setHours(0, 0, 0, 0)

      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      weekEnd.setHours(23, 59, 59, 999)

      return selectedDate >= weekStart && selectedDate <= weekEnd
    } else if (filter === 'month') {
      return (
        selectedDate.getMonth() === today.getMonth() &&
        selectedDate.getFullYear() === today.getFullYear()
      )
    }
    return true
  }

  // Modal States
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [isSetLeaderModalOpen, setIsSetLeaderModalOpen] = useState(false)
  type MemberType = {
    id: string
    name: string
    role: string
    email?: string
    isCurrentUser: boolean
  }
  const [selectedMemberForLeader, setSelectedMemberForLeader] =
    useState<MemberType | null>(null)
  const [isRemoveMemberModalOpen, setIsRemoveMemberModalOpen] = useState(false)
  const [selectedMemberForRemoval, setSelectedMemberForRemoval] =
    useState<MemberType | null>(null)
  const [isLeaveGroupModalOpen, setIsLeaveGroupModalOpen] = useState(false)

  // Add Member Modal State
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false)

  useEffect(() => {
    const bottomNav = document.querySelector('nav.fixed.bottom-0')
    if (bottomNav) {
      if (
        isDeleteModalOpen ||
        isSetLeaderModalOpen ||
        isRemoveMemberModalOpen ||
        isLeaveGroupModalOpen ||
        isAddMemberModalOpen
      ) {
        bottomNav.classList.add('blur-sm', 'pointer-events-none')
      } else {
        bottomNav.classList.remove('blur-sm', 'pointer-events-none')
      }
    }
    return () => {
      const nav = document.querySelector('nav.fixed.bottom-0')
      if (nav) {
        nav.classList.remove('blur-sm', 'pointer-events-none')
      }
    }
  }, [
    isDeleteModalOpen,
    isSetLeaderModalOpen,
    isRemoveMemberModalOpen,
    isLeaveGroupModalOpen,
    isAddMemberModalOpen
  ])

  const isHeadChef = groupData?.currentUserRole === 'head_chef'

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen)
  const toggleMemberMenu = (id: string) => {
    setOpenMemberMenuId(openMemberMenuId === id ? null : id)
  }

  const handleEdit = () => {
    navigate(`/main/family-group/${id}/edit`, {
      state: { group: groupData, returningFromEdit: true }
    })
    setIsSettingsOpen(false)
  }

  const handleDeleteGroup = async () => {
    if (!id) {
      setDeleteError('Không tìm thấy ID nhóm')
      return
    }

    setIsDeleting(true)
    setDeleteError(null)

    const result = await groupService.deleteGroup(id)

    result.match(
      () => {
        setIsDeleteModalOpen(false)
        navigate('/main/family-group')
      },
      (error) => {
        console.error('Failed to delete group:', error)
        if (error.type === 'unauthorized') {
          setDeleteError('Bạn cần đăng nhập để xóa nhóm')
        } else if (error.type === 'not-found') {
          setDeleteError('Không tìm thấy nhóm')
        } else if (error.type === 'forbidden') {
          setDeleteError('Bạn không có quyền xóa nhóm này')
        } else if (error.type === 'network-error') {
          setDeleteError('Lỗi kết nối mạng')
        } else {
          setDeleteError('Không thể xóa nhóm')
        }
      }
    )

    setIsDeleting(false)
  }

  const handleSetLeader = async () => {
    if (!id || !selectedMemberForLeader || !groupData?.currentUserId) return

    setIsSettingLeader(true)
    setSetLeaderError(null)

    // Transfer leadership by making requests sequentially
    // (not in parallel to avoid race conditions)
    const currentLeaderId = groupData!.currentUserId
    const targetMemberId = selectedMemberForLeader.id

    // First, set the target member as head_chef
    const firstResult = await groupService.updateMemberRole(
      id,
      targetMemberId,
      'head_chef'
    )

    firstResult.match(
      async () => {
        // Then, set the current leader as member
        const secondResult = await groupService.updateMemberRole(
          id,
          currentLeaderId,
          'member'
        )

        secondResult.match(
          () => {
            setIsSetLeaderModalOpen(false)
            setSelectedMemberForLeader(null)
            setOpenMemberMenuId(null)
            // Refresh group data
            setRefreshKey(prev => prev + 1)
          },
          (error) => {
            console.error('Failed to demote current leader:', error)
            if (error.type === 'unauthorized') {
              setSetLeaderError('Bạn cần đăng nhập để thực hiện thao tác này')
            } else if (error.type === 'not-found') {
              setSetLeaderError('Không tìm thấy nhóm')
            } else if (error.type === 'forbidden') {
              setSetLeaderError('Bạn không có quyền thực hiện thao tác này')
            } else {
              setSetLeaderError('Không thể đặt làm trưởng nhóm')
            }
          }
        )
      },
      (error) => {
        console.error('Failed to set leader:', error)
        if (error.type === 'unauthorized') {
          setSetLeaderError('Bạn cần đăng nhập để thực hiện thao tác này')
        } else if (error.type === 'not-found') {
          setSetLeaderError('Không tìm thấy nhóm')
        } else if (error.type === 'forbidden') {
          setSetLeaderError('Bạn không có quyền thực hiện thao tác này')
        } else {
          setSetLeaderError('Không thể đặt làm trưởng nhóm')
        }
      }
    )

    setIsSettingLeader(false)
  }

  const handleRemoveMember = async () => {
    if (!id || !selectedMemberForRemoval || !groupData) return

    // Only head_chef can remove members
    if (groupData?.currentUserRole !== 'head_chef') {
      setRemoveMemberError('Chỉ trưởng nhóm mới có quyền xóa thành viên')
      return
    }

    setIsRemovingMember(true)
    setRemoveMemberError(null)

    const result = await groupService.removeMember(
      id,
      selectedMemberForRemoval.id
    )

    result.match(
      () => {
        // Update local state: remove the member from the list
        setGroupData({
          ...groupData,
          members: groupData.members.filter(
            (m) => m.id !== selectedMemberForRemoval.id
          ),
          memberCount: groupData.memberCount - 1
        })
        setIsRemoveMemberModalOpen(false)
        setSelectedMemberForRemoval(null)
        setOpenMemberMenuId(null)
      },
      (error) => {
        console.error('Failed to remove member:', error)
        if (error.type === 'unauthorized') {
          setRemoveMemberError('Bạn cần đăng nhập để thực hiện thao tác này')
        } else if (error.type === 'not-found') {
          setRemoveMemberError('Không tìm thấy nhóm')
        } else if (error.type === 'forbidden') {
          setRemoveMemberError('Bạn không có quyền thực hiện thao tác này')
        } else {
          setRemoveMemberError('Không thể xóa thành viên')
        }
      }
    )

    setIsRemovingMember(false)
  }

  const handleLeaveGroup = async () => {
    if (!id) return

    setIsLeavingGroup(true)
    setLeaveGroupError(null)

    const result = await groupService.leaveGroup(id)

    result.match(
      () => {
        setIsLeaveGroupModalOpen(false)
        setIsSettingsOpen(false)
        navigate('/main/family-group')
      },
      (error) => {
        console.error('Failed to leave group:', error)
        if (error.type === 'unauthorized') {
          setLeaveGroupError('Bạn cần đăng nhập để rời nhóm')
        } else if (error.type === 'not-found') {
          setLeaveGroupError('Không tìm thấy nhóm')
        } else {
          setLeaveGroupError('Không thể rời nhóm')
        }
      }
    )

    setIsLeavingGroup(false)
  }

  const handleCreatePlan = () => {
    navigate(`/main/family-group/${id}/add-plan`)
  }

  const handleOpenAddMemberModal = () => {
    setIsAddMemberModalOpen(true)
  }

  const handleMemberAdded = async () => {
    // Refresh group data by fetching members again
    if (!id) return

    // Fetch current user info
    const userResult = await userService.getCurrentUser()
    const currentUserId = userResult.isOk() ? userResult.value.data.id : null

    // Fetch group info using the members endpoint (accessible to all members)
    const membersResult = await groupService.getGroupMembers(id)

    membersResult.match(
      (response) => {
        const group = response.data
        const memberships = group.members || group.group_memberships || []

        // Map members to display format
        const members = memberships.map((membership: GroupMembership) => {
          const role = membership.role as 'head_chef' | 'member'
          return {
            id: membership.user.id,
            name: getDisplayName(membership.user),
            role: mapRoleToUI(role),
            email: membership.user.email,
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
        console.error('Failed to refresh group members:', err)
      }
    )
  }

  const handleAddMemberCancel = () => {
    setIsAddMemberModalOpen(false)
  }

  const handleBackdropClick = () => {
    if (
      isDeleteModalOpen ||
      isSetLeaderModalOpen ||
      isRemoveMemberModalOpen ||
      isLeaveGroupModalOpen ||
      isAddMemberModalOpen
    )
      return
    if (isSettingsOpen) setIsSettingsOpen(false)
    if (openMemberMenuId) setOpenMemberMenuId(null)
  }

  // Helper to render plan status badge
  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'created':
        return (
          <div className="flex items-center gap-1 rounded-full border border-blue-300 bg-white px-2 py-0.5">
            <Circle size={8} fill="#3B82F6" className="text-blue-500" />
            <span className="text-[10px] font-medium text-blue-500">
              Mới tạo
            </span>
          </div>
        )
      case 'completed':
        return (
          <div className="flex items-center gap-1 rounded-full border border-green-300 bg-white px-2 py-0.5">
            <CheckCircle2 size={12} className="text-green-500" />
            <span className="text-[10px] font-medium text-green-500">
              Đã xong
            </span>
          </div>
        )
      case 'in_progress':
        return (
          <div className="flex items-center gap-1 rounded-full border border-[#C3485C] bg-white px-2 py-0.5">
            <Circle size={8} fill="#C3485C" className="text-[#C3485C]" />
            <span className="text-[10px] font-medium text-[#C3485C]">
              Đang thực hiện
            </span>
          </div>
        )
      case 'cancelled':
        return (
          <div className="flex items-center gap-1 rounded-full border border-gray-300 bg-white px-2 py-0.5">
            <X size={8} className="text-gray-500" />
            <span className="text-[10px] font-medium text-gray-500">
              Đã hủy
            </span>
          </div>
        )
      case 'expired':
        return (
          <div className="flex items-center gap-1 rounded-full border border-red-300 bg-white px-2 py-0.5">
            <Clock size={8} className="text-red-500" />
            <span className="text-[10px] font-medium text-red-500">
              Hết hạn
            </span>
          </div>
        )
      default:
        return null
    }
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
                        setIsDeleteModalOpen(true)
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
                      setIsLeaveGroupModalOpen(true)
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
            src={groupData.avatarUrl || 'https://cdn-icons-png.flaticon.com/512/3253/3253272.png'}
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
          {activeTab === 'members' && isHeadChef && (
            <Button
              variant="primary"
              size="fit"
              className="mt-6"
              icon={UserPlus}
              onClick={handleOpenAddMemberModal}
            >
              Thêm thành viên
            </Button>
          )}
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
            onClick={() => {
              setActiveTab('shopping-plan')
              setTimeFilter('today')
              setSelectedDate(new Date())
            }}
          >
            Kế hoạch mua sắm
          </button>
        </div>

        {/* Tab Content */}
        <div className="mt-4">
          {activeTab === 'members' && (
            <div>
              <h3 className="mb-4 text-sm text-gray-600">
                Danh sách thành viên ({groupData.members.length})
              </h3>
              <div className="space-y-3">
                {groupData.members.map((member) => (
                  <UserCard
                    key={member.id}
                    id={member.id}
                    name={member.name}
                    role={member.role}
                    email={member.email}
                    variant="selected"
                    onClick={() =>
                      navigate(
                        `/main/family-group/${groupData.id}/user/${member.id}`
                      )
                    }
                    actionElement={
                      isHeadChef && !member.isCurrentUser ? (
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleMemberMenu(member.id)
                            }}
                            className="rounded-full p-1 text-gray-400 transition-colors hover:text-gray-600"
                          >
                            <MoreVertical size={20} />
                          </button>
                          {openMemberMenuId === member.id && (
                            <div className="absolute right-0 top-full z-10 mt-1 w-52 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  navigate(
                                    `/main/family-group/${groupData.id}/user/${member.id}`
                                  )
                                }}
                                className="flex w-full items-center px-4 py-2 text-left text-sm font-medium text-gray-700 hover:bg-gray-100"
                              >
                                <User size={16} className="mr-2" /> Xem thông
                                tin
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setSelectedMemberForLeader(member)
                                  setIsSetLeaderModalOpen(true)
                                }}
                                className="flex w-full items-center px-4 py-2 text-left text-sm font-medium text-gray-700 hover:bg-gray-100"
                              >
                                <Shield size={16} className="mr-2" /> Đặt làm
                                nhóm trưởng
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setSelectedMemberForRemoval(member)
                                  setIsRemoveMemberModalOpen(true)
                                }}
                                className="flex w-full items-center px-4 py-2 text-left text-sm font-medium text-red-600 hover:bg-gray-100"
                              >
                                <LogOut size={16} className="mr-2" /> Xóa khỏi
                                nhóm
                              </button>
                            </div>
                          )}
                        </div>
                      ) : undefined
                    }
                  />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'shopping-plan' && (
            <div className="relative flex min-h-[400px] flex-col items-center pb-24 pt-2">
              {/* Filter Buttons */}
              <div className="mb-6 flex w-full justify-between gap-2 px-1">
                {[
                  { id: 'today', label: 'Hôm nay' },
                  { id: 'week', label: 'Tuần này' },
                  { id: 'month', label: 'Tháng này' }
                ].map((filter) => {
                  const inRange = isFilterInRange(filter.id as TimeFilterType)
                  const isActive = timeFilter === filter.id && inRange
                  return (
                    <button
                      key={filter.id}
                      onClick={() =>
                        handleTimeFilterChange(filter.id as TimeFilterType)
                      }
                      className={`
                        flex-1 rounded-lg px-2 py-1.5 text-sm font-semibold transition-colors
                        ${
                          isActive
                            ? 'bg-[#C3485C] text-white shadow-md'
                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                        }
                      `}
                    >
                      {filter.label}
                    </button>
                  )
                })}
              </div>

              {/* Calendar Strip */}
              <div className="mb-6 w-full">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      const newDate = new Date(selectedDate)
                      newDate.setDate(newDate.getDate() - 1)
                      setSelectedDate(newDate)
                    }}
                    className="shrink-0 rounded-full p-2 transition-colors hover:bg-gray-100"
                  >
                    <ChevronLeft size={24} className="text-gray-600" />
                  </button>

                  <div
                    ref={calendarScrollRef}
                    className="scrollbar-hide flex flex-1 snap-x snap-center items-center gap-2 overflow-x-auto"
                  >
                    {weekDates.map((day, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedDate(day.fullDate)}
                        data-selected={day.active ? 'true' : 'false'}
                        className="flex shrink-0 snap-center flex-col items-center transition-transform active:scale-95"
                      >
                        {day.active ? (
                          <div className="flex h-[5.0rem] w-14 cursor-pointer flex-col items-center justify-between rounded-xl bg-[#C3485C] py-2 shadow-lg shadow-red-100">
                            <span className="text-[10px] font-medium text-white">
                              {day.label}
                            </span>
                            <div className="flex size-8 items-center justify-center rounded-full bg-[#F8EFCE]">
                              <span className="text-sm font-bold text-[#C3485C]">
                                {day.date}
                              </span>
                            </div>
                            <span className="mt-1 text-[10px] font-medium text-white">
                              Tháng {day.fullDate.getMonth() + 1}
                            </span>
                          </div>
                        ) : day.isToday ? (
                          <div className="mt-6 flex size-10 cursor-pointer items-center justify-center rounded-full border border-[#F8EFCE] bg-[#F8EFCE] shadow-sm transition-colors hover:border-[#ffdcc4] hover:bg-[#ffdcc4]">
                            <span className="text-sm font-bold text-[#C3485C]">
                              {day.date}
                            </span>
                          </div>
                        ) : (
                          <div className="mt-6 flex size-10 cursor-pointer items-center justify-center rounded-full border border-gray-100 bg-white shadow-sm transition-colors hover:border-gray-200 hover:bg-gray-50">
                            <span className="text-sm font-bold text-gray-900">
                              {day.date}
                            </span>
                          </div>
                        )}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => {
                      const newDate = new Date(selectedDate)
                      newDate.setDate(newDate.getDate() + 1)
                      setSelectedDate(newDate)
                    }}
                    className="shrink-0 rounded-full p-2 transition-colors hover:bg-gray-100"
                  >
                    <ChevronRight size={24} className="text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Plans List */}
              <div className="w-full">
                {isPlansLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="size-8 animate-spin rounded-full border-b-2 border-[#C3485C]"></div>
                  </div>
                ) : plansError ? (
                  <div className="px-6 py-8 text-center">
                    <p className="text-sm text-red-500">{plansError}</p>
                  </div>
                ) : shoppingPlans.length === 0 ? (
                  <div className="w-full px-6 py-8 text-center">
                    <p className="text-sm leading-relaxed text-gray-800">
                      Nhóm chưa có kế hoạch mua sắm nào cả. Hãy tạo kế hoạch
                      mua sắm mới!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {shoppingPlans.map((plan) => (
                      <div
                        key={plan.plan_id}
                        className="cursor-pointer rounded-xl border border-gray-100 bg-white p-4 shadow-sm transition-all hover:shadow-md"
                        onClick={() =>
                          navigate(
                            `/main/family-group/${groupData.id}/plan/${plan.plan_id}`
                          )
                        }
                      >
                        <div className="mb-2 flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-base font-bold text-gray-900">
                              {(plan.others?.name as string) || 'Kế hoạch mua sắm'}
                            </p>
                            <p className="mt-1 text-xs text-gray-500">
                              {getUserNameById(plan.assigner_id)}
                            </p>
                            <p className="mt-1 text-xs text-gray-500">
                              {plan.shopping_list.length} nguyên liệu • {' '}
                              {new Date(plan.deadline).toLocaleDateString(
                                'vi-VN',
                                {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                }
                              )}
                            </p>
                          </div>
                          {renderStatusBadge(plan.plan_status)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Floating Action Button for Create Plan */}
              <div className="mt-4">
                <Button
                  variant="primary"
                  size="fit"
                  icon={Plus}
                  onClick={handleCreatePlan}
                >
                  Tạo kế hoạch mới
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* DELETE CONFIRMATION MODAL */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm">
          <div
            className="w-full max-w-[320px] rounded-2xl bg-white p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-5 text-center text-lg font-bold text-gray-900">
              Xóa Nhóm Gia Đình?
            </h3>
            <div className="mb-5 flex justify-center">
              <AlertTriangle
                size={64}
                className="fill-[#C3485C] text-white"
                strokeWidth={1.5}
              />
            </div>
            <p className="mb-2 text-center text-sm leading-relaxed text-gray-600">
              Hành động này{' '}
              <span className="font-semibold text-[#C3485C]">
                không thể hoàn tác
              </span>
              . Tất cả dữ liệu sẽ bị xóa.
            </p>
            {deleteError && (
              <p className="mb-4 text-center text-sm text-red-600">
                {deleteError}
              </p>
            )}
            <div className="flex justify-center gap-3">
              <div className="w-1/2">
                <Button
                  variant={isDeleting ? 'disabled' : 'primary'}
                  onClick={handleDeleteGroup}
                  icon={Trash2}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  {isDeleting ? 'Đang xóa...' : 'Xóa'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant={isDeleting ? 'disabled' : 'secondary'}
                  onClick={() => {
                    setIsDeleteModalOpen(false)
                    setDeleteError(null)
                  }}
                  icon={X}
                  className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SET LEADER MODAL */}
      {isSetLeaderModalOpen && selectedMemberForLeader && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm">
          <div
            className="w-full max-w-[320px] rounded-2xl bg-white p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-5 text-center text-lg font-bold text-gray-900">
              Đặt Làm Trưởng Nhóm?
            </h3>
            <div className="mb-5 flex justify-center">
              <Shield size={64} className="text-[#C3485C]" strokeWidth={1.5} />
            </div>
            <p className="mb-6 text-center text-sm leading-relaxed text-gray-600">
              Bạn có chắc muốn chuyển quyền trưởng nhóm cho{' '}
              <span className="font-semibold text-[#C3485C]">
                {selectedMemberForLeader.name}
              </span>
              ?
            </p>
            {setLeaderError && (
              <p className="mb-4 text-center text-sm text-red-600">
                {setLeaderError}
              </p>
            )}
            <div className="flex justify-center gap-3">
              <div className="w-1/2">
                <Button
                  variant={isSettingLeader ? 'disabled' : 'primary'}
                  onClick={handleSetLeader}
                  icon={Shield}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  {isSettingLeader ? 'Đang lưu...' : 'Xác nhận'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setIsSetLeaderModalOpen(false)
                    setSelectedMemberForLeader(null)
                    setSetLeaderError(null)
                  }}
                  icon={X}
                  className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* REMOVE MEMBER MODAL */}
      {isRemoveMemberModalOpen && selectedMemberForRemoval && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm">
          <div
            className="w-full max-w-[320px] rounded-2xl bg-white p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-5 text-center text-lg font-bold text-gray-900">
              Xóa Thành Viên?
            </h3>
            <div className="mb-5 flex justify-center">
              <AlertTriangle
                size={64}
                className="fill-[#C3485C] text-white"
                strokeWidth={1.5}
              />
            </div>
            <p className="mb-6 text-center text-sm leading-relaxed text-gray-600">
              Bạn có chắc muốn xóa{' '}
              <span className="font-semibold text-[#C3485C]">
                {selectedMemberForRemoval.name}
              </span>{' '}
              khỏi nhóm?
            </p>
            {removeMemberError && (
              <p className="mb-4 text-center text-sm text-red-600">
                {removeMemberError}
              </p>
            )}
            <div className="flex justify-center gap-3">
              <div className="w-1/2">
                <Button
                  variant={isRemovingMember ? 'disabled' : 'primary'}
                  onClick={handleRemoveMember}
                  icon={LogOut}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  {isRemovingMember ? 'Đang xóa...' : 'Xóa'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setIsRemoveMemberModalOpen(false)
                    setSelectedMemberForRemoval(null)
                    setRemoveMemberError(null)
                  }}
                  icon={X}
                  className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* LEAVE GROUP MODAL */}
      {isLeaveGroupModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm">
          <div
            className="w-full max-w-[320px] rounded-2xl bg-white p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-5 text-center text-lg font-bold text-gray-900">
              Rời Nhóm?
            </h3>
            <div className="mb-5 flex justify-center">
              <LogOut size={64} className="text-[#C3485C]" strokeWidth={1.5} />
            </div>
            <p className="mb-6 text-center text-sm leading-relaxed text-gray-600">
              Bạn có chắc muốn rời khỏi nhóm{' '}
              <span className="font-semibold text-[#C3485C]">
                {groupData.name}
              </span>
              ?
            </p>
            {leaveGroupError && (
              <p className="mb-4 text-center text-sm text-red-600">
                {leaveGroupError}
              </p>
            )}
            <div className="flex justify-center gap-3">
              <div className="w-1/2">
                <Button
                  variant={isLeavingGroup ? 'disabled' : 'primary'}
                  onClick={handleLeaveGroup}
                  icon={LogOut}
                  className="bg-[#C3485C] hover:bg-[#a83648]"
                >
                  {isLeavingGroup ? 'Đang rời...' : 'Rời nhóm'}
                </Button>
              </div>
              <div className="w-1/2">
                <Button
                  variant="secondary"
                  onClick={() => setIsLeaveGroupModalOpen(false)}
                  icon={X}
                  className="bg-[#FFD7C1] text-[#C3485C] hover:bg-[#ffc5a3]"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ADD MEMBER MODAL */}
      {isAddMemberModalOpen && (
        <div className="fixed inset-0 z-[100] overflow-y-auto">
          <div className="flex min-h-full items-center justify-center bg-black/60 px-4 backdrop-blur-sm">
            <div
              className="my-8 w-full max-w-[480px] rounded-2xl bg-white shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
                <h3 className="text-lg font-bold text-gray-900">
                  Thêm Thành Viên
                </h3>
                <button
                  onClick={handleAddMemberCancel}
                  className="rounded-full p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Modal Body - AddMember Component */}
              <div className="px-6 py-4">
                <AddMember
                  groupId={id}
                  onMemberAdded={handleMemberAdded}
                  onCancel={handleAddMemberCancel}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GroupDetail
