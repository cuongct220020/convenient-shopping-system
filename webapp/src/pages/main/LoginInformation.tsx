import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../../components/BackButton';
import { Button } from '../../components/Button';
import { Pencil, Lock } from 'lucide-react';

const LoginInformation = () => {
  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">

      {/* Back Navigation */}
      <BackButton onClick={() => window.history.back()} text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-8">
        Thông tin đăng nhập
      </h1>

      <div className="flex flex-col gap-8">
        
        {/* Email Section */}
        <div>
          <h3 className="font-bold text-black mb-2 text-base">Email</h3>
          <div className="flex items-center">
            <Pencil size={18} className="text-black shrink-0" fill="black" />
            <span className="ml-3 text-gray-800 text-base">
              your-email@gmail.com
            </span>
          </div>
        </div>

        {/* Username Section */}
        <div>
          <h3 className="font-bold text-black mb-2 text-base">Tên đăng nhập</h3>
          <div className="flex items-center">
            <Pencil size={18} className="text-black shrink-0" fill="black" />
            <span className="ml-3 text-gray-800 text-base">
              linhsieungausrp3z
            </span>
          </div>
        </div>

        {/* Password Section */}
        <div>
          <h3 className="font-bold text-black mb-2 text-base">Mật khẩu</h3>
          <div>
            <Button
              variant="secondary"
              icon={Lock}
              size="fit"
            >
              Đổi mật khẩu
            </Button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default LoginInformation;