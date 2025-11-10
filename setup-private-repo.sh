#!/bin/bash
set -e

echo "🔒 Setting up private SaaS repository..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch:${NC} $CURRENT_BRANCH"

# 2. Check if saas remote exists
if git remote get-url saas &> /dev/null; then
    echo -e "${GREEN}✓${NC} Remote 'saas' already configured"
else
    echo -e "${RED}✗${NC} Remote 'saas' not found"
    exit 1
fi

# 3. Push to private repo
echo ""
echo -e "${BLUE}Pushing to private repository...${NC}"
git push saas $CURRENT_BRANCH:main

# 4. Rename local branch to main
echo ""
echo -e "${BLUE}Renaming local branch to 'main'...${NC}"
git branch -m $CURRENT_BRANCH main

# 5. Set upstream to saas/main
echo ""
echo -e "${BLUE}Setting upstream to saas/main...${NC}"
git branch --set-upstream-to=saas/main

# 6. Verify setup
echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Repository status:"
git remote -v
echo ""
git branch -vv
echo ""
echo -e "${GREEN}You can now use:${NC}"
echo "  git push      # pushes to private repo"
echo "  git pull      # pulls from private repo"
echo ""
echo -e "${BLUE}Optional:${NC} Remove public remote if you don't need it:"
echo "  git remote remove origin"
