#!/usr/bin/env python3
"""
创建带密码保护的主编私人作战室
访问密码: CheeseAI
"""

import os
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DASHBOARD_DIR = os.path.join(OUTPUT_DIR, "my-wealth")

# 访问密码 (主编指定)
ACCESS_PASSWORD = "CheeseAI"
PASSWORD_HASH = hashlib.sha256(ACCESS_PASSWORD.encode()).hexdigest()

def create_secure_dashboard():
    """创建带密码保护的私人作战室"""
    print("创建带密码保护的私人作战室...")
    
    # 创建目录
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    # 1. 创建登录页面
    create_login_page()
    
    # 2. 创建主仪表板页面
    create_main_dashboard()
    
    # 3. 创建JavaScript验证脚本
    create_auth_script()
    
    print(f"✅ 私人作战室创建完成，访问密码: {ACCESS_PASSWORD}")
    print(f"🔗 访问地址: https://finance.cheese.ai/my-wealth/")

def create_login_page():
    """创建登录页面"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主编私人作战室 - 登录</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
        .login-container {{
            max-width: 400px;
            margin: 5rem auto;
            padding: 2rem;
            background: white;
            border-radius: 1rem;
            box-shadow: var(--shadow-xl);
        }}
        
        .login-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .login-logo {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .password-input {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #ddd;
            border-radius: 0.5rem;
            font-size: 1rem;
            margin-bottom: 1rem;
            transition: border-color 0.3s;
        }}
        
        .password-input:focus {{
            border-color: #0d47a1;
            outline: none;
        }}
        
        .login-button {{
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #0d47a1 0%, #1a237e 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.3s;
        }}
        
        .login-button:hover {{
            opacity: 0.9;
        }}
        
        .error-message {{
            color: #f44336;
            text-align: center;
            margin-top: 1rem;
            display: none;
        }}
        
        .password-hint {{
            font-size: 0.875rem;
            color: #666;
            text-align: center;
            margin-top: 1rem;
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="login-logo">🔐</div>
            <h1>主编私人作战室</h1>
            <p>50.4万持仓专项雷达</p>
        </div>
        
        <form id="login-form">
            <input type="password" 
                   class="password-input" 
                   id="password" 
                   placeholder="请输入访问密码" 
                   required
                   autocomplete="current-password">
            
            <button type="submit" class="login-button">进入作战室</button>
            
            <div class="error-message" id="error-message">
                密码错误，请重新输入
            </div>
            
            <div class="password-hint">
                提示: 密码为团队名称 + AI
            </div>
        </form>
        
        <div class="text-center mt-4">
            <a href="/" class="source-tag">返回首页</a>
        </div>
    </div>
    
    <script>
        // 密码验证逻辑
        const PASSWORD_HASH = "{PASSWORD_HASH}";
        
        document.getElementById('login-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const errorElement = document.getElementById('error-message');
            
            // 计算输入密码的哈希值
            async function sha256(message) {{
                const msgBuffer = new TextEncoder().encode(message);
                const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
                const hashArray = Array.from(new Uint8Array(hashBuffer));
                const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                return hashHex;
            }}
            
            sha256(password).then(hash => {{
                if (hash === PASSWORD_HASH) {{
                    // 密码正确，设置访问令牌并跳转
                    const token = btoa(Date.now() + ':' + hash);
                    localStorage.setItem('wealth_dashboard_token', token);
                    localStorage.setItem('wealth_dashboard_expiry', Date.now() + 3600000); // 1小时有效期
                    window.location.href = 'dashboard.html';
                }} else {{
                    // 密码错误
                    errorElement.style.display = 'block';
                    document.getElementById('password').value = '';
                    document.getElementById('password').focus();
                    
                    // 3秒后隐藏错误信息
                    setTimeout(() => {{
                        errorElement.style.display = 'none';
                    }}, 3000);
                }}
            }});
        }});
        
        // 检查是否已有有效令牌
        window.addEventListener('load', function() {{
            const token = localStorage.getItem('wealth_dashboard_token');
            const expiry = localStorage.getItem('wealth_dashboard_expiry');
            
            if (token && expiry && Date.now() < parseInt(expiry)) {{
                // 有有效令牌，直接跳转
                window.location.href = 'dashboard.html';
            }}
        }});
        
        // 回车键提交
        document.getElementById('password').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                document.getElementById('login-form').dispatchEvent(new Event('submit'));
            }}
        }});
    </script>
</body>
</html>'''
    
    login_path = os.path.join(DASHBOARD_DIR, "index.html")
    with open(login_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✅ 登录页面创建完成: {login_path}")

def create_main_dashboard():
    """创建主仪表板页面"""
    # 主编持仓数据（根据反馈调整）
    portfolio = {
        "total_amount": 504000,
        "etf_funds": [  # ETF类型基金（部分持仓）
            {"code": "205856", "name": "电网设备", "amount": 75000, "daily_change": 0.85},
            {"code": "000051", "name": "沪深300", "amount": 70000, "daily_change": 0.42},
            {"code": "008142", "name": "黄金", "amount": 52000, "daily_change": 0.28},
            {"code": "019702", "name": "科创成长", "amount": 52000, "daily_change": 1.25},
            {"code": "015061", "name": "300增强", "amount": 30000, "daily_change": 0.65},
            {"code": "002251", "name": "军工安全", "amount": 30000, "daily_change": 0.92},
        ],
        "other_funds": [  # 其他类型基金（模拟数据）
            {"type": "混合型", "amount": 120000, "daily_change": 0.38},
            {"type": "债券型", "amount": 80000, "daily_change": 0.12},
            {"type": "货币型", "amount": 50000, "daily_change": 0.05},
            {"type": "QDII", "amount": 45000, "daily_change": 0.65},
        ]
    }
    
    # 计算统计数据
    etf_total = sum(fund["amount"] for fund in portfolio["etf_funds"])
    other_total = sum(fund["amount"] for fund in portfolio["other_funds"])
    
    total_pnl = 0
    contributions = []
    
    # 计算ETF盈亏
    for fund in portfolio["etf_funds"]:
        daily_pnl = fund["amount"] * (fund["daily_change"] / 100)
        total_pnl += daily_pnl
        contributions.append({
            "name": fund["name"],
            "type": "ETF",
            "daily_pnl": daily_pnl,
            "daily_change": fund["daily_change"]
        })
    
    # 计算其他基金盈亏
    for fund in portfolio["other_funds"]:
        daily_pnl = fund["amount"] * (fund["daily_change"] / 100)
        total_pnl += daily_pnl
        contributions.append({
            "name": fund["type"],
            "type": fund["type"],
            "daily_pnl": daily_pnl,
            "daily_change": fund["daily_change"]
        })
    
    # 按贡献度排序
    contributions.sort(key=lambda x: abs(x["daily_pnl"]), reverse=True)
    total_change = (total_pnl / portfolio["total_amount"]) * 100
    
    # 生成HTML
    html = generate_dashboard_html(portfolio, contributions, total_pnl, total_change, etf_total, other_total)
    
    dashboard_path = os.path.join(DASHBOARD_DIR, "dashboard.html")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✅ 主仪表板创建完成: {dashboard_path}")

def generate_dashboard_html(portfolio, contributions, total_pnl, total_change, etf_total, other_total):
    """生成仪表板HTML"""
    
    # 生成ETF持仓卡片
    etf_cards = ""
    for fund in portfolio["etf_funds"]:
        daily_pnl = fund["amount"] * (fund["daily_change"] / 100)
        pnl_class = "price-up" if daily_pnl > 0 else "price-down"
        pnl_sign = "+" if daily_pnl > 0 else ""
        
        etf_cards += f'''
        <div class="finance-card">
            <div class="card-header">
                <h4>{fund["name"]}</h4>
                <span class="source-tag">ETF</span>
            </div>
            <div class="card-content">
                <p>持仓: {fund["amount"]/10000:.1f}万</p>
                <p>涨跌: <span class="{pnl_class}">{fund["daily_change"]:+.2f}%</span></p>
                <p>盈亏: <span class="{pnl_class}">{pnl_sign}{daily_pnl:.1f}元</span></p>
            </div>
        </div>
        '''
    
    # 生成其他基金卡片
    other_cards = ""
    for fund in portfolio["other_funds"]:
        daily_pnl = fund["amount"] * (fund["daily_change"] / 100)
        pnl_class = "price-up" if daily_pnl > 0 else "price-down"
        pnl_sign = "+" if daily_pnl > 0 else ""
        
        other_cards += f'''
        <div class="finance-card">
            <div class="card-header">
                <h4>{fund["type"]}</h4>
                <span class="source-tag">{fund["type"][:2]}</span>
            </div>
            <div class="card-content">
                <p>持仓: {fund["amount"]/10000:.1f}万</p>
                <p>涨跌: <span class="{pnl_class}">{fund["daily_change"]:+.2f}%</span></p>
                <p>盈亏: <span class="{pnl_class}">{pnl_sign}{daily_pnl:.1f}元</span></p>
            </div>
        </div>
        '''
    
    # 生成盈亏贡献榜
    contributions_html = ""
    for i, contrib in enumerate(contributions[:5], 1):  # 显示前5名
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅" if i == 4 else "🎖️"
        pnl_class = "price-up" if contrib["daily_pnl"] > 0 else "price-down"
        pnl_sign = "+" if contrib["daily_pnl"] > 0 else ""
        
        contributions_html += f'''
        <div class="metric-item">
            <div class="metric-label">{medal} {contrib["name"]}</div>
            <div class="metric-value {pnl_class}">{pnl_sign}{contrib["daily_pnl"]:.1f}元</div>
            <div class="metric-sub">{contrib["daily_change"]:+.2f}%</div>
        </div>
        '''
    
    # 8%基准线计算
    daily_8_percent = 0.021
    vs_target = "✅ 超越" if total_change > daily_8_percent else "⚠️ 未达"
    target_class = "price-up" if total_change > daily_8_percent else "price-down"
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主编私人作战室 - 50.4万持仓雷达</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <script src="auth.js"></script>
    <style>
        .wealth-header {{
            background: linear-gradient(135deg, #0d47a1 0%, #1a237e 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-radius: 0 0 1rem 1rem;
        }}
        
        .wealth-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .portfolio-breakdown {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        .logout-button {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: background 0.3s;
        }}
        
        .logout-button:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        @media (max-width: 768px) {{
            .logout-button {{
                position: relative;
                top: 0;
                right: 0;
                margin-bottom: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 验证脚本 -->
    <script>
        // 检查访问权限
        if (!checkAuth()) {{
            window.location.href = 'index.html';
        }}
    </script>
    
    <!-- 作战室头部 -->
    <header class="wealth-header">
        <div class="container">
            <button class="logout-button" onclick="logout()">退出登录</button>
            <h1>主编私人作战室</h1>
            <p>50.4万持仓专项雷达 | 实时监控与智能分析</p>
            <div class="mt-4">
                <a href="/" class="source-tag">返回首页</a>
                <span class="ml-3 text-sm">最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")} (北京时间)</span>
            </div>
        </div>
    </header>
    
    <main class="main-content">
        <div class="container">
            <!-- 总览统计 -->
            <div class="finance-card">
                <h2 class="section-title">📈 持仓总览</h2>
                <div class="amber-metrics-card">
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-label">总持仓</div>
                            <div class="metric-value">{portfolio["total_amount"]/10000:.1f}万</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">今日盈亏</div>
                            <div class="metric-value {'price-up' if total_pnl > 0 else 'price-down'}">
                                {'+' if total_pnl > 0 else ''}{total_pnl:.1f}元
                            </div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">涨跌幅</div>
                            <div class="metric-value {'price-up' if total_change > 0 else 'price-down'}