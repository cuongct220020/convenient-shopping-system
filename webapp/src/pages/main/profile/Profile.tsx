import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Info,
  HeartPulse,
  Heart,
  LogOut
} from 'lucide-react';

const Profile = () => {
  const navigate = useNavigate();
  return (
    <div className="flex-1 p-5 pb-24 bg-white overflow-y-auto max-w-sm mx-auto w-full">
      {/* Header */}
      <h2 className="text-2xl font-bold text-red-600 mb-6">
        Tài khoản
      </h2>

      {/* User Profile Info */}
      <div className="flex items-center mb-8">
        <div className="w-16 h-16 rounded-full bg-purple-300 flex justify-center items-center shrink-0">
          <span className="text-white font-bold text-2xl">UN</span>
        </div>
        <div className="ml-4">
          <h3 className="font-bold text-lg text-gray-900">username1234</h3>
          <p className="text-sm text-gray-500">user-email@gmail.com</p>
        </div>
      </div>

      {/* Menu List */}
      <div className="flex flex-col">
        
        {/* Item 1: Login Info */}
        <MenuItem 
          icon={<User size={20} className="text-black fill-black" />} 
          text="Thông tin đăng nhập"
          onClick={() => navigate('/main/profile/login-information')} 
        />

        {/* Item 2: Personal Profile */}
        <MenuItem 
          icon={<Info size={20} className="text-black fill-black" />} 
          text="Hồ sơ cá nhân" 
          onClick={() => navigate('/main/profile/personal-profile')} 
        />

        {/* Item 3: Health Profile */}
        <MenuItem 
          icon={<HeartPulse size={20} className="text-black" />} 
          text="Hồ sơ sức khỏe" 
          onClick={() => navigate('/main/profile/health-profile')} 
        />

        {/* Item 4: Favorites */}
        <MenuItem 
          icon={<Heart size={20} className="text-black fill-black" />} 
          text="Danh mục yêu thích" 
          onClick={() => navigate('/main/profile/favorites')} 
        />

        {/* Logout Button */}
        <button className="flex items-center py-4 w-full mt-2 group">
          <div className="w-8 flex justify-center">
            <LogOut size={20} className="text-red-600" />
          </div>
          <span className="ml-4 text-red-600 font-bold text-base group-hover:text-red-700">
            Đăng xuất
          </span>
        </button>

      </div>
    </div>
  );
};

// Helper component for list items
interface MenuItemProps {
  icon: React.ReactNode;
  text: string;
  onClick?: () => void;
}

const MenuItem: React.FC<MenuItemProps> = ({ icon, text, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="flex items-center py-4 border-b border-gray-100 w-full hover:bg-gray-50 transition-colors"
    >
      <div className="w-8 flex justify-center">
        {icon}
      </div>
      <span className="ml-4 text-gray-800 font-medium text-base text-left flex-1">
        {text}
      </span>
    </button>
  );
};

export default Profile;