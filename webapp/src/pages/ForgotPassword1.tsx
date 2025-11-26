import { useState } from 'react';
import { Send } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import loginBg from '../assets/login-bg.png';
import { InputField } from '../components/InputField';
import { Button } from '../components/Button';
import { BackButton } from '../components/BackButton';

export default function ForgotPassword() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState<{
    email: string | null;
  }>({
    email: null
  });
  const [touched, setTouched] = useState<{
    email: boolean;
  }>({
    email: false
  });

  // Validation function
  const validateEmailOrUsername = (input: string): string | null => {
    if (!input.trim()) {
      return "Email hoặc tên đăng nhập không được để trống";
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    
    const isEmail = emailRegex.test(input);
    const isUsername = usernameRegex.test(input);
    
    if (!isEmail && !isUsername) {
      return "Email hoặc tên đăng nhập không hợp lệ";
    }
    
    return null;
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    
    if (touched.email) {
      setErrors(prev => ({
        ...prev,
        email: validateEmailOrUsername(value)
      }));
    }
  };

  const handleEmailBlur = () => {
    setTouched(prev => ({ ...prev, email: true }));
    setErrors(prev => ({
      ...prev,
      email: validateEmailOrUsername(email)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate email field
    const emailError = validateEmailOrUsername(email);
    
    setErrors({
      email: emailError
    });
    
    setTouched({
      email: true
    });
    
    // If no errors, proceed with password reset
    if (!emailError) {
      console.log('Password reset request for:', email);
      // Add actual password reset logic here
      navigate('/forgot-password-2');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center relative overflow-hidden font-sans">
      
      {/* Mobile Container */}
      <div className="w-[375px] h-[812px] bg-white relative shadow-2xl overflow-hidden flex flex-col">

        {/* Header: Back Button */}
        <div className="my-4">
          <BackButton to="/login" text="Quay lại" />
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto no-scrollbar relative z-10">
          <div className="px-6 pb-8 pt-2">
        
            {/* Title */}
            <div className="mb-4">
              <h2 className="text-center text-3xl font-bold text-[#c93045] mb-8">Đặt lại mật khẩu</h2>
              <p className="text-sm text-gray-600">
                Nhập email hoặc tên tài khoản của bạn.
              </p>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <InputField
                  id="email"
                  label="Email"
                  subLabel="Tên đăng nhập"
                  placeholder="email@gmail.com"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={handleEmailBlur}
                  error={errors.email}
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