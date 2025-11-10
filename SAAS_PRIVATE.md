# 🔒 Action Cut - Private SaaS Repository

**This is the PRIVATE development repository for Action Cut SaaS.**

## ⚠️ Important

- This repository is **private** and contains production code
- **Never push to public repositories**
- Keep all secrets in `.env` files (already gitignored)
- Customer data must never be committed

## 🏗️ Structure

This is a fork of the open-source MTB Video Editor, enhanced with:
- Multi-tenant architecture
- Clerk authentication
- GCP Cloud Run deployment
- Production monitoring
- User quotas & billing

## 🔐 Secrets Management

All secrets must be in environment variables or secret managers:

```bash
# Local development (.env - gitignored)
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
GCP_PROJECT_ID=action-cut-prod

# Production (GCP Secret Manager)
gcloud secrets create clerk-secret-key --data-file=-
gcloud secrets create openai-api-key --data-file=-
```

## 📋 Development Workflow

```bash
# Development
git checkout -b feature/new-feature
# ... work ...
git commit -m "feat: Add new feature"
git push saas feature/new-feature

# Production deployment
git checkout main
git tag v1.0.0
git push saas main --tags
# Trigger GCP Cloud Run deployment
```

## 🚫 Never Commit

- `.env`, `.env.production` (gitignored)
- `gcp-service-account.json` (gitignored)
- `clerk-secret-key.txt` (gitignored)
- Customer videos or data (gitignored)
- Any API keys or tokens

## 🔗 Links

- **Public Open Source:** https://github.com/HWernisch/multimodal-agents-course
- **Production Dashboard:** (add Clerk dashboard link)
- **GCP Console:** (add GCP console link)
- **Monitoring:** (add monitoring link)

## 📚 Documentation

See main documentation files:
- [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md) - Architecture
- [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) - GCP deployment
- [MTB_EDITOR_README.md](MTB_EDITOR_README.md) - Features & roadmap

---

**⚠️ REMINDER: This is PRIVATE. Never push to public repos!**
