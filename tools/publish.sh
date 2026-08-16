#!/usr/bin/env bash
# 本地优先的发布流程。先在本地把站点跑通、验过，再决定 push。
# 用法:
#   bash tools/publish.sh          # 构建 + 验证 + 本地预览 (不 push)
#   bash tools/publish.sh --commit "提交说明" # 构建 + 验证, 通过后只在本地提交
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/3 构建 (engine/site.py)"
python engine/site.py

echo "==> 2/3 本地门禁 (verify_site.mjs)"
node tools/verify_site.mjs   # 不通过会非0退出，下面就不会执行

echo "==> 3/3 完成"
if [[ "${1:-}" == "--commit" ]]; then
  echo "验证通过，创建本地提交..."
  git add docs/
  if git diff --cached --quiet; then
    echo "(无改动可提交)"
  else
    git commit -m "${2:-chore: 重建站点}"
  fi
  echo "已完成本地提交；仓库不再使用 GitHub Actions。"
else
  echo "验证通过。本地预览:"
  echo "  python -m http.server -d docs 8080   然后打开 http://localhost:8080/"
  echo "确认无误后可选地运行:  bash tools/publish.sh --commit \"提交说明\""
fi
