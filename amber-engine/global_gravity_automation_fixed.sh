#!/bin/bash
# 全球引力定时巡航自动化脚本 (修复版)
# 版本: 2.0.0
# 修复时间: 2026-03-24 21:50
# 作者: 工程师 Cheese
# 团队: Cheese Intelligence Team
# 修复内容: 确保Skill处理被正确触发

set -e  # 遇到错误退出

# 配置
SCRIPT_DIR="/home/luckyelite/scripts"
LOG_FILE="$SCRIPT_DIR/automation_log.txt"
FETCH_SCRIPT="$SCRIPT_DIR/fetch_global_raw_v2.py"
SKILL_SCRIPT="$SCRIPT_DIR/Skill_Global_Audit.py"
INBOX_DIR="$SCRIPT_DIR/skill_inbox"
WEB_REPORT_DIR="$SCRIPT_DIR/web_reports"

# 时间戳
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE_TAG=$(date '+%Y%m%d')

# 日志函数
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# 错误处理函数
handle_error() {
    log_message "❌ 错误: $1"
    log_message "🔧 错误详情: $2"
    exit 1
}

# 确保目录存在
ensure_directories() {
    mkdir -p "$INBOX_DIR"
    mkdir -p "$INBOX_DIR/processed"
    mkdir -p "$WEB_REPORT_DIR"
    log_message "✅ 目录结构检查完成"
}

# 阶段1: 数据抓取
stage1_data_fetch() {
    log_message "="*60
    log_message "📥 阶段1: 数据抓取 (20:00)"
    log_message "="*60
    
    if [ ! -f "$FETCH_SCRIPT" ]; then
        handle_error "数据搬运脚本不存在" "$FETCH_SCRIPT"
    fi
    
    log_message "🚀 执行数据抓取: $FETCH_SCRIPT --auto"
    START_TIME=$(date +%s)
    
    cd "$SCRIPT_DIR" && python3 "$FETCH_SCRIPT" --auto >> "$LOG_FILE" 2>&1
    FETCH_EXIT_CODE=$?
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ $FETCH_EXIT_CODE -eq 0 ]; then
        log_message "✅ 数据抓取完成 (耗时: ${DURATION}秒)"
        
        # 检查数据文件是否生成
        if [ -f "$INBOX_DIR/raw_global_data.json" ]; then
            FILE_SIZE=$(stat -c%s "$INBOX_DIR/raw_global_data.json")
            log_message "📦 数据文件: $INBOX_DIR/raw_global_data.json (大小: ${FILE_SIZE}字节)"
        else
            log_message "⚠️  数据文件未生成，尝试重新抓取..."
            cd "$SCRIPT_DIR" && python3 "$FETCH_SCRIPT" --auto >> "$LOG_FILE" 2>&1
        fi
    else
        handle_error "数据抓取失败" "退出码: $FETCH_EXIT_CODE"
    fi
}

# 阶段2: 数据投递验证
stage2_data_delivery() {
    log_message "="*60
    log_message "📨 阶段2: 数据投递验证 (20:05)"
    log_message "="*60
    
    # 等待数据文件稳定
    sleep 5
    
    if [ ! -f "$INBOX_DIR/raw_global_data.json" ]; then
        log_message "❌ 数据文件不存在，重新执行阶段1"
        stage1_data_fetch
        sleep 3
    fi
    
    FILE_SIZE=$(stat -c%s "$INBOX_DIR/raw_global_data.json" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -lt 1000 ]; then
        log_message "⚠️  数据文件过小 (${FILE_SIZE}字节)，可能抓取失败"
        log_message "🔧 尝试使用备用数据源..."
        cd "$SCRIPT_DIR" && python3 "$FETCH_SCRIPT" --fallback >> "$LOG_FILE" 2>&1
    else
        log_message "✅ 数据投递验证通过 (大小: ${FILE_SIZE}字节)"
    fi
}

# 阶段3: Skill处理触发
stage3_skill_processing() {
    log_message "="*60
    log_message "⚙️  阶段3: Skill处理触发 (20:06)"
    log_message "="*60
    
    # 确保数据文件存在
    if [ ! -f "$INBOX_DIR/raw_global_data.json" ]; then
        log_message "❌ 无法找到数据文件，跳过Skill处理"
        return 1
    fi
    
    # 方法1: 直接触发Skill处理
    log_message "🔧 方法1: 直接触发Skill处理..."
    START_TIME=$(date +%s)
    
    cd "$SCRIPT_DIR" && python3 "$SKILL_SCRIPT" --file "$INBOX_DIR/raw_global_data.json" >> "$LOG_FILE" 2>&1
    SKILL_EXIT_CODE=$?
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ $SKILL_EXIT_CODE -eq 0 ]; then
        log_message "✅ Skill处理完成 (耗时: ${DURATION}秒)"
        
        # 检查报告是否生成
        LATEST_REPORT=$(ls -t "$WEB_REPORT_DIR"/global_dragon_tiger_*.html 2>/dev/null | head -1)
        if [ -n "$LATEST_REPORT" ]; then
            log_message "📊 报告生成: $(basename "$LATEST_REPORT")"
            
            # 更新最新报告链接
            cd "$WEB_REPORT_DIR" && ln -sf "$(basename "$LATEST_REPORT")" global_dragon_tiger_latest.html
            log_message "🔗 最新报告链接已更新"
        fi
    else
        log_message "⚠️  Skill处理失败，尝试方法2..."
        
        # 方法2: 使用--inbox参数
        log_message "🔧 方法2: 使用inbox模式..."
        cd "$SCRIPT_DIR" && python3 "$SKILL_SCRIPT" --inbox "$INBOX_DIR" >> "$LOG_FILE" 2>&1
    fi
    
    # 确保监听模式运行（用于后续处理）
    ensure_skill_watch_mode
}

# 确保Skill监听模式运行
ensure_skill_watch_mode() {
    log_message "🔍 检查Skill监听模式..."
    
    SKILL_WATCH_PROCESS=$(pgrep -f "Skill_Global_Audit.py.*--watch")
    if [ -z "$SKILL_WATCH_PROCESS" ]; then
        log_message "🔧 启动Skill监听模式..."
        cd "$SCRIPT_DIR" && nohup python3 "$SKILL_SCRIPT" --watch --inbox "$INBOX_DIR" > "$SCRIPT_DIR/skill_watch.log" 2>&1 &
        SKILL_PID=$!
        sleep 3
        
        if kill -0 "$SKILL_PID" 2>/dev/null; then
            log_message "✅ Skill监听模式已启动 (PID: $SKILL_PID)"
            log_message "📝 监听日志: $SCRIPT_DIR/skill_watch.log"
        else
            log_message "⚠️  Skill监听模式启动失败"
        fi
    else
        log_message "✅ Skill监听模式已在运行 (PID: $SKILL_WATCH_PROCESS)"
    fi
}

# 阶段4: Web部署验证
stage4_web_deployment() {
    log_message "="*60
    log_message "🌐 阶段4: Web部署验证 (20:10)"
    log_message "="*60
    
    # 查找最新报告
    LATEST_REPORT=$(ls -t "$WEB_REPORT_DIR"/global_dragon_tiger_*.html 2>/dev/null | head -1)
    if [ -z "$LATEST_REPORT" ]; then
        log_message "❌ 未找到生成的报告"
        return 1
    fi
    
    REPORT_NAME=$(basename "$LATEST_REPORT")
    log_message "📄 最新报告: $REPORT_NAME"
    
    # 部署到Web服务器
    log_message "🚀 部署报告到Web服务器..."
    sudo cp "$LATEST_REPORT" "/var/www/gemini_master/master-audit/"
    sudo rm -f "/var/www/gemini_master/master-audit/global_dragon_tiger_latest.html"
    sudo ln -s "/var/www/gemini_master/master-audit/$REPORT_NAME" "/var/www/gemini_master/master-audit/global_dragon_tiger_latest.html"
    
    # 验证部署
    if [ -f "/var/www/gemini_master/master-audit/$REPORT_NAME" ]; then
        log_message "✅ Web部署成功: /var/www/gemini_master/master-audit/$REPORT_NAME"
        log_message "🔗 最新链接: /var/www/gemini_master/master-audit/global_dragon_tiger_latest.html"
    else
        log_message "⚠️  Web部署可能失败，检查权限"
    fi
}

# 阶段5: 执行结果汇总
stage5_result_summary() {
    log_message "="*60
    log_message "📊 阶段5: 执行结果汇总 (20:15)"
    log_message "="*60
    
    # 统计信息
    if [ -f "$INBOX_DIR/raw_global_data.json" ]; then
        FILE_SIZE=$(stat -c%s "$INBOX_DIR/raw_global_data.json")
        log_message "📦 数据文件大小: ${FILE_SIZE}字节"
    fi
    
    REPORT_COUNT=$(ls "$WEB_REPORT_DIR"/global_dragon_tiger_*.html 2>/dev/null | wc -l)
    log_message "📄 报告文件数量: ${REPORT_COUNT}"
    
    LATEST_REPORT=$(ls -t "$WEB_REPORT_DIR"/global_dragon_tiger_*.html 2>/dev/null | head -1)
    if [ -n "$LATEST_REPORT" ]; then
        REPORT_TIME=$(stat -c%y "$LATEST_REPORT" 2>/dev/null | cut -d'.' -f1)
        log_message "🕒 最新报告时间: ${REPORT_TIME}"
    fi
    
    # 检查Web访问
    WEB_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost:10168/master-audit/global_dragon_tiger_latest.html 2>/dev/null || echo "无法访问")
    log_message "🌐 Web访问状态: HTTP ${WEB_STATUS}"
    
    log_message "✅ 全球引力定时巡航执行完成"
    log_message "🔗 访问地址: https://localhost:10168/master-audit/global_dragon_tiger_latest.html"
}

# 主函数
main() {
    log_message "="*70
    log_message "🌍 全球引力定时巡航启动 (修复版 v2.0.0)"
    log_message "执行日期: $DATE_TAG"
    log_message "执行时间: $TIMESTAMP"
    log_message "团队: Cheese Intelligence Team"
    log_message "="*70
    
    # 确保目录结构
    ensure_directories
    
    # 执行各阶段
    stage1_data_fetch
    stage2_data_delivery
    stage3_skill_processing
    stage4_web_deployment
    stage5_result_summary
    
    log_message "="*70
    log_message "🎉 自动化流水线执行完成"
    log_message "下次执行: 明日 20:00"
    log_message "="*70
}

# 执行主函数
main "$@"