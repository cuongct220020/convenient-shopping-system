import React, { useState, useEffect } from 'react';
import { UserPlus, Plus } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../../../components/Button';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import GroupCard from '../../../components/GroupCard';
import { groupService } from '../../../services/group';

// Interface for Group Data
interface GroupData {
  id: string;
  name: string;
  role: 'Trưởng nhóm' | 'Thành viên';
  memberCount: number;
  iconSrc: string;
}

// Helper function to map backend role to UI role
function mapRoleToUI(role: 'head_chef' | 'member'): 'Trưởng nhóm' | 'Thành viên' {
  return role === 'head_chef' ? 'Trưởng nhóm' : 'Thành viên';
}

// Helper function to get default avatar URL
function getAvatarUrl(url: string | null): string {
  return url || new URL('../../../assets/family.png', import.meta.url).href;
}

const FamilyGroup: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [groups, setGroups] = useState<GroupData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch groups on mount and when refreshKey changes
  useEffect(() => {
    const fetchGroups = async () => {
      setIsLoading(true);
      setError(null);

      const result = await groupService.getGroups();

      result.match(
        (response) => {
          const mappedGroups: GroupData[] = response.data.groups.map((group) => ({
            id: group.id,
            name: group.group_name,
            role: mapRoleToUI(group.role_in_group),
            memberCount: group.member_count,
            iconSrc: getAvatarUrl(group.group_avatar_url)
          }));
          setGroups(mappedGroups);
        },
        (error) => {
          console.error('Failed to fetch groups:', error);
          if (error.type === 'unauthorized') {
            setError('Bạn cần đăng nhập để xem nhóm');
          } else if (error.type === 'network-error') {
            setError('Lỗi kết nối mạng');
          } else {
            setError('Không thể tải danh sách nhóm');
          }
        }
      );

      setIsLoading(false);
    };

    fetchGroups();
  }, [refreshKey, location.key]);

  // Check if navigation state indicates a refresh is needed
  useEffect(() => {
    if (location.state?.refresh) {
      setRefreshKey(prev => prev + 1);
      // Clear the state to prevent infinite refresh
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, location.pathname, navigate]);

  const handleCreateGroup = () => {
    navigate('/main/family-group/add');
  };

  // --- RENDER: LOADING STATE ---
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <LoadingSpinner size="lg" showText text="Đang tải..." />
      </div>
    );
  }

  // --- RENDER: ERROR STATE ---
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center pt-20 px-6 text-center">
        <p className="text-red-500 mb-4">{error}</p>
        <Button
          variant="primary"
          size="fit"
          onClick={() => window.location.reload()}
        >
          Thử lại
        </Button>
      </div>
    );
  }

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
              onClick={() => navigate(`/main/family-group/${group.id}`)}
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