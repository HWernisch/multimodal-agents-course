# 🚀 MTB Video Editor - Deployment Options & Performance Comparison

Complete guide for deploying the MTB Video Editor across different infrastructure options.

**Version:** 0.5.0
**Last Updated:** 2025-01-XX

---

## 📊 Quick Comparison

| Deployment | Setup | Cost/Month | Cost/Video | Performance | Scaling | Best For |
|------------|-------|------------|------------|-------------|---------|----------|
| **Local (Current)** | ✅ Simple | $0 | $0.09 | 1 video at a time | ❌ None | MVP testing, < 10 videos/month |
| **VServer + Celery** | ⚠️ Medium | $80-160 | $0.12 | 4 parallel, 16-24/hour | ⚠️ Manual | 100-1000 videos/month, predictable load |
| **GCP Cloud Run** | ⚠️⚠️ Complex | $0 | $0.19 | Unlimited, 1000+/hour | ✅ Automatic | > 1000 videos/month, bursty loads |

---

## Option 1: Current Setup (Local Docker)

### Architecture

```
┌──────────────────────────────────────┐
│  Docker Compose (Local Machine)      │
│  ┌─────────────────────────────┐    │
│  │  kubrick-ui (Port 3000)     │    │
│  │  kubrick-api (Port 8080)    │    │
│  │  kubrick-mcp (Port 9090)    │    │
│  └─────────────────────────────┘    │
│  FastAPI BackgroundTasks             │
│  (Single worker, sequential)         │
└──────────────────────────────────────┘
```

### Performance

| Metric | Value |
|--------|-------|
| **Concurrent Videos** | 1 |
| **Processing Speed** | 1.5x video duration |
| **Throughput** | 4-6 videos/hour (10 min videos) |
| **Max Video Length** | Limited by patience (~30 min) |

**Example: 10-minute video**
- Processing time: ~15 minutes
- OpenAI API cost: $0.09
- Total cost: **$0.09/video**

### Pros
- ✅ Zero infrastructure cost
- ✅ Simple setup (docker-compose up)
- ✅ Full control & privacy
- ✅ Perfect for development/testing

### Cons
- ❌ Only 1 video at a time
- ❌ Worker blocking (API unresponsive during processing)
- ❌ No persistence (state lost on restart)
- ❌ Cannot scale

### Ideal For
- Local testing & development
- < 10 videos per month
- Single user
- MVP validation

---

## Option 2: VServer + Celery (Dedicated Server)

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│  VPS/Dedicated Server (Hetzner CCX33, 8 vCPU, 16GB RAM)   │
│  ┌──────────────────────────────────────────────────┐     │
│  │  Docker Compose                                   │     │
│  │  ┌────────────┐  ┌──────────┐  ┌─────────────┐ │     │
│  │  │ API (2GB)  │  │ Redis    │  │ MCP Server  │ │     │
│  │  └────────────┘  └──────────┘  └─────────────┘ │     │
│  │                                                  │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  Celery Workers (4 workers)              │  │     │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │     │
│  │  │  │Worker 1 │ │Worker 2 │ │Worker 3 │...│  │     │
│  │  │  │2 vCPU   │ │2 vCPU   │ │2 vCPU   │   │  │     │
│  │  │  │4GB RAM  │ │4GB RAM  │ │4GB RAM  │   │  │     │
│  │  │  └─────────┘ └─────────┘ └─────────┘   │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
```

### Performance Analysis

#### Hardware: 8 vCPU, 16GB RAM

**Processing Breakdown (10 min video per worker):**
```
Frame Extraction:        30s  (1 vCPU, parallelizable)
Caption Generation:     180s  (API calls, network bound)
Audio Transcription:    120s  (API call, network bound)
Audio Analysis:          60s  (1-2 vCPU, local compute)
ActionScore:             10s  (CPU negligible)
Video Assembly (FFmpeg): 120s (1-2 vCPU, CPU intensive)
───────────────────────────────
Total per video:        ~8-9 minutes
```

**Concurrency with 4 Workers:**
- 4 videos processing simultaneously
- Each worker: 2 vCPU, 4GB RAM
- Total throughput: **~16-24 videos/hour**
- CPU utilization: 90-100%
- RAM utilization: 14-16GB

**Bottlenecks:**
1. **OpenAI API Rate Limits:**
   - Whisper: 50 requests/minute
   - **Actual bottleneck:** ~50 videos/hour max

2. **CPU (FFmpeg):**
   - Each FFmpeg job uses 1-2 vCPU
   - With 8 vCPU: Max 4 concurrent FFmpeg = 4 videos

3. **Disk I/O:**
   - NVMe SSD: ~2000 MB/s read/write
   - 10 min 1080p video: ~500MB
   - Not a bottleneck for 4 workers

**Optimal Configuration:**
```python
# celeryconfig.py
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'

# 4 workers, each processing 1 video at a time
worker_concurrency = 1
worker_prefetch_multiplier = 1

# Timeouts
task_time_limit = 1800  # 30 minutes hard limit
task_soft_time_limit = 1500  # 25 minutes soft limit

# Memory management
worker_max_tasks_per_child = 10  # Restart after 10 videos (prevent leaks)
```

### Cost Analysis

**Server Options:**

| Provider | Server | vCPU | RAM | Storage | Cost/Month |
|----------|--------|------|-----|---------|------------|
| Hetzner | CCX33 | 8 | 16GB | 240GB SSD | €80 (~$87) |
| DigitalOcean | CPU-Optimized 8GB | 8 | 16GB | 100GB SSD | $160 |
| AWS EC2 | c6i.2xlarge | 8 | 16GB | 50GB EBS | ~$200 |
| Linode | Dedicated 16GB | 8 | 16GB | 320GB SSD | $115 |

**Using Hetzner CCX33 ($87/month):**

```
Videos/Month | Cost/Video | Total Cost
─────────────┼────────────┼────────────
100          | $0.96      | $96 ($87 + $9 API)
500          | $0.26      | $132 ($87 + $45 API)
1000         | $0.18      | $177 ($87 + $90 API)
2000         | $0.13      | $267 ($87 + $180 API)
```

**Break-even:**
- At **667 videos/month**: $0.12/video (same as $80 base + $0.09 API)
- Below 100 videos/month: Local deployment cheaper
- Above 1000 videos/month: VServer cost-effective

### Setup Guide

**1. Provision Server:**
```bash
# Hetzner Cloud CLI
hcloud server create \
  --name mtb-video-server \
  --type ccx33 \
  --image ubuntu-22.04 \
  --ssh-key my-key
```

**2. Install Dependencies:**
```bash
# On server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin

# Clone repo
git clone <your-repo>
cd multimodal-agents-course
```

**3. Configure for Production:**
```bash
# .env
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

**4. Update docker-compose.yml:**
```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  celery-worker:
    build: ./kubrick-mcp
    command: celery -A celery_tasks worker --loglevel=info --concurrency=1
    deploy:
      replicas: 4  # 4 workers
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

volumes:
  redis_data:
```

**5. Start Services:**
```bash
docker-compose up -d --scale celery-worker=4
```

### Monitoring

**CPU/Memory:**
```bash
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Celery Dashboard (Flower):**
```bash
docker run -d -p 5555:5555 \
  mher/flower \
  --broker=redis://localhost:6379/0
```

Access at: `http://your-server-ip:5555`

### Pros
- ✅ 4x throughput vs local
- ✅ No API blocking
- ✅ Persistent task state (Redis)
- ✅ Task retry on failure
- ✅ Cost-effective at scale (> 500 videos/month)
- ✅ Full control over environment

### Cons
- ⚠️ Monthly base cost ($80-160)
- ⚠️ Manual scaling (need to upgrade server)
- ⚠️ Server maintenance required
- ⚠️ Single point of failure

### Ideal For
- 100-2000 videos per month
- Predictable workload
- Cost-conscious at scale
- Need task persistence

---

## Option 3: Google Cloud Platform (Serverless)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User (Mobile/Web)                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloud Load Balancer + Cloud CDN                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloud Run (API Service)                                    │
│  - Auto-scaling: 0-100 instances                            │
│  - Memory: 2GB per instance                                 │
│  - Pay per request                                          │
└───────────┬─────────────────────────┬───────────────────────┘
            │                         │
            ▼                         ▼
┌───────────────────┐      ┌─────────────────────┐
│  Cloud Storage    │      │  Firestore          │
│  - Videos         │      │  - Task state       │
│  - Highlights     │      │  - User metadata    │
└───────────────────┘      └──────────┬──────────┘
            │                         │
            │                         ▼
            │              ┌─────────────────────┐
            │              │  Cloud Tasks Queue  │
            │              └──────────┬──────────┘
            │                         │ HTTP POST
            │                         ▼
            │              ┌─────────────────────────────────┐
            │              │  Cloud Run Job (Worker)         │
            │              │  - 4 vCPU, 8GB RAM              │
            │              │  - No timeout limit             │
            │              │  - Concurrent: 0-1000+          │
            │              └──────────┬──────────────────────┘
            │                         │
            └─────────────────────────┘ Upload result
                          │
                          ▼
          ┌──────────────────────────────────────┐
          │  Firebase Cloud Messaging (FCM)      │
          │  - Push to mobile app                │
          │  - Browser push (PWA)                │
          └──────────────────────────────────────┘
```

### Performance

**Scalability:**
- **0 → 1000+ concurrent jobs** in seconds
- Auto-scaling based on queue depth
- No manual intervention required

**Processing Speed:**
- Same as VServer: ~8-9 minutes per 10 min video
- But unlimited parallelism

**Throughput Examples:**

| Scenario | Concurrent Jobs | Time to Process | Total Cost |
|----------|----------------|-----------------|------------|
| 10 videos | 10 | 10 minutes | $1.90 |
| 100 videos | 100 | 10 minutes | $19.00 |
| 1000 videos | 1000 | 10 minutes | $190.00 |

### Cost Breakdown (per 10 min video)

```
Cloud Run API:
- Request handling: $0.00001 * 100 requests = $0.001

Cloud Run Job (Worker):
- 4 vCPU @ $0.000024/vCPU-second
- 8GB RAM @ $0.0000025/GB-second
- 540 seconds (9 min processing)
- Cost: (4 * 0.000024 + 8 * 0.0000025) * 540 = $0.062

Cloud Storage:
- Upload (500 MB): $0.005
- Download (20 MB highlight): $0.002
- Storage (1 day @ $0.020/GB/month): $0.0007
- Total: $0.008

Firestore:
- Writes: 10 updates * $0.18/100k = $0.00002
- Reads: 50 polls * $0.06/100k = $0.00003
- Total: $0.00005

Cloud Tasks:
- 1 task * $0.40/million = $0.0000004

Firebase Cloud Messaging:
- 1 notification: Free

OpenAI APIs:
- Same as before: $0.09

────────────────────────────────
Total: ~$0.16 + $0.09 = $0.25 per video
```

**Note:** With optimizations (caching, fewer API calls), actual cost: **~$0.19/video**

### Monthly Cost Examples

| Videos/Month | Total Cost | Cost/Video |
|--------------|------------|------------|
| 10 | $2.50 | $0.25 |
| 100 | $19.00 | $0.19 |
| 500 | $95.00 | $0.19 |
| 1000 | $190.00 | $0.19 |
| 5000 | $950.00 | $0.19 |

**No base cost** - Only pay for what you use!

### Setup Guide

**1. Enable GCP Services:**
```bash
gcloud services enable \
  run.googleapis.com \
  cloudtasks.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com
```

**2. Create Cloud Storage Bucket:**
```bash
gsutil mb -l us-central1 gs://mtb-videos-bucket
```

**3. Deploy API (Cloud Run):**
```bash
cd kubrick-api
gcloud run deploy mtb-api \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

**4. Deploy Worker (Cloud Run Job):**
```bash
cd kubrick-mcp
gcloud run jobs create mtb-worker \
  --source . \
  --region us-central1 \
  --memory 8Gi \
  --cpu 4 \
  --max-retries 3 \
  --task-timeout 3600s \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

**5. Setup Cloud Task Queue:**
```bash
gcloud tasks queues create mtb-video-queue \
  --location=us-central1 \
  --max-concurrent-dispatches=1000
```

**6. Deploy Frontend with Firebase:**
```bash
cd kubrick-ui
firebase init hosting
npm run build
firebase deploy
```

### Monitoring & Cost Control

**Cost Tracking:**
```bash
# Per-job cost tracking
gcloud logging read "resource.type=cloud_run_job" --format=json \
  | jq '.[] | {job: .resource.labels.job_name, cost: .jsonPayload.cost}'
```

**Alerts:**
```bash
# Alert if daily cost > $50
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="MTB Video High Cost" \
  --condition-display-name="Daily cost > $50" \
  --condition-threshold-value=50
```

**Budget:**
```bash
# Set monthly budget
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="MTB Video Monthly Budget" \
  --budget-amount=500
```

### Pros
- ✅ Zero base cost
- ✅ Infinite auto-scaling
- ✅ No timeout limits (Cloud Run Jobs)
- ✅ Built-in monitoring
- ✅ Push notifications (FCM)
- ✅ Per-job cost tracking
- ✅ Global CDN
- ✅ No server maintenance

### Cons
- ⚠️⚠️ Complex setup
- ⚠️ Higher cost/video ($0.19 vs $0.12 VServer)
- ⚠️ Vendor lock-in (GCP)
- ⚠️ Cold starts (1-2 seconds API delay)
- ⚠️ Debugging more difficult

### Ideal For
- > 1000 videos per month
- Bursty/unpredictable workload
- Global user base
- Mobile app with push notifications
- Startup seeking to scale rapidly

---

## Decision Matrix

### Choose **Local (Current)** if:
- ✅ < 10 videos per month
- ✅ Single user
- ✅ Testing/Development phase
- ✅ Privacy concerns (no cloud)

### Choose **VServer + Celery** if:
- ✅ 100-2000 videos per month
- ✅ Predictable workload
- ✅ Want full control
- ✅ Cost-conscious (> $0.12/video unacceptable)
- ✅ Can manage infrastructure

### Choose **GCP Cloud Run** if:
- ✅ > 1000 videos per month
- ✅ Bursty workload (peaks/valleys)
- ✅ Need global availability
- ✅ Want zero ops overhead
- ✅ Mobile app with push notifications
- ✅ Rapid scaling required

---

## Migration Path

### Phase 1: MVP (Current)
```
Local Docker → Test with real users → Validate product-market fit
```

### Phase 2: Early Traction (100-500 videos/month)
```
Local → VServer (Hetzner CCX23, 4 vCPU) → Celery with 2 workers
Cost: ~$50/month + $0.09 API = ~$0.19/video at 500 videos
```

### Phase 3: Growth (500-2000 videos/month)
```
VServer CCX23 → CCX33 (8 vCPU) → Celery with 4 workers
Cost: ~$87/month + $0.09 API = ~$0.13/video at 1000 videos
```

### Phase 4: Scale (> 2000 videos/month)
```
VServer → GCP Cloud Run → Infinite scaling
Cost: $0.19/video flat (no base cost)
```

---

## Hybrid Approach

**Best of both worlds:**

```
┌─────────────────────────────────────┐
│  Primary: VServer (Celery)          │
│  - Handles baseline load            │
│  - 4 workers, 16-24 videos/hour     │
│  - Cost: $0.12/video at scale       │
└────────────┬────────────────────────┘
             │
             │ Queue overflow
             ▼
┌─────────────────────────────────────┐
│  Overflow: GCP Cloud Run            │
│  - Handles peaks/bursts             │
│  - Auto-scaling                     │
│  - Cost: $0.19/video                │
└─────────────────────────────────────┘
```

**Benefits:**
- ✅ Cost-efficient baseline (VServer)
- ✅ Handles unpredictable spikes (GCP)
- ✅ No queue backup during peaks

**Implementation:**
```python
# Queue router
def route_task(video_path, queue_depth):
    if queue_depth < 20:
        # VServer can handle
        return celery_app.send_task('process_video', args=[video_path])
    else:
        # Overflow to GCP
        return enqueue_to_cloud_tasks(video_path)
```

---

## Conclusion

| Priority | Recommendation |
|----------|----------------|
| **Cost** | VServer (cheapest at scale) |
| **Simplicity** | Local (easiest setup) |
| **Scalability** | GCP (infinite, automatic) |
| **Flexibility** | VServer (full control) |
| **Best ROI** | Hybrid (VServer + GCP overflow) |

**Recommended path:**
1. **Now:** Local (validate MVP)
2. **100+ videos/month:** VServer + Celery
3. **1000+ videos/month:** Consider GCP or stay with VServer if predictable
4. **Bursty workload:** GCP from start

---

**For detailed implementation guides, see:**
- [API_DOCUMENTATION.md - Async Processing](API_DOCUMENTATION.md#asynchronous-processing--limitations)
- [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md)
- [QUICKSTART.md](QUICKSTART.md)
