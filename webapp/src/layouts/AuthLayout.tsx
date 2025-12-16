import React from 'react'
import { Outlet, useMatches } from 'react-router-dom'
import { BackButton } from '../components/BackButton'
import loginBg from '../assets/login-bg.png'

export default function AuthLayout() {
  const matches = useMatches()
  const currentMatch = matches[matches.length - 1]
  const { backTo = '/', backText = 'Trang chủ' } = (currentMatch?.handle as any) || {}

  return (
    <div className="relative min-h-screen w-screen overflow-hidden bg-gray-100 font-sans">
      {/* Background gradient/image full screen */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="absolute inset-0 bg-black/5"></div>
      </div>

      {/* Main Content Container */}
      <div className="relative flex min-h-screen w-full">
        <div className="relative flex w-full h-screen flex-col overflow-hidden bg-white">
          {/* Header: Back Button */}
          <div className="my-4">
            <BackButton to={backTo} text={backText} />
          </div>

          {/* Scrollable Content Area */}
          <div className="no-scrollbar relative z-10 flex-1 overflow-y-auto">
            <div className="px-4 sm:px-6 md:px-8 pb-8 pt-2">
              <Outlet />
            </div>
          </div>

          {/* Background Image Decoration (Bottom) */}
          <div className="pointer-events-none absolute inset-x-0 bottom-0 z-0 h-64 sm:h-80 md:h-96">
            {/* Using a gradient overlay to fade image into white */}
            <div className="absolute inset-0 z-10 bg-gradient-to-t from-white/10 via-white/40 to-white"></div>
            {/* Food background placeholder */}
            <img
              src={loginBg}
              alt="Food Background"
              className="size-full object-cover opacity-70"
            />
          </div>
        </div>
      </div>
    </div>
  )
}