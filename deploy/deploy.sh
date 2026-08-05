#!/usr/bin/env bash
# Ubuntu / Debian 静态网站首次部署脚本。
set -euo pipefail

PROJECT_DIR="/var/www/tourism-review-llm-evaluation"
SITE_NAME="tourism-review-ai"

if [ "${EUID}" -eq 0 ]; then
  echo "请使用普通用户运行此脚本；脚本会在需要时调用 sudo。"
  exit 1
fi

read -r -p "请输入 GitHub 仓库地址（例如 https://github.com/USER/${SITE_NAME}.git）：" REPO_URL
if [ -z "${REPO_URL}" ]; then
  echo "未提供仓库地址，部署已取消。"
  exit 1
fi

if ! command -v git >/dev/null 2>&1 || ! command -v nginx >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git nginx curl
fi

if [ -e "${PROJECT_DIR}" ]; then
  echo "目标目录 ${PROJECT_DIR} 已存在。为避免覆盖现有文件，部署已停止。"
  exit 1
fi

sudo mkdir -p /var/www
sudo git clone "${REPO_URL}" "${PROJECT_DIR}"
sudo chown -R www-data:www-data "${PROJECT_DIR}"
sudo find "${PROJECT_DIR}" -type d -exec chmod 755 {} \;
sudo find "${PROJECT_DIR}" -type f -exec chmod 644 {} \;
sudo cp "${PROJECT_DIR}/deploy/nginx.conf" "/etc/nginx/sites-available/${SITE_NAME}"
sudo ln -sfn "/etc/nginx/sites-available/${SITE_NAME}" "/etc/nginx/sites-enabled/${SITE_NAME}"

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx

SERVER_IP="$(hostname -I | awk '{print $1}')"
echo "部署完成。请访问：http://${SERVER_IP}/"
