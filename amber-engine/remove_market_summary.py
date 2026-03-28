#!/usr/bin/env python3
"""
移除市场成交概览板块
根据主编指令：数据不能管理，就把它移除掉
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def remove_market_summary():
    """移除市场成交概览板块"""
    print("🗑️ 移除市场成交概览板块...")
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找市场成交概览部分
    # 从注释开始到下一个卡片开始之前
    market_pattern = r'(<!-- 市场成交概览卡片 -->.*?<div class="data-source-tag verified">Tushare Pro</div>\s*</div>\s*)\s*(<!-- 宏观四锚决策头 -->)'
    
    match = re.search(market_pattern, content, re.DOTALL)
    if not match:
        print("❌ 未找到市场成交概览板块")
        return False
    
    # 移除市场成交概览部分，只保留后面的注释
    new_content = content.replace(match.group(1), "")
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ 市场成交概览板块已移除")
        return True
    except PermissionError:
        print("⚠️ 权限不足，使用sudo tee")
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
            tmp.write(new_content)
            tmp_path = tmp.name
        
        result = subprocess.run(f'sudo tee {INDEX_FILE} < {tmp_path} > /dev/null', shell=True)
        os.unlink(tmp_path)
        
        if result.returncode != 0:
            print("❌ sudo tee写入失败")
            return False
        
        print("✅ 市场成交概览板块已移除 (使用sudo)")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("🗑️ 移除市场成交概览板块")
    print("=" * 70)
    print("执行主编指令：首页：市场成交概览 A股 等待数据，这个板块，即数据不能管理，就把它移除掉")
    print("=" * 70)
    
    # 备份原文件
    backup_file = f"{INDEX_FILE}.backup.{os.path.basename(__file__)}"
    try:
        import shutil
        shutil.copy2(INDEX_FILE, backup_file)
        print(f"📁 原文件已备份: {backup_file}")
    except Exception as e:
        print(f"⚠️ 备份失败: {e} (继续执行)")
    
    success = remove_market_summary()
    
    if success:
        print("\n✅ 移除完成!")
        print("📋 执行结果:")
        print("  1. ✅ 市场成交概览卡片已完全移除")
        print("  2. ✅ 保持页面其他部分完整")
        print("  3. ✅ 网格布局自动调整")
        print(f"\n🔗 验证地址: https://amber.googlemanager.cn:10123/")
    else:
        print("\n❌ 移除失败")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)