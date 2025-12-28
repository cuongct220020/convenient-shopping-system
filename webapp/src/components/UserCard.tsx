import React from 'react';
import { User, X, Plus } from 'lucide-react';

export type UserCardVariant = 'selected' | 'candidate';

export interface UserCardProps {
  id: string | number;
  name: string;
  role: string;
  email?: string;
  avatarSrc?: string;
  onRemove?: (id: string | number) => void;
  isRemovable?: boolean;
  variant?: UserCardVariant;
  onAdd?: (id: string | number) => void;
}

const UserCard: React.FC<UserCardProps> = ({
  id,
  name,
  role,
  email,
  avatarSrc,
  onRemove,
  isRemovable = false,
  variant = 'selected',
  onAdd,
}) => {
  const isCandidate = variant === 'candidate';

  return (
    <div className="flex items-center justify-between p-4 bg-gray-100 rounded-xl">
      <div className="flex items-center space-x-4">
        {/* Avatar */}
        <div className="w-12 h-12 rounded-full bg-gray-300 flex items-center justify-center overflow-hidden">
          {avatarSrc ? (
            <img src={avatarSrc} alt={name} className="w-full h-full object-cover" />
          ) : (
            <User size={24} className="text-gray-600" />
          )}
        </div>

        {/* User Info */}
        <div>
          <h3 className="font-bold text-gray-900">{name}</h3>
          {!isCandidate && <p className="text-sm font-medium text-gray-700">{role}</p>}
          {email && <p className="text-xs text-gray-500 italic">{email}</p>}
        </div>
      </div>

      {/* Action Button */}
      {isCandidate && onAdd ? (
        // Add Button (+) for candidate variant
        <button
          onClick={() => onAdd(id)}
          className="w-10 h-10 rounded-full bg-[#FFD7C1] flex items-center justify-center text-[#C3485C] hover:bg-[#ffc5a3] transition-colors shrink-0"
          type="button"
        >
          <Plus size={24} strokeWidth={2.5} />
        </button>
      ) : (
        // Remove Button (X) for selected variant
        isRemovable && onRemove && (
          <button
            onClick={() => onRemove(id)}
            className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-full transition-colors"
            type="button"
          >
            <X size={24} />
          </button>
        )
      )}
    </div>
  );
};

export default UserCard;