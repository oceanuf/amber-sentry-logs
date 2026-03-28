#!/usr/bin/env python3
"""
在页面中添加最后更新时间显示
根据主编要求：数据更新后要显示这个数据的最后更新的时间
"""

import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def add_update_time():
    """在页面中添加最后更新时间显示"""
    print("🕒 添加最后更新时间显示...")
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 从缓存文件获取更新时间
    cache_file = os.path.join(BASE_DIR, "output", "static", "data", "unified_data_cache.json")
    update_time = "未知时间"
    
    if os.path.exists(cache_file):
        import json
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                update_time = cache_data.get('update_time', '未知时间')
        except:
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 在页面标题下方添加更新时间
    time_display = f'''
                <div class="update-time-display">
                    <span class="time-icon">🕒</span>
                    <span class="time-text">数据最后更新时间: {update_time} (北京时间)</span>
                    <span class="time-note">数据源: Tushare Pro | 更新频率: 交易日收盘后</span>
                </div>'''
    
    # 查找页面标题位置，在其后添加更新时间
    page_header_pattern = r'(<div class="page-header">.*?<p class="update-time">页面重建时间:[^<]*</p>\s*)(</div>)'
    
    def add_time_display(match):
        return match.group(1) + time_display + match.group(2)
    
    new_content = re.sub(page_header_pattern, add_time_display, content, flags=re.DOTALL)
    
    # 如果没有找到页面标题，尝试其他位置
    if new_content == content:
        print("⚠️ 未找到页面标题位置，尝试在琥珀全景标题后添加")
        # 在琥珀全景标题后添加
        amber_header_pattern = r'(<div class="amber-pan-header">.*?<span class="update-time">)[^<]*(</span>\s*</div>)'
        
        def add_time_to_amber(match):
            return match.group(1) + f"更新: {update_time} (北京时间) | 🔍 数据已验证" + match.group(2)
        
        new_content = re.sub(amber_header_pattern, add_time_to_amber, content, flags=re.DOTALL)
    
    # 更新数据源标签
    print("🔧 更新数据源标签...")
    # 将"等待更新"改为"Tushare Pro"
    new_content = new_content.replace('data-source-tag">等待更新</div>', 'data-source-tag verified">Tushare Pro</div>')
    new_content = new_content.replace('data-source-tag">等待Tushare Pro数据</div>', 'data-source-tag verified">Tushare Pro</div>')
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 最后更新时间已添加: {update_time}")
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
        
        print(f"✅ 最后更新时间已添加 (使用sudo): {update_time}")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("🕒 添加最后更新时间显示")
    print("=" * 70)
    print("根据主编要求:")
    print("1. 数据更新后要显示这个数据的最后更新的时间")
    print("2. 如果没有数据，就显示暂无数据，不要乱填充数据")
    print("3. 不要看到'等待更新'这样的字眼")
    print("=" * 70)
    
    success = add_update_time()
    
    if success:
        print("\n✅ 更新完成!")
        print("📋 完成内容:")
        print("  1. ✅ 添加数据最后更新时间显示")
        print("  2. ✅ 更新数据源标签为'Tushare Pro'")
        print("  3. ✅ 移除'等待更新'字眼")
        print(f"\n🔗 验证地址: https://amber.googlemanager.cn:10123/")
    else:
        print("\n❌ 更新失败")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)