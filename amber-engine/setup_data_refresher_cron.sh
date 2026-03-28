#!/bin/bash
# [2613-201号-B] 档案馆数据装填器Cron配置脚本
# 版本: V1.0.0
# 作者: 工程师 Cheese
# 创建时间: 2026-03-28 16:24 GMT+8

set -e

WORKSPACE_DIR="/home/luckyelite/.openclaw/workspace/amber-engine"
START_SCRIPT="$WORKSPACE_DIR/start_data_refresher.sh"
CRON_LOG="$WORKSPACE_DIR/logs/cron_data_refresher.log"

# 确保日志目录存在
mkdir -p "$WORKSPACE_DIR/logs"

echo "=== 配置档案馆数据装填器Cron任务 ==="
echo "工作目录: $WORKSPACE_DIR"
echo "启动脚本: $START_SCRIPT"

# 检查启动脚本
if [ ! -f "$START_SCRIPT" ]; then
    echo "错误: 找不到启动脚本 $START_SCRIPT"
    exit 1
fi

# 添加执行权限
chmod +x "$START_SCRIPT"

# 创建Cron任务
CRON_JOB="@reboot $START_SCRIPT start >> $CRON_LOG 2>&1"

echo "Cron任务: $CRON_JOB"
echo "日志文件: $CRON_LOG"

# 检查是否已存在相同任务
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$START_SCRIPT" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "警告: 已存在类似Cron任务:"
    echo "$EXISTING_CRON"
    echo "是否替换? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # 删除现有任务
        crontab -l 2>/dev/null | grep -v "$START_SCRIPT" | crontab -
        echo "已删除现有任务"
    else
        echo "保留现有任务"
        exit 0
    fi
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron任务配置完成"
echo ""
echo "验证配置:"
crontab -l | grep "$START_SCRIPT"

echo ""
echo "手动启动命令:"
echo "  $START_SCRIPT start"
echo ""
echo "查看状态命令:"
echo "  $START_SCRIPT status"
echo ""
echo "查看日志命令:"
echo "  $START_SCRIPT logs"

# 立即启动服务
echo ""
echo "是否立即启动数据装填器? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "启动数据装填器..."
    $START_SCRIPT start
    sleep 2
    $START_SCRIPT status
fi

echo ""
echo "=== 配置完成 ==="
echo "数据装填器将在系统重启后自动启动"
echo "每小时自动刷新518880等标的的实时净值"