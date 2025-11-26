import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send } from 'lucide-react';
import loginBg from '../assets/login-bg.png';
import { InputField } from '../components/InputField';
import { Button } from '../components/Button';
import { BackButton } from '../components/BackButton';

export default function ForgotPassword2() {
  const navigate = useNavigate();
  
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [errors, setErrors] = useState<{
    password1: string | null;
    password2: string | null;
  }>({
    password1: null,
    password2: null
  });
  const [touched, setTouched] = useState<{
    password1: boolean;
    password2: boolean;
  }>({
    password1: false,
    password2: false
  });

  // Validation functions
  const validatePassword = (password: string): string | null => {
    if (!password.trim()) {
      return "Mật khẩu không được để trống";
    }
    if (password.length < 6) {
      return "Mật khẩu phải có ít nhất 6 ký tự";
    }
    return null;
  };

  const validateConfirmPassword = (confirmPassword: string, password: string): string | null => {
    if (!confirmPassword.trim()) {
      return "Xác nhận mật khẩu không được để trống";
    }
    if (confirmPassword !== password) {
      return "Mật khẩu xác nhận không khớp";
    }
    return null;
  };

  const handlePassword1Change = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword1(value);
    
    if (touched.password1) {
      setErrors(prev => ({
        ...prev,
        password1: validatePassword(value)
      }));
    }
    
    // Also validate confirm password if it has been touched
    if (touched.password2) {
      setErrors(prev => ({
        ...prev,
        password2: validateConfirmPassword(password2, value)
      }));
    }
  };

  const handlePassword1Blur = () => {
    setTouched(prev => ({ ...prev, password1: true }));
    setErrors(prev => ({
      ...prev,
      password1: validatePassword(password1)
    }));
  };

  const handlePassword2Change = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword2(value);
    
    if (touched.password2) {
      setErrors(prev => ({
        ...prev,
        password2: validateConfirmPassword(value, password1)
      }));
    }
  };

  const handlePassword2Blur = () => {
    setTouched(prev => ({ ...prev, password2: true }));
    setErrors(prev => ({
      ...prev,
      password2: validateConfirmPassword(password2, password1)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    const password1Error = validatePassword(password1);
    const password2Error = validateConfirmPassword(password2, password1);
    
    setErrors({
      password1: password1Error,
      password2: password2Error
    });
    
    setTouched({
      password1: true,
      password2: true
    });
    
    // If no errors, proceed with password reset
    if (!password1Error && !password2Error) {
      console.log('Password reset confirmed');
      // Add actual password reset logic here
      navigate('/forgot-password-notification');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center relative overflow-hidden font-sans">
      
      {/* Mobile Container */}
      <div className="w-[375px] h-[812px] bg-white relative shadow-2xl overflow-hidden flex flex-col">

        {/* Header: Back Button */}
        <div className="my-4">
          <BackButton to="/forgot-password-1" text="Quay lại" />
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto no-scrollbar relative z-10">
          <div className="px-6 pb-8 pt-2">
          
            {/* Title */}
            <div className="mb-4">
              <h2 className="text-center text-3xl font-bold text-[#c93045] mb-8">Đặt lại mật khẩu</h2>
              <p className="text-sm text-gray-600">
                Xin chào <span className="font-semibold">Username</span>, vui lòng nhập mật khẩu bạn muốn thay đổi.
              </p>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <InputField
                  id="password"
                  type="password"
                  label="Mật khẩu mới"
                  placeholder="Nhập mật khẩu"
                  value={password1}
                  onChange={handlePassword1Change}
                  onBlur={handlePassword1Blur}
                  error={errors.password1}
                />
              </div>

              <div className="mb-4">
                <InputField
                  id="confirm-password"
                  type="password"
                  label="Xác nhận mật khẩu mới"
                  placeholder="Nhập lại mật khẩu"
                  value={password2}
                  onChange={handlePassword2Change}
                  onBlur={handlePassword2Blur}
                  error={errors.password2}
                />
              </div>

              <Button variant="primary" icon={Send} size="fit" type="submit">
                Xác nhận
              </Button>
            </form>

            {/* Bottom Spacer for scrolling over background */}
            <div className="h-20"></div>
          </div>
        </div>

        {/* Background Image Decoration (Bottom) */}
        <div className="absolute bottom-0 left-0 right-0 h-80 z-0 pointer-events-none">
           {/* Using a gradient overlay to fade image into white */}
           <div className="absolute inset-0 bg-gradient-to-t from-white/10 via-white/40 to-white z-10"></div>
           {/* Food background placeholder */}
           <img
            src={loginBg}
            alt="Food Background"
            className="w-full h-full object-cover opacity-70"
           />
        </div>
      </div>
    </div>
  );
}