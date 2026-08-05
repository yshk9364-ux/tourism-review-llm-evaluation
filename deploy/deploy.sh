#!/usr/bin/env bash
# Ubuntu / Debian 静态网站首次部署脚本。
set -euo pipefail

PROJECT_DIR="/var/www/tourism-review-llm-evaluation"
SITE_NAME="tourism-review-llm-evaluation"

if [ "${EUID}" -eq 0 ]; then
  echo "请使用普通用户运行此脚本；脚本会在需要时调用 sudo。"
  exit 1
fi

read -r -p "请输入 GitHub 仓库地址（例如 https://github.com/USER/${SITE_NAME}.git）：" REPO_URL
if [ -z "${REPO_URL}" ]; then
  echo "未提供仓库地址，部署已取消。"
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git
fi

if ! command -v nginx >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y nginx
fi

if [ -e "${PROJECT_DIR}/.git" ]; then
  echo "目录 ${PROJECT_DIR} 已包含 Git 仓库，请改用 deploy/update.sh 更新。"
  exit 1
fi

sudo mkdir -p /var/www
sudo git clone "${REPO_URL}" "${PROJECT_DIR}"
sudo cp "${PROJECT_DIR}/deploy/nginx.conf" "/etc/nginx/sites-available/${SITE_NAME}"
sudo ln -sfn "/etc/nginx/sites-available/${SITE_NAME}" "/etc/nginx/sites-enabled/${SITE_NAME}"

# 此配置使用 default_server。首次部署到新服务器时移除 Debian 默认站点，避免默认站点冲突。
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

SERVER_IP="$(hostname -I | awk '{print $1}')"
echo "部署完成。请访问：http://${SERVER_IP}/"
