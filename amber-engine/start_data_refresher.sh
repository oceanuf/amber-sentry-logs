#!/bin/bash
# [2613-201号-B] 档案馆数据装填器启动脚本
# 版本: V1.0.0
# 作者: 工程师 Cheese
# 创建时间: 2026-03-28 16:23 GMT+8

set -e

WORKSPACE_DIR="/home/luckyelite/.openclaw/workspace/amber-engine"
SCRIPT_PATH="$WORKSPACE_DIR/data_refresher.py"
LOG_DIR="$WORKSPACE_DIR/logs"
PID_FILE="$LOG_DIR/data_refresher.pid"
LOG_FILE="$LOG_DIR/data_refresher_service.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 检查Python脚本是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "错误: 找不到数据装填器脚本 $SCRIPT_PATH"
    exit 1
fi

# 检查Python依赖
echo "检查Python依赖..."
python3 -c "import tushare, akshare, schedule" 2>/dev/null || {
    echo "安装缺失的Python依赖..."
    pip install tushare akshare schedule
}

# 设置Tushare Token环境变量
if [ -f "$WORKSPACE_DIR/.env" ]; then
    source "$WORKSPACE_DIR/.env"
    echo "已加载.env文件中的环境变量"
fi

# 检查Tushare Token
if [ -z "$TUSHARE_TOKEN" ]; then
    echo "警告: TUSHARE_TOKEN环境变量未设置"
    echo "请设置TUSHARE_TOKEN: export TUSHARE_TOKEN='your_token_here'"
    echo "或在.env文件中添加: TUSHARE_TOKEN='your_token_here'"
fi

case "$1" in
    start)
        echo "启动档案馆数据装填器..."
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "数据装填器已在运行 (PID: $PID)"
                exit 0
            else
                echo "发现旧的PID文件，清理..."
                rm -f "$PID_FILE"
            fi
        fi
        
        # 启动服务
        nohup python3 "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1 &
        PID=$!
        echo $PID > "$PID_FILE"
        echo "数据装填器已启动 (PID: $PID)"
        echo "日志文件: $LOG_FILE"
        ;;
    
    stop)
        echo "停止档案馆数据装填器..."
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                kill "$PID"
                echo "已发送停止信号 (PID: $PID)"
            else
                echo "进程不存在 (PID: $PID)"
            fi
            rm -f "$PID_FILE"
        else
            echo "未找到PID文件，尝试查找进程..."
            PIDS=$(pgrep -f "data_refresher.py")
            if [ -n "$PIDS" ]; then
                echo "找到进程: $PIDS"
                kill $PIDS
                echo "已停止所有相关进程"
            else
                echo "未找到运行中的数据装填器进程"
            fi
        fi
        ;;
    
    restart)
        echo "重启档案馆数据装填器..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo "档案馆数据装填器状态:"
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ 运行中 (PID: $PID)"
                echo "启动时间: $(ps -p $PID -o lstart | tail -1)"
                echo "内存使用: $(ps -p $PID -o rss | tail -1) KB"
                
                # 显示最近日志
                echo ""
                echo "最近日志:"
                tail -10 "$LOG_FILE" 2>/dev/null || echo "无日志文件"
            else
                echo "❌ PID文件存在但进程不存在"
                rm -f "$PID_FILE"
            fi
        else
            PIDS=$(pgrep -f "data_refresher.py")
            if [ -n "$PIDS" ]; then
                echo "✅ 运行中 (PID: $PIDS) - 但无PID文件"
            else
                echo "❌ 未运行"
            fi
        fi
        ;;
    
    logs)
        echo "显示数据装填器日志:"
        if [ -f "$LOG_FILE" ]; then
            tail -50 "$LOG_FILE"
        else
            echo "无日志文件"
        fi
        ;;
    
    test)
        echo "测试数据装填器..."
        python3 "$SCRIPT_PATH" --test || {
            echo "测试失败"
            exit 1
        }
        echo "测试成功"
        ;;
    
    *)
        echo "使用方法: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "命令说明:"
        echo "  start   启动数据装填器服务"
        echo "  stop    停止数据装填器服务"
        echo "  restart 重启数据装填器服务"
        echo "  status  查看服务状态"
        echo "  logs    查看最近日志"
        echo "  test    测试脚本功能"
        exit 1
        ;;
esac

exit 0