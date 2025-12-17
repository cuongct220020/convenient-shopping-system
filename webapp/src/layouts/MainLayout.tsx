import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Apple,
  Soup,
  BookOpen,
  Star,
  User
} from 'lucide-react';

// Define the available tab names
type TabName = 'nutrition' | 'meals' | 'diary' | 'favorites' | 'profile';

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  // Determine active tab from current location
  const currentActiveTab = (() => {
    const path = location.pathname;
    if (path.includes('/nutrition')) return 'nutrition';
    if (path.includes('/meals')) return 'meals';
    if (path.includes('/diary')) return 'diary';
    if (path.includes('/favorites')) return 'favorites';
    if (path.includes('/profile')) return 'profile';
    return 'profile'; // default
  })();

  const handlePress = (tab: TabName) => {
    navigate(`/main/${tab}`);
  };

  return (
    <div className="min-h-screen bg-white relative">
      {/* Main Content Area - Renders the specific screen content */}
      <main className="pb-16">
        <Outlet />
      </main>

      {/* Bottom Navigation Bar - Fixed at bottom */}
      <nav className="fixed bottom-0 left-0 right-0 bg-gray-100 border-t border-gray-200 px-2.5 py-2.5 h-16 flex justify-around items-center max-w-sm mx-auto w-full z-50">

        {/* Tab 1: Nutrition (Apple) */}
        <TabItem
          isActive={currentActiveTab === 'nutrition'}
          onPress={() => handlePress('nutrition')}
        >
          <Apple
            size={24}
            className={currentActiveTab === 'nutrition' ? 'text-red-700 fill-red-700' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 2: Meals (Bowl) */}
        <TabItem
          isActive={currentActiveTab === 'meals'}
          onPress={() => handlePress('meals')}
        >
          <Soup
            size={24}
            className={currentActiveTab === 'meals' ? 'text-red-700' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 3: Diary (Book) */}
        <TabItem
          isActive={currentActiveTab === 'diary'}
          onPress={() => handlePress('diary')}
        >
          <BookOpen
            size={24}
            className={currentActiveTab === 'diary' ? 'text-red-700' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 4: Favorites (Star) */}
        <TabItem
          isActive={currentActiveTab === 'favorites'}
          onPress={() => handlePress('favorites')}
        >
          <Star
            size={24}
            className={currentActiveTab === 'favorites' ? 'text-red-700' : 'text-gray-400'}
          />
        </TabItem>

        {/* Tab 5: Profile (User) - Active in screenshots */}
        <TabItem
          isActive={currentActiveTab === 'profile'}
          onPress={() => handlePress('profile')}
        >
          <User
            size={24}
            className={currentActiveTab === 'profile' ? 'text-red-700 fill-red-700' : 'text-gray-400'}
          />
        </TabItem>

      </nav>
    </div>
  );
}

// Helper component for individual tabs
interface TabItemProps {
  isActive: boolean;
  children: React.ReactNode;
  onPress: () => void;
}

const TabItem: React.FC<TabItemProps> = ({ isActive, children, onPress }) => {
  return (
    <button
      onClick={onPress}
      className={`
        w-12 h-10 flex justify-center items-center rounded-xl
        transition-colors duration-200 hover:bg-red-100
        ${isActive ? 'bg-orange-100' : ''}
      `}
    >
      {children}
    </button>
  );
};