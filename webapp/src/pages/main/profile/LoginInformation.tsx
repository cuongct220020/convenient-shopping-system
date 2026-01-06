import { useEffect, useState } from 'react';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { InputField } from '../../../components/InputField';
import { Lock, Eye, EyeOff } from 'lucide-react';
import { userService } from '../../../services/user';

const LoginInformation = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);

  // Form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');

  // Validation and loading state
  const [errors, setErrors] = useState<{
    currentPassword?: string;
    newPassword?: string;
    repeatPassword?: string;
    general?: string;
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    userService.getCurrentUser().match(
      (response) => {
        setEmail(response.data.email);
        setUsername(response.data.username);
        setIsLoading(false);
      },
      (error) => {
        console.error('Failed to fetch user:', error);
        setIsLoading(false);
      }
    );
  }, []);

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!currentPassword) {
      newErrors.currentPassword = 'Vui lòng nhập mật khẩu hiện tại';
    }

    if (!newPassword) {
      newErrors.newPassword = 'Vui lòng nhập mật khẩu mới';
    } else if (newPassword.length < 6) {
      newErrors.newPassword = 'Mật khẩu mới phải có ít nhất 6 ký tự';
    }

    if (!repeatPassword) {
      newErrors.repeatPassword = 'Vui lòng nhập lại mật khẩu mới';
    } else if (newPassword !== repeatPassword) {
      newErrors.repeatPassword = 'Mật khẩu nhập lại không khớp';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;

    setIsSubmitting(true);
    setErrors({});

    userService
      .changePassword({
        current_password: currentPassword,
        new_password: newPassword
      })
      .match(
        () => {
          setIsSubmitting(false);
          setIsModalOpen(false);
          setCurrentPassword('');
          setNewPassword('');
          setRepeatPassword('');
        },
        (error) => {
          setIsSubmitting(false);
          setErrors({
            general: error.desc || 'Đổi mật khẩu thất bại. Vui lòng thử lại.'
          });
        }
      );
  };

  const handleCancel = () => {
    setIsModalOpen(false);
    setCurrentPassword('');
    setNewPassword('');
    setRepeatPassword('');
    setErrors({});
  };

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">

      {/* Back Navigation */}
      <BackButton to="/main/profile" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-8">
        Thông tin đăng nhập
      </h1>

      <div className="flex flex-col gap-8">
        {isLoading ? (
          <div className="flex justify-center items-center py-8">
            <span className="text-gray-500">Đang tải...</span>
          </div>
        ) : (
          <>
            {/* Email Section */}
            <div>
              <h3 className="font-bold text-black mb-2 text-base">Email</h3>
              <span className="text-gray-800 text-base">
                {email}
              </span>
            </div>

            {/* Username Section */}
            <div>
              <h3 className="font-bold text-black mb-2 text-base">Tên đăng nhập</h3>
              <span className="text-gray-800 text-base">
                {username}
              </span>
            </div>

            {/* Password Section */}
            <div>
              <Button
                variant="primary"
                icon={Lock}
                size="fit"
                onClick={() => setIsModalOpen(true)}
              >
                Đổi mật khẩu
              </Button>
            </div>
          </>
        )}
      </div>

      {/* Password Change Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-black mb-6">Đổi mật khẩu</h2>

            <div className="flex flex-col gap-4">
              {/* Current Password */}
              <div className="relative">
                <InputField
                  label="Mật khẩu hiện tại"
                  type={showCurrentPassword ? 'text' : 'password'}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  error={errors.currentPassword}
                  placeholder="Nhập mật khẩu hiện tại"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
                >
                  {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              {/* New Password */}
              <div className="relative">
                <InputField
                  label="Mật khẩu mới"
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  error={errors.newPassword}
                  placeholder="Nhập mật khẩu mới"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
                >
                  {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              {/* Repeat Password */}
              <div className="relative">
                <InputField
                  label="Nhập lại mật khẩu mới"
                  type={showRepeatPassword ? 'text' : 'password'}
                  value={repeatPassword}
                  onChange={(e) => setRepeatPassword(e.target.value)}
                  error={errors.repeatPassword}
                  placeholder="Nhập lại mật khẩu mới"
                />
                <button
                  type="button"
                  onClick={() => setShowRepeatPassword(!showRepeatPassword)}
                  className="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
                >
                  {showRepeatPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              {/* General Error */}
              {errors.general && (
                <p className="text-sm text-red-600">{errors.general}</p>
              )}

              {/* Buttons */}
              <div className="flex gap-3 mt-2">
                <Button
                  variant={isSubmitting ? 'disabled' : 'secondary'}
                  size="full"
                  onClick={handleCancel}
                >
                  Hủy
                </Button>
                <Button
                  variant={isSubmitting ? 'disabled' : 'primary'}
                  size="full"
                  onClick={handleSubmit}
                >
                  {isSubmitting ? 'Đang xử lý...' : 'Xác nhận'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginInformation;
