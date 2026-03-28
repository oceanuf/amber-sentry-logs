#!/bin/bash
# 琥珀引擎 - 50万量化实验室自动化启动脚本

echo "🚀 启动50万量化实验室自动化系统"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=" * 60

# 1. 启动live_trade_sim.py (每15分钟)
echo "📈 启动实战交易算法 (每15分钟)..."
nohup python3 ./scripts/live_trade_sim.py --service 15 > /tmp/live_trade_sim.log 2>&1 &
echo $! > /tmp/live_trade_sim.pid
echo "✅ 实战交易算法已启动 (PID: $(cat /tmp/live_trade_sim.pid))"

# 2. 启动refresh_museum.py (每30秒)
echo "🔄 启动博物馆数据刷新 (每30秒)..."
nohup python3 ./scripts/refresh_museum.py --service 30 > /tmp/refresh_museum.log 2>&1 &
echo $! > /tmp/refresh_museum.pid
echo "✅ 博物馆数据刷新已启动 (PID: $(cat /tmp/refresh_museum.pid))"

# 3. 设置每日报告Cron任务
echo "📊 设置每日报告Cron任务 (每晚20:00)..."
(crontab -l 2>/dev/null | grep -v "generate_daily_report.py"; echo "0 20 * * 1-5 cd . && python3 scripts/generate_daily_report.py >> /tmp/daily_report.log 2>&1") | crontab -
echo "✅ 每日报告Cron任务已设置"

echo ""
echo "🎉 50万量化实验室自动化系统启动完成!"
echo ""
echo "📋 运行状态:"
echo "  实战交易算法: 每15分钟扫描一次"
echo "  博物馆数据刷新: 每30秒更新一次"
echo "  每日报告生成: 每晚20:00自动执行"
echo ""
echo "📁 日志文件:"
echo "  /tmp/live_trade_sim.log - 实战交易日志"
echo "  /tmp/refresh_museum.log - 数据刷新日志"
echo "  /tmp/daily_report.log - 每日报告日志"
echo ""
echo "🛑 停止命令: ./stop_quant_lab.sh"
