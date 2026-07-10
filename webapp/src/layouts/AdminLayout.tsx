import { Navigate, NavLink, Outlet, useNavigate } from 'react-router-dom'
import React, { useState } from 'react'
import { ChevronRight, Users, LogOut } from 'lucide-react'
import { LocalStorage } from '../services/storage/local'
import { Time } from '../utils/time'
import { userService } from '../services/user'
import { disconnectWebSocket } from '../hooks/useWebSocketNotification'

export default function ProtectedAdminLayout() {
  const navigate = useNavigate()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  
  // Check if user is logged in by checking LocalStorage directly
  const auth = LocalStorage.inst.auth
  const isLoggedIn =
    auth !== null &&
    auth.expires_in_minutes * 60 + auth.token_last_refresh_timestamp > Time.now

  const handleLogout = async () => {
    setIsLoggingOut(true)
    const result = await userService.logout()
    result.match(
      () => {
        // Disconnect WebSocket
        disconnectWebSocket()
        // Clear local auth token
        LocalStorage.inst.auth = null
        // Navigate to admin login page
        navigate('/admin/login')
      },
      (error) => {
        console.error('Logout failed:', error)
        // Disconnect WebSocket even if API call fails
        disconnectWebSocket()
        // Even if API call fails, clear local auth and navigate to login
        LocalStorage.inst.auth = null
        navigate('/admin/login')
      }
    )
    setIsLoggingOut(false)
  }

  if (!isLoggedIn) {
    return <Navigate to="/admin/login" replace />
  }
  return (
    <div className="flex min-h-screen bg-white font-sans text-gray-800">
      <aside className="flex w-64 shrink-0 flex-col justify-between border-r border-gray-200 p-6">
        <div>
          {/* Logo */}
          <div className="mb-10">
            <h1 className="text-2xl font-bold">
              <span className="text-[#C3485C]">S</span>
              <span className="text-[#f7b686]">hop</span>
              <span className="text-[#C3485C]">S</span>
              <span className="text-[#f7b686]">ense</span> Admin
            </h1>
            <div className="mx-auto mt-4 h-0.5 w-full bg-gray-200"></div>
          </div>

          {/* Menu */}
          <nav className="space-y-6">
            <NavLink
              to="/admin/ingredient-menu"
              className={({ isActive }) =>
                `flex cursor-pointer items-center justify-between font-medium transition-colors ${
                  isActive
                    ? 'text-[#C3485C] hover:text-[#b02a3d]'
                    : 'text-gray-600 hover:text-[#C3485C]'
                }`
              }
            >
              <span>Danh mục nguyên liệu</span>
              <ChevronRight size={18} />
            </NavLink>

            <NavLink
              to="/admin/dish-menu"
              className={({ isActive }) =>
                `flex cursor-pointer items-center justify-between font-medium transition-colors ${
                  isActive
                    ? 'text-[#C3485C] hover:text-[#b02a3d]'
                    : 'text-gray-600 hover:text-[#C3485C]'
                }`
              }
            >
              <span>Danh mục món ăn</span>
              <ChevronRight size={18} />
            </NavLink>

            <NavLink
              to="/admin/user-management"
              className={({ isActive }) =>
                `flex cursor-pointer items-center justify-between font-medium transition-colors ${
                  isActive
                    ? 'text-[#C3485C] hover:text-[#b02a3d]'
                    : 'text-gray-600 hover:text-[#C3485C]'
                }`
              }
            >
              <span>Quản lý người dùng</span>
              <ChevronRight size={18} />
            </NavLink>

            {/* <div className="cursor-pointer font-medium text-gray-600 transition-colors hover:text-[#C3485C]">
              Quản lý nhóm
            </div> */}
          </nav>
        </div>

        {/* User Profile */}
        <div className="sticky bottom-0">
          <div className="mx-auto mb-6 h-0.5 w-full bg-gray-200"></div>
          <div className="flex items-center space-x-3 mb-4">
            <div className="flex size-10 items-center justify-center rounded-full bg-emerald-400 text-white">
              <Users size={20} />
            </div>
            <div className="overflow-hidden flex-1">
              <p className="truncate text-sm font-bold text-gray-900">
                Admin
              </p>
              <p className="truncate text-xs text-gray-500">
                Quản trị viên
              </p>
            </div>
          </div>
          {/* Logout Button */}
          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <LogOut size={18} />
            <span className="text-sm font-medium">
              {isLoggingOut ? 'Đang đăng xuất...' : 'Đăng xuất'}
            </span>
          </button>
        </div>
      </aside>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
