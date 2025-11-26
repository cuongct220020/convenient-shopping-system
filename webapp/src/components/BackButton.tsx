import { Link } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';

interface BackButtonProps {
  to?: string;
  text?: string;
  className?: string;
}

/**
 * BackButton Component
 * A reusable back navigation button with customizable text and destination
 */
export const BackButton = ({
  to = "/",
  text = "Trang chủ",
  className = ""
}: BackButtonProps) => {
  return (
    <div className="px-4 py-2 flex items-center">
      <Link 
        to={to} 
        className={`flex items-center text-[#c93045] font-bold text-sm hover:opacity-80 ${className}`}
      >
        <ChevronLeft size={20} strokeWidth={3} />
        <span className="ml-1">{text}</span>
      </Link>
    </div>
  );
};