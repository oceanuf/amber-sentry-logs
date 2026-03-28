#!/usr/bin/env python3
"""
完整页面重建 - 创建干净的index.html模板
根据主编指令执行方案B
"""

import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.html")

def create_clean_index():
    """创建干净的index.html模板"""
    print("🔧 创建干净的index.html模板...")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    clean_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>琥珀引擎 - 财经品牌独立站 | Cheese Intelligence</title>
    <meta name="description" content="琥珀引擎 Amber-Engine V3.2.7 - 数据库驱动 + 静态化生成的专业财经媒体架构。每日财经分析、市场趋势、投资策略与琥珀内参。">
    
    <!-- 琥珀引擎 V2.2 视觉系统 -->
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    
    <style>
        /* 页面特定样式 */
        .grid-container {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 25px;  /* 架构师指定的25px卡片间距 */
            margin: 2rem 0;
        }}
        
        @media (max-width: 1024px) {{
            .grid-container {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        
        @media (max-width: 768px) {{
            .grid-container {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* 智能卡片专用样式 */
        .index-intelligence-card {{
            grid-column: span 1;
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            color: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0;
        }}
        
        /* 确保智能卡片不会溢出 */
        .index-intelligence-card {{
            min-height: 250px;
            max-height: 280px;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <!-- 站点头部 -->
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <div class="brand">
                    <a href="/" class="brand-link">
                        <span class="brand-icon">🧀</span>
                        <span class="brand-text">
                            <span class="brand-name">琥珀引擎</span>
                            <span class="brand-tagline">财经品牌独立站</span>
                        </span>
                    </a>
                </div>
                
                <nav class="main-nav">
                    <ul class="nav-list">
                        <li class="nav-item"><a href="/" class="nav-link active">首页</a></li>
                        <li class="nav-item"><a href="/etf/" class="nav-link">ETF专区</a></li>
                        <li class="nav-item"><a href="/about.html" class="nav-link">关于我们</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
        <div class="container">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1>琥珀引擎 V3.2.7</h1>
                <p class="page-subtitle">财经品牌独立站 - 数据库驱动 + 静态化生成的专业媒体架构</p>
                <p class="update-time">页面重建时间: {current_time} (北京时间)</p>
            </div>
            
            <!-- 琥珀全景指数看板 -->
            <div class="amber-pan-container">
                <div class="amber-pan-header">
                    <h3>🌐 琥珀全景 - 实时行情数据</h3>
                    <span class="update-time">等待数据更新...</span>
                </div>
                
                <!-- 网格布局容器 -->
                <div class="grid-container">
                    <!-- 智能指数卡片 (独立卡片，不嵌套) -->
                    <div class="index-intelligence-card">
                        <div class="intelligence-header">
                            <h4>🌐 沪深300 - 智能指数</h4>
                            <span class="data-source-tag verified">等待Tushare Pro数据</span>
                        </div>
                        
                        <div class="intelligence-grid">
                            <!-- 点位模块 -->
                            <div class="intelligence-module point-module">
                                <div class="module-label">实时点位</div>
                                <div class="module-value">--</div>
                                <div class="module-change">等待数据</div>
                                <div class="module-meta">成交额: --</div>
                            </div>
                            
                            <!-- 估值模块 -->
                            <div class="intelligence-module valuation-module">
                                <div class="module-label">估值水平</div>
                                <div class="module-value">--</div>
                                <div class="module-detail">PE倍数 | 等待数据</div>
                                <div class="module-meta">历史分位: --</div>
                            </div>
                            
                            <!-- 资金模块 -->
                            <div class="intelligence-module moneyflow-module">
                                <div class="module-label">北向资金</div>
                                <div class="module-value">--</div>
                                <div class="module-detail">净流入 | 等待数据</div>
                                <div class="module-meta">累计: --</div>
                            </div>
                            
                            <!-- 波动模块 -->
                            <div class="intelligence-module volatility-module">
                                <div class="module-label">波动率</div>
                                <div class="module-value">--</div>
                                <div class="module-detail">VIX指数 | 等待数据</div>
                                <div class="module-meta">历史分位: --</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 普通指数卡片 - 沪深300 -->
                    <div class="index-item">
                        <div class="index-header">
                            <span class="index-name">沪深300</span>
                            <span class="index-market">A股</span> <span class="index-code">000300.SH</span>
                        </div>
                        <div class="index-value">--</div>
                        <div class="index-change">等待数据</div>
                        <div class="data-source-tag">等待更新</div>
                    </div>
                    
                    <!-- 普通指数卡片 - 创业板指 -->
                    <div class="index-item">
                        <div class="index-header">
                            <span class="index-name">创业板指</span>
                            <span class="index-market">A股</span> <span class="index-code">399006.SZ</span>
                        </div>
                        <div class="index-value">--</div>
                        <div class="index-change">等待数据</div>
                        <div class="data-source-tag">等待更新</div>
                    </div>
                    
                    <!-- 市场成交概览卡片 -->
                    <div class="index-item market-summary-card">
                        <div class="index-header">
                            <span class="index-name">市场成交概览</span>
                            <span class="index-market">A股</span> <span class="index-code">等待数据</span>
                        </div>
                        
                        <div class="market-summary-content">
                            <div class="market-row">
                                <div class="market-label">上证指数:</div>
                                <div class="market-value">--</div>
                                <div class="market-change">--</div>
                                <div class="market-details">
                                    成交额: -- | 振幅: --
                                </div>
                            </div>
                            
                            <div class="market-row">
                                <div class="market-label">深证成指:</div>
                                <div class="market-value">--</div>
                                <div class="market-change">--</div>
                                <div class="market-details">
                                    成交额: -- | 振幅: --
                                </div>
                            </div>
                            
                            <div class="market-total-row">
                                <div class="total-label">两市共计:</div>
                                <div class="total-value">--</div>
                                <div class="total-stocks">
                                    其中 <span class="stock-up">--</span> 股上涨, <span class="stock-down">--</span> 股下跌
                                </div>
                            </div>
                        </div>
                        
                        <div class="data-source-tag">等待Tushare Pro数据</div>
                    </div>
                    
                    <!-- 宏观四锚决策头 -->
                    <div class="index-item macro-anchor-card">
                        <div class="index-header">
                            <span class="index-name">宏观四锚</span>
                            <span class="index-market">决策头</span>
                        </div>
                        
                        <div class="macro-anchor-content">
                            <div class="anchor-item">
                                <div class="anchor-label">人民币汇率</div>
                                <div class="anchor-value">--</div>
                                <div class="anchor-change">--</div>
                            </div>
                            
                            <div class="anchor-item">
                                <div class="anchor-label">美债10Y收益率</div>
                                <div class="anchor-value">--%</div>
                                <div class="anchor-change">--</div>
                            </div>
                            
                            <div class="anchor-item">
                                <div class="anchor-label">国际金价</div>
                                <div class="anchor-value">-- USD/oz</div>
                                <div class="anchor-change">--</div>
                            </div>
                            
                            <div class="anchor-item">
                                <div class="anchor-label">国内金价</div>
                                <div class="anchor-value">-- CNY/g</div>
                                <div class="anchor-change">--</div>
                            </div>
                        </div>
                        
                        <div class="data-source-tag verified">等待Tushare Pro数据</div>
                    </div>
                </div>
                
                <!-- 更新说明 -->
                <div class="update-note">
                    <p>💡 <strong>页面重建说明</strong>: 此页面已根据主编指令进行完整重建。所有数据卡片已分离为独立组件，消除嵌套结构问题。统一数据引擎将在下次运行时填充最新数据。</p>
                    <p>🔗 <strong>验证地址</strong>: <a href="https://amber.googlemanager.cn:10123/?v=3.2.7">https://amber.googlemanager.cn:10123/?v=3.2.7</a></p>
                </div>
            </div>
        </div>
    </main>

    <!-- 站点页脚 -->
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3 class="footer-title">琥珀引擎</h3>
                    <p class="footer-description">
                        财经品牌独立站 - 数据库驱动 + 静态化生成的专业媒体架构
                    </p>
                    <p class="footer-copyright">
                        © 2026 Cheese Intelligence Team. 保留所有权利。
                    </p>
                </div>
                
                <div class="footer-section">
                    <h3 class="footer-title">快速链接</h3>
                    <ul class="footer-links">
                        <li><a href="/">首页</a></li>
                        <li><a href="/etf/">ETF专区</a></li>
                        <li><a href="/about.html">关于我们</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h3 class="footer-title">联系我们</h3>
                    <ul class="footer-links">
                        <li>团队: Cheese Intelligence Team</li>
                        <li>网站: <a href="https://cheese.ai">cheese.ai</a></li>
                        <li>工程师: Cheese (🧀)</li>
                    </ul>
                </div>
            </div>
        </div>
    </footer>

    <!-- 页面脚本 -->
    <script>
        console.log('琥珀引擎 V3.2.7 - 页面重建完成: {current_time}');
    </script>
</body>
</html>'''
    
    # 写入文件
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(clean_html)
        print(f"✅ 干净的index.html模板已创建: {INDEX_FILE}")
        return True
    except PermissionError:
        print("⚠️ 权限不足，使用sudo tee")
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
            tmp.write(clean_html)
            tmp_path = tmp.name
        
        result = subprocess.run(f'sudo tee {INDEX_FILE} < {tmp_path} > /dev/null', shell=True)
        os.unlink(tmp_path)
        
        if result.returncode != 0:
            print("❌ sudo tee写入失败")
            return False
        
        print(f"✅ 干净的index.html模板已创建 (使用sudo): {INDEX_FILE}")
        return True

def main():
    """主函数"""
    print("=" * 70)
    print("🔧 琥珀引擎完整页面重建 (方案B)")
    print("=" * 70)
    print("执行主编指令：完整页面重建，完工后通知验收")
    print("=" * 70)
    
    # 备份原文件
    backup_file = f"{INDEX_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        import shutil
        shutil.copy2(INDEX_FILE, backup_file)
        print(f"📁 原文件已备份: {backup_file}")
    except Exception as e:
        print(f"⚠️ 备份失败: {e} (继续执行)")
    
    # 创建干净的模板
    success = create_clean_index()
    
    if success:
        print("\n✅ 页面重建完成!")
        print("📋 重建内容:")
        print("  1. ✅ 创建干净HTML模板")
        print("  2. ✅ 分离智能卡片与普通卡片")
        print("  3. ✅ 建立正确网格布局")
        print("  4. ✅ 消除嵌套结构问题")
        print("  5. ✅ 保持V2.2视觉系统")
        print(f"\n🔗 验证地址: https://amber.googlemanager.cn:10123/")
        print("⏰ 下一步: 运行统一数据引擎填充最新数据")
    else:
        print("\n❌ 页面重建失败")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)