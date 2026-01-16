import React, { useState, useEffect } from 'react'
import { LayoutGrid, Edit, Trash2, Lock, User, Activity, Plus, X, Save } from 'lucide-react'
import { UserItem } from '../components/Item'
import { Button } from '../components/Button'
import { InputField } from '../components/InputField'
import { DropdownInputField } from '../components/DropDownInputField'
import { Pagination } from '../components/Pagination'
import { userService } from '../services/user'
import userAvatar from '../assets/user.png'

const ITEMS_PER_PAGE = 10

type User = {
  user_id: string
  username: string
  email: string
  phone_num: string | null
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  identity_profile: UserIdentityProfile | null
  health_profile: UserHealthProfile | null
  system_role: 'user' | 'admin'
  is_active: boolean
  created_at: string
  last_login: string | null
}

type UserIdentityProfile = {
  gender?: 'male' | 'female' | 'other' | null
  date_of_birth?: string | null
  occupation?: string | null
  address?: {
    ward?: string | null
    district?: string | null
    city?: string | null
    province?: string | null
  } | null
}

type UserHealthProfile = {
  height_cm?: number | null
  weight_kg?: number | null
  activity_level?: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active' | null
  curr_condition?: 'normal' | 'pregnant' | 'injured' | null
  health_goal?: 'lose_weight' | 'maintain' | 'gain_weight' | null
}

type TabType = 'personal' | 'health' | 'login'

const UserManagement = () => {
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('personal')
  const [identityProfile, setIdentityProfile] = useState<UserIdentityProfile | null>(null)
  const [healthProfile, setHealthProfile] = useState<UserHealthProfile | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [loading, setLoading] = useState(true)
  const [userDetailLoading, setUserDetailLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Add user modal state
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false)
  const [isCreatingUser, setIsCreatingUser] = useState(false)
  const [createUserError, setCreateUserError] = useState<string | null>(null)
  const [isDeletingUser, setIsDeletingUser] = useState(false)
  const [deleteUserError, setDeleteUserError] = useState<string | null>(null)
  const [newUserForm, setNewUserForm] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_num: '',
    is_active: true,
    system_role: 'user' as 'user' | 'admin'
  })
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  // Edit user state
  const [isEditing, setIsEditing] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [updateError, setUpdateError] = useState<string | null>(null)
  const [editForm, setEditForm] = useState({
    username: '',
    first_name: '',
    last_name: '',
    phone_num: '',
    system_role: 'user' as 'user' | 'admin',
    is_active: true,
    // Identity profile
    gender: '' as 'male' | 'female' | 'other' | '',
    date_of_birth: '',
    occupation: '',
    ward: '',
    district: '',
    city: '',
    province: '',
    // Health profile
    height_cm: '',
    weight_kg: '',
    activity_level: '' as 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active' | '',
    curr_condition: '' as 'normal' | 'pregnant' | 'injured' | '',
    health_goal: '' as 'lose_weight' | 'maintain' | 'gain_weight' | ''
  })

  // Fetch users from API
  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true)
      setError(null)
      const result = await userService.getUsersList(currentPage, ITEMS_PER_PAGE)

      result.match(
        (response) => {
          // Transform API response to match our User type
          const users = response.data.data.map((user: any) => ({
            ...user,
            identity_profile: user.identity_profile as UserIdentityProfile | null,
            health_profile: user.health_profile as UserHealthProfile | null
          }))
          setUsers(users)
          setTotalPages(response.data.total_pages)
          setTotalItems(response.data.total_items)
          setLoading(false)
        },
        (err) => {
          console.error('Failed to fetch users:', err)
          setError('Failed to load users. Please try again.')
          setLoading(false)
        }
      )
    }

    fetchUsers()
  }, [currentPage])

  const startIndex = users.length > 0 ? (currentPage - 1) * ITEMS_PER_PAGE + 1 : 0
  const endIndex = Math.min(currentPage * ITEMS_PER_PAGE, totalItems)

  const handleUserClick = async (user: any) => {
    // Set basic info from the list while fetching full details
    setSelectedUser(user)
    setViewMode('view')
    setActiveTab('personal')
    setDeleteUserError(null)
    setUserDetailLoading(true)

    // Fetch full user details including identity_profile and health_profile
    const result = await userService.getUserById(user.id || user.user_id)

    result.match(
      (response) => {
        const userData = response.data as any
        // Transform the user data for display
        const transformedUser = {
          id: userData.user_id,
          name: userData.first_name && userData.last_name
            ? `${userData.first_name} ${userData.last_name}`
            : userData.username,
          username: userData.username,
          email: userData.email,
          phoneNumber: userData.phone_num || 'Chưa có thông tin',
          avatar: userData.avatar_url || userAvatar,
          systemRole: userData.system_role,
          isActive: userData.is_active,
          createdAt: new Date(userData.created_at).toLocaleDateString('vi-VN'),
          lastLogin: userData.last_login ? new Date(userData.last_login).toLocaleDateString('vi-VN') : 'Never',
          // Keep original data for reference
          ...userData
        }
        setSelectedUser(transformedUser)
        setIdentityProfile(userData.identity_profile || null)
        setHealthProfile(userData.health_profile || null)
        setUserDetailLoading(false)
      },
      (err) => {
        console.error('Failed to fetch user details:', err)
        // Fall back to using the data from the list
        setIdentityProfile(user.identity_profile || null)
        setHealthProfile(user.health_profile || null)
        setUserDetailLoading(false)
      }
    )
  }

  const handleEditClick = () => {
    setIsEditing(true)
    setUpdateError(null)
    setDeleteUserError(null)
    // Initialize edit form with current user data
    setEditForm({
      username: selectedUser.username || '',
      first_name: selectedUser.first_name || '',
      last_name: selectedUser.last_name || '',
      phone_num: selectedUser.phone_num || '',
      system_role: selectedUser.system_role || 'user',
      is_active: selectedUser.is_active ?? true,
      gender: identityProfile?.gender || '',
      date_of_birth: identityProfile?.date_of_birth || '',
      occupation: identityProfile?.occupation || '',
      ward: identityProfile?.address?.ward || '',
      district: identityProfile?.address?.district || '',
      city: identityProfile?.address?.city || '',
      province: identityProfile?.address?.province || '',
      height_cm: healthProfile?.height_cm?.toString() || '',
      weight_kg: healthProfile?.weight_kg?.toString() || '',
      activity_level: healthProfile?.activity_level || '',
      curr_condition: healthProfile?.curr_condition || '',
      health_goal: healthProfile?.health_goal || ''
    })
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setUpdateError(null)
  }

  const handleSaveClick = async () => {
    if (!selectedUser?.id) return

    setIsUpdating(true)
    setUpdateError(null)

    // Build update data - only include fields that have values
    const updateData: any = {
      system_role: editForm.system_role,
      is_active: editForm.is_active
    }

    // Personal tab fields - only include if not empty
    if (editForm.username) updateData.username = editForm.username
    if (editForm.first_name) updateData.first_name = editForm.first_name
    if (editForm.last_name) updateData.last_name = editForm.last_name
    if (editForm.phone_num) updateData.phone_num = editForm.phone_num

    // Identity profile - only include fields that have values
    const identityProfile: any = {}
    if (editForm.gender) identityProfile.gender = editForm.gender
    if (editForm.date_of_birth) identityProfile.date_of_birth = editForm.date_of_birth
    if (editForm.occupation) identityProfile.occupation = editForm.occupation

    // Address - only include fields that have values
    const address: any = {}
    if (editForm.ward) address.ward = editForm.ward
    if (editForm.district) address.district = editForm.district
    if (editForm.city) address.city = editForm.city
    if (editForm.province) address.province = editForm.province
    if (Object.keys(address).length > 0) {
      identityProfile.address = address
    }
    if (Object.keys(identityProfile).length > 0) {
      updateData.identity_profile = identityProfile
    }

    // Health profile - only include fields that have values
    const healthProfile: any = {}
    if (editForm.height_cm) healthProfile.height_cm = parseFloat(editForm.height_cm)
    if (editForm.weight_kg) healthProfile.weight_kg = parseFloat(editForm.weight_kg)
    if (editForm.activity_level) healthProfile.activity_level = editForm.activity_level
    if (editForm.curr_condition) healthProfile.curr_condition = editForm.curr_condition
    if (editForm.health_goal) healthProfile.health_goal = editForm.health_goal
    if (Object.keys(healthProfile).length > 0) {
      updateData.health_profile = healthProfile
    }


    const result = await userService.updateUser(selectedUser.id, updateData)

    result.match(
      () => {
        setIsUpdating(false)
        setIsEditing(false)
        // Refresh the user details
        const fetchUserDetails = async () => {
          const userResult = await userService.getUserById(selectedUser.id)
          userResult.match(
            (userData) => {
              const transformedUser = {
                ...userData.data,
                id: userData.data.user_id,
                name: userData.data.first_name && userData.data.last_name
                  ? `${userData.data.first_name} ${userData.data.last_name}`
                  : userData.data.username,
                phoneNumber: userData.data.phone_num || 'Chưa có thông tin',
                avatar: userData.data.avatar_url || userAvatar,
                systemRole: userData.data.system_role,
                isActive: userData.data.is_active,
                createdAt: new Date(userData.data.created_at).toLocaleDateString('vi-VN'),
                lastLogin: userData.data.last_login ? new Date(userData.data.last_login).toLocaleDateString('vi-VN') : 'Never'
              }
              setSelectedUser(transformedUser)
              setIdentityProfile(userData.data.identity_profile || null)
              setHealthProfile(userData.data.health_profile || null)
            },
            () => {}
          )
        }
        fetchUserDetails()
        // Refresh the user list
        const fetchUsers = async () => {
          setLoading(true)
          const listResult = await userService.getUsersList(currentPage, ITEMS_PER_PAGE)
          listResult.match(
            (response) => {
              const users = response.data.data.map((user: any) => ({
                ...user,
                identity_profile: user.identity_profile as UserIdentityProfile | null,
                health_profile: user.health_profile as UserHealthProfile | null
              }))
              setUsers(users)
              setTotalPages(response.data.total_pages)
              setTotalItems(response.data.total_items)
              setLoading(false)
            },
            () => setLoading(false)
          )
        }
        fetchUsers()
      },
      (error) => {
        setIsUpdating(false)
        setUpdateError(error.desc || 'Không thể cập nhật người dùng. Vui lòng thử lại.')
      }
    )
  }

  const handleDeleteClick = async () => {
    if (!selectedUser?.id) return

    setIsDeletingUser(true)
    setDeleteUserError(null)

    const result = await userService.deleteUser(selectedUser.id)

    result.match(
      () => {
        setIsDeletingUser(false)
        closeModal()
        // Refresh the user list
        const fetchUsers = async () => {
          setLoading(true)
          const listResult = await userService.getUsersList(currentPage, ITEMS_PER_PAGE)
          listResult.match(
            (response) => {
              const users = response.data.data.map((user: any) => ({
                ...user,
                identity_profile: user.identity_profile as UserIdentityProfile | null,
                health_profile: user.health_profile as UserHealthProfile | null
              }))
              setUsers(users)
              setTotalPages(response.data.total_pages)
              setTotalItems(response.data.total_items)
              setLoading(false)
            },
            () => setLoading(false)
          )
        }
        fetchUsers()
      },
      (error) => {
        setIsDeletingUser(false)
        setDeleteUserError(error.desc || 'Không thể xóa người dùng. Vui lòng thử lại.')
      }
    )
  }

  const closeModal = () => {
    setSelectedUser(null)
    setViewMode(null)
    setActiveTab('personal')
    setUserDetailLoading(false)
    setIsEditing(false)
    setUpdateError(null)
  }

  // Add user modal handlers
  const openAddUserModal = () => {
    setIsAddUserModalOpen(true)
    setCreateUserError(null)
    setFormErrors({})
    setNewUserForm({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      phone_num: '',
      is_active: true,
      system_role: 'user'
    })
  }

  const closeAddUserModal = () => {
    setIsAddUserModalOpen(false)
    setCreateUserError(null)
    setFormErrors({})
    setNewUserForm({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      phone_num: '',
      is_active: true,
      system_role: 'user'
    })
  }

  const validateCreateUserForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!newUserForm.username.trim()) {
      errors.username = 'Vui lòng nhập tên đăng nhập'
    }
    if (!newUserForm.email.trim()) {
      errors.email = 'Vui lòng nhập email'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newUserForm.email)) {
      errors.email = 'Email không hợp lệ'
    }
    if (!newUserForm.password.trim()) {
      errors.password = 'Vui lòng nhập mật khẩu'
    } else if (newUserForm.password.length < 6) {
      errors.password = 'Mật khẩu phải có ít nhất 6 ký tự'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleCreateUser = async () => {
    if (!validateCreateUserForm()) return

    setIsCreatingUser(true)
    setCreateUserError(null)

    const result = await userService.createUser({
      username: newUserForm.username.trim(),
      email: newUserForm.email.trim(),
      password: newUserForm.password.trim(),
      first_name: newUserForm.first_name.trim() || undefined,
      last_name: newUserForm.last_name.trim() || undefined,
      phone_num: newUserForm.phone_num.trim() || undefined,
      is_active: newUserForm.is_active,
      system_role: newUserForm.system_role
    })

    result.match(
      () => {
        setIsCreatingUser(false)
        closeAddUserModal()
        // Refresh the user list
        setCurrentPage(1)
        // Trigger a refetch
        const fetchUsers = async () => {
          setLoading(true)
          const listResult = await userService.getUsersList(1, ITEMS_PER_PAGE)
          listResult.match(
            (response) => {
              const users = response.data.data.map((user: any) => ({
                ...user,
                identity_profile: user.identity_profile as UserIdentityProfile | null,
                health_profile: user.health_profile as UserHealthProfile | null
              }))
              setUsers(users)
              setTotalPages(response.data.total_pages)
              setTotalItems(response.data.total_items)
              setLoading(false)
            },
            () => setLoading(false)
          )
        }
        fetchUsers()
      },
      (error) => {
        setIsCreatingUser(false)
        setCreateUserError(error.desc || 'Không thể tạo người dùng. Vui lòng thử lại.')
      }
    )
  }

  // Transform user data for display
  const displayUsers = users.map((user) => ({
    ...user, // Preserve all original user data including identity_profile and health_profile
    id: user.user_id,
    name: user.first_name && user.last_name
      ? `${user.first_name} ${user.last_name}`
      : user.username,
    username: user.username,
    email: user.email,
    phoneNumber: user.phone_num || 'Chưa có thông tin',
    avatar: user.avatar_url || userAvatar,
    systemRole: user.system_role,
    isActive: user.is_active,
    createdAt: new Date(user.created_at).toLocaleDateString('vi-VN'),
    lastLogin: user.last_login ? new Date(user.last_login).toLocaleDateString('vi-VN') : 'Never'
  }))

  const formatAddress = (address: NonNullable<UserIdentityProfile['address']>): string => {
    if (!address) return ''
    const parts = [address.ward, address.district, address.city, address.province].filter(Boolean)
    return parts.join(', ')
  }

  return (
    <div className="flex min-h-screen flex-1 flex-col pt-6">
      {/* Header */}
      <div className="mb-8 flex flex-col space-y-6 px-6">
        <div className="flex items-center">
          <h2 className="text-xl font-bold text-gray-800 flex-1">
            Quản lý người dùng
          </h2>

          <Button
            variant="primary"
            size="fit"
            icon={Plus}
            onClick={openAddUserModal}
          >
            Thêm người dùng
          </Button>
        </div>

        <div className="flex items-center justify-end text-sm text-gray-600">
          <LayoutGrid size={16} className="mr-2" />
          <span>
            Đang hiển thị{' '}
            <span className="font-bold">
              {startIndex} - {endIndex}
            </span>{' '}
            / {totalItems} người dùng
          </span>
        </div>
      </div>

      {/* Grid Container - Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="px-6 flex h-64 items-center justify-center text-gray-500">
            Đang tải...
          </div>
        ) : error ? (
          <div className="px-6 flex h-64 items-center justify-center text-red-500">
            {error}
          </div>
        ) : displayUsers.length > 0 ? (
          <div className="px-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {displayUsers.map((user) => (
              <UserItem
                key={user.id}
                name={user.name}
                username={user.username}
                email={user.email}
                image={user.avatar}
                onClick={() => handleUserClick(user)}
              />
            ))}
          </div>
        ) : (
          <div className="px-6 flex h-64 items-center justify-center text-gray-500">
            Không tìm thấy người dùng nào.
          </div>
        )}
      </div>

      {/* Pagination - Always at Bottom */}
      <div className="sticky bottom-0 bg-white px-6 py-4">
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          className=""
        />
      </div>

      
      {/* View/Edit User Modal */}
      {selectedUser && viewMode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Background overlay */}
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={closeModal}
          />

          {/* Form container */}
          <div className="relative z-10 bg-white rounded-lg p-6 w-full max-w-2xl">
            {viewMode === 'view' && (
              <div>
                {userDetailLoading ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#C3485C] mb-4"></div>
                    <p className="text-gray-500 text-sm">Đang tải thông tin...</p>
                  </div>
                ) : (
                  <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-800">Thông tin người dùng</h2>
                  <button
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* User Header with Avatar */}
                <div className="flex flex-col items-center mb-6">
                  <img
                    src={selectedUser.avatar}
                    alt="Avatar"
                    className="w-24 h-24 rounded-full object-cover border-2 border-gray-200 mb-3"
                  />
                  <p className="text-lg font-semibold text-gray-900 text-center">{selectedUser.name}</p>
                  <p className="text-sm text-gray-500 text-center">@{selectedUser.username}</p>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 mb-6">
                  <button
                    onClick={() => setActiveTab('personal')}
                    className={`flex items-center justify-center gap-2 flex-1 px-4 py-3 font-medium text-sm transition-colors ${
                      activeTab === 'personal'
                        ? 'text-[#C3485C] border-b-2 border-[#C3485C]'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <User size={16} />
                    Hồ sơ cá nhân
                  </button>
                  <button
                    onClick={() => setActiveTab('health')}
                    className={`flex items-center justify-center gap-2 flex-1 px-4 py-3 font-medium text-sm transition-colors ${
                      activeTab === 'health'
                        ? 'text-[#C3485C] border-b-2 border-[#C3485C]'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Activity size={16} />
                    Hồ sơ sức khỏe
                  </button>
                  <button
                    onClick={() => setActiveTab('login')}
                    className={`flex items-center justify-center gap-2 flex-1 px-4 py-3 font-medium text-sm transition-colors ${
                      activeTab === 'login'
                        ? 'text-[#C3485C] border-b-2 border-[#C3485C]'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Lock size={16} />
                    Thông tin đăng nhập
                  </button>
                </div>

                {/* Tab Content */}
                <div className="max-h-[50vh] overflow-y-auto pr-2">
                  {/* Personal Profile Tab */}
                  {activeTab === 'personal' && (
                    <div className="space-y-4">
                      {isEditing ? (
                        <>
                          <InputField
                            label="Họ"
                            value={editForm.first_name}
                            onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                          />
                          <InputField
                            label="Tên"
                            value={editForm.last_name}
                            onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                          />
                          <InputField
                            label="Số điện thoại"
                            type="tel"
                            value={editForm.phone_num}
                            onChange={(e) => setEditForm({ ...editForm, phone_num: e.target.value })}
                          />
                          <div>
                            <DropdownInputField
                              label="Giới tính"
                              options={[
                                { value: '', label: 'Chưa có thông tin' },
                                { value: 'male', label: 'Nam' },
                                { value: 'female', label: 'Nữ' },
                                { value: 'other', label: 'Khác' }
                              ]}
                              value={editForm.gender}
                              onChange={(value) => setEditForm({ ...editForm, gender: value as any })}
                              placeholder="Chọn giới tính"
                            />
                          </div>
                          <InputField
                            label="Ngày sinh"
                            type="date"
                            value={editForm.date_of_birth}
                            onChange={(e) => setEditForm({ ...editForm, date_of_birth: e.target.value })}
                          />
                          <InputField
                            label="Nghề nghiệp"
                            value={editForm.occupation}
                            onChange={(e) => setEditForm({ ...editForm, occupation: e.target.value })}
                          />
                          <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Địa chỉ</label>
                            <InputField
                              placeholder="Phường/Xã"
                              value={editForm.ward}
                              onChange={(e) => setEditForm({ ...editForm, ward: e.target.value })}
                              containerClassName="space-y-0"
                            />
                            <InputField
                              placeholder="Quận/Huyện"
                              value={editForm.district}
                              onChange={(e) => setEditForm({ ...editForm, district: e.target.value })}
                              containerClassName="space-y-0"
                            />
                            <InputField
                              placeholder="Thành phố"
                              value={editForm.city}
                              onChange={(e) => setEditForm({ ...editForm, city: e.target.value })}
                              containerClassName="space-y-0"
                            />
                            <InputField
                              placeholder="Tỉnh"
                              value={editForm.province}
                              onChange={(e) => setEditForm({ ...editForm, province: e.target.value })}
                              containerClassName="space-y-0"
                            />
                          </div>
                        </>
                      ) : (
                        <>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Họ và tên:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.name}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Số điện thoại:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {selectedUser.phoneNumber !== 'Chưa có thông tin' ? selectedUser.phoneNumber : 'Chưa có thông tin'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Giới tính:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {identityProfile?.gender
                                ? identityProfile.gender === 'male' ? 'Nam' : identityProfile.gender === 'female' ? 'Nữ' : 'Khác'
                                : 'Chưa có thông tin'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Ngày sinh:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {identityProfile?.date_of_birth || 'Chưa có thông tin'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Nghề nghiệp:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {identityProfile?.occupation || 'Chưa có thông tin'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Địa chỉ:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {identityProfile?.address ? (formatAddress(identityProfile.address) || 'Chưa có thông tin') : 'Chưa có thông tin'}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* Health Profile Tab */}
                  {activeTab === 'health' && (
                    <div className="space-y-6">
                      {isEditing ? (
                        <>
                          <InputField
                            label="Chiều cao (cm)"
                            type="number"
                            value={editForm.height_cm}
                            onChange={(e) => setEditForm({ ...editForm, height_cm: e.target.value })}
                            placeholder="Nhập chiều cao"
                          />
                          <InputField
                            label="Cân nặng (kg)"
                            type="number"
                            step="0.1"
                            value={editForm.weight_kg}
                            onChange={(e) => setEditForm({ ...editForm, weight_kg: e.target.value })}
                            placeholder="Nhập cân nặng"
                          />
                          <div>
                            <DropdownInputField
                              label="Cường độ vận động hàng ngày"
                              options={[
                                { value: '', label: 'Chưa có thông tin' },
                                { value: 'sedentary', label: 'Ít vận động' },
                                { value: 'light', label: 'Vận động nhẹ' },
                                { value: 'moderate', label: 'Vận động vừa' },
                                { value: 'active', label: 'Vận động tích cực' },
                                { value: 'very_active', label: 'Vận động rất tích cực' }
                              ]}
                              value={editForm.activity_level}
                              onChange={(value) => setEditForm({ ...editForm, activity_level: value as any })}
                              placeholder="Chọn cường độ vận động"
                            />
                          </div>
                          <div>
                            <DropdownInputField
                              label="Tình trạng hiện tại"
                              options={[
                                { value: '', label: 'Chưa có thông tin' },
                                { value: 'normal', label: 'Bình thường' },
                                { value: 'pregnant', label: 'Mang thai' },
                                { value: 'injured', label: 'Chấn thương' }
                              ]}
                              value={editForm.curr_condition}
                              onChange={(value) => setEditForm({ ...editForm, curr_condition: value as any })}
                              placeholder="Chọn tình trạng"
                            />
                          </div>
                          <div>
                            <DropdownInputField
                              label="Mục tiêu sức khỏe"
                              options={[
                                { value: '', label: 'Chưa có thông tin' },
                                { value: 'lose_weight', label: 'Giảm cân' },
                                { value: 'maintain', label: 'Duy trì' },
                                { value: 'gain_weight', label: 'Tăng cân' }
                              ]}
                              value={editForm.health_goal}
                              onChange={(value) => setEditForm({ ...editForm, health_goal: value as any })}
                              placeholder="Chọn mục tiêu"
                            />
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="flex items-center gap-4">
                            <span className="text-sm font-medium text-gray-700 w-32">Chiều cao:</span>
                            <span className="text-sm text-gray-900">
                              {healthProfile?.height_cm ? `${healthProfile.height_cm} cm` : 'Chưa có thông tin'}
                            </span>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-sm font-medium text-gray-700 w-32">Cân nặng:</span>
                            <span className="text-sm text-gray-900">
                              {healthProfile?.weight_kg ? `${healthProfile.weight_kg} kg` : 'Chưa có thông tin'}
                            </span>
                          </div>
                          <div>
                            <h3 className="text-sm font-medium text-gray-700 mb-3">Cường độ vận động hàng ngày</h3>
                            <p className="text-sm text-gray-900">
                              {healthProfile?.activity_level
                                ? healthProfile.activity_level === 'sedentary' ? 'Ít vận động'
                                : healthProfile.activity_level === 'light' ? 'Vận động nhẹ'
                                : healthProfile.activity_level === 'moderate' ? 'Vận động vừa'
                                : healthProfile.activity_level === 'active' ? 'Vận động tích cực'
                                : 'Vận động rất tích cực'
                                : 'Chưa có thông tin'}
                            </p>
                          </div>
                          <div>
                            <h3 className="text-sm font-medium text-gray-700 mb-3">Tình trạng hiện tại</h3>
                            <p className="text-sm text-gray-900">
                              {healthProfile?.curr_condition
                                ? healthProfile.curr_condition === 'normal' ? 'Bình thường'
                                : healthProfile.curr_condition === 'pregnant' ? 'Mang thai'
                                : 'Chấn thương'
                                : 'Chưa có thông tin'}
                            </p>
                          </div>
                          <div>
                            <h3 className="text-sm font-medium text-gray-700 mb-3">Mục tiêu sức khỏe</h3>
                            <p className="text-sm text-gray-900">
                              {healthProfile?.health_goal
                                ? healthProfile.health_goal === 'lose_weight' ? 'Giảm cân'
                                : healthProfile.health_goal === 'maintain' ? 'Duy trì'
                                : 'Tăng cân'
                                : 'Chưa có thông tin'}
                            </p>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* Login Information Tab */}
                  {activeTab === 'login' && (
                    <div className="space-y-4">
                      {isEditing ? (
                        <>
                          <InputField
                            label="Tên đăng nhập"
                            value={editForm.username}
                            onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                          />
                          <InputField
                            label="Email"
                            type="email"
                            value={selectedUser.email}
                            disabled
                          />
                          <div>
                            <DropdownInputField
                              label="Vai trò hệ thống"
                              options={[
                                { value: 'user', label: 'Người dùng' },
                                { value: 'admin', label: 'Quản trị viên' }
                              ]}
                              value={editForm.system_role}
                              onChange={(value) => setEditForm({ ...editForm, system_role: value as 'user' | 'admin' })}
                              placeholder="Chọn vai trò"
                            />
                          </div>
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              id="edit_is_active"
                              checked={editForm.is_active}
                              onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <label htmlFor="edit_is_active" className="ml-2 text-sm text-gray-700">
                              Kích hoạt tài khoản
                            </label>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">ID:</span>
                            <span className="ml-2 text-sm text-gray-900">#{selectedUser.id}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Ngày tạo:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.createdAt}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Đăng nhập lần cuối:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.lastLogin}</span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div>
                            <span className="text-sm font-medium text-gray-500">ID:</span>
                            <span className="ml-2 text-sm text-gray-900">#{selectedUser.id}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Tên đăng nhập:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.username}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Email:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.email}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Vai trò hệ thống:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {selectedUser.systemRole === 'admin' ? 'Quản trị viên' : 'Người dùng'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Trạng thái:</span>
                            <span className={`ml-2 text-sm ${selectedUser.isActive ? 'text-green-600' : 'text-red-600'}`}>
                              {selectedUser.isActive ? 'Hoạt động' : 'Vô hiệu'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Ngày tạo:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.createdAt}</span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-500">Đăng nhập lần cuối:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedUser.lastLogin}</span>
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col items-end space-y-3 mt-6 pt-4 border-t border-gray-200">
                  {(updateError || deleteUserError) && (
                    <div className="w-full p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                      {updateError || deleteUserError}
                    </div>
                  )}
                  {isEditing ? (
                    <div className="flex space-x-3">
                      <Button
                        variant={isUpdating ? 'disabled' : 'secondary'}
                        size="fit"
                        onClick={() => !isUpdating && handleCancelEdit()}
                      >
                        Hủy
                      </Button>
                      <Button
                        variant={isUpdating ? 'disabled' : 'primary'}
                        size="fit"
                        icon={Save}
                        onClick={() => !isUpdating && handleSaveClick()}
                      >
                        {isUpdating ? 'Đang lưu...' : 'Lưu'}
                      </Button>
                    </div>
                  ) : (
                    <div className="flex space-x-3">
                      <Button
                        variant="secondary"
                        size="fit"
                        icon={Edit}
                        onClick={handleEditClick}
                      >
                        Chỉnh sửa
                      </Button>
                      <Button
                        variant={isDeletingUser ? 'disabled' : 'primary'}
                        size="fit"
                        icon={Trash2}
                        onClick={() => !isDeletingUser && handleDeleteClick()}
                      >
                        {isDeletingUser ? 'Đang xóa...' : 'Xóa'}
                      </Button>
                    </div>
                  )}
                </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {isAddUserModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={closeAddUserModal}
          />
          <div className="relative z-10 bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">Thêm người dùng mới</h2>
              <button
                onClick={closeAddUserModal}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <InputField
                label="Tên đăng nhập *"
                value={newUserForm.username}
                onChange={(e) => setNewUserForm({ ...newUserForm, username: e.target.value })}
                error={formErrors.username}
                placeholder="Nhập tên đăng nhập"
              />

              <InputField
                label="Email *"
                type="email"
                value={newUserForm.email}
                onChange={(e) => setNewUserForm({ ...newUserForm, email: e.target.value })}
                error={formErrors.email}
                placeholder="nhap email@example.com"
              />

              <InputField
                label="Mật khẩu *"
                type="password"
                value={newUserForm.password}
                onChange={(e) => setNewUserForm({ ...newUserForm, password: e.target.value })}
                error={formErrors.password}
                placeholder="Nhập mật khẩu"
              />

              <InputField
                label="Họ"
                value={newUserForm.first_name}
                onChange={(e) => setNewUserForm({ ...newUserForm, first_name: e.target.value })}
                placeholder="Nhập họ"
              />

              <InputField
                label="Tên"
                value={newUserForm.last_name}
                onChange={(e) => setNewUserForm({ ...newUserForm, last_name: e.target.value })}
                placeholder="Nhập tên"
              />

              <InputField
                label="Số điện thoại"
                type="tel"
                value={newUserForm.phone_num}
                onChange={(e) => setNewUserForm({ ...newUserForm, phone_num: e.target.value })}
                placeholder="Nhập số điện thoại"
              />

              <DropdownInputField
                label="Vai trò hệ thống"
                options={[
                  { value: 'user', label: 'Người dùng' },
                  { value: 'admin', label: 'Quản trị viên' }
                ]}
                value={newUserForm.system_role}
                onChange={(value) => setNewUserForm({ ...newUserForm, system_role: value as 'user' | 'admin' })}
                placeholder="Chọn vai trò"
              />

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={newUserForm.is_active}
                  onChange={(e) => setNewUserForm({ ...newUserForm, is_active: e.target.checked })}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                  Kích hoạt tài khoản
                </label>
              </div>

              {createUserError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {createUserError}
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
              <Button
                variant="secondary"
                size="fit"
                onClick={() => !isCreatingUser && closeAddUserModal()}
              >
                Hủy
              </Button>
              <Button
                variant={isCreatingUser ? 'disabled' : 'primary'}
                size="fit"
                onClick={() => !isCreatingUser && handleCreateUser()}
              >
                {isCreatingUser ? 'Đang tạo...' : 'Tạo người dùng'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserManagement