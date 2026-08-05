#!/usr/bin/env bash
# 已部署网站的更新脚本。
set -euo pipefail

PROJECT_DIR="/var/www/tourism-review-llm-evaluation"
SITE_NAME="tourism-review-ai"

if [ "${EUID}" -ne 0 ]; then
  exec sudo "$0" "$@"
fi

if [ ! -d "${PROJECT_DIR}/.git" ]; then
  echo "未找到部署仓库：${PROJECT_DIR}"
  exit 1
fi

cd "${PROJECT_DIR}"
git -c safe.directory="${PROJECT_DIR}" config core.filemode false
git -c safe.directory="${PROJECT_DIR}" pull --ff-only origin main
chown -R www-data:www-data "${PROJECT_DIR}"
find "${PROJECT_DIR}" -type d -exec chmod 755 {} \;
find "${PROJECT_DIR}" -type f -exec chmod 644 {} \;
# HTTPS 配置由 Certbot 维护，更新静态文件时不覆盖现有虚拟主机配置。
nginx -t
systemctl reload nginx
echo "网站文件已更新并重载 Nginx。"
