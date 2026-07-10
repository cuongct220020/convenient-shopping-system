import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { InputField } from '../../../components/InputField';
import { Eye, EyeOff } from 'lucide-react';

const OldPassword = () => {
  const nagivate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ currentPassword?: string }>({});

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const validateForm = (): boolean => {
    const newErrors: { currentPassword?: string } = {};

    if (!currentPassword.trim()) {
      newErrors.currentPassword = 'Vui lòng nhập mật khẩu hiện tại';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      // Handle password confirmation logic here
      nagivate('/main/profile/authentication')
    }
  };

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">
      {/* Back Navigation */}
      {/* Assumes the previous route was LoginInformation */}
      <BackButton to="/main/profile/login-information" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-2">
        Đổi mật khẩu
      </h1>

      {/* Description */}
      <p className="text-base text-gray-800 mb-8">
        Bạn cần xác nhận mật khẩu hiện tại để thực hiện thao tác này
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Current Password Input */}
        <div className="relative">
          <InputField
            label="Mật khẩu hiện tại"
            placeholder="Nhập mật khẩu"
            type={showPassword ? 'text' : 'password'}
            id="current-password"
            name="currentPassword"
            value={currentPassword}
            onChange={(e) => {
              setCurrentPassword(e.target.value);
              // Clear error when user starts typing
              if (errors.currentPassword) {
                setErrors(prev => ({ ...prev, currentPassword: undefined }));
              }
            }}
            // Add padding to the right so text doesn't overlap the icon
            inputClassName="pr-10"
            error={errors.currentPassword}
            required
          />
          {/* Password Visibility Toggle Icon */}
          {/* Positioned absolutely to sit over the right side of the input field */}
          <button
            type="button"
            onClick={togglePasswordVisibility}
            className="absolute right-3 top-[36px] text-gray-400 hover:text-gray-600 focus:outline-none"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        </div>

        {/* Forgot Password Link */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => {}}
            className="text-red-600 font-bold text-sm hover:underline"
          >
            Quên mật khẩu?
          </button>
        </div>

        {/* Confirm Button */}
        <div className="mt-8">
          <Button
            type="submit"
            variant="primary"
            size="fit"
            className="mx-auto" // Center the button horizontally
          >
            Xác nhận
          </Button>
        </div>
      </form>
    </div>
  );
};

export default OldPassword;