import React, { useState, useMemo } from 'react'
import { Search, LayoutGrid, Check, Edit, Trash2 } from 'lucide-react'
import { UserItem } from '../components/Item'
import { Button } from '../components/Button'
import { Pagination } from '../components/Pagination'
import userAvatar from '../assets/user.png'

// Dữ liệu giả lập cho người dùng
const possibleNames = [
  'Nguyễn Văn A',
  'Trần Thị B',
  'Lê Văn C',
  'Phạm Thị D',
  'Hoàng Văn E',
  'Vũ Thị F',
  'Đỗ Văn G',
  'Bùi Thị H',
  'Đinh Văn I',
  'Mai Thị K',
  'Tô Văn L',
  'Ngô Thị M',
  'Dương Văn N',
  'Trịnh Thị O',
  'Lý Văn P'
]
const possibleGenders = ['Nam', 'Nữ', 'Khác']
const possibleAddresses = [
  'Hà Nội',
  'TP. Hồ Chí Minh',
  'Đà Nẵng',
  'Hải Phòng',
  'Cần Thơ',
  'An Giang',
  'Bà Rịa - Vũng Tàu',
  'Bắc Giang',
  'Bắc Kạn',
  'Bạc Liêu'
]
const possibleJobs = [
  'Lập trình viên',
  'Kế toán',
  'Nhân viên văn phòng',
  'Giáo viên',
  'Bác sĩ',
  'Kỹ sư',
  'Thiết kế đồ họa',
  'Marketing',
  'Kinh doanh',
  'Quản lý nhân sự'
]

const allUsersData = Array(50)
  .fill(null)
  .map((_, index) => {
    const randomNameIndex = Math.floor(Math.random() * possibleNames.length)
    const randomGenderIndex = Math.floor(Math.random() * possibleGenders.length)
    const randomAddressIndex = Math.floor(Math.random() * possibleAddresses.length)
    const randomJobIndex = Math.floor(Math.random() * possibleJobs.length)
    const name = possibleNames[randomNameIndex]
    const nameWithoutSpaces = name.toLowerCase().replace(/\s/g, '')
    const phoneNumber = `0${Math.floor(Math.random() * 900000000) + 100000000}`

    return {
      id: index + 1,
      name: name,
      username: `${nameWithoutSpaces}${index}`,
      email: `${nameWithoutSpaces}${index}@gmail.com`,
      gender: possibleGenders[randomGenderIndex],
      address: possibleAddresses[randomAddressIndex],
      job: possibleJobs[randomJobIndex],
      phoneNumber: phoneNumber,
      avatar: userAvatar,
      birthday: new Date(1970 + Math.floor(Math.random() * 40), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toLocaleDateString('vi-VN'),
      image: userAvatar
    }
  })

const ITEMS_PER_PAGE = 20

const UserManagement = () => {
  const [currentPage, setCurrentPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'view' | 'edit' | null>(null)

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

  const { totalPages, currentItems, startIndex, endIndex, totalItems } =
    useMemo(() => {
      let filteredData = allUsersData

      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        filteredData = filteredData.filter((user) =>
          user.name.toLowerCase().includes(query) ||
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query) ||
          user.address.toLowerCase().includes(query) ||
          user.job.toLowerCase().includes(query) ||
          user.phoneNumber.includes(query)
        )
      }

      const totalItems = filteredData.length
      const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE) || 1
      const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
      const endIndex = startIndex + ITEMS_PER_PAGE
      const currentItems = filteredData.slice(startIndex, endIndex)

      return {
        totalPages,
        currentItems,
        startIndex: totalItems === 0 ? 0 : startIndex + 1,
        endIndex: Math.min(endIndex, totalItems),
        totalItems
      }
    }, [currentPage, searchQuery])

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
        {currentItems.length > 0 ? (
          <div className="px-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {currentItems.map((user) => (
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
                      <span className="text-sm font-medium text-gray-500">Giới tính:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.gender}</span>
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
                      <span className="text-sm font-medium text-gray-500">Ngày sinh:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.birthday}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Địa chỉ:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.address}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Nghề nghiệp:</span>
                      <span className="ml-2 text-sm text-gray-900">{selectedUser.job}</span>
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
                    <label className="block text-sm font-medium text-gray-700 mb-1">Giới tính</label>
                    <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" defaultValue={selectedUser.gender}>
                      <option value="">Chọn giới tính</option>
                      {possibleGenders.map((gender) => (
                        <option key={gender} value={gender}>{gender}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Địa chỉ</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.address}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nghề nghiệp</label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.job}
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
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ngày sinh</label>
                    <input
                      type="date"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue={selectedUser.birthday}
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