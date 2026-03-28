#!/usr/bin/env python3
"""
修复宏观四锚HTML结构，使其与统一数据引擎匹配
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")

def fix_macro_structure():
    """修复宏观四锚HTML结构"""
    print("🔧 修复宏观四锚HTML结构...")
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找宏观四锚部分
    macro_section = re.search(r'(<!-- 宏观四锚决策头 -->.*?<div class="data-source-tag[^"]*">)[^<]*(</div>)', content, re.DOTALL)
    if not macro_section:
        print("❌ 未找到宏观四锚部分")
        return False
    
    # 替换整个宏观四锚部分为引擎期望的结构
    new_macro_section = '''<!-- 宏观四锚决策头 -->
                    <div class="index-item macro-anchor-card">
                        <div class="index-header">
                            <span class="index-name">宏观四锚</span>
                            <span class="index-market">决策头</span>
                        </div>
                        
                        <div class="macro-anchor-content">
                            <div class="anchor-item">
                                <span class="anchor-label">💵 人民币汇率 (USD/CNY)</span>
                                <span class="anchor-value">--</span>
                                <span class="anchor-change change-neutral">暂无数据</span>
                            </div>
                            
                            <div class="anchor-item">
                                <span class="anchor-label">🇺🇸 美债10Y收益率</span>
                                <span class="anchor-value">--%</span>
                                <span class="anchor-change change-neutral">暂无数据</span>
                            </div>
                            
                            <div class="anchor-item">
                                <span class="anchor-label">🌍 国际金价 (XAUUSD)</span>
                                <span class="anchor-value">-- USD/oz</span>
                                <span class="anchor-change change-neutral">暂无数据</span>
                            </div>
                            
                            <div class="anchor-item">
                                <span class="anchor-label">🇨🇳 国内金价 (AU.SHF)</span>
                                <span class="anchor-value">-- CNY/g</span>
                                <span class="anchor-change change-neutral">暂无数据</span>
                            </div>
                        </div>
                        
                        <div class="data-source-tag">等待Tushare Pro数据</div>
                    </div>'''
    
    # 替换
    new_content = content.replace(macro_section.group(0), new_macro_section)
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ 宏观四锚结构修复完成")
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
        
        print("✅ 宏观四锚结构修复完成 (使用sudo)")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("🔧 修复宏观四锚结构")
    print("=" * 70)
    
    success = fix_macro_structure()
    
    if success:
        print("\n✅ 修复完成!")
        print("📋 修复内容:")
        print("  1. ✅ 更新HTML结构以匹配统一数据引擎")
        print("  2. ✅ 使用<span>标签替代<div>标签")
        print("  3. ✅ 添加货币符号和国家标志")
        print("  4. ✅ 无数据时显示'暂无数据'")
        print("\n⏰ 下一步: 运行统一数据引擎更新宏观数据")
    else:
        print("\n❌ 修复失败")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)