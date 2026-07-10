import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  MoreVertical,
  User,
  Shield,
  LogOut,
  AlertTriangle,
  X,
  UserPlus,
  Trash2
} from 'lucide-react'
import { Button } from '../../../components/Button'
import { UserCard } from '../../../components/UserCard'
import AddMember from './AddMember'
import { groupService } from '../../../services/group'

interface GroupDetailMembersProps {
  groupData: {
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
  }
  isHeadChef: boolean
  onRefresh: () => void
}

type MemberType = {
  id: string
  name: string
  role: string
  email?: string
  isCurrentUser: boolean
}

const GroupDetailMembers: React.FC<GroupDetailMembersProps> = ({
  groupData,
  isHeadChef,
  onRefresh
}) => {
  const navigate = useNavigate()
  const id = groupData.id

  // Modal States
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [isSetLeaderModalOpen, setIsSetLeaderModalOpen] = useState(false)
  const [selectedMemberForLeader, setSelectedMemberForLeader] =
    useState<MemberType | null>(null)
  const [isRemoveMemberModalOpen, setIsRemoveMemberModalOpen] = useState(false)
  const [selectedMemberForRemoval, setSelectedMemberForRemoval] =
    useState<MemberType | null>(null)
  const [isLeaveGroupModalOpen, setIsLeaveGroupModalOpen] = useState(false)
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false)

  // Loading and error states
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [isSettingLeader, setIsSettingLeader] = useState(false)
  const [setLeaderError, setSetLeaderError] = useState<string | null>(null)
  const [isRemovingMember, setIsRemovingMember] = useState(false)
  const [removeMemberError, setRemoveMemberError] = useState<string | null>(
    null
  )
  const [isLeavingGroup, setIsLeavingGroup] = useState(false)
  const [leaveGroupError, setLeaveGroupError] = useState<string | null>(null)

  // Menu state
  const [openMemberMenuId, setOpenMemberMenuId] = useState<string | null>(null)

  // Manage bottom nav blur effect
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

  const toggleMemberMenu = (id: string) => {
    setOpenMemberMenuId(openMemberMenuId === id ? null : id)
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
            onRefresh()
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
        setIsRemoveMemberModalOpen(false)
        setSelectedMemberForRemoval(null)
        setOpenMemberMenuId(null)
        // Refresh to reflect member removal
        onRefresh()
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

  const handleOpenAddMemberModal = () => {
    setIsAddMemberModalOpen(true)
  }

  const handleMemberAdded = async () => {
    onRefresh()
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
    if (openMemberMenuId) setOpenMemberMenuId(null)
  }

  return (
    <div onClick={handleBackdropClick}>
      {/* Add Member Button */}
      <div className="mb-4 flex justify-center">
        {isHeadChef && (
          <Button
            variant="primary"
            size="fit"
            icon={UserPlus}
            onClick={handleOpenAddMemberModal}
          >
            Thêm thành viên
          </Button>
        )}
      </div>

      {/* Members List */}
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
              avatarSrc={member.avatar || undefined}
              variant="selected"
              onClick={() =>
                navigate(`/main/family-group/${groupData.id}/user/${member.id}`)
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
                          <User size={16} className="mr-2" /> Xem thông tin
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedMemberForLeader(member)
                            setIsSetLeaderModalOpen(true)
                          }}
                          className="flex w-full items-center px-4 py-2 text-left text-sm font-medium text-gray-700 hover:bg-gray-100"
                        >
                          <Shield size={16} className="mr-2" /> Đặt làm nhóm
                          trưởng
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedMemberForRemoval(member)
                            setIsRemoveMemberModalOpen(true)
                          }}
                          className="flex w-full items-center px-4 py-2 text-left text-sm font-medium text-red-600 hover:bg-gray-100"
                        >
                          <LogOut size={16} className="mr-2" /> Xóa khỏi nhóm
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

      {/* DELETE GROUP MODAL */}
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
                  groupId={groupData.id}
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

export default GroupDetailMembers
