#!/bin/bash
# 琥珀引擎算法自省执行脚本
# 每周五收盘后自动执行，明早09:00首次执行

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"
REPORT_DIR="$SCRIPT_DIR/../reports/algo_audit"

# 创建目录
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

# 执行时间
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/algo_audit_${TIMESTAMP}.log"

echo "🧀 琥珀引擎算法自省脚本执行" > "$LOG_FILE"
echo "⏰ 执行时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 执行Python脚本
cd "$SCRIPT_DIR"
python3 algo_self_audit.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "🏁 执行完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "📊 退出代码: $EXIT_CODE" >> "$LOG_FILE"

# 发送通知 (可选)
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 算法自省执行成功" >> "$LOG_FILE"
    # 这里可以添加通知逻辑，如发送邮件或消息
else
    echo "❌ 算法自省执行失败，请检查日志" >> "$LOG_FILE"
fi

exit $EXIT_CODE