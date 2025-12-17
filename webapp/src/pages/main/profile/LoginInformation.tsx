import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { NotificationCard } from '../../../components/NotificationCard';
import { Lock, Save, X } from 'lucide-react';

const LoginInformation = () => {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [email, setEmail] = useState('your-email@gmail.com');
  const [username, setUsername] = useState('linhsieungausrp3z');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [originalValues, setOriginalValues] = useState({ email: '', username: '' });
  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">

      {/* Back Navigation */}
      <BackButton to="/main/profile" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-8">
        Thông tin đăng nhập
      </h1>

      <div className="flex flex-col gap-8">
        
        {/* Email Section */}
        <div>
          <h3 className="font-bold text-black mb-2 text-base">Email</h3>
          {isEditing ? (
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#C3485C] focus:border-transparent"
              placeholder="Nhập email"
            />
          ) : (
            <span className="text-gray-800 text-base">
              {email}
            </span>
          )}
        </div>

        {/* Username Section */}
        <div>
          <h3 className="font-bold text-black mb-2 text-base">Tên đăng nhập</h3>
          {isEditing ? (
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#C3485C] focus:border-transparent"
              placeholder="Nhập tên đăng nhập"
            />
          ) : (
            <span className="text-gray-800 text-base">
              {username}
            </span>
          )}
        </div>

        {/* Edit/Save Button */}
        <div className="flex justify-end">
          <Button
            variant="secondary"
            size="fit"
            onClick={() => {
              if (isEditing) {
                // Check if values have changed
                if (email !== originalValues.email || username !== originalValues.username) {
                  setShowConfirmModal(true);
                } else {
                  // No changes, just exit edit mode
                  setIsEditing(false);
                }
              } else {
                // Entering edit mode, store current values
                setOriginalValues({ email, username });
                setIsEditing(true);
              }
            }}
          >
            {isEditing ? 'Lưu' : 'Chỉnh sửa'}
          </Button>
        </div>

        {/* Password Section */}
        <div>
          <h3 className="font-bold text-black mb-2 text-base">Mật khẩu</h3>
          <div>
            <Button
              variant="secondary"
              icon={Lock}
              size="fit"
              onClick={() => navigate('/main/profile/old-password')}
            >
              Đổi mật khẩu
            </Button>
          </div>
        </div>

      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <NotificationCard
            title="Xác nhận thay đổi"
            message="Bạn có chắc chắn muốn lưu thay đổi thông tin đăng nhập không?"
            iconBgColor="bg-yellow-500"
            buttonText="Xác nhận"
            buttonIcon={Save}
            onButtonClick={() => {
              // Save the changes
              console.log('Saving:', { email, username });
              setOriginalValues({ email, username });
              setShowConfirmModal(false);
              setIsEditing(false);
            }}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={() => {
              // Revert changes
              setEmail(originalValues.email);
              setUsername(originalValues.username);
              setShowConfirmModal(false);
            }}
          />
        </div>
      )}
    </div>
  );
};

export default LoginInformation;