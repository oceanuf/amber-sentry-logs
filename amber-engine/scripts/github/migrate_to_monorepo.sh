#!/bin/bash
# 单体仓库文件迁移脚本 V1.0.0
# 基于[2614-001]档案馆单体仓库同步法典 V3.1
# 生效日期: 2026-03-30

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REPO_ROOT="$(pwd)"
echo -e "${GREEN}=== 单体仓库文件迁移脚本启动 ===${NC}"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "仓库根目录: $REPO_ROOT"
echo ""

# 步骤1: 创建备份目录
BACKUP_DIR="$REPO_ROOT/backup_monorepo_migration_$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}[步骤1] 创建备份目录: $BACKUP_DIR${NC}"

# 步骤2: 迁移报告文件到 docs/reports/
echo -e "${YELLOW}[步骤2] 迁移报告文件到 docs/reports/${NC}"
REPORT_FILES=(
    "2613-*.md"
    "琥珀引擎演武场重筑执行报告*.md"
    "琥珀引擎演武场重筑执行总结*.md"
    "Task-*.md"
    "档案馆模组化树状图报告*.md"
    "GITHUB_SYNC_REPORT.md"
    "ARCHIVE_TASK_COMPLETION_REPORT.md"
    "EXECUTIVE_SUMMARY_FINAL.md"
    "config_optimization_execution.md"
    "config_optimization_report.md"
    "Cheese_MVP_Roadmap.md"
    "琥珀引擎v3.2.7技术方案.md"
    "access_guide.md"
    "琥珀引擎收盘自动更新报告*.md"
    "琥珀引擎系统健康检查报告*.md"
    "项目进度总结*.md"
    "P0修复完成报告.md"
    "V2_SYNC_EXECUTION_REPORT.md"
    "TASK_*.md"
    "ARCHITECT_PRESENTATION.md"
    "TECHNICAL_MANIFEST.md"
    "AMBER_ENGINE_AUDIT_REPORT_FINAL.md"
    "ARCHIVE_SEAL*.md"
    "ARCHIVE_V1_MANIFEST.md"
    "AMBER_STATUS.md"
    "Cheese_Intelligence_V2_Architecture_Completion_Report.md"
    "Cheese_About_Page.md"
    "CHIEF_MANIFESTO.md"
    "REPORT_EMAIL_TEMPLATE.md"
)

mkdir -p "$REPO_ROOT/docs/reports"

for pattern in "${REPORT_FILES[@]}"; do
    for file in $REPO_ROOT/$pattern; do
        if [ -f "$file" ]; then
            echo "迁移报告: $(basename "$file")"
            mv "$file" "$REPO_ROOT/docs/reports/"
        fi
    done
done

# 步骤3: 迁移脚本文件到 scripts/
echo -e "${YELLOW}[步骤3] 迁移脚本文件到 scripts/${NC}"
SCRIPT_FILES=(
    "*.sh"
    "*.py"
    "*.php"
)

# 检查scripts目录结构
mkdir -p "$REPO_ROOT/scripts/github"
mkdir -p "$REPO_ROOT/scripts/automation"
mkdir -p "$REPO_ROOT/scripts/data"

# 移动现有的github相关脚本
if [ -f "$REPO_ROOT/sync_core_files.sh" ]; then
    echo "迁移脚本: sync_core_files.sh"
    mv "$REPO_ROOT/sync_core_files.sh" "$REPO_ROOT/scripts/github/"
fi

if [ -f "$REPO_ROOT/archive_only_sync.sh" ]; then
    echo "迁移脚本: archive_only_sync.sh"
    mv "$REPO_ROOT/archive_only_sync.sh" "$REPO_ROOT/scripts/github/"
fi

if [ -f "$REPO_ROOT/verify_sync.sh" ]; then
    echo "迁移脚本: verify_sync.sh"
    mv "$REPO_ROOT/verify_sync.sh" "$REPO_ROOT/scripts/github/"
fi

if [ -f "$REPO_ROOT/simple_archive_sync.sh" ]; then
    echo "迁移脚本: simple_archive_sync.sh"
    mv "$REPO_ROOT/simple_archive_sync.sh" "$REPO_ROOT/scripts/github/"
fi

# 步骤4: 清理根目录杂文件
echo -e "${YELLOW}[步骤4] 清理根目录杂文件${NC}"

# 保留的核心文件
KEEP_FILES=(
    "AGENTS.md"
    "SOUL.md"
    "USER.md"
    "IDENTITY.md"
    "MEMORY.md"
    "HEARTBEAT.md"
    "TOOLS.md"
    "BOOTSTRAP.md"
    ".gitignore"
    ".env"
    ".env.template"
    ".env.amber"
    "README.md"
)

# 创建临时列表
TEMP_LIST="$BACKUP_DIR/files_to_keep.txt"
for file in "${KEEP_FILES[@]}"; do
    echo "$file" >> "$TEMP_LIST"
done

# 移动非核心文件到备份目录
echo "清理根目录..."
find "$REPO_ROOT" -maxdepth 1 -type f \( -name "*.md" -o -name "*.sh" -o -name "*.py" -o -name "*.php" -o -name "*.json" -o -name "*.html" \) | while read -r file; do
    filename=$(basename "$file")
    if ! grep -q "^$filename$" "$TEMP_LIST" 2>/dev/null; then
        if [[ "$filename" != "migrate_to_monorepo.sh" ]]; then
            echo "备份: $filename"
            mv "$file" "$BACKUP_DIR/"
        fi
    fi
done

# 步骤5: 验证目录结构
echo -e "${YELLOW}[步骤5] 验证目录结构${NC}"

REQUIRED_DIRS=("web" "vaults" "docs/reports" "scripts" "database")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        echo -e "${GREEN}✅ 目录存在: $dir${NC}"
    else
        echo -e "${RED}❌ 目录缺失: $dir${NC}"
        exit 1
    fi
done

# 步骤6: 生成迁移报告
echo -e "${YELLOW}[步骤6] 生成迁移报告${NC}"

MIGRATION_REPORT="$REPO_ROOT/docs/reports/monorepo-migration-$(date '+%Y%m%d_%H%M%S').md"
cat > "$MIGRATION_REPORT" << EOF
# 单体仓库迁移执行报告
**迁移时间**: $(date '+%Y-%m-%d %H:%M:%S')
**法典依据**: [2614-001]档案馆单体仓库同步法典 V3.1
**执行脚本**: migrate_to_monorepo.sh V1.0.0

## 迁移摘要
- **备份目录**: $BACKUP_DIR
- **迁移报告数量**: $(find "$REPO_ROOT/docs/reports" -name "*.md" | wc -l)
- **清理文件数量**: $(find "$BACKUP_DIR" -type f | wc -l)

## 目录结构验证
$(for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        echo "- ✅ $dir"
    else
        echo "- ❌ $dir"
    fi
done)

## 保留的核心文件
$(for file in "${KEEP_FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        echo "- ✅ $file"
    else
        echo "- ❌ $file"
    fi
done)

## 迁移状态
✅ 单体仓库结构迁移完成

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**执行者**: 工程师 Cheese 🧀
**法典版本**: V3.1 (2614-001)
EOF

echo -e "${GREEN}📄 迁移报告已生成: $MIGRATION_REPORT${NC}"

# 步骤7: 更新.gitignore
echo -e "${YELLOW}[步骤7] 更新.gitignore${NC}"

if [ -f "$REPO_ROOT/.gitignore" ]; then
    cat >> "$REPO_ROOT/.gitignore" << EOF

# 基于[2614-001]法典的安全忽略规则
*.log
private_*.json
config_*.json
.env
.env.*
backup_*/
backup_monorepo_*/
amber-sentry-logs/
__pycache__/
*.pyc
*.db
*.sqlite
*.sqlite3
credentials.json
secrets.json
token.json
EOF
    echo -e "${GREEN}✅ .gitignore已更新${NC}"
fi

echo -e "${GREEN}=== 单体仓库迁移完成 ===${NC}"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "备份目录: $BACKUP_DIR"
echo "迁移报告: $MIGRATION_REPORT"
echo ""
echo -e "${YELLOW}⚠️ 重要提示:${NC}"
echo "1. 请检查备份目录中的文件，确保重要文件已正确迁移"
echo "2. 运行 ./scripts/github/sync_clean.sh 进行首次法典合规同步"
echo "3. 访问 https://github.com/your-username/amber-engine 验证仓库结构"