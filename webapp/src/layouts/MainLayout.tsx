import React from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Apple, Soup, BookOpen, Star, User } from 'lucide-react'

// Define the available tab names
type TabName = 'nutrition' | 'food' | 'diary' | 'favorites' | 'profile'

export default function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  // Determine active tab from current location
  const currentActiveTab = (() => {
    const path = location.pathname
    if (path.includes('/nutrition')) return 'nutrition'
    if (path.includes('/food')) return 'food'
    if (path.includes('/diary')) return 'diary'
    if (path.includes('/favorites')) return 'favorites'
    if (path.includes('/profile')) return 'profile'
    return 'profile' // default
  })()

  const handlePress = (tab: TabName) => {
    navigate(`/main/${tab}`)
  }

  return (
    <div className="relative min-h-screen bg-white">
      {/* Main Content Area - Renders the specific screen content */}
      <main className="pb-16">
        <Outlet />
      </main>

      {/* Bottom Navigation Bar - Fixed at bottom */}
      <nav className="fixed inset-x-0 bottom-0 z-50 mx-auto flex h-16 w-full max-w-sm items-center justify-around border-t border-gray-200 bg-gray-100 p-2.5">
        {/* Tab 1: Nutrition (Apple) */}
        <TabItem
          isActive={currentActiveTab === 'nutrition'}
          onPress={() => handlePress('nutrition')}
        >
          <Apple
            size={24}
            className={
              currentActiveTab === 'nutrition'
                ? 'fill-red-700 text-red-700'
                : 'text-gray-400'
            }
          />
        </TabItem>

        {/* Tab 2: Meals (Bowl) */}
        <TabItem
          isActive={currentActiveTab === 'food'}
          onPress={() => handlePress('food')}
        >
          <Soup
            size={24}
            className={
              currentActiveTab === 'food' ? 'text-red-700' : 'text-gray-400'
            }
          />
        </TabItem>

        {/* Tab 3: Diary (Book) */}
        <TabItem
          isActive={currentActiveTab === 'diary'}
          onPress={() => handlePress('diary')}
        >
          <BookOpen
            size={24}
            className={
              currentActiveTab === 'diary' ? 'text-red-700' : 'text-gray-400'
            }
          />
        </TabItem>

        {/* Tab 4: Favorites (Star) */}
        <TabItem
          isActive={currentActiveTab === 'favorites'}
          onPress={() => handlePress('favorites')}
        >
          <Star
            size={24}
            className={
              currentActiveTab === 'favorites'
                ? 'text-red-700'
                : 'text-gray-400'
            }
          />
        </TabItem>

        {/* Tab 5: Profile (User) - Active in screenshots */}
        <TabItem
          isActive={currentActiveTab === 'profile'}
          onPress={() => handlePress('profile')}
        >
          <User
            size={24}
            className={
              currentActiveTab === 'profile'
                ? 'fill-red-700 text-red-700'
                : 'text-gray-400'
            }
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
        flex h-10 w-12 items-center justify-center rounded-xl
        transition-colors duration-200 hover:bg-red-100
        ${isActive ? 'bg-orange-100' : ''}
      `}
    >
      {children}
    </button>
  )
}
