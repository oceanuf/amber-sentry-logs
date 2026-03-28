#!/bin/bash
# 琥珀引擎演武场自动重筑脚本 V2.0
# 可以直接从Cron执行，无需通过AI代理
# 修复：移除绝对路径，符合[2614-001]安全防线协议

set -e

echo "🧀 琥珀引擎演武场自动重筑脚本启动"
echo "============================================================"
echo "⏰ 执行时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 自动检测工作目录 (脚本应位于 amber-engine/scripts/ 下运行)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到工作目录
cd "$PROJECT_ROOT"

# 执行修复版脚本
echo "🚀 执行演武场重筑脚本..."
sudo python3 scripts/rebuild_minimalist_fixed_v2.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "✅ 演武场重筑完成"
    
    # 记录执行日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 演武场重筑成功" >> logs/arena_rebuild.log
    
    # 生成简短的执行报告
    REPORT_FILE="琥珀引擎演武场重筑执行报告_$(date '+%Y-%m-%d_%H%M').md"
    cat > "$REPORT_FILE" << EOF
# 🧀 琥珀引擎演武场自动重筑报告

## 执行摘要
- **时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **状态**: ✅ 成功
- **脚本**: rebuild_minimalist_fixed_v2.py
- **方式**: 自动执行 (Cron任务)

## 生成文件
- PORTFOLIO.md (核心看板)
- RADAR.md (机会雷达)

## 下次执行
- **预计时间**: $(date -d '+15 minutes' '+%Y-%m-%d %H:%M:%S')

---
*报告自动生成于: $(date '+%Y-%m-%d %H:%M:%S')*
EOF
    
    echo "📋 执行报告已生成: $REPORT_FILE"
else
    echo "❌ 演武场重筑失败"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 演武场重筑失败" >> logs/arena_rebuild_error.log
    exit 1
fi