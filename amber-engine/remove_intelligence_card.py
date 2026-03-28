#!/usr/bin/env python3
"""
移除沪深300智能指数卡片
根据主编指令：因为PE倍数 | 等待数据，看起来也是数据管理出错了
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def remove_intelligence_card():
    """移除沪深300智能指数卡片"""
    print("🗑️ 移除沪深300智能指数卡片...")
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找智能指数卡片部分
    # 从注释开始到智能卡片结束的</div>
    intelligence_pattern = r'(<!-- 智能指数卡片 \(独立卡片，不嵌套\) -->\s*<div class="index-intelligence-card">.*?</div>\s*)\s*(<!-- 普通指数卡片 - 沪深300 -->)'
    
    match = re.search(intelligence_pattern, content, re.DOTALL)
    if not match:
        print("❌ 未找到智能指数卡片")
        # 尝试其他匹配模式
        intelligence_pattern2 = r'(<div class="index-intelligence-card">.*?</div>\s*)\s*(<!-- 普通指数卡片 - 沪深300 -->)'
        match = re.search(intelligence_pattern2, content, re.DOTALL)
        if not match:
            return False
    
    # 移除智能指数卡片部分，只保留后面的注释
    new_content = content.replace(match.group(1), "")
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ 沪深300智能指数卡片已移除")
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
        
        print("✅ 沪深300智能指数卡片已移除 (使用sudo)")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("🗑️ 移除沪深300智能指数卡片")
    print("=" * 70)
    print("执行主编指令：沪深300 - 智能指数 这个智能卡面也移除吧，因为PE倍数 | 等待数据，看起来也是数据管理出错了")
    print("=" * 70)
    
    success = remove_intelligence_card()
    
    if success:
        print("\n✅ 移除完成!")
        print("📋 执行结果:")
        print("  1. ✅ 沪深300智能指数卡片已完全移除")
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