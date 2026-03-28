# Cheese Intelligence MVP补丁路线图
## 基于首席架构师建议的最小可行性路径

**制定时间**: 2026年3月14日 13:30 (GMT+8)
**制定者**: Cheese (奶酪) - 金融教授 & 数字营销专家
**状态**: ✅ 第一项已完成，三项待实施

---

## 📋 MVP补丁概览

### ✅ **已完成** (2026-03-14)
1. **PDF生命周期管理** - 30/90策略集成到日志清理流程

### 🚀 **待实施** (根据今晚19:00执行情况决定优先级)
2. **邮件通知系统** - 本地msmtp → SendGrid API
3. **健康检查监控** - HTTP状态码 + MySQL进程探测 + Webhook告警
4. **备份恢复系统** - wp db export + archive同步

---

## 🔧 MVP 1: PDF生命周期管理 (已完成)

### 🎯 实现状态
- **脚本位置**: `../Documents/Cheese_Intelligence/log_and_pdf_manager.sh`
- **cron集成**: 每周日00:00执行（原日志监控任务升级）
- **策略生效**: 30天活跃期 → 90天归档期 → 90天清理期

### 📊 技术架构
```
PDF文件生命周期:
├── 活跃期 (0-30天)
│   └── /var/www/cheese_blog/wp-content/uploads/reports/
├── 归档期 (30-90天)  
│   └── ../Documents/Cheese_Intelligence/archive/pdf/YYYY-MM/
└── 清理期 (90+天) - 自动删除
```

### 🔍 验证方法
1. 等待文件自然老化测试
2. 手动修改文件时间进行测试
3. 监控每周日执行日志

---

## 📧 MVP 2: 邮件通知系统

### 🎯 目标
- 发布成功后发送"每日简报"邮件
- 包含PDF附件和关键指标
- 初期使用本地msmtp，后期集成SendGrid

### 📋 实施路径

#### 阶段1: 本地邮件系统 (本周内)
```bash
# 安装依赖
sudo apt-get install msmtp msmtp-mta mailutils

# 配置msmtp
~/.msmtprc:
defaults
auth on
tls on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
account default
host smtp.gmail.com
port 587
from your-email@gmail.com
user your-email@gmail.com
password your-app-password
```

#### 阶段2: 邮件通知脚本
```bash
#!/bin/bash
# cheese_email_notifier.sh

# 配置
RECIPIENT="haiyang@example.com"
SUBJECT="Cheese Intelligence 每日简报 - $(date +%Y-%m-%d)"
PDF_PATH="$1"
LOG_PATH="$2"

# 生成邮件内容
BODY="
Cheese Intelligence 系统报告
============================

📅 报告时间: $(date)
🌐 博客状态: https://cheese.ai/blog
📊 今日发布: 已完成

📈 关键指标:
- 文章ID: $ARTICLE_ID
- PDF大小: $(stat -c%s "$PDF_PATH") 字节
- 生成时间: $GENERATION_TIME 秒

📋 系统状态:
$(systemctl status nginx mariadb php8.2-fpm --no-pager)

🔗 相关链接:
- 博客首页: https://cheese.ai/blog
- About页面: https://cheese.ai/blog/about
- PDF下载: $(basename "$PDF_PATH")

---
Cheese Intelligence - AI驱动的财经观察哨
"

# 发送邮件（带附件）
echo "$BODY" | mail -s "$SUBJECT" -a "$PDF_PATH" "$RECIPIENT"
```

#### 阶段3: SendGrid集成 (可选)
- 注册SendGrid账户
- 获取API密钥
- 使用curl或专用库发送
- 支持HTML格式和跟踪

### 🎨 邮件设计要素
1. **品牌一致性**: Cheese Intelligence主题色和logo
2. **内容结构**: 简报摘要 + 关键指标 + 系统状态
3. **行动号召**: 博客访问链接 + PDF下载
4. **移动优化**: 响应式设计

---

## 🩺 MVP 3: 健康检查监控

### 🎯 目标
- 定时探测博客可访问性
- 监控MySQL和Web服务状态
- 异常时通过Webhook发送告警

### 📋 实施路径

#### 阶段1: 基础健康检查脚本
```bash
#!/bin/bash
# health_check.sh

# 配置
BLOG_URL="https://cheese.ai/blog"
WEBHOOK_URL="https://api.example.com/webhook/cheese-alert"
CHECK_INTERVAL=300  # 5分钟

# 检查函数
check_http() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BLOG_URL")
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "✅ HTTP检查通过: $HTTP_CODE"
        return 0
    else
        echo "❌ HTTP检查失败: $HTTP_CODE"
        send_alert "HTTP服务异常" "状态码: $HTTP_CODE"
        return 1
    fi
}

check_mysql() {
    if systemctl is-active --quiet mariadb; then
        echo "✅ MySQL服务运行正常"
        return 0
    else
        echo "❌ MySQL服务停止"
        send_alert "MySQL服务停止" "请立即检查数据库服务"
        return 1
    fi
}

check_disk() {
    USAGE=$(df /var/www --output=pcent | tail -1 | tr -d '% ')
    if [ "$USAGE" -lt 90 ]; then
        echo "✅ 磁盘空间正常: ${USAGE}%"
        return 0
    else
        echo "⚠️  磁盘空间紧张: ${USAGE}%"
        send_alert "磁盘空间紧张" "使用率: ${USAGE}%"
        return 1
    fi
}

# Webhook告警函数
send_alert() {
    local title="$1"
    local message="$2"
    local timestamp=$(date -Iseconds)
    
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"title\": \"$title\",
            \"message\": \"$message\",
            \"timestamp\": \"$timestamp\",
            \"system\": \"Cheese Intelligence\",
            \"severity\": \"critical\"
        }"
}

# 主检查循环
main() {
    echo "🩺 开始健康检查 - $(date)"
    
    check_http
    check_mysql
    check_disk
    
    echo "🩺 健康检查完成 - $(date)"
}

main
```

#### 阶段2: 监控仪表板 (可选)
- 使用Grafana + Prometheus
- 实时显示系统指标
- 历史趋势分析
- 告警规则配置

#### 阶段3: 手机通知集成
- Telegram Bot通知
- Slack Webhook
- 短信告警（Twilio）

### 📊 监控指标
1. **可用性**: HTTP状态码、响应时间
2. **服务状态**: Nginx、MySQL、PHP-FPM
3. **资源使用**: CPU、内存、磁盘、网络
4. **业务指标**: 发布成功率、PDF生成时间

---

## 💾 MVP 4: 备份恢复系统

### 🎯 目标
- 定期备份WordPress数据库
- 同步Markdown源文件到archive目录
- 支持一键恢复

### 📋 实施路径

#### 阶段1: 数据库备份脚本
```bash
#!/bin/bash
# cheese_backup_system.sh

# 配置
BACKUP_DIR="../Documents/Cheese_Intelligence/backup"
DB_BACKUP_DIR="${BACKUP_DIR}/database"
FILE_BACKUP_DIR="${BACKUP_DIR}/files"
RETENTION_DAYS=30

# 创建目录
mkdir -p "$DB_BACKUP_DIR"
mkdir -p "$FILE_BACKUP_DIR"

# 数据库备份
backup_database() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${DB_BACKUP_DIR}/cheese_blog_${timestamp}.sql"
    
    echo "📦 开始数据库备份..."
    
    cd /var/www/cheese_blog
    wp db export "$backup_file" --add-drop-table
    
    if [ $? -eq 0 ]; then
        # 压缩备份
        gzip "$backup_file"
        echo "✅ 数据库备份完成: ${backup_file}.gz"
        echo "📊 备份大小: $(stat -c%s "${backup_file}.gz") 字节"
    else
        echo "❌ 数据库备份失败"
        return 1
    fi
}

# 文件备份
backup_files() {
    echo "📁 开始文件备份..."
    
    # 备份Markdown源文件
    rsync -av --delete \
        ../Documents/Cheese_Intelligence/reports/ \
        "${FILE_BACKUP_DIR}/reports/"
    
    # 备份配置文件
    rsync -av \
        ../Documents/Cheese_Intelligence/*.sh \
        ../Documents/Cheese_Intelligence/*.py \
        ../Documents/Cheese_Intelligence/*.md \
        "${FILE_BACKUP_DIR}/config/"
    
    echo "✅ 文件备份完成"
}

# 清理旧备份
cleanup_old_backups() {
    echo "🗑️  清理${RETENTION_DAYS}天前的备份..."
    
    find "$DB_BACKUP_DIR" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
    find "$FILE_BACKUP_DIR" -type f -mtime +${RETENTION_DAYS} -delete
    
    echo "✅ 旧备份清理完成"
}

# 生成备份报告
generate_report() {
    local report_file="${BACKUP_DIR}/backup_report_$(date +%Y%m%d).txt"
    
    echo "📋 备份报告 - $(date)" > "$report_file"
    echo "========================" >> "$report_file"
    echo "" >> "$report_file"
    
    echo "数据库备份:" >> "$report_file"
    find "$DB_BACKUP_DIR" -name "*.sql.gz" -exec stat -c "%y %n (%s bytes)" {} \; >> "$report_file"
    
    echo "" >> "$report_file"
    echo "文件备份:" >> "$report_file"
    du -sh "${FILE_BACKUP_DIR}"/* >> "$report_file"
    
    echo "📄 备份报告生成: $report_file"
}

# 主函数
main() {
    echo "🚀 开始Cheese Intelligence备份 - $(date)"
    
    backup_database
    backup_files
    cleanup_old_backups
    generate_report
    
    echo "🎉 备份完成 - $(date)"
    echo "📁 备份目录: $BACKUP_DIR"
}

main
```

#### 阶段2: 恢复脚本
```bash
#!/bin/bash
# cheese_restore_system.sh

# 恢复数据库
restore_database() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        echo "❌ 备份文件不存在: $backup_file"
        return 1
    fi
    
    echo "🔄 恢复数据库..."
    
    # 解压备份
    gunzip -c "$backup_file" > /tmp/restore.sql
    
    # 导入数据库
    cd /var/www/cheese_blog
    wp db import /tmp/restore.sql
    
    # 清理临时文件
    rm /tmp/restore.sql
    
    echo "✅ 数据库恢复完成"
}

# 恢复文件
restore_files() {
    local source_dir="$1"
    local target_dir="$2"
    
    echo "🔄 恢复文件: $source_dir → $target_dir"
    
    rsync -av "$source_dir/" "$target_dir/"
    
    echo "✅ 文件恢复完成"
}
```

#### 阶段3: 备份策略
- **每日增量备份**: 数据库 + 配置文件
- **每周全量备份**: 所有Markdown源文件
- **月度归档**: 压缩存储到NAS或云存储
- **保留策略**: 30天本地，90天归档

### 🔒 安全考虑
1. **加密备份**: 敏感数据加密存储
2. **异地备份**: 同步到Synology NAS
3. **访问控制**: 备份文件权限限制
4. **恢复测试**: 定期测试恢复流程

---

## 🗓️ 实施时间线

### 第1周 (2026-03-14 至 03-16)
- ✅ PDF生命周期管理 - 已完成
- 📧 邮件通知系统 - 本地msmtp实现
- 🩺 健康检查监控 - 基础脚本开发

### 第2周 (2026-03-17 至 03-23)
- 💾 备份恢复系统 - 数据库备份实现
- 📧 邮件通知系统 - SendGrid集成（可选）
- 🩺 健康检查监控 - Webhook告警集成

### 第3周 (2026-03-24 至 03-30)
- 💾 备份恢复系统 - 文件备份和恢复脚本
- 🩺 健康检查监控 - 监控仪表板（可选）
- 🔄 系统优化 - 根据运行反馈调整

### 第4周 (2026-03-31 至 04-06)
- 🧪 全面测试 - 所有MVP功能集成测试
- 📊 性能评估 - 系统稳定性和效率评估
- 📈 优化迭代 - 基于实际使用优化

---

## 📊 成功指标

### 技术指标
1. **系统可用性**: 99.9% uptime
2. **备份完整性**: 100%备份成功率
3. **告警响应**: 5分钟内异常检测
4. **资源使用**: 磁盘空间 < 80%

### 业务指标
1. **发布成功率**: 每日发布100%成功
2. **通知及时性**: 发布后5分钟内收到邮件
3. **恢复能力**: 30分钟内完成系统恢复
4. **用户体验**: 博客访问延迟 < 2秒

---

## 🎯 决策点

### 今晚19:00后评估
1. **首次自动执行结果**
   - 发布成功率
   - PDF生成质量
   - 系统稳定性

2. **MVP优先级调整**
   - 根据实际需求调整实施顺序
   - 重点解决发现的问题
   - 优化现有流程

3. **资源分配**
   - 开发时间投入
   - 第三方服务集成决策
   - 监控频率调整

---

## 📝 变更记录

### 2026-03-14
- ✅ PDF生命周期管理补丁完成
- 📋 MVP路线图制定完成
- 🔄 日志监控cron任务更新为综合维护任务

### 下一步
- 等待今晚19:00首次自动执行
- 根据执行结果调整MVP实施计划
- 开始邮件通知系统开发

---

**保持敏捷，持续改进！** 🧀🚀