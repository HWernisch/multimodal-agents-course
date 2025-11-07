import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Progress } from '@/components/ui/progress';
import { Play, Download, Zap, Film, Clock, TrendingUp } from 'lucide-react';

interface MTBHighlightGeneratorProps {
  videoPath?: string;
  videoName?: string;
}

interface GenerationStatus {
  status: 'idle' | 'detecting' | 'assembling' | 'completed' | 'error';
  message: string;
  progress: number;
}

export default function MTBHighlightGenerator({ videoPath, videoName }: MTBHighlightGeneratorProps) {
  // State
  const [targetDuration, setTargetDuration] = useState(60); // seconds
  const [minActionScore, setMinActionScore] = useState(60);
  const [status, setStatus] = useState<GenerationStatus>({
    status: 'idle',
    message: '',
    progress: 0
  });
  const [taskId, setTaskId] = useState<string | null>(null);
  const [highlightVideoPath, setHighlightVideoPath] = useState<string | null>(null);
  const [numHighlights, setNumHighlights] = useState<number>(0);

  // Format duration helper
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Poll task status
  useEffect(() => {
    if (!taskId || status.status === 'completed' || status.status === 'error') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8080/task-status/${taskId}`);
        if (response.ok) {
          const data = await response.json();

          if (data.status === 'completed') {
            setStatus({
              status: 'completed',
              message: `Highlight reel ready! ${data.num_highlights || 0} clips selected.`,
              progress: 100
            });
            setHighlightVideoPath(data.output_path);
            setNumHighlights(data.num_highlights || 0);
            setTaskId(null);
          } else if (data.status === 'failed' || data.status === 'error') {
            setStatus({
              status: 'error',
              message: data.message || 'Generation failed',
              progress: 0
            });
            setTaskId(null);
          } else if (data.message) {
            // Update progress message
            setStatus(prev => ({
              ...prev,
              message: data.message
            }));
          }
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, status.status]);

  // Generate highlight reel
  const handleGenerate = async () => {
    if (!videoPath) {
      setStatus({
        status: 'error',
        message: 'Please upload and process a video first',
        progress: 0
      });
      return;
    }

    setStatus({
      status: 'detecting',
      message: 'Analyzing video for action moments...',
      progress: 10
    });

    try {
      // Call the generate-mtb-highlight-reel endpoint
      // Note: This endpoint needs to be created in the API (Phase 3 extension)
      // For now, we'll simulate with direct MCP tool calls if available

      const response = await fetch('http://localhost:8080/generate-mtb-highlight', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_path: videoPath,
          target_duration_seconds: targetDuration,
          min_action_score: minActionScore,
          use_ffmpeg: true
        })
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = await response.json();

      if (data.task_id) {
        // Background task started
        setTaskId(data.task_id);
        setStatus({
          status: 'detecting',
          message: 'Processing started...',
          progress: 25
        });
      } else if (data.output_path) {
        // Direct response (no background task)
        setStatus({
          status: 'completed',
          message: `Highlight reel ready! ${data.num_highlights || 0} clips selected.`,
          progress: 100
        });
        setHighlightVideoPath(data.output_path);
        setNumHighlights(data.num_highlights || 0);
      }
    } catch (error) {
      console.error('Error generating highlight:', error);
      setStatus({
        status: 'error',
        message: 'Failed to generate highlight reel. Make sure the video is processed first.',
        progress: 0
      });
    }
  };

  // Download highlight video
  const handleDownload = () => {
    if (highlightVideoPath) {
      const filename = highlightVideoPath.split('/').pop() || 'highlight.mp4';
      const link = document.createElement('a');
      link.href = `http://localhost:8080/media/${highlightVideoPath}`;
      link.download = filename;
      link.click();
    }
  };

  // Reset
  const handleReset = () => {
    setStatus({ status: 'idle', message: '', progress: 0 });
    setHighlightVideoPath(null);
    setNumHighlights(0);
    setTaskId(null);
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Header - Mobile Optimized */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-3">
          <Film className="w-8 h-8 sm:w-10 sm:h-10 text-red-500" />
          <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-red-500 to-red-600 bg-clip-text text-transparent">
            MTB Highlight Generator
          </h2>
        </div>
        <p className="text-sm sm:text-base text-zinc-400">
          AI-powered action detection for your mountainbike videos
        </p>
      </div>

      {/* Video Info */}
      {videoPath && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center gap-2 text-sm text-zinc-400">
            <Play className="w-4 h-4 text-red-500" />
            <span className="truncate">{videoName || videoPath.split('/').pop()}</span>
          </div>
        </div>
      )}

      {/* Controls - Mobile First with Large Touch Targets */}
      <div className="space-y-6 bg-zinc-900 border border-zinc-800 rounded-lg p-4 sm:p-6">

        {/* Target Duration Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-base sm:text-lg font-semibold flex items-center gap-2">
              <Clock className="w-5 h-5 text-red-500" />
              Target Duration
            </label>
            <span className="text-2xl sm:text-3xl font-bold text-red-500 min-w-[80px] text-right">
              {formatDuration(targetDuration)}
            </span>
          </div>

          <Slider
            value={[targetDuration]}
            onValueChange={(v) => setTargetDuration(v[0])}
            min={15}
            max={300}
            step={5}
            disabled={status.status === 'detecting' || status.status === 'assembling'}
            className="touch-manipulation"
          />

          <div className="flex justify-between text-xs sm:text-sm text-zinc-500">
            <span>15s</span>
            <span>5min</span>
          </div>
        </div>

        {/* Min Action Score Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-base sm:text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-red-500" />
              Action Intensity
            </label>
            <span className="text-2xl sm:text-3xl font-bold text-red-500 min-w-[60px] text-right">
              {minActionScore}
            </span>
          </div>

          <Slider
            value={[minActionScore]}
            onValueChange={(v) => setMinActionScore(v[0])}
            min={30}
            max={90}
            step={5}
            disabled={status.status === 'detecting' || status.status === 'assembling'}
            className="touch-manipulation"
          />

          <div className="flex justify-between text-xs sm:text-sm text-zinc-500">
            <span>More clips</span>
            <span>Only epic moments</span>
          </div>

          <p className="text-xs sm:text-sm text-zinc-400">
            {minActionScore < 50 && "Low threshold - includes calmer segments"}
            {minActionScore >= 50 && minActionScore < 70 && "Balanced - good mix of action"}
            {minActionScore >= 70 && "High threshold - only intense action!"}
          </p>
        </div>
      </div>

      {/* Generation Status */}
      {status.status !== 'idle' && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 sm:p-6 space-y-4">
          {/* Progress Bar */}
          {status.progress > 0 && status.status !== 'error' && (
            <div className="space-y-2">
              <Progress value={status.progress} className="h-3" />
              <p className="text-sm text-center text-zinc-400">{status.progress}%</p>
            </div>
          )}

          {/* Status Message */}
          <div className={`p-4 rounded-lg ${
            status.status === 'error' ? 'bg-red-900/20 border border-red-800' :
            status.status === 'completed' ? 'bg-green-900/20 border border-green-800' :
            'bg-blue-900/20 border border-blue-800'
          }`}>
            <p className={`text-sm sm:text-base text-center ${
              status.status === 'error' ? 'text-red-400' :
              status.status === 'completed' ? 'text-green-400' :
              'text-blue-400'
            }`}>
              {status.message}
            </p>
          </div>

          {/* Highlight Stats */}
          {status.status === 'completed' && numHighlights > 0 && (
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="bg-zinc-800 rounded-lg p-3">
                <p className="text-xs text-zinc-400">Clips Selected</p>
                <p className="text-2xl font-bold text-red-500">{numHighlights}</p>
              </div>
              <div className="bg-zinc-800 rounded-lg p-3">
                <p className="text-xs text-zinc-400">Total Duration</p>
                <p className="text-2xl font-bold text-red-500">{formatDuration(targetDuration)}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons - Large Touch Targets (min 44px height) */}
      <div className="space-y-3">
        {status.status === 'idle' || status.status === 'error' ? (
          <Button
            onClick={handleGenerate}
            disabled={!videoPath}
            className="w-full h-14 sm:h-16 text-lg sm:text-xl font-bold bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 disabled:opacity-50 touch-manipulation"
          >
            <Zap className="w-6 h-6 mr-2" />
            Generate Highlight Reel
          </Button>
        ) : status.status === 'completed' ? (
          <div className="space-y-3">
            <Button
              onClick={handleDownload}
              className="w-full h-14 sm:h-16 text-lg sm:text-xl font-bold bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 touch-manipulation"
            >
              <Download className="w-6 h-6 mr-2" />
              Download Highlight Video
            </Button>
            <Button
              onClick={handleReset}
              variant="outline"
              className="w-full h-12 sm:h-14 text-base sm:text-lg border-zinc-700 hover:bg-zinc-800 touch-manipulation"
            >
              Create Another Highlight
            </Button>
          </div>
        ) : (
          <Button
            disabled
            className="w-full h-14 sm:h-16 text-lg sm:text-xl font-bold bg-zinc-800 cursor-not-allowed"
          >
            <div className="animate-spin mr-2 h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
            Processing...
          </Button>
        )}
      </div>

      {/* Help Text */}
      <div className="text-xs sm:text-sm text-zinc-500 text-center space-y-1 px-2">
        <p>📱 Tip: Upload your MTB action cam footage and let AI find the best moments!</p>
        <p>🎬 The AI analyzes speed, jumps, tricks, and audio to create your highlight reel.</p>
      </div>
    </div>
  );
}
