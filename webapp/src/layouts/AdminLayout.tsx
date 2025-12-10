import { Sidebar } from '../components/Sidebar'

interface AdminLayoutProps {
  children: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <div className="flex bg-white font-sans text-gray-800" style={{ width: '1440px', height: '1024px' }}>
      <Sidebar />
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}