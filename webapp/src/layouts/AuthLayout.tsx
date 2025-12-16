import React from 'react'

interface AuthLayoutProps {
  children: React.ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="relative min-h-screen w-screen overflow-hidden bg-gray-100 font-sans">
      {/* Background gradient/image full screen */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="absolute inset-0 bg-black/5"></div>
      </div>

      {/* Main Content Container */}
      <div className="relative flex min-h-screen w-full">
        <div className="relative flex w-full h-screen flex-col overflow-hidden bg-white">
          {/* Content is passed in as children */}
          {children}
        </div>
      </div>
    </div>
  )
}