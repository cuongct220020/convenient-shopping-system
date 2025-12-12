import { Sidebar } from '../components/Sidebar'

interface AdminLayoutProps {
  children: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <div className="flex min-h-screen bg-white font-sans text-gray-800">
      <Sidebar />
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}