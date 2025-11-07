import { useState, useEffect } from 'react';
import BackgroundAnimation from '@/components/BackgroundAnimation';
import MTBHighlightGenerator from '@/components/MTBHighlightGenerator';
import VideoSidebar from '@/components/VideoSidebar';
import { Film, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

interface UploadedVideo {
  id: string;
  url: string;
  file: File;
  timestamp: Date;
  videoPath?: string;
  taskId?: string;
  processingStatus?: 'pending' | 'in_progress' | 'completed' | 'failed';
}

const MTBEditor = () => {
  const navigate = useNavigate();
  const [uploadedVideos, setUploadedVideos] = useState<UploadedVideo[]>([]);
  const [activeVideo, setActiveVideo] = useState<UploadedVideo | null>(null);
  const [isProcessingVideo, setIsProcessingVideo] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Auto-select the last uploaded video if no video is currently active
  useEffect(() => {
    if (!activeVideo && uploadedVideos.length > 0) {
      const lastVideo = uploadedVideos[uploadedVideos.length - 1];
      if (lastVideo.processingStatus === 'completed') {
        setActiveVideo(lastVideo);
        console.log('🚵 Auto-selecting last uploaded video:', lastVideo.videoPath);
      }
    }
  }, [uploadedVideos, activeVideo]);

  // Poll for video processing status
  useEffect(() => {
    const pollInterval = setInterval(() => {
      uploadedVideos.forEach(async (video) => {
        if (video.taskId && video.processingStatus === 'in_progress') {
          try {
            const response = await fetch(`http://localhost:8080/task-status/${video.taskId}`);
            if (response.ok) {
              const data = await response.json();
              if (data.status === 'completed' || data.status === 'failed') {
                setUploadedVideos(prev => prev.map(v =>
                  v.id === video.id
                    ? { ...v, processingStatus: data.status }
                    : v
                ));
              }
            }
          } catch (error) {
            console.error('Error polling task status:', error);
          }
        }
      });
    }, 7000);

    return () => clearInterval(pollInterval);
  }, [uploadedVideos]);

  const handleVideoUpload = async (file: File) => {
    setIsProcessingVideo(true);
    setUploadProgress(0);

    try {
      // Step 1: Upload video
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('http://localhost:8080/upload-video', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload video');
      }

      const uploadData = await uploadResponse.json();
      setUploadProgress(50);

      // Step 2: Process video
      const processResponse = await fetch('http://localhost:8080/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_path: uploadData.video_path
        }),
      });

      if (!processResponse.ok) {
        throw new Error('Failed to start video processing');
      }

      const processData = await processResponse.json();
      setUploadProgress(75);

      // Create video object
      const fileUrl = URL.createObjectURL(file);
      const newVideo: UploadedVideo = {
        id: uploadData.video_path,
        url: fileUrl,
        file,
        timestamp: new Date(),
        videoPath: uploadData.video_path,
        taskId: processData.task_id,
        processingStatus: 'in_progress'
      };

      setUploadedVideos(prev => [...prev, newVideo]);
      console.log('🚵 New MTB video uploaded:', newVideo.videoPath);
      setActiveVideo(newVideo);
      setUploadProgress(100);

    } catch (error) {
      console.error('🚵 Error in video upload/processing:', error);
      const fileUrl = URL.createObjectURL(file);
      const errorVideo: UploadedVideo = {
        id: Date.now().toString(),
        url: fileUrl,
        file,
        timestamp: new Date(),
        processingStatus: 'failed'
      };
      setUploadedVideos(prev => [...prev, errorVideo]);
    } finally {
      setIsProcessingVideo(false);
      setUploadProgress(0);
    }
  };

  const selectVideo = (video: UploadedVideo) => {
    console.log('🚵 User selected video:', video.videoPath);
    setActiveVideo(video);
  };

  const removeVideo = (videoId: string) => {
    const videoToRemove = uploadedVideos.find(v => v.id === videoId);
    if (videoToRemove) {
      URL.revokeObjectURL(videoToRemove.url);
      setUploadedVideos(prev => prev.filter(v => v.id !== videoId));
      if (activeVideo?.id === videoId) {
        setActiveVideo(null);
      }
    }
  };

  return (
    <div className="min-h-screen bg-black text-white font-mono relative w-full overflow-hidden">
      <BackgroundAnimation />

      {/* Mobile-First Layout */}
      <div className="flex flex-col relative z-10 min-h-screen">

        {/* Header with Navigation - Mobile Optimized */}
        <header className="border-b border-zinc-800 bg-black/80 backdrop-blur-sm sticky top-0 z-20">
          <div className="flex items-center justify-between p-3 sm:p-4">
            <div className="flex items-center gap-2 sm:gap-3">
              <Film className="w-6 h-6 sm:w-8 sm:h-8 text-red-500" />
              <div>
                <h1 className="text-lg sm:text-xl font-bold">MTB Video Editor</h1>
                <p className="text-xs text-zinc-400 hidden sm:block">AI-Powered Highlight Generator</p>
              </div>
            </div>

            {/* Switch to Chat Mode - Touch Optimized */}
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              className="h-10 sm:h-12 px-3 sm:px-4 border-zinc-700 hover:bg-zinc-800 touch-manipulation"
            >
              <MessageSquare className="w-5 h-5 mr-0 sm:mr-2" />
              <span className="hidden sm:inline">Chat Mode</span>
            </Button>
          </div>
        </header>

        {/* Main Content - Mobile Scrollable */}
        <div className="flex-1 overflow-y-auto">
          {/* Desktop: Show sidebar, Mobile: Hide */}
          <div className="hidden lg:block">
            <div className="pr-96">
              <div className="p-4 sm:p-6">
                <MTBHighlightGenerator
                  videoPath={activeVideo?.videoPath}
                  videoName={activeVideo?.file.name}
                />
              </div>
            </div>
          </div>

          {/* Mobile: Full width, no sidebar */}
          <div className="lg:hidden">
            <div className="p-4">
              {/* Mobile Video Selector */}
              {uploadedVideos.length > 0 && (
                <div className="mb-6 space-y-3">
                  <label className="text-sm font-semibold text-zinc-400">
                    Select Video ({uploadedVideos.length})
                  </label>
                  <div className="grid gap-2">
                    {uploadedVideos.map((video) => (
                      <button
                        key={video.id}
                        onClick={() => selectVideo(video)}
                        className={`p-3 rounded-lg border-2 transition-all touch-manipulation ${
                          activeVideo?.id === video.id
                            ? 'border-red-500 bg-red-900/20'
                            : 'border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1 text-left">
                            <p className="text-sm font-semibold truncate">{video.file.name}</p>
                            <p className="text-xs text-zinc-400">
                              {video.processingStatus === 'completed' && '✓ Ready'}
                              {video.processingStatus === 'in_progress' && '⏳ Processing...'}
                              {video.processingStatus === 'failed' && '✗ Failed'}
                            </p>
                          </div>
                          {activeVideo?.id === video.id && (
                            <div className="w-2 h-2 rounded-full bg-red-500 ml-2" />
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Upload Button for Mobile */}
              <div className="mb-6">
                <Button
                  onClick={() => document.getElementById('mobile-video-upload')?.click()}
                  variant="outline"
                  className="w-full h-12 border-dashed border-2 border-zinc-700 hover:border-red-500 touch-manipulation"
                  disabled={isProcessingVideo}
                >
                  <Film className="w-5 h-5 mr-2" />
                  {isProcessingVideo ? 'Uploading...' : 'Upload MTB Video'}
                </Button>
                <input
                  id="mobile-video-upload"
                  type="file"
                  accept="video/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleVideoUpload(file);
                  }}
                  className="hidden"
                />
              </div>

              {/* Highlight Generator */}
              <MTBHighlightGenerator
                videoPath={activeVideo?.videoPath}
                videoName={activeVideo?.file.name}
              />
            </div>
          </div>
        </div>

        {/* Mobile Bottom Info Bar */}
        <div className="lg:hidden border-t border-zinc-800 bg-black/80 backdrop-blur-sm p-3">
          <div className="flex items-center justify-between text-xs text-zinc-400">
            <span>{uploadedVideos.length} video{uploadedVideos.length !== 1 ? 's' : ''}</span>
            {activeVideo && (
              <span className="text-red-500">
                {activeVideo.processingStatus === 'completed' ? '● Ready' : '● Processing'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <VideoSidebar
          uploadedVideos={uploadedVideos}
          activeVideo={activeVideo}
          isProcessingVideo={isProcessingVideo}
          uploadProgress={uploadProgress}
          onVideoUpload={handleVideoUpload}
          onSelectVideo={selectVideo}
          onRemoveVideo={removeVideo}
        />
      </div>
    </div>
  );
};

export default MTBEditor;
