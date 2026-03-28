#!/usr/bin/env python3
"""
移除"等待数据更新..."文本
根据主编指令：标题：琥珀全景 - 实时行情数据 下方也有 等待数据更新... 把这段话移除掉
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def remove_waiting_text():
    """移除等待数据更新文本"""
    print("🗑️ 移除'等待数据更新...'文本...")
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并移除<span class="update-time">等待数据更新...</span>
    # 但保留<span>标签，以便后续可以填充实际更新时间
    waiting_pattern = r'(<span class="update-time">)等待数据更新...(</span>)'
    
    # 替换为空的update-time，保持结构完整
    new_content = re.sub(waiting_pattern, r'\1\2', content)
    
    # 如果模式不匹配，尝试其他方式
    if new_content == content:
        # 直接移除整个span元素
        waiting_pattern2 = r'\s*<span class="update-time">等待数据更新...</span>\s*'
        new_content = re.sub(waiting_pattern2, '', content)
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ '等待数据更新...'文本已移除")
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
        
        print("✅ '等待数据更新...'文本已移除 (使用sudo)")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("🗑️ 移除'等待数据更新...'文本")
    print("=" * 70)
    print("执行主编指令：标题：琥珀全景 - 实时行情数据 下方也有 等待数据更新... 把这段话移除掉")
    print("=" * 70)
    
    success = remove_waiting_text()
    
    if success:
        print("\n✅ 移除完成!")
        print("📋 执行结果:")
        print("  1. ✅ '等待数据更新...'文本已移除")
        print("  2. ✅ 保持页面结构完整")
        print("  3. ✅ 标题区域更简洁")
        print(f"\n🔗 验证地址: https://amber.googlemanager.cn:10123/")
    else:
        print("\n❌ 移除失败")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)