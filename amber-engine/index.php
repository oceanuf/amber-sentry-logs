<?php
/**
 * 🏛️ 琥珀引擎档案馆 - 唯一逻辑入口
 * 基于[2613-199号]V2.0同步法典规范
 * 版本: V1.0.0 (档案馆专用版)
 * 创建时间: 2026-03-28 15:34 GMT+8
 */

// 错误报告设置
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 加载Parsedown解析器
require_once __DIR__ . '/lib/Parsedown.php';

// 档案馆配置
define('ARCHIVE_VERSION', 'V1.0.0');
define('ARCHIVE_BUILD', '2026-03-28');
define('ARCHIVE_AUTHOR', 'Cheese Intelligence Team');

// 安全头
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('X-XSS-Protection: 1; mode=block');

/**
 * 获取Markdown文件内容
 */
function get_markdown_content($file_path) {
    if (!file_exists($file_path)) {
        return "## 📭 文件未找到\n\n请求的文件 `{$file_path}` 不存在于档案馆中。";
    }
    
    $content = file_get_contents($file_path);
    if ($content === false) {
        return "## ❌ 读取失败\n\n无法读取文件 `{$file_path}`。";
    }
    
    return $content;
}

/**
 * 加载JSON数据并生成动态表格
 */
function generate_dynamic_table($ticker) {
    $database_dir = __DIR__ . '/database';
    $json_path = $database_dir . '/' . $ticker . '.json';
    
    if (!file_exists($json_path)) {
        return "<div style='color: #f7768e; font-family: monospace;'>❌ JSON数据文件不存在: {$ticker}.json</div>";
    }
    
    try {
        $json_content = file_get_contents($json_path);
        $data = json_decode($json_content, true);
        
        if (!$data) {
            return "<div style='color: #f7768e; font-family: monospace;'>❌ JSON解析失败</div>";
        }
        
        // 提取最新数据
        $current_price = $data['current_price'] ?? 0;
        $change_pct = $data['change_pct'] ?? '0.00%';
        $nav_history = $data['nav_history'] ?? [];
        $last_update = $data['last_update'] ?? '未知';
        
        // 判断涨跌颜色
        $change_color = '#9ece6a'; // 绿色
        if (strpos($change_pct, '-') === 0) {
            $change_color = '#f7768e'; // 红色
        }
        
        // 生成表格HTML
        $html = '<div style="overflow-x: auto; margin: 20px 0;">';
        $html .= '<table style="width: 100%; border-collapse: collapse; font-family: monospace; background: #1a1b26; color: #c0caf5; border-radius: 8px; overflow: hidden;">';
        
        // 表头
        $html .= '<thead>';
        $html .= '<tr style="background: #24283b;">';
        $html .= '<th style="padding: 12px 16px; text-align: left; border-bottom: 2px solid #414868;">📊 实时数据</th>';
        $html .= '<th style="padding: 12px 16px; text-align: right; border-bottom: 2px solid #414868;">数值</th>';
        $html .= '</tr>';
        $html .= '</thead>';
        
        // 主体
        $html .= '<tbody>';
        
        // 最新价格
        $html .= '<tr style="border-bottom: 1px solid #414868;">';
        $html .= '<td style="padding: 12px 16px;">最新净值</td>';
        $html .= '<td style="padding: 12px 16px; text-align: right; font-weight: bold;">' . number_format($current_price, 3) . '</td>';
        $html .= '</tr>';
        
        // 涨跌幅
        $html .= '<tr style="border-bottom: 1px solid #414868;">';
        $html .= '<td style="padding: 12px 16px;">日涨跌幅</td>';
        $html .= '<td style="padding: 12px 16px; text-align: right; font-weight: bold; color: ' . $change_color . ';">' . $change_pct . '</td>';
        $html .= '</tr>';
        
        // 更新时间
        $html .= '<tr style="border-bottom: 1px solid #414868;">';
        $html .= '<td style="padding: 12px 16px;">数据更新时间</td>';
        $html .= '<td style="padding: 12px 16px; text-align: right; font-size: 0.9em;">' . $last_update . '</td>';
        $html .= '</tr>';
        
        // 净值历史标题
        $html .= '<tr style="background: #24283b;">';
        $html .= '<td colspan="2" style="padding: 12px 16px; text-align: center; font-weight: bold;">📈 净值走势 (最近30日)</td>';
        $html .= '</tr>';
        
        // 净值历史数据
        $recent_history = array_slice($nav_history, -10); // 显示最近10条
        foreach ($recent_history as $item) {
            $date = $item['date'] ?? '未知';
            $price = $item['price'] ?? 0;
            $change = $item['change'] ?? '0.00%';
            
            // 判断涨跌颜色
            $row_change_color = '#9ece6a';
            if (strpos($change, '-') === 0) {
                $row_change_color = '#f7768e';
            }
            
            $html .= '<tr style="border-bottom: 1px solid #414868;">';
            $html .= '<td style="padding: 10px 16px; font-size: 0.9em;">' . $date . '</td>';
            $html .= '<td style="padding: 10px 16px; text-align: right;">';
            $html .= '<span style="margin-right: 20px;">' . number_format($price, 3) . '</span>';
            $html .= '<span style="color: ' . $row_change_color . ';">' . $change . '</span>';
            $html .= '</td>';
            $html .= '</tr>';
        }
        
        $html .= '</tbody>';
        $html .= '</table>';
        $html .= '</div>';
        
        // 数据源说明
        $html .= '<div style="font-family: monospace; font-size: 0.8em; color: #565f89; margin-top: 10px; text-align: center;">';
        $html .= '数据源: TUSHARE | 更新频率: 每小时 | 渲染方式: PHP动态注入';
        $html .= '</div>';
        
        return $html;
        
    } catch (Exception $e) {
        return "<div style='color: #f7768e; font-family: monospace;'>❌ 生成表格失败: " . htmlspecialchars($e->getMessage()) . "</div>";
    }
}

/**
 * 处理动态内容注入
 */
function inject_dynamic_content($markdown_content) {
    // 检查是否有[[VALUATION_ZONE]]锚点
    if (strpos($markdown_content, '[[VALUATION_ZONE]]') !== false) {
        // 从YAML头部提取TICKER
        if (preg_match('/TICKER:\s*"([^"]+)"/', $markdown_content, $matches)) {
            $ticker = $matches[1];
            $dynamic_table = generate_dynamic_table($ticker);
            $markdown_content = str_replace('[[VALUATION_ZONE]]', $dynamic_table, $markdown_content);
        } else {
            $error_msg = "<div style='color: #f7768e; font-family: monospace;'>❌ 无法从YAML头部提取TICKER</div>";
            $markdown_content = str_replace('[[VALUATION_ZONE]]', $error_msg, $markdown_content);
        }
    }
    
    return $markdown_content;
}

/**
 * 渲染Markdown为HTML
 */
function render_markdown($markdown) {
    // 先注入动态内容
    $markdown = inject_dynamic_content($markdown);
    
    $parsedown = new Parsedown();
    $parsedown->setSafeMode(true);
    $parsedown->setMarkupEscaped(true);
    
    return $parsedown->text($markdown);
}

/**
 * 生成页面HTML
 */
function generate_page($title, $content_html) {
    $html = <<<HTML
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏛️ {$title} - 琥珀引擎档案馆</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        .archive-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .archive-title {
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .archive-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .archive-version {
            font-size: 0.875rem;
            opacity: 0.7;
            margin-top: 0.5rem;
        }
        
        .archive-nav {
            background: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: center;
            gap: 2rem;
        }
        
        .nav-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .nav-link:hover {
            background: #f0f4ff;
            color: #4c51bf;
        }
        
        .archive-content {
            max-width: 900px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        .content-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            margin-bottom: 2rem;
        }
        
        .content-title {
            font-size: 1.75rem;
            color: #2d3748;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .markdown-content {
            font-size: 1rem;
            color: #4a5568;
        }
        
        .markdown-content h1,
        .markdown-content h2,
        .markdown-content h3,
        .markdown-content h4 {
            color: #2d3748;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .markdown-content p {
            margin-bottom: 1rem;
        }
        
        .markdown-content code {
            background: #f7fafc;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.875em;
        }
        
        .markdown-content pre {
            background: #1a202c;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .markdown-content pre code {
            background: transparent;
            padding: 0;
            color: inherit;
        }
        
        .archive-footer {
            text-align: center;
            padding: 2rem;
            color: #718096;
            font-size: 0.875rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }
        
        @media (max-width: 768px) {
            .archive-nav {
                flex-direction: column;
                gap: 0.5rem;
                align-items: center;
            }
            
            .archive-content {
                padding: 0 0.5rem;
            }
            
            .content-card {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <header class="archive-header">
        <h1 class="archive-title">🏛️ 琥珀引擎档案馆</h1>
        <p class="archive-subtitle">基于[2613-199号]V2.0同步法典规范</p>
        <p class="archive-version">版本: ARCHIVE_V1_MANIFEST.md V1.0.0 | 构建: 2026-03-28</p>
    </header>
    
    <nav class="archive-nav">
        <a href="?page=manifest" class="nav-link">📜 架构法典</a>
        <a href="?page=formulas" class="nav-link">🧮 核心算法库</a>
        <a href="?page=assets" class="nav-link">🔍 标的透视镜</a>
        <a href="?page=research" class="nav-link">📚 战略研究室</a>
        <a href="?page=strategy" class="nav-link">⚡ 生存线看板</a>
    </nav>
    
    <main class="archive-content">
        <div class="content-card">
            <h2 class="content-title">{$title}</h2>
            <div class="markdown-content">
                {$content_html}
            </div>
        </div>
    </main>
    
    <footer class="archive-footer">
        <p>🧀 Cheese Intelligence Team | 工程师: Cheese | 架构师: Gemini | 主编: Haiyang</p>
        <p>© 2026 琥珀引擎档案馆 - 所有内容基于[2613-001号]命令发布规范</p>
    </footer>
</body>
</html>
HTML;

    return $html;
}

// 主逻辑
try {
    // 获取请求的页面
    $page = $_GET['page'] ?? 'manifest';
    
    // 检查是否请求特定ETF文件
    $etf_file = $_GET['etf'] ?? '';
    if ($etf_file) {
        // 处理ETF文件请求
        $file_path = __DIR__ . '/vaults/Assets/' . $etf_file . '.md';
        if (!file_exists($file_path)) {
            $file_path = __DIR__ . '/vaults/Assets/' . $etf_file . '_Gold.md';
        }
        
        // 从文件名提取标题
        $page_title = '标的透视镜';
        if (preg_match('/^(\d+)/', $etf_file, $matches)) {
            $page_title = $matches[1] . ' - 标的透视镜';
        }
    } else {
        // 根据页面参数确定文件路径
        switch ($page) {
            case 'manifest':
                $file_path = __DIR__ . '/ARCHIVE_V1_MANIFEST.md';
                $page_title = '架构法典';
                break;
                
            case 'formulas':
                $file_path = __DIR__ . '/vaults/Formulas/README.md';
                $page_title = '核心算法库';
                break;
                
            case 'assets':
                $file_path = __DIR__ . '/vaults/Assets/README.md';
                $page_title = '标的透视镜';
                break;
                
            case 'research':
                $file_path = __DIR__ . '/vaults/Research/README.md';
                $page_title = '战略研究室';
                break;
                
            case 'strategy':
                $file_path = __DIR__ . '/vaults/Strategy/README.md';
                $page_title = '生存线看板';
                break;
                
            default:
                $file_path = __DIR__ . '/ARCHIVE_V1_MANIFEST.md';
                $page_title = '架构法典';
        }
    }
    
    // 获取并渲染Markdown内容
    $markdown_content = get_markdown_content($file_path);
    $html_content = render_markdown($markdown_content);
    
    // 输出页面
    echo generate_page($page_title, $html_content);
    
} catch (Exception $e) {
    // 错误处理
    $error_html = "<h3>❌ 系统错误</h3><p>错误信息: " . htmlspecialchars($e->getMessage()) . "</p>";
    echo generate_page('系统错误', $error_html);
}
?>