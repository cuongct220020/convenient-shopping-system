import { useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import { Button } from '../components/Button';

export default function ForgotPasswordNotification() {
  const navigate = useNavigate();

  const handleClose = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center relative overflow-hidden font-sans">
      
      {/* Mobile Container */}
      <div className="w-[375px] h-[812px] bg-gray-700 relative flex items-center justify-center px-6">
        
        {/* Success Card */}
        <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full text-center">
          
          {/* Title */}
          <h2 className="text-xl font-bold text-gray-800 mb-6">
            Mật khẩu đã thay đổi
          </h2>
          
          {/* Success Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center">
              <CheckCircle size={48} className="text-white" strokeWidth={2.5} />
            </div>
          </div>
          
          {/* Message */}
          <p className="text-sm text-gray-600 mb-8 leading-relaxed">
            Mật khẩu đặt lại thành công, bạn vui lòng đăng nhập bằng mật khẩu mới
          </p>
          
          {/* Close Button */}
          <Button 
            variant="primary" 
            size="fit" 
            onClick={handleClose}
          >
            Đóng
          </Button>
        </div>
      </div>
    </div>
  );
}