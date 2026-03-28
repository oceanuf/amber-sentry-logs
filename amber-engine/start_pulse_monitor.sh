#!/bin/bash
# 琥珀引擎脉冲哨兵启动脚本

cd /home/luckyelite/.openclaw/workspace/amber-engine

echo "🏛️ 启动琥珀引擎脉冲哨兵..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "信标: https://gist.githubusercontent.com/oceanuf/ba3d0c5ac402cc67529e97591203a6d3/raw/amber_cmd.json"
echo "日志: pulse_monitor.log"
echo ""

# 检查是否已在运行
if pgrep -f "amber_pulse_monitor.py" > /dev/null; then
    echo "⚠️ 脉冲哨兵已在运行，PID: $(pgrep -f 'amber_pulse_monitor.py')"
    echo "停止现有进程..."
    pkill -f "amber_pulse_monitor.py"
    sleep 2
fi

# 启动新的脉冲哨兵
echo "🚀 启动脉冲哨兵..."
nohup python3 amber_pulse_monitor.py >> pulse_monitor.log 2>&1 &

# 等待启动
sleep 3

# 检查是否启动成功
if pgrep -f "amber_pulse_monitor.py" > /dev/null; then
    PID=$(pgrep -f "amber_pulse_monitor.py")
    echo "✅ 脉冲哨兵启动成功，PID: $PID"
    echo "📡 开始监听云端信标..."
    echo "📝 查看日志: tail -f pulse_monitor.log"
else
    echo "❌ 脉冲哨兵启动失败"
    echo "查看错误信息: tail -n 20 pulse_monitor.log"
fi
