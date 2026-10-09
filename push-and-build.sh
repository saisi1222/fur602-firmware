#!/usr/bin/env bash
# 用 GitHub PAT 建库并推送，触发 FUR-602 固件编译。
# 用法: GH_PAT=ghp_xxx bash push-and-build.sh
set -euo pipefail

PAT="${GH_PAT:-}"
if [ -z "$PAT" ]; then
  echo "缺少 GitHub PAT。用法: GH_PAT=ghp_xxx bash push-and-build.sh" >&2
  echo "PAT scope 需勾: 经典 token 选 'repo'; 细粒度选 contents:write + workflows:write" >&2
  exit 1
fi

REPO="fur602-firmware"

# 1) 确保本地变更已提交
git add -A
if ! git diff --cached --quiet; then
  git commit -m "FUR-602 full firmware build: padavanonly base + closed mtwifi + nft fullcone + cpufreq"
fi

# 2) 取登录名
LOGIN=$(curl -fsSL -H "Authorization: Bearer $PAT" -H "Accept: application/vnd.github+json" \
  https://api.github.com/user | python3 -c "import sys,json;print(json.load(sys.stdin)['login'])")
echo "GitHub login: $LOGIN"

# 3) 建公开库（已存在则忽略错误）
curl -fsSL -X POST -H "Authorization: Bearer $PAT" -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$REPO\",\"private\":false,\"auto_init\":false}" \
  https://api.github.com/user/repos || echo "(仓库可能已存在，继续)"

# 4) 设置 remote 并推送 main（推送即触发 workflow）
REMOTE="https://$PAT@github.com/$LOGIN/$REPO.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "本地分支: $BRANCH -> 推送到 main"
git push -u origin "$BRANCH:main" --force

echo
echo "==== 完成 ===="
echo "仓库: https://github.com/$LOGIN/$REPO"
echo "Actions: https://github.com/$LOGIN/$REPO/actions  (推上去已自动触发编译)"
