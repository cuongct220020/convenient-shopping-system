import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { OPTInput } from '../../../components/OPTInput';
import { NotificationCard } from '../../../components/NotificationCard';
import { RefreshCcw, CheckCircle, X } from 'lucide-react';
import { userService } from '../../../services/user';

const Authentication = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Get newEmail from navigation state
  const { newEmail, returnTo } = location.state || { newEmail: '', returnTo: '/main/profile/login-information' };

  useEffect(() => {
    if (!newEmail) {
      navigate(returnTo);
    }
  }, [newEmail, navigate, returnTo]);

  // Countdown timer for resend
  useEffect(() => {
    if (countdown > 0 && !canResend) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0 && !canResend) {
      setCanResend(true);
    }
  }, [countdown, canResend]);

  const handleOtpComplete = (code: string) => {
    setOtpCode(code);
  };

  const handleResendOtp = () => {
    if (!canResend || !newEmail) return;

    setCountdown(60);
    setCanResend(false);
    setOtpCode('');

    userService.requestEmailChange(newEmail).match(
      () => {
        // OTP resent successfully
      },
      () => {
        setErrorMessage('Không thể gửi lại mã OTP. Vui lòng thử lại.');
        setShowErrorModal(true);
      }
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode.length !== 6 || !newEmail) {
      alert('Vui lòng nhập đủ 6 số.');
      return;
    }

    setIsLoading(true);

    userService.confirmEmailChange(newEmail, otpCode).match(
      () => {
        setIsLoading(false);
        setShowSuccessModal(true);
      },
      () => {
        setIsLoading(false);
        setErrorMessage('Mã OTP không đúng hoặc đã hết hạn. Vui lòng thử lại.');
        setShowErrorModal(true);
      }
    );
  };

  const formatCountdown = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">
      {/* Back Navigation */}
      <BackButton to={returnTo} text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-2">
        Xác nhận thay đổi email
      </h1>

      {/* Description */}
      <form onSubmit={handleSubmit} className="max-w-sm mx-auto">
        {/* Description Text */}
        <p className="mb-6 text-justify text-sm leading-relaxed text-gray-700">
          Vui lòng nhập mã xác nhận 6 chữ số vừa được gửi đến email <strong>{newEmail}</strong> để hoàn tất việc thay đổi email.
        </p>

        {/* OTP Input Component */}
        <div className="mb-8 px-2">
          <OPTInput length={6} onComplete={handleOtpComplete} />
        </div>

        {/* Submit Button */}
        <div className="mb-6">
          <Button
            type="submit"
            variant={isLoading ? 'disabled' : 'primary'}
            size="fit"
          >
            {isLoading ? 'Đang xác nhận...' : 'Xác nhận'}
          </Button>
        </div>

        {/* Resend Timer */}
        <button
          type="button"
          className={`flex w-full items-center justify-center text-sm transition-colors ${
            canResend
              ? 'text-[#C3485C] hover:text-[#a0283a]'
              : 'text-gray-400 cursor-not-allowed'
          }`}
          onClick={handleResendOtp}
          disabled={!canResend}
        >
          <RefreshCcw size={16} className="mr-2" />
          <span>
            {canResend
              ? 'Gửi lại mã'
              : `Gửi lại mã ${formatCountdown(countdown)}`}
          </span>
        </button>

        {/* Bottom Spacer */}
        <div className="h-16 sm:h-20"></div>
      </form>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <NotificationCard
            title="Thay đổi email thành công!"
            message="Email của bạn đã được thay đổi thành công."
            iconBgColor="bg-green-500"
            buttonText="Hoàn tất"
            buttonIcon={CheckCircle}
            onButtonClick={() => navigate(returnTo)}
          />
        </div>
      )}

      {/* Error Modal */}
      {showErrorModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <NotificationCard
            title="Xác thực thất bại"
            message={errorMessage}
            iconBgColor="bg-red-500"
            buttonText="Thử lại"
            buttonIcon={RefreshCcw}
            onButtonClick={() => {
              setShowErrorModal(false);
              setOtpCode('');
            }}
            button2Text="Hủy"
            button2Icon={X}
            onButton2Click={() => {
              setShowErrorModal(false);
              navigate(returnTo);
            }}
          />
        </div>
      )}
    </div>
  );
};

export default Authentication;
