#!/bin/bash
# 琥珀引擎 - 50万量化实验室自动化停止脚本

echo "🛑 停止50万量化实验室自动化系统"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=" * 60

# 1. 停止live_trade_sim.py
if [ -f /tmp/live_trade_sim.pid ]; then
    pid=$(cat /tmp/live_trade_sim.pid)
    if kill -0 $pid 2>/dev/null; then
        kill $pid
        echo "✅ 停止实战交易算法 (PID: $pid)"
    else
        echo "⚠️ 实战交易算法进程不存在"
    fi
    rm -f /tmp/live_trade_sim.pid
else
    echo "⚠️ 实战交易算法PID文件不存在"
fi

# 2. 停止refresh_museum.py
if [ -f /tmp/refresh_museum.pid ]; then
    pid=$(cat /tmp/refresh_museum.pid)
    if kill -0 $pid 2>/dev/null; then
        kill $pid
        echo "✅ 停止博物馆数据刷新 (PID: $pid)"
    else
        echo "⚠️ 博物馆数据刷新进程不存在"
    fi
    rm -f /tmp/refresh_museum.pid
else
    echo "⚠️ 博物馆数据刷新PID文件不存在"
fi

# 3. 移除每日报告Cron任务
echo "📊 移除每日报告Cron任务..."
(crontab -l 2>/dev/null | grep -v "generate_daily_report.py") | crontab -
echo "✅ 每日报告Cron任务已移除"

echo ""
echo "🎉 50万量化实验室自动化系统已停止!"
echo ""
echo "📋 清理完成:"
echo "  实战交易算法: 已停止"
echo "  博物馆数据刷新: 已停止"
echo "  每日报告生成: Cron任务已移除"
