#!/usr/bin/env python3
"""
修复总览页面JavaScript执行问题
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OVERVIEW_FILE = os.path.join(BASE_DIR, "web", "bronze_etf_details.html")
FIXED_FILE = os.path.join(BASE_DIR, "web", "bronze_etf_details_fixed.html")

def fix_javascript():
    """修复JavaScript执行问题"""
    print("🔧 修复总览页面JavaScript问题...")
    
    with open(OVERVIEW_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到JavaScript部分
    script_start = content.find('<script>')
    script_end = content.find('</script>', script_start) + 9
    
    if script_start == -1 or script_end == -1:
        print("❌ 找不到JavaScript标签")
        return
    
    old_script = content[script_start:script_end]
    
    # 修复1: 添加DOMContentLoaded事件监听器
    # 修复2: 修复详情页链接路径
    new_script = '''<script>
        // 等待DOM完全加载
        document.addEventListener('DOMContentLoaded', function() {
            console.log('青铜法典页面加载完成，开始初始化...');
            
            // ETF数据
            const etfData = ''' + content[content.find('const etfData ='):content.find(';', content.find('const etfData ='))+1] + '''
            
            // 获取所有赛道
            const sectors = [...new Set(etfData.map(etf => etf.sector))];
            console.log(`发现 ${etfData.length} 支标的，${sectors.length} 个赛道`);
            
            // 初始化筛选器
            const filterContainer = document.getElementById('filterContainer');
            if (!filterContainer) {
                console.error('找不到filterContainer元素');
                return;
            }
            
            sectors.forEach(sector => {
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.textContent = sector;
                btn.dataset.filter = sector;
                btn.addEventListener('click', () => filterETFs(sector));
                filterContainer.appendChild(btn);
            });
            
            // 渲染ETF卡片
            function renderETFs(filter = 'all') {
                const etfGrid = document.getElementById('etfGrid');
                const noResults = document.getElementById('noResults');
                
                if (!etfGrid) {
                    console.error('找不到etfGrid元素');
                    return;
                }
                
                etfGrid.innerHTML = '';
                
                const filtered = etfData.filter(etf => 
                    filter === 'all' || etf.sector === filter
                );
                
                console.log(`筛选结果: ${filtered.length} 支标的`);
                
                if (filtered.length === 0) {
                    if (noResults) noResults.style.display = 'block';
                    return;
                }
                
                if (noResults) noResults.style.display = 'none';
                
                filtered.forEach(etf => {
                    const card = document.createElement('div');
                    card.className = 'etf-card';
                    // 修复链接路径：使用bronze_details/而不是details/
                    card.innerHTML = `
                        <div class="etf-code">${etf.code}</div>
                        <div class="etf-name">${etf.name}</div>
                        <div class="etf-sector">${etf.sector}</div>
                        <a href="bronze_details/${etf.code}.html" class="etf-link">查看详情 →</a>
                    `;
                    etfGrid.appendChild(card);
                });
            }
            
            // 筛选ETF
            function filterETFs(filter) {
                console.log(`筛选赛道: ${filter}`);
                
                // 更新按钮状态
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                const activeBtn = document.querySelector(`[data-filter="${filter}"]`);
                if (activeBtn) activeBtn.classList.add('active');
                
                // 渲染筛选结果
                renderETFs(filter);
            }
            
            // 搜索功能
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const searchTerm = this.value.toLowerCase();
                    const etfGrid = document.getElementById('etfGrid');
                    const noResults = document.getElementById('noResults');
                    
                    if (!searchTerm) {
                        const activeFilter = document.querySelector('.filter-btn.active');
                        if (activeFilter) {
                            renderETFs(activeFilter.dataset.filter);
                        } else {
                            renderETFs('all');
                        }
                        return;
                    }
                    
                    if (etfGrid) etfGrid.innerHTML = '';
                    const filtered = etfData.filter(etf => 
                        etf.code.toLowerCase().includes(searchTerm) || 
                        etf.name.toLowerCase().includes(searchTerm) ||
                        etf.sector.toLowerCase().includes(searchTerm)
                    );
                    
                    console.log(`搜索"${searchTerm}": 找到 ${filtered.length} 个结果`);
                    
                    if (filtered.length === 0) {
                        if (noResults) noResults.style.display = 'block';
                        return;
                    }
                    
                    if (noResults) noResults.style.display = 'none';
                    filtered.forEach(etf => {
                        const card = document.createElement('div');
                        card.className = 'etf-card';
                        card.innerHTML = `
                            <div class="etf-code">${etf.code}</div>
                            <div class="etf-name">${etf.name}</div>
                            <div class="etf-sector">${etf.sector}</div>
                            <a href="bronze_details/${etf.code}.html" class="etf-link">查看详情 →</a>
                        `;
                        if (etfGrid) etfGrid.appendChild(card);
                    });
                });
            }
            
            // 初始渲染
            renderETFs('all');
            console.log('初始渲染完成');
            
            // 添加键盘快捷键
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'k') {
                    e.preventDefault();
                    if (searchInput) searchInput.focus();
                }
            });
        });
        
        // 错误处理
        window.addEventListener('error', function(e) {
            console.error('页面JavaScript错误:', e.message, 'at', e.filename, ':', e.lineno);
        });
    </script>'''
    
    # 替换JavaScript
    fixed_content = content[:script_start] + new_script + content[script_end:]
    
    # 保存修复后的文件
    with open(FIXED_FILE, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 修复完成: {FIXED_FILE}")
    
    # 替换原始文件
    import shutil
    shutil.copy2(FIXED_FILE, OVERVIEW_FILE)
    print(f"✅ 原始文件已更新: {OVERVIEW_FILE}")
    
    # 部署到Web服务器
    deploy_to_web()

def deploy_to_web():
    """部署修复后的文件到Web服务器"""
    print("🚀 部署到Web服务器...")
    
    # 复制到bronze_details目录
    target_dir = "/var/www/gemini_master/bronze_details"
    if os.path.exists(target_dir):
        import shutil
        shutil.copy2(OVERVIEW_FILE, os.path.join(target_dir, "bronze_etf_details.html"))
        print(f"✅ 复制到: {target_dir}/bronze_etf_details.html")
        
        # 更新符号链接
        master_audit_link = "/var/www/gemini_master/master-audit/bronze_etf_details.html"
        if os.path.islink(master_audit_link):
            os.unlink(master_audit_link)
        os.symlink(os.path.join(target_dir, "bronze_etf_details.html"), master_audit_link)
        print(f"✅ 更新符号链接: {master_audit_link}")
    else:
        print(f"⚠️  目标目录不存在: {target_dir}")

def test_fix():
    """测试修复效果"""
    print("🧪 测试修复效果...")
    
    # 检查文件是否存在
    if os.path.exists(OVERVIEW_FILE):
        with open(OVERVIEW_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含DOMContentLoaded
        if 'DOMContentLoaded' in content:
            print("✅ 修复已应用: 包含DOMContentLoaded事件监听器")
        else:
            print("❌ 修复未应用: 不包含DOMContentLoaded")
        
        # 检查链接路径
        if 'bronze_details/${etf.code}.html' in content:
            print("✅ 链接路径已修复: 使用bronze_details/")
        else:
            print("❌ 链接路径未修复")
        
        # 检查控制台日志
        if 'console.log' in content:
            print("✅ 调试日志已添加")
        else:
            print("❌ 无调试日志")
    else:
        print(f"❌ 文件不存在: {OVERVIEW_FILE}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 青铜法典总览页面修复工具")
    print("=" * 60)
    
    fix_javascript()
    test_fix()
    
    print("\n🌐 测试访问:")
    print(f"  总览页: https://localhost:10168/master-audit/bronze_etf_details.html")
    print(f"  详情页示例: https://localhost:10168/master-audit/bronze_details/510300.html")
    print("\n📋 修复内容:")
    print("  1. 添加DOMContentLoaded事件监听器，确保DOM完全加载后执行")
    print("  2. 修复详情页链接路径: details/ → bronze_details/")
    print("  3. 添加调试日志，便于问题诊断")
    print("  4. 添加错误处理，捕获JavaScript错误")
    print("=" * 60)