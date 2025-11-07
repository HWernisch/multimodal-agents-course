import { useNavigate } from 'react-router-dom';
import { Film } from 'lucide-react';
import { Button } from '@/components/ui/button';

const ChatHeader = () => {
  const navigate = useNavigate();

  return (
    <div className="border-b border-red-900 bg-black p-3 sm:p-4">
      <div className="max-w-4xl mx-auto flex items-center justify-between gap-3">
        <div className="flex-1">
          <h1 className="text-xl sm:text-2xl font-bold text-red-500">KUBRICK AI</h1>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">HAL 9000 COMPUTER SYSTEM</p>
        </div>
        <Button
          onClick={() => navigate('/mtb-editor')}
          variant="outline"
          className="h-10 sm:h-12 px-3 sm:px-4 border-red-900 hover:bg-red-900/20 touch-manipulation"
        >
          <Film className="w-5 h-5 mr-0 sm:mr-2" />
          <span className="hidden sm:inline">MTB Editor</span>
        </Button>
        <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse hidden sm:block"></div>
      </div>
    </div>
  );
};

export default ChatHeader;
