import React, { useState, useEffect, useMemo } from 'react'
import { Search, LayoutGrid, Check, Edit, Trash2 } from 'lucide-react'
import { UserItem } from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
import { userService } from '../services/user'
import userAvatar from '../assets/user.png'

const ITEMS_PER_PAGE = 20

type User = {
  user_id: string
  username: string
  email: string
  phone_num: string | null
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  identity_profile: unknown | null
  health_profile: unknown | null
  system_role: 'user' | 'admin'
  is_active: boolean
  created_at: string
  last_login: string | null
}

const UserManagement = () => {
  const [currentPage, setCurrentPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch users from API
  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true)
      setError(null)
      const result = await userService.getUsersList(currentPage, ITEMS_PER_PAGE)

      result.match(
        (response) => {
          setUsers(response.data.data)
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

  // Filter users based on search query
  const filteredUsers = useMemo(() => {
    if (!searchQuery) return users

    const query = searchQuery.toLowerCase()
    return users.filter((user) =>
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      (user.first_name && user.first_name.toLowerCase().includes(query)) ||
      (user.last_name && user.last_name.toLowerCase().includes(query)) ||
      (user.phone_num && user.phone_num.includes(query))
    )
  }, [users, searchQuery])

  const startIndex = users.length > 0 ? (currentPage - 1) * ITEMS_PER_PAGE + 1 : 0
  const endIndex = Math.min(currentPage * ITEMS_PER_PAGE, totalItems)

  const handleUserClick = (user: any) => {
    setSelectedUser(user)
    setViewMode('view')
  }

  const handleEditClick = () => {
    setViewMode('edit')
  }

  const handleSaveClick = () => {
    // Here you would typically save the changes
    closeModal()
  }

  const handleDeleteClick = () => {
    // Here you would typically delete the user
    closeModal()
  }

  const closeModal = () => {
    setSelectedUser(null)
    setViewMode(null)
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    setCurrentPage(1)
  }

  // Transform user data for display
  const displayUsers = useMemo(() => {
    return filteredUsers.map((user) => ({
      id: user.user_id,
      name: user.first_name && user.last_name
        ? `${user.first_name} ${user.last_name}`
        : user.username,
      username: user.username,
      email: user.email,
      phoneNumber: user.phone_num || 'N/A',
      avatar: user.avatar_url || userAvatar,
      systemRole: user.system_role,
      isActive: user.is_active,
      createdAt: new Date(user.created_at).toLocaleDateString('vi-VN'),
      lastLogin: user.last_login ? new Date(user.last_login).toLocaleDateString('vi-VN') : 'Never'
    }))
  }, [filteredUsers])

  return (
    <div className="flex min-h-screen flex-1 flex-col pt-6">
      {/* Header */}
      <div className="mb-8 flex flex-col space-y-6 px-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-800">
            Quản lý người dùng
          </h2>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Tìm kiếm..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-64 rounded-lg border border-gray-300 py-2 pl-4 pr-10 text-sm focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-600"
              />
              <Search
                className="absolute right-3 top-2.5 text-gray-400"
                size={18}
              />
            </div>
          </div>
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
                <h2 className="text-xl font-bold text-gray-800 mb-4">Thông tin người dùng</h2>
                <div className="grid grid-cols-12 gap-6 max-h-[85vh] overflow-y-auto pr-2">
                  {/* Avatar Column - spans 4 columns */}
                  <div className="col-span-4 flex flex-col items-center">
                    <img
                      src={selectedUser.avatar}
                      alt="Avatar"
                      className="w-32 h-32 rounded-full object-cover border-2 border-gray-200 mb-4"
                    />
                    <p className="text-lg font-semibold text-gray-900 text-center">{selectedUser.name}</p>
                    <p className="text-sm text-gray-500 text-center">@{selectedUser.username}</p>
                  </div>

                  {/* Info Column - spans 8 columns */}
                  <div className="col-span-8 space-y-3">
                    <div>
                      <span className="text-sm font-medium text-gray-500">ID:</span>
                      <span className="ml-2 text-sm text-gray-900">#{selectedUser.id}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Email:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.email}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Số điện thoại:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.phoneNumber}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Vai trò hệ thống:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.systemRole === 'admin' ? 'Quản trị viên' : 'Người dùng'}</span>
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
                    <div className="flex justify-end space-x-3 mt-6">
                      <Button
                        variant="primary"
                        size="fit"
                        icon={Check}
                        onClick={closeModal}
                      >
                        Quay lại
                      </Button>
                      <Button
                        variant="secondary"
                        size="fit"
                        icon={Edit}
                        onClick={handleEditClick}
                      >
                        Chỉnh sửa
                      </Button>
                      <Button
                        variant="secondary"
                        size="fit"
                        icon={Trash2}
                        onClick={handleDeleteClick}
                      >
                        Xóa
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {viewMode === 'edit' && (
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-4">Chỉnh sửa người dùng</h2>
                <div className="space-y-4 max-h-[85vh] overflow-y-auto pr-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ảnh đại diện</label>
                    <div className="flex items-center space-x-4">
                      <img
                        src={selectedUser.avatar}
                        alt="Avatar"
                        className="w-20 h-20 rounded-full object-cover border-2 border-gray-200"
                      />
                      <button className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
                        Thay đổi ảnh
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tên</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.name}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tên đăng nhập</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.username}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.email}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                    <input
                      type="tel"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.phoneNumber}
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <Button
                    variant="secondary"
                    size="fit"
                    onClick={() => setViewMode('view')}
                  >
                    Hủy
                  </Button>
                  <Button
                    variant="primary"
                    size="fit"
                    onClick={handleSaveClick}
                  >
                    Lưu
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default UserManagement