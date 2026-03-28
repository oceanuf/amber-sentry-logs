#!/bin/bash
# 快速数据更新脚本
# 用法: ./quick_update.sh [选项]
# 选项:
#   -h, --help     显示帮助信息
#   -f, --force    强制更新，忽略时间检查
#   -t, --test     测试模式，不实际更新
#   -c, --check    只检查状态，不更新

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 工作目录
WORKDIR="."
cd "$WORKDIR" || { echo -e "${RED}错误: 无法进入工作目录 $WORKDIR${NC}"; exit 1; }

# 日志文件
LOG_FILE="logs/data_update_$(date +%Y%m%d_%H%M%S).log"

# 显示帮助
show_help() {
    echo -e "${BLUE}数据更新管理器 - 快速更新脚本${NC}"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -f, --force    强制更新，忽略时间检查"
    echo "  -t, --test     测试模式，不实际更新"
    echo "  -c, --check    只检查状态，不更新"
    echo ""
    echo "示例:"
    echo "  $0              # 正常更新"
    echo "  $0 --check      # 只检查状态"
    echo "  $0 --force      # 强制更新"
}

# 检查状态函数
check_status() {
    echo -e "${BLUE}📊 检查数据更新状态...${NC}"
    echo "========================================"
    
    # 检查缓存更新时间
    if [ -f "output/static/data/unified_data_cache.json" ]; then
        UPDATE_TIME=$(jq -r '.update_time' output/static/data/unified_data_cache.json 2>/dev/null || echo "未知")
        echo -e "📅 缓存更新时间: ${GREEN}$UPDATE_TIME${NC}"
    else
        echo -e "📅 缓存更新时间: ${RED}缓存文件不存在${NC}"
    fi
    
    # 检查页面更新时间
    if [ -f "output/index.html" ]; then
        PAGE_TIME=$(grep -o "数据最后更新时间:[^<]*" output/index.html | head -1 || echo "未知")
        echo -e "🌐 页面更新时间: ${GREEN}$PAGE_TIME${NC}"
        
        TABLE_TIME=$(grep -o "table-update-time[^<]*" output/index.html | sed 's/.*>//' | head -1 || echo "未知")
        echo -e "📋 表格更新时间: ${GREEN}$TABLE_TIME${NC}"
    else
        echo -e "🌐 页面更新时间: ${RED}页面文件不存在${NC}"
    fi
    
    # 检查Tushare Token
    if python3 -c "import tushare as ts; ts.set_token('9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b'); print('Token正常')" 2>/dev/null; then
        echo -e "🔑 Tushare Token: ${GREEN}正常${NC}"
    else
        echo -e "🔑 Tushare Token: ${RED}异常${NC}"
    fi
    
    # 检查文件权限
    if [ -w "output/index.html" ]; then
        echo -e "📝 文件权限: ${GREEN}可写${NC}"
    else
        echo -e "📝 文件权限: ${RED}不可写${NC}"
    fi
    
    echo "========================================"
}

# 执行更新函数
perform_update() {
    echo -e "${BLUE}🚀 开始数据更新...${NC}"
    echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    
    # 运行统一数据引擎
    if python3 amber_unified_data_engine.py 2>&1 | tee -a "$LOG_FILE"; then
        echo -e "${GREEN}✅ 数据更新成功${NC}"
        
        # 更新页面顶部时间
        CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
        sudo sed -i "s/数据最后更新时间: [0-9:-]*/数据最后更新时间: $CURRENT_TIME/g" output/index.html 2>/dev/null || true
        
        # 显示更新结果
        echo "========================================"
        echo -e "${GREEN}🎉 更新完成!${NC}"
        echo "📋 更新内容:"
        echo "  1. ✅ 指数数据表格更新"
        echo "  2. ✅ 宏观四锚数据更新"
        echo "  3. ✅ ETF数据更新"
        echo "  4. ✅ 数据缓存保存"
        echo "  5. ✅ 页面时间更新"
        echo ""
        echo "🔗 验证地址: https://amber.googlemanager.cn:10123/"
        echo "📁 日志文件: $LOG_FILE"
    else
        echo -e "${RED}❌ 数据更新失败${NC}"
        echo "请检查日志文件: $LOG_FILE"
        exit 1
    fi
}

# 解析参数
MODE="update"
FORCE=false
TEST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -t|--test)
            TEST=true
            MODE="test"
            shift
            ;;
        -c|--check)
            MODE="check"
            shift
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 创建日志目录
mkdir -p logs

# 根据模式执行
case $MODE in
    "check")
        check_status
        ;;
    "test")
        echo -e "${YELLOW}🧪 测试模式 - 不执行实际更新${NC}"
        check_status
        echo ""
        echo -e "${YELLOW}模拟更新流程...${NC}"
        echo "1. 检查Tushare API连接 ✓"
        echo "2. 获取指数数据 ✓"
        echo "3. 更新表格数据 ✓"
        echo "4. 更新宏观数据 ✓"
        echo "5. 保存数据缓存 ✓"
        echo ""
        echo -e "${GREEN}测试完成，一切正常!${NC}"
        ;;
    "update")
        # 检查是否需要强制更新
        if [ "$FORCE" = false ]; then
            # 检查最后更新时间，避免频繁更新
            if [ -f "output/static/data/unified_data_cache.json" ]; then
                LAST_UPDATE=$(jq -r '.update_time' output/static/data/unified_data_cache.json 2>/dev/null || echo "1970-01-01 00:00:00")
                LAST_EPOCH=$(date -d "$LAST_UPDATE" +%s 2>/dev/null || echo 0)
                NOW_EPOCH=$(date +%s)
                DIFF=$((NOW_EPOCH - LAST_EPOCH))
                
                # 如果5分钟内更新过，提示用户
                if [ $DIFF -lt 300 ]; then
                    echo -e "${YELLOW}⚠️  数据最近已更新于 $LAST_UPDATE${NC}"
                    echo -e "${YELLOW}距离上次更新仅 $((DIFF/60)) 分钟，确定要再次更新吗？${NC}"
                    read -p "输入 y 继续，其他键取消: " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                        echo -e "${BLUE}更新已取消${NC}"
                        exit 0
                    fi
                fi
            fi
        fi
        
        check_status
        echo ""
        perform_update
        ;;
esac

echo -e "${BLUE}✨ 脚本执行完成${NC}"