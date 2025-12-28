import React, { useState } from 'react';
import { UserPlus, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/Button';
import GroupCard from '../../../components/GroupCard';

// Interface for Group Data
interface GroupData {
  id: number;
  name: string;
  role: 'Trưởng nhóm' | 'Thành viên';
  memberCount: number;
  iconSrc: string;
}

const FamilyGroup: React.FC = () => {
  const navigate = useNavigate();
  // Mock Data: Toggle this array to empty [] to see the "No Groups" screen.
  const [groups, setGroups] = useState<GroupData[]>([
    { id: 1, name: 'Gia đình haha', role: 'Trưởng nhóm', memberCount: 5, iconSrc: 'https://cdn-icons-png.flaticon.com/512/3253/3253272.png' },
    { id: 2, name: 'Gia đình haha', role: 'Thành viên', memberCount: 5, iconSrc: 'https://cdn-icons-png.flaticon.com/512/3253/3253272.png' },
    { id: 3, name: 'Gia đình haha', role: 'Trưởng nhóm', memberCount: 5, iconSrc: 'https://cdn-icons-png.flaticon.com/512/3253/3253272.png' },
    { id: 4, name: 'Gia đình haha', role: 'Trưởng nhóm', memberCount: 5, iconSrc: 'https://cdn-icons-png.flaticon.com/512/3253/3253272.png' },
  ]);

  const handleCreateGroup = () => {
    console.log('Create/Add group clicked');
    navigate('/main/family-group/add');
  };

  // --- RENDER: LIST VIEW (If groups exist) ---
  if (groups.length > 0) {
    return (
      <div className="p-6 pb-24"> {/* Added pb-24 to avoid overlap with bottom tab bar */}
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-[#C3485C]">
            Nhóm Gia Đình
          </h1>
          <button 
            onClick={handleCreateGroup}
            className="w-10 h-10 bg-[#C3485C] rounded-full flex justify-center items-center text-white shadow-md transition-transform active:scale-95"
          >
            <Plus size={24} strokeWidth={2.5} />
          </button>
        </div>

        {/* Scrollable List */}
        <div className="flex flex-col gap-4">
          {groups.map(group => (
            <GroupCard
              key={group.id}
              name={group.name}
              role={group.role}
              memberCount={group.memberCount}
              iconSrc={group.iconSrc}
            />
          ))}
        </div>
      </div>
    );
  }

  // --- RENDER: EMPTY VIEW (If no groups) ---
  return (
    <div className="flex flex-col items-center pt-10 px-6 text-center">
      <h1 className="text-2xl font-bold text-[#C3485C] mb-4">
        Nhóm Gia Đình
      </h1>
      
      <p className="text-gray-600 mb-8 max-w-xs">
        Bạn chưa thuộc nhóm nào cả. Hãy tạo nhóm để bắt đầu lên kế hoạch mua sắm!
      </p>
      
      <Button
        variant="primary"
        size="fit"
        icon={UserPlus}
        onClick={handleCreateGroup}
      >
        Tạo nhóm mới
      </Button>
    </div>
  );
};

export default FamilyGroup;