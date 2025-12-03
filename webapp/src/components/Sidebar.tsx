import React from 'react'
import { ChevronRight, Users } from 'lucide-react'

export const Sidebar = () => {
  return (
    <aside className="w-65 flex shrink-0 flex-col justify-between border-r border-gray-200 p-6">
      <div>
        {/* Logo */}
        <div className="mb-10">
          <h1 className="text-2xl font-bold">
            <span className="text-[#c93045]">S</span>
            <span className="text-[#f7b686]">hop</span>
            <span className="text-[#c93045]">S</span>
            <span className="text-[#f7b686]">ense</span> Admin
          </h1>
          <div className="w-46 mx-auto mt-4 h-0.5 bg-gray-200"></div>
        </div>

        {/* Menu */}
        <nav className="space-y-6">
          <div className="flex cursor-pointer items-center justify-between font-medium text-[#c93045] hover:text-[#b02a3d]">
            <span>Danh mục nguyên liệu</span>
            <ChevronRight size={18} />
          </div>

          <div className="cursor-pointer font-medium text-gray-600 transition-colors hover:text-[#c93045]">
            Danh mục món ăn
          </div>

          <div className="cursor-pointer font-medium text-gray-600 transition-colors hover:text-[#c93045]">
            Quản lý người dùng
          </div>

          <div className="cursor-pointer font-medium text-gray-600 transition-colors hover:text-[#c93045]">
            Quản lý nhóm
          </div>
        </nav>
      </div>

      {/* User Profile */}
      <div className="mt-auto">
        <div className="w-46 mx-auto mb-6 h-0.5 bg-gray-200"></div>
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
  )
}
