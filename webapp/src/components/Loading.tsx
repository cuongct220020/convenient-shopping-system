import { ReactNode } from 'react'

type LoadingOverlayProps = {
  isLoading: boolean
  children: ReactNode
}
export function LoadingOverlay({ isLoading, children }: LoadingOverlayProps) {
  return (
    <div className="relative flex flex-1">
      {children}
      {isLoading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/50 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-2">
            <div className="size-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-500" />
            <span className="text-sm text-gray-600">Loading...</span>
          </div>
        </div>
      )}
    </div>
  )
}
