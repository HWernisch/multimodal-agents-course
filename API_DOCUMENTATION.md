# 🔌 MTB Video Editor - API Documentation

Complete API reference for the MTB Action Video Editor backend.

**Base URL:** `http://localhost:8080`
**Version:** 0.5.0

---

## Table of Contents

1. [Authentication](#authentication)
2. [Video Management](#video-management)
   - [Upload Video](#upload-video)
   - [Process Video](#process-video)
   - [Delete Media](#delete-media)
3. [Highlight Generation](#highlight-generation)
   - [Generate MTB Highlight](#generate-mtb-highlight)
   - [Get Task Status](#get-task-status)
4. [Highlight Library](#highlight-library)
   - [List Highlights](#list-highlights)
   - [Get Storage Info](#get-storage-info)
5. [MCP Tools](#mcp-tools)
6. [Error Handling](#error-handling)

---

## Authentication

Currently **no authentication required** for local deployment.

For production deployment, consider adding:
- API Keys
- JWT tokens
- OAuth 2.0

---

## Video Management

### Upload Video

Upload a video file for processing.

**Endpoint:** `POST /upload-video`

**Request:**
- Content-Type: `multipart/form-data`
- Body: File field named `file`

**cURL Example:**
```bash
curl -X POST http://localhost:8080/upload-video \
  -F "file=@/path/to/your/mtb-video.mp4"
```

**Response:**
```json
{
  "video_path": "/shared_media/mtb-video_1234567890.mp4",
  "message": "Video uploaded successfully"
}
```

**Status Codes:**
- `200 OK` - Video uploaded successfully
- `400 Bad Request` - No file provided or invalid file type
- `500 Internal Server Error` - Upload failed

---

### Process Video

Process an uploaded video (frame extraction, captions, audio analysis).

**Endpoint:** `POST /process-video`

**Request:**
```json
{
  "video_path": "/shared_media/mtb-video_1234567890.mp4"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8080/process-video \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/shared_media/mtb-video_1234567890.mp4"
  }'
```

**Response:**
```json
{
  "task_id": "task_abc123def456",
  "status": "pending",
  "message": "Video processing started"
}
```

**Status Codes:**
- `200 OK` - Processing started
- `400 Bad Request` - Invalid video path
- `404 Not Found` - Video file not found
- `500 Internal Server Error` - Processing failed to start

**Monitoring:**
Use the `task_id` to poll status via `/task-status/{task_id}` endpoint.

---

### Delete Media

Delete a video or highlight file from the server.

**Endpoint:** `DELETE /media/{file_path:path}`

**Path Parameters:**
- `file_path` - Relative path to file (e.g., `uploads/video.mp4` or `highlights/highlight_123.mp4`)

**Security:**
- Only files under `/shared_media/` can be deleted
- Path traversal attempts (e.g., `../`) are rejected
- Returns 403 Forbidden for unauthorized paths

**cURL Example:**
```bash
curl -X DELETE http://localhost:8080/media/highlights/highlight_1234567890.mp4
```

**Response:**
```json
{
  "message": "File deleted successfully",
  "file_path": "highlights/highlight_1234567890.mp4"
}
```

**Status Codes:**
- `200 OK` - File deleted successfully
- `403 Forbidden` - Path not allowed (security violation)
- `404 Not Found` - File doesn't exist
- `500 Internal Server Error` - Deletion failed

---

## Highlight Generation

### Generate MTB Highlight

Generate a highlight reel from a processed video.

**Endpoint:** `POST /generate-mtb-highlight`

**Request:**
```json
{
  "video_path": "/shared_media/mtb-video_1234567890.mp4",
  "target_duration_seconds": 60,
  "min_action_score": 65,
  "add_transitions": true,
  "use_ffmpeg": true
}
```

**Parameters:**
- `video_path` (required, string) - Path to processed video
- `target_duration_seconds` (required, number) - Desired highlight length (15-300 seconds)
- `min_action_score` (optional, number) - Minimum action score threshold (0-100, default: 60)
- `add_transitions` (optional, boolean) - Add fade transitions (default: true)
- `use_ffmpeg` (optional, boolean) - Use FFmpeg for faster assembly (default: true)

**cURL Example:**
```bash
curl -X POST http://localhost:8080/generate-mtb-highlight \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/shared_media/mtb-video_1234567890.mp4",
    "target_duration_seconds": 60,
    "min_action_score": 65
  }'
```

**Response:**
```json
{
  "task_id": "task_xyz789abc123",
  "status": "in_progress",
  "message": "Highlight generation started",
  "estimated_time_seconds": 120
}
```

**Status Codes:**
- `200 OK` - Generation started
- `400 Bad Request` - Invalid parameters or video not processed
- `404 Not Found` - Video file not found
- `500 Internal Server Error` - Generation failed to start

**Processing Flow:**
1. Detect action highlights (analyze frames + audio)
2. Select best clips (based on scores + diversity)
3. Assemble clips (with optional transitions)
4. Export final MP4 file

**Monitoring:**
Poll `/task-status/{task_id}` every 2-3 seconds until `status: "completed"`

---

### Get Task Status

Check the status of a background task (video processing or highlight generation).

**Endpoint:** `GET /task-status/{task_id}`

**Path Parameters:**
- `task_id` - Task identifier from processing/generation request

**cURL Example:**
```bash
curl http://localhost:8080/task-status/task_xyz789abc123
```

**Response (In Progress):**
```json
{
  "task_id": "task_xyz789abc123",
  "status": "in_progress",
  "progress_percent": 45,
  "message": "Analyzing frame 23/45",
  "started_at": "2025-01-15T10:30:00Z"
}
```

**Response (Completed - Highlight Generation):**
```json
{
  "task_id": "task_xyz789abc123",
  "status": "completed",
  "message": "Highlight reel generated successfully",
  "result": {
    "highlight_path": "/shared_media/highlights/highlight_1234567890.mp4",
    "duration_seconds": 62.5,
    "clips_count": 8,
    "average_action_score": 78.3
  },
  "started_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:32:15Z",
  "duration_seconds": 135
}
```

**Response (Failed):**
```json
{
  "task_id": "task_xyz789abc123",
  "status": "failed",
  "message": "No action clips found above threshold",
  "error": "Minimum score too high (80). Try lowering to 50-60.",
  "started_at": "2025-01-15T10:30:00Z",
  "failed_at": "2025-01-15T10:31:00Z"
}
```

**Status Values:**
- `pending` - Task queued, not started
- `in_progress` - Task running
- `completed` - Task finished successfully
- `failed` - Task failed with error

**Status Codes:**
- `200 OK` - Task found (check `status` field for actual status)
- `404 Not Found` - Task ID not found

**Polling Recommendations:**
- Poll every 2-3 seconds during processing
- Stop polling when status is `completed` or `failed`
- Timeout after 10 minutes for long videos

---

## Highlight Library

### List Highlights

Get a list of all saved highlight reels with metadata.

**Endpoint:** `GET /highlights`

**cURL Example:**
```bash
curl http://localhost:8080/highlights
```

**Response:**
```json
{
  "highlights": [
    {
      "filename": "highlight_1234567890.mp4",
      "path": "/shared_media/highlights/highlight_1234567890.mp4",
      "size_bytes": 15728640,
      "size_mb": 15.0,
      "created_at": "2025-01-15T10:32:15Z",
      "duration_seconds": 62.5,
      "original_video": "mtb-video_1234567890.mp4"
    },
    {
      "filename": "highlight_0987654321.mp4",
      "path": "/shared_media/highlights/highlight_0987654321.mp4",
      "size_bytes": 23068672,
      "size_mb": 22.0,
      "created_at": "2025-01-14T15:20:00Z",
      "duration_seconds": 90.0,
      "original_video": "trail-ride_0987654321.mp4"
    }
  ],
  "count": 2
}
```

**Status Codes:**
- `200 OK` - List retrieved successfully (may be empty array)
- `500 Internal Server Error` - Failed to read directory

**Notes:**
- Sorted by creation time (newest first)
- Includes file metadata (size, date, etc.)
- Links to original video if available

---

### Get Storage Info

Get storage statistics for videos and highlights.

**Endpoint:** `GET /storage-info`

**cURL Example:**
```bash
curl http://localhost:8080/storage-info
```

**Response:**
```json
{
  "videos": {
    "count": 5,
    "total_size_bytes": 524288000,
    "total_size_mb": 500.0,
    "total_size_gb": 0.49
  },
  "highlights": {
    "count": 8,
    "total_size_bytes": 157286400,
    "total_size_mb": 150.0,
    "total_size_gb": 0.15
  },
  "total": {
    "count": 13,
    "total_size_bytes": 681574400,
    "total_size_mb": 650.0,
    "total_size_gb": 0.64
  },
  "latest_highlight": {
    "filename": "highlight_1234567890.mp4",
    "created_at": "2025-01-15T10:32:15Z",
    "size_mb": 15.0
  },
  "oldest_highlight": {
    "filename": "highlight_0000000001.mp4",
    "created_at": "2025-01-10T08:15:00Z",
    "size_mb": 12.5
  }
}
```

**Status Codes:**
- `200 OK` - Statistics retrieved successfully
- `500 Internal Server Error` - Failed to calculate stats

**Use Cases:**
- Display storage usage in UI
- Monitor disk space
- Alert when nearing capacity
- Show user their storage footprint

---

## MCP Tools

The following tools are available via the MCP (Model Context Protocol) server.
They can be called programmatically from the API or used by AI agents.

### Tool: detect_action_highlights

Detect action moments in a processed video.

**Parameters:**
- `video_path` (string) - Path to video
- `target_duration_seconds` (number) - Desired total length
- `min_action_score` (number, optional) - Minimum score threshold (default: 60)

**Returns:**
```json
{
  "highlights": [
    {
      "timestamp": 45.2,
      "duration": 3.0,
      "overall_score": 87.5,
      "action_type": "jumping",
      "motion_score": 92,
      "audio_intensity": 78,
      "caption": "Rider performing jump in mid-air with high speed"
    }
  ],
  "total_clips": 8,
  "total_duration": 26.5
}
```

---

### Tool: assemble_highlight_video

Assemble detected highlights into a final video.

**Parameters:**
- `video_path` (string) - Path to original video
- `highlights` (array) - List of highlight objects from detection
- `output_filename` (string, optional) - Custom output filename
- `add_transitions` (boolean, optional) - Add fade effects (default: true)
- `use_ffmpeg` (boolean, optional) - Use FFmpeg method (default: true)

**Returns:**
```json
{
  "output_path": "/shared_media/highlights/highlight_1234567890.mp4",
  "duration_seconds": 62.5,
  "method_used": "ffmpeg"
}
```

---

### Tool: generate_mtb_highlight_reel

End-to-end highlight generation (combines detect + assemble).

**Parameters:**
- `video_path` (string) - Path to video
- `target_duration_seconds` (number) - Desired length
- `min_action_score` (number, optional) - Score threshold (default: 60)
- `add_transitions` (boolean, optional) - Fade effects (default: true)
- `use_ffmpeg` (boolean, optional) - Assembly method (default: true)

**Returns:**
```json
{
  "highlight_path": "/shared_media/highlights/highlight_1234567890.mp4",
  "duration_seconds": 62.5,
  "clips_selected": 8,
  "average_score": 78.3,
  "clips_details": [...]
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": "Brief error description",
  "detail": "Detailed explanation of what went wrong",
  "status_code": 400
}
```

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid parameters, missing fields |
| 403 | Forbidden | Security violation (path traversal attempt) |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Processing failure, file I/O error |

### Common Errors

**1. Video Not Processed**
```json
{
  "error": "Video not processed",
  "detail": "Please process video first using /process-video endpoint",
  "status_code": 400
}
```

**Solution:** Call `/process-video` and wait for completion before generating highlights.

---

**2. No Clips Found**
```json
{
  "error": "No action clips found",
  "detail": "No clips found above threshold 80. Try lowering min_action_score to 50-60.",
  "status_code": 400
}
```

**Solution:** Lower `min_action_score` parameter (try 50-60 instead of 80).

---

**3. Invalid Video Path**
```json
{
  "error": "Invalid video path",
  "detail": "Path must be under /shared_media/ directory",
  "status_code": 403
}
```

**Solution:** Ensure path starts with `/shared_media/` and doesn't contain `..` (path traversal).

---

**4. File Not Found**
```json
{
  "error": "File not found",
  "detail": "Video file does not exist at specified path",
  "status_code": 404
}
```

**Solution:** Verify video was uploaded successfully and path is correct.

---

**5. Processing Timeout**
```json
{
  "error": "Processing timeout",
  "detail": "Video processing took longer than 30 minutes",
  "status_code": 500
}
```

**Solution:** Video might be too long. Try with shorter video or increase timeout.

---

## Rate Limiting

Currently **no rate limiting** for local deployment.

For production, consider implementing:
- Per-IP rate limiting (e.g., 100 requests/hour)
- Per-user rate limiting with API keys
- Concurrent processing limits (e.g., max 3 videos simultaneously)

---

## CORS Configuration

**Current:** CORS enabled for all origins (`*`)

**Frontend allowed:** `http://localhost:3000`

For production, restrict to specific domains:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

---

## Best Practices

### 1. Polling
```javascript
async function pollTaskStatus(taskId) {
  while (true) {
    const response = await fetch(`/task-status/${taskId}`);
    const data = await response.json();

    if (data.status === 'completed' || data.status === 'failed') {
      return data;
    }

    await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2s
  }
}
```

### 2. Error Handling
```javascript
try {
  const response = await fetch('/generate-mtb-highlight', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path, target_duration_seconds })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  const data = await response.json();
  // Handle success
} catch (error) {
  console.error('Highlight generation failed:', error.message);
  // Show user-friendly error
}
```

### 3. File Upload
```javascript
const formData = new FormData();
formData.append('file', videoFile);

const response = await fetch('/upload-video', {
  method: 'POST',
  body: formData // Don't set Content-Type header, browser will set it
});
```

---

## Performance Tips

1. **Use FFmpeg for assembly** - 5-10x faster than MoviePy
   ```json
   { "use_ffmpeg": true }
   ```

2. **Adjust frame count** - Fewer frames = faster processing
   - Default: 45 frames
   - For quick tests: 20-30 frames
   - For high quality: 60+ frames

3. **Batch processing** - Process multiple videos sequentially to avoid memory issues

4. **Cache processed videos** - Don't reprocess the same video multiple times

---

## Example Workflows

### Complete Workflow: Upload → Process → Generate → Download

```bash
# 1. Upload video
VIDEO_PATH=$(curl -X POST http://localhost:8080/upload-video \
  -F "file=@mtb-ride.mp4" | jq -r '.video_path')

echo "Uploaded to: $VIDEO_PATH"

# 2. Process video
TASK_ID=$(curl -X POST http://localhost:8080/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_path\": \"$VIDEO_PATH\"}" | jq -r '.task_id')

echo "Processing task: $TASK_ID"

# 3. Wait for processing to complete
while true; do
  STATUS=$(curl http://localhost:8080/task-status/$TASK_ID | jq -r '.status')
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Processing failed!"
    exit 1
  fi

  sleep 3
done

# 4. Generate highlight
TASK_ID=$(curl -X POST http://localhost:8080/generate-mtb-highlight \
  -H "Content-Type: application/json" \
  -d "{
    \"video_path\": \"$VIDEO_PATH\",
    \"target_duration_seconds\": 60,
    \"min_action_score\": 65
  }" | jq -r '.task_id')

echo "Generating highlight: $TASK_ID"

# 5. Wait for generation to complete
while true; do
  RESULT=$(curl http://localhost:8080/task-status/$TASK_ID)
  STATUS=$(echo $RESULT | jq -r '.status')
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    HIGHLIGHT_PATH=$(echo $RESULT | jq -r '.result.highlight_path')
    echo "✅ Highlight ready: $HIGHLIGHT_PATH"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "❌ Generation failed!"
    exit 1
  fi

  sleep 3
done

# 6. Download highlight (via browser or file system access)
echo "Download at: http://localhost:8080/media/${HIGHLIGHT_PATH#/shared_media/}"
```

---

## Support

- **Documentation:** [README.md](README.md)
- **Technical Details:** [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md)
- **Setup Guide:** [QUICKSTART.md](QUICKSTART.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Issues:** GitHub Issues

---

**API Version:** 0.5.0
**Last Updated:** 2025-01-XX
**Maintained by:** MTB Video Editor Team
