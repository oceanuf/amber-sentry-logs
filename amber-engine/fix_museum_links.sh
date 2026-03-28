#!/bin/bash
# 博物馆页面链接修复脚本

echo "🔧 开始修复博物馆页面链接..."

# 备份原始文件
BACKUP_FILE="/var/www/gemini_master/master-audit/list.html.backup"
sudo cp /var/www/gemini_master/master-audit/list.html "$BACKUP_FILE"
echo "📁 备份创建: $BACKUP_FILE"

# 修复 bronze_etf_details.html 链接
echo "🔄 修复 bronze_etf_details.html 链接..."
sudo sed -i 's|href="bronze_etf_details.html"|href="bronze_static_final.html"|g' /var/www/gemini_master/master-audit/list.html
sudo sed -i 's|href='\''bronze_etf_details.html'\''|href='\''bronze_static_final.html'\''|g' /var/www/gemini_master/master-audit/list.html

echo "✅ 修复完成"
echo "🌐 请访问: https://gemini.googlemanager.cn:10168/master-audit/list.html"
