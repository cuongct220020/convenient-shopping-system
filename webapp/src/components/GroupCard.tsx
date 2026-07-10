import React from 'react';

interface GroupCardProps {
  name: string;
  role: 'Trưởng nhóm' | 'Thành viên';
  memberCount: number;
  iconSrc: string;
  onClick?: () => void;
}

const GroupCard: React.FC<GroupCardProps> = ({ name, role, memberCount, iconSrc, onClick }) => {
  return (
    <div
      className={`flex items-center bg-gray-50 rounded-2xl p-4 shadow-sm ${onClick ? 'cursor-pointer active:scale-[0.98] transition-transform' : ''}`}
      onClick={onClick}
    >
      {/* Icon/Avatar */}
      <div className="w-16 h-16 mr-4 flex-shrink-0">
         <img 
           src={iconSrc} 
           alt={name} 
           className="w-full h-full object-cover rounded-full"
         />
      </div>
      
      {/* Info */}
      <div className="flex flex-col items-start">
        <h3 className="text-lg font-bold text-gray-900 leading-tight mb-1">{name}</h3>
        <p className="text-sm font-semibold text-gray-800 mb-0.5">{role}</p>
        <p className="text-sm text-gray-500 italic">{memberCount} thành viên</p>
      </div>
    </div>
  );
};

export default GroupCard;