<?php
/**
 * 琥珀引擎Web中枢
 * 基于[2614-001]档案馆单体仓库同步法典 V3.1
 * 强制使用相对路径引用
 */

header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>琥珀引擎 - 档案馆单体仓库</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        
        .module {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid #e9ecef;
        }
        
        .module:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .module h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .module p {
            color: #666;
            margin-bottom: 20px;
        }
        
        .module ul {
            list-style: none;
            padding-left: 0;
        }
        
        .module li {
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .module li:last-child {
            border-bottom: none;
        }
        
        .module a {
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .module a:hover {
            color: #764ba2;
            text-decoration: underline;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            color: #666;
        }
        
        .code-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-family: 'Courier New', monospace;
            margin-right: 5px;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .content {
                padding: 20px;
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧀 琥珀引擎档案馆</h1>
            <p class="subtitle">基于[2614-001]档案馆单体仓库同步法典 V3.1</p>
            <p class="subtitle">物理对齐 · 逻辑透明 · 绝对安全</p>
        </div>
        
        <div class="content">
            <div class="module">
                <h2>📁 物理拓扑结构</h2>
                <p>严格遵守单体仓库(Monorepo)结构规范：</p>
                <ul>
                    <li><span class="code-badge">/web/</span> Web中枢 (当前页面)</li>
                    <li><span class="code-badge">/vaults/</span> 档案核心 (.md内容文件)</li>
                    <li><span class="code-badge">/docs/reports/</span> 审计留痕 (执行报告)</li>
                    <li><span class="code-badge">/scripts/</span> 自动化工具</li>
                    <li><span class="code-badge">/database/</span> 数据模版 (.json结构定义)</li>
                </ul>
            </div>
            
            <div class="module">
                <h2>🛡️ 安全防线协议</h2>
                <p>同步前强制执行"三不原则"：</p>
                <ul>
                    <li>✅ 不泄露Token (严禁ghp_硬编码)</li>
                    <li>✅ 不泄露绝对路径 (严禁../)</li>
                    <li>✅ 不泄露私密数据 (.gitignore严格过滤)</li>
                </ul>
                <p>审查脚本: <span class="code-badge">scripts/github/sync_clean.sh</span></p>
            </div>
            
            <div class="module">
                <h2>📝 语义化提交标准</h2>
                <p>所有Commit必须具备可追溯性：</p>
                <ul>
                    <li><span class="code-badge">[ARCH]</span> 架构级调整</li>
                    <li><span class="code-badge">[VAULT]</span> 内容更新</li>
                    <li><span class="code-badge">[DOC]</span> 文档归档</li>
                    <li><span class="code-badge">[SEC]</span> 安全加固</li>
                    <li><span class="code-badge">[DATA]</span> 数据结构变更</li>
                </ul>
                <p>格式: <span class="code-badge">[前缀]: 描述 (关联任务号)</span></p>
            </div>
            
            <div class="module">
                <h2>⚙️ 自动化同步流程</h2>
                <p>严禁直接使用原始git push指令：</p>
                <ol style="padding-left: 20px; margin-top: 10px;">
                    <li>确认根目录位置</li>
                    <li>运行安全扫描脚本</li>
                    <li>git add (仅限法典目录)</li>
                    <li>执行同步脚本</li>
                </ol>
                <p style="margin-top: 15px;">
                    <strong>示例命令：</strong><br>
                    <span class="code-badge">./scripts/github/sync_clean.sh "[ARCH]: 目录结构重构 (2614-001)"</span>
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p>📅 法典生效日期: 2026-03-30 (第14周起始)</p>
            <p>📜 法典编号: <strong>2614-001</strong> | 签发人: <strong>首席架构师 Gemini</strong></p>
            <p>🚀 执行者: <strong>工程师 Cheese 🧀</strong> | 更新时间: <?php echo date('Y-m-d H:i:s'); ?></p>
            <p style="margin-top: 10px; font-size: 0.9rem; opacity: 0.7;">
                主编掌舵，架构师谋略，工程师实干！
            </p>
        </div>
    </div>
</body>
</html>