import React, { useState } from 'react';
import { Camera, Search, Check } from 'lucide-react';
import { BackButton } from '../../../components/BackButton'; // Adjust path as needed
import { InputField } from '../../../components/InputField'; // Adjust path as needed
import { Button } from '../../../components/Button'; // Adjust path as needed
import UserCard, { UserCardProps } from '../../../components/UserCard'; // Adjust path as needed

const AddGroup: React.FC = () => {
  // State for form inputs
  const [groupName, setGroupName] = useState('');
  const [memberSearch, setMemberSearch] = useState('');

  // Mock state for selected members based on the image
  const [selectedMembers, setSelectedMembers] = useState<UserCardProps[]>([
    {
      id: 'user-1',
      name: 'Bạn (Tôi)',
      role: 'Trưởng nhóm',
      isRemovable: false, // Current user cannot remove themselves in this context
    },
    {
      id: 'user-2',
      name: 'Bùi Mạnh Hưng',
      role: 'Thành viên',
      email: 'hungdeptrai@gmail.com',
      isRemovable: true,
    },
  ]);

  const handleRemoveMember = (id: string | number) => {
    setSelectedMembers(prev => prev.filter(member => member.id !== id));
  };

  const handleSubmit = () => {
    console.log('Creating group:', { groupName, members: selectedMembers });
    // Add logic to submit data to backend
  };

  return (
    <div className="min-h-screen bg-white p-6 pb-24 relative">
      {/* Header */}
      <div className="relative mb-6 flex items-center">
        <BackButton text="Quay lại" className="absolute left-0" />
      </div>
      <h1 className="text-xl font-bold text-[#C3485C] text-center">Tạo Nhóm Mới</h1>

      {/* Group Image Upload Placeholder */}
      <div className="flex flex-col items-center mb-8">
        <div className="relative">
          <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center">
            {/* Placeholder for image or actual image preview would go here */}
          </div>
          <button className="absolute bottom-0 right-0 bg-gray-200 p-2 rounded-full text-gray-600 hover:bg-gray-300 transition-colors border-2 border-white">
            <Camera size={20} />
          </button>
        </div>
        <p className="text-sm font-medium text-gray-700 mt-3">Tải ảnh nhóm lên</p>
      </div>

      {/* Form Fields */}
      <div className="space-y-6">
        <InputField
          label="Tên nhóm gia đình"
          labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
          placeholder="Ví dụ: Gia đình haha"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
        />

        <InputField
          label="Thêm thành viên"
          labelClassName="after:content-['*'] after:ml-0.5 after:text-red-500"
          placeholder="Nhập username hoặc email..."
          icon={<Search size={20} />}
          value={memberSearch}
          onChange={(e) => setMemberSearch(e.target.value)}
        />
      </div>

      {/* Selected Members List */}
      <div className="mt-8">
        <h2 className="text-sm font-bold text-gray-700 mb-4 uppercase">
          THÀNH VIÊN ĐÃ CHỌN ({selectedMembers.length})
        </h2>
        <div className="flex flex-col gap-3">
          {selectedMembers.map(member => (
            <UserCard
              key={member.id}
              {...member}
              onRemove={handleRemoveMember}
            />
          ))}
        </div>
      </div>

      {/* Submit Button - Fixed at bottom of padding area */}
      <div className="mt-10">
         <Button variant="primary" onClick={handleSubmit} size="fit" icon={Check}>
            Tạo nhóm
         </Button>
      </div>
    </div>
  );
};

export default AddGroup;