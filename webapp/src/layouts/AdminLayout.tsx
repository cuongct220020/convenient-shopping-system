import { NavLink, Outlet } from 'react-router-dom'
import React from 'react'
import { ChevronRight, Users } from 'lucide-react'

export default function AdminLayout() {
  return (
    <div className="flex min-h-screen bg-white font-sans text-gray-800">
      <aside className="w-64 flex shrink-0 flex-col justify-between border-r border-gray-200 p-6">
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

            <div className="cursor-pointer font-medium text-gray-600 transition-colors hover:text-[#C3485C]">
              Quản lý nhóm
            </div>
          </nav>
        </div>

        {/* User Profile */}
        <div className="mt-auto">
          <div className="mx-auto mb-6 h-0.5 w-full bg-gray-200"></div>
          <div className="flex items-center space-x-3">
            <div className="flex size-10 items-center justify-center rounded-full bg-emerald-400 text-white">
              <Users size={20} />
            </div>
            <div className="overflow-hidden">
              <p className="truncate text-sm font-bold text-gray-900">
                username12bc
              </p>
              <p className="truncate text-xs text-gray-500">
                nguyenvana @gmail.com
              </p>
            </div>
          </div>
        </div>
      </aside>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}