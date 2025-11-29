import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { RefreshCcw } from 'lucide-react'; // Importing an icon for the resend button
import loginBg from '../assets/login-bg.png';
import { Button } from '../components/Button';
import { BackButton } from '../components/BackButton';
import { OtpInput } from '../components/OtpInput';

export default function LoginAuthentication() {
  const navigate = useNavigate();
  const location = useLocation();
  const [otpCode, setOtpCode] = useState('');

  // Retrieve username passed from the Login page state, or use a placeholder
  // In a real app, ensure you handle the case where state is undefined safely.
  const username = location.state?.username || "User";

  const handleOtpComplete = (code: string) => {
    setOtpCode(code);
    console.log('OTP Entered:', code);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode.length === 6) {
        console.log("Submitting OTP:", otpCode);
        // Add actual verification logic here
        navigate('/forgot-password-2')
    } else {
        alert("Vui lòng nhập đủ 6 số.");
    }
  };

  return (
    // Reusing the main container styling from Login.tsx for consistency
    <div className="min-h-screen bg-gray-100 flex justify-center items-center relative overflow-hidden font-sans">

      {/* Mobile Container */}
      <div className="w-[375px] h-[812px] bg-white relative shadow-2xl overflow-hidden flex flex-col">

        {/* Header: Back Button */}
        <div className="my-4">
          {/* Using existing BackButton component */}
          <BackButton to="/forgot-password-1" text="Quay lại" />
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto no-scrollbar relative z-10">
          <div className="px-6 pt-4 pb-8">
            <form onSubmit={handleSubmit}>
              {/* Title */}
              <h2 className="text-3xl font-bold text-[#c93045] text-center mb-6">
                Xác thực email
              </h2>

              {/* Description Text */}
              {/* Using text-justify to match the block text look in image_0.png */}
              <p className="text-gray-700 text-sm leading-relaxed text-justify mb-4">
                Chúng tôi vừa gửi mã xác nhận 6 chữ số đến email của bạn (nếu email đã được đăng ký). Bạn vui lòng nhập mã để tiếp tục
              </p>

              {/* New OTP Input Component */}
              <div className="px-2 mb-8">
                   <OtpInput length={6} onComplete={handleOtpComplete} />
              </div>

              {/* Submit Button */}
              {/* Using existing Button component with fit size */}
              <div className="mb-6">
                <Button type="submit" variant="primary" size="fit">
                  Xác nhận
                </Button>
              </div>

              {/* Resend Timer */}
              <button type="button" className="w-full flex items-center justify-center text-gray-500 text-sm hover:text-[#c93045] transition-colors">
                  <RefreshCcw size={16} className="mr-2" />
                  <span>Gửi lại mã 00:59</span>
              </button>

              {/* Bottom Spacer */}
              <div className="h-20"></div>
            </form>
          </div>
        </div>

        {/* Background Image Decoration (Bottom) - Same as Login page */}
        <div className="absolute bottom-0 left-0 right-0 h-80 z-0 pointer-events-none">
           <div className="absolute inset-0 bg-gradient-to-t from-white/10 via-white/40 to-white z-10"></div>
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