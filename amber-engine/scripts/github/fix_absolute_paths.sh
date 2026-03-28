#!/bin/bash
# 绝对路径清理脚本 V1.0.0
# 基于[2614-001]安全防线协议
# 修复所有绝对路径泄露问题

set -e

REPO_ROOT="."
BACKUP_DIR="$REPO_ROOT/backup_absolute_paths_$(date +%Y%m%d_%H%M%S)"

echo "=== 绝对路径清理脚本启动 ==="
echo "仓库根目录: $REPO_ROOT"
echo "备份目录: $BACKUP_DIR"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 需要处理的文件类型
FILE_TYPES=("*.sh" "*.py" "*.php" "*.js" "*.md" "*.json" "*.txt")

# 统计函数
total_files=0
total_replacements=0

# 处理每个文件类型
for file_type in "${FILE_TYPES[@]}"; do
    echo "处理 $file_type 文件..."
    
    # 查找文件
    files=$(find "$REPO_ROOT" -name "$file_type" -type f 2>/dev/null | head -100)
    
    for file in $files; do
        # 跳过备份目录
        if [[ "$file" == "$BACKUP_DIR"* ]]; then
            continue
        fi
        
        # 检查是否包含绝对路径
        if grep -q "../" "$file" 2>/dev/null; then
            total_files=$((total_files + 1))
            
            # 创建备份
            backup_file="$BACKUP_DIR/$(basename "$file")_$(date +%s)"
            cp "$file" "$backup_file"
            
            echo "修复: $file"
            
            # 执行替换
            # 1. 替换 ./ 为 ./
            # 2. 替换 . 为 .
            # 3. 替换 ../ 为 ../
            # 4. 替换 ../ 为 ../
            
            # 临时文件
            temp_file="${file}.tmp"
            
            # 执行多级替换
            sed \
                -e "s|./|./|g" \
                -e "s|.|.|g" \
                -e "s|../|../|g" \
                -e "s|../scripts/|../scripts/|g" \
                -e "s|../|../|g" \
                "$file" > "$temp_file"
            
            # 计算替换次数
            replacements=$(diff "$file" "$temp_file" | grep "^<" | wc -l)
            total_replacements=$((total_replacements + replacements))
            
            # 替换原文件
            mv "$temp_file" "$file"
            
            echo "  -> 完成 ($replacements 处替换)"
        fi
    done
done

echo ""
echo "=== 清理完成 ==="
echo "处理文件数: $total_files"
echo "总替换次数: $total_replacements"
echo "备份目录: $BACKUP_DIR"
echo ""

# 验证清理结果
echo "验证清理结果..."
remaining=$(grep -r "../" "$REPO_ROOT" --include="*.sh" --include="*.py" --include="*.php" --include="*.js" --include="*.md" 2>/dev/null | wc -l)

if [ "$remaining" -eq 0 ]; then
    echo "✅ 所有绝对路径已清理完成"
else
    echo "⚠️ 仍有 $remaining 处绝对路径需要手动处理"
    grep -r "../" "$REPO_ROOT" --include="*.sh" --include="*.py" --include="*.php" --include="*.js" --include="*.md" 2>/dev/null | head -20
fi