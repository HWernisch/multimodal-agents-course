import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Download, Trash2, Film, HardDrive, RefreshCw } from 'lucide-react';

interface Highlight {
  filename: string;
  path: string;
  size: number;
  size_mb: number;
  created: number;
  original_video: string;
}

interface StorageInfo {
  total_files: number;
  total_size_mb: number;
  videos: {
    count: number;
    size_mb: number;
  };
  highlights: {
    count: number;
    size_mb: number;
  };
}

export default function HighlightLibrary() {
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [storageInfo, setStorageInfo] = useState<StorageInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // Load highlights
      const highlightsRes = await fetch('http://localhost:8080/highlights');
      if (highlightsRes.ok) {
        const data = await highlightsRes.json();
        setHighlights(data.highlights || []);
      }

      // Load storage info
      const storageRes = await fetch('http://localhost:8080/storage-info');
      if (storageRes.ok) {
        const data = await storageRes.json();
        setStorageInfo(data);
      }
    } catch (error) {
      console.error('Error loading highlight library:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDownload = (highlight: Highlight) => {
    const link = document.createElement('a');
    link.href = `http://localhost:8080/media/${highlight.path}`;
    link.download = highlight.filename;
    link.click();
  };

  const handleDelete = async (highlight: Highlight) => {
    if (!confirm(`Delete highlight "${highlight.filename}"?\n\nThis cannot be undone.`)) {
      return;
    }

    setDeletingId(highlight.filename);
    try {
      const response = await fetch(`http://localhost:8080/media/${highlight.path}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        // Reload data
        await loadData();
      } else {
        alert('Failed to delete highlight');
      }
    } catch (error) {
      console.error('Error deleting highlight:', error);
      alert('Error deleting highlight');
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Film className="w-6 h-6 sm:w-8 sm:h-8 text-red-500" />
          <div>
            <h2 className="text-xl sm:text-2xl font-bold">Highlight Library</h2>
            <p className="text-sm text-zinc-400">Manage your saved highlights</p>
          </div>
        </div>
        <Button
          onClick={loadData}
          variant="outline"
          className="h-10 border-zinc-700 hover:bg-zinc-800 touch-manipulation"
          disabled={isLoading}
        >
          <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {/* Storage Info */}
      {storageInfo && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <HardDrive className="w-5 h-5 text-red-500" />
            <h3 className="font-semibold">Storage Usage</h3>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-zinc-800 rounded p-3 text-center">
              <p className="text-xs text-zinc-400">Total Files</p>
              <p className="text-2xl font-bold text-red-500">{storageInfo.total_files}</p>
            </div>
            <div className="bg-zinc-800 rounded p-3 text-center">
              <p className="text-xs text-zinc-400">Total Size</p>
              <p className="text-2xl font-bold text-red-500">{storageInfo.total_size_mb}</p>
              <p className="text-xs text-zinc-500">MB</p>
            </div>
            <div className="bg-zinc-800 rounded p-3 text-center">
              <p className="text-xs text-zinc-400">Videos</p>
              <p className="text-2xl font-bold text-blue-500">{storageInfo.videos.count}</p>
              <p className="text-xs text-zinc-500">{storageInfo.videos.size_mb} MB</p>
            </div>
            <div className="bg-zinc-800 rounded p-3 text-center">
              <p className="text-xs text-zinc-400">Highlights</p>
              <p className="text-2xl font-bold text-green-500">{storageInfo.highlights.count}</p>
              <p className="text-xs text-zinc-500">{storageInfo.highlights.size_mb} MB</p>
            </div>
          </div>
        </div>
      )}

      {/* Highlights List */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Film className="w-5 h-5 text-red-500" />
          Saved Highlights ({highlights.length})
        </h3>

        {isLoading ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
            <div className="animate-spin mx-auto w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full mb-3"></div>
            <p className="text-zinc-400">Loading highlights...</p>
          </div>
        ) : highlights.length === 0 ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
            <Film className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
            <p className="text-zinc-400">No highlights yet</p>
            <p className="text-sm text-zinc-500 mt-1">Generate your first highlight reel!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {highlights.map((highlight) => (
              <div
                key={highlight.filename}
                className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold truncate text-sm sm:text-base">
                      {highlight.filename}
                    </h4>
                    <div className="flex flex-wrap gap-3 mt-2 text-xs sm:text-sm text-zinc-400">
                      <span className="flex items-center gap-1">
                        <Film className="w-4 h-4" />
                        {highlight.original_video}
                      </span>
                      <span>{highlight.size_mb} MB</span>
                      <span>{formatDate(highlight.created)}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleDownload(highlight)}
                      variant="outline"
                      className="flex-1 sm:flex-none h-10 border-green-700 hover:bg-green-900/20 text-green-500 touch-manipulation"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">Download</span>
                    </Button>
                    <Button
                      onClick={() => handleDelete(highlight)}
                      variant="outline"
                      className="flex-1 sm:flex-none h-10 border-red-700 hover:bg-red-900/20 text-red-500 touch-manipulation"
                      disabled={deletingId === highlight.filename}
                    >
                      {deletingId === highlight.filename ? (
                        <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4 mr-2" />
                          <span className="hidden sm:inline">Delete</span>
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help Text */}
      {highlights.length > 0 && (
        <div className="text-xs sm:text-sm text-zinc-500 text-center">
          <p>💾 Highlights are saved permanently until you delete them manually.</p>
          <p>🗑️ Use the delete button to free up disk space.</p>
        </div>
      )}
    </div>
  );
}
