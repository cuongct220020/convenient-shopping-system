import React from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Info, HeartPulse, Heart, LogOut } from 'lucide-react'
const Profile = () => {
  const navigate = useNavigate()
  return (
    <div className="mx-auto w-full max-w-sm flex-1 overflow-y-auto bg-white p-5 pb-24">
      {/* Header */}
      <h2 className="mb-6 text-2xl font-bold text-red-600">Tài khoản</h2>

      {/* User Profile Info */}
      <div className="mb-8 flex items-center">
        <div className="flex size-16 shrink-0 items-center justify-center rounded-full bg-purple-300">
          <span className="text-2xl font-bold text-white">UN</span>
        </div>
        <div className="ml-4">
          <h3 className="text-lg font-bold text-gray-900">username1234</h3>
          <p className="text-sm text-gray-500">user-email@gmail.com</p>
        </div>
      </div>

      {/* Menu List */}
      <div className="flex flex-col">
        {/* Item 1: Login Info */}
        <MenuItem
          icon={<User size={20} className="fill-black text-black" />}
          text="Thông tin đăng nhập"
          onClick={() => navigate('/main/profile/login-information')}
        />

        {/* Item 2: Personal Profile */}
        <MenuItem
          icon={<Info size={20} className="fill-black text-black" />}
          text="Hồ sơ cá nhân"
          onClick={() => navigate('/main/profile/personal-profile')}
        />

        {/* Item 3: Health Profile */}
        <MenuItem
          icon={<HeartPulse size={20} className="text-black" />}
          text="Hồ sơ sức khỏe"
          onClick={() => navigate('/main/profile/health-profile')}
        />

        {/* Item 4: Favorites */}
        <MenuItem
          icon={<Heart size={20} className="fill-black text-black" />}
          text="Danh mục yêu thích"
          onClick={() => navigate('/main/profile/favorites')}
        />

        {/* Logout Button */}
        <button className="group mt-2 flex w-full items-center py-4">
          <div className="flex w-8 justify-center">
            <LogOut size={20} className="text-red-600" />
          </div>
          <span className="ml-4 text-base font-bold text-red-600 group-hover:text-red-700">
            Đăng xuất
          </span>
        </button>
      </div>
    </div>
  )
}

// Helper component for list items
interface MenuItemProps {
  icon: React.ReactNode
  text: string
  onClick?: () => void
}

const MenuItem: React.FC<MenuItemProps> = ({ icon, text, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center border-b border-gray-100 py-4 transition-colors hover:bg-gray-50"
    >
      <div className="flex w-8 justify-center">{icon}</div>
      <span className="ml-4 flex-1 text-left text-base font-medium text-gray-800">
        {text}
      </span>
    </button>
  )
}

export default Profile
