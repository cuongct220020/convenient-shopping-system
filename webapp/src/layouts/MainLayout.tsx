import React from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Bell, Soup, User, Archive, ShoppingCart } from 'lucide-react'

// Define the available tab names
const TabNames = ['notification', 'food', 'meal', 'family-group', 'profile'] as const
type TabName = (typeof TabNames)[number]

export default function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  // Determine active tab from current location
  const currentActiveTab = ((): TabName => {
    const path = location.pathname
    return TabNames.find((e) => path.includes(`/${e}`)) ?? 'profile'
  })()

  const handlePress = (tab: TabName) => {
    navigate(`/main/${tab}`)
  }

  return (
    <div className="relative min-h-screen bg-white">
      {/* Main Content Area - Renders the specific screen content */}
      <main className="pb-16 max-w-sm mx-auto w-full">
        <Outlet />
      </main>

      {/* Bottom Navigation Bar - Fixed at bottom */}
      <nav className="fixed bottom-0 left-0 right-0 bg-gray-100 px-2.5 py-2.5 h-16 flex justify-around items-center max-w-sm mx-auto w-full z-50">

        {/* Tab 1: Notification (Bell) */}
        <TabItem
          isActive={currentActiveTab === 'notification'}
          onPress={() => handlePress('notification')}
        >
          <Bell
            size={24}
            strokeWidth={2.5}
            className={currentActiveTab === 'notification' ? 'text-[#C3485C] fill-[#C3485C]' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 2: Food Storage (Bowl) */}
        <TabItem
          isActive={currentActiveTab === 'food'}
          onPress={() => handlePress('food')}
        >
          <Archive
            size={24}
            strokeWidth={2.5}
            className={currentActiveTab === 'food' ? 'text-[#C3485C]' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 3: Meal (Book) */}
        <TabItem
          isActive={currentActiveTab === 'meal'}
          onPress={() => handlePress('meal')}
        >
          <Soup
            size={24}
            strokeWidth={2.5}
            className={currentActiveTab === 'meal' ? 'text-[#C3485C]' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 4: Family Group (Shopping) */}
        <TabItem
          isActive={currentActiveTab === 'family-group'}
          onPress={() => handlePress('family-group')}
        >
          <ShoppingCart
            size={24}
            strokeWidth={2.5}
            className={currentActiveTab === 'family-group' ? 'text-[#C3485C]' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 5: Profile (User)1*/}
        <TabItem
          isActive={currentActiveTab === 'profile'}
          onPress={() => handlePress('profile')}
        >
          <User
            size={24}
            strokeWidth={2.5}
            className={currentActiveTab === 'profile' ? 'text-[#C3485C] fill-[#C3485C]' : 'text-gray-400'}
          />
        </TabItem>
      </nav>
    </div>
  )
}

// Helper component for individual tabs
interface TabItemProps {
  isActive: boolean
  children: React.ReactNode
  onPress: () => void
}

const TabItem: React.FC<TabItemProps> = ({ isActive, children, onPress }) => {
  return (
    <button
      onClick={onPress}
      className={`
        w-12 h-10 flex justify-center items-center rounded-xl
        transition-colors duration-200 hover:bg-[#FFD7C1]
        ${isActive ? 'bg-[#FFD7C1]' : ''}
      `}
    >
      {children}
    </button>
  )
}
