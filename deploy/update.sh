#!/usr/bin/env bash
# 已部署网站的更新脚本。
set -euo pipefail

PROJECT_DIR="/var/www/tourism-review-llm-evaluation"

if [ ! -d "${PROJECT_DIR}/.git" ]; then
  echo "未找到部署仓库：${PROJECT_DIR}"
  exit 1
fi

cd "${PROJECT_DIR}"
git pull --ff-only
sudo cp deploy/nginx.conf /etc/nginx/sites-available/tourism-review-llm-evaluation
sudo nginx -t
sudo systemctl reload nginx
echo "网站文件已更新并重载 Nginx。"
