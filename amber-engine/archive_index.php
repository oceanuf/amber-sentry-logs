<?php
/**
 * [2613-201号-B] 档案馆效能增强令 - PHP母模板自动索引 (Auto-Navigator)
 * 版本: V1.0.0
 * 作者: 工程师 Cheese
 * 创建时间: 2026-03-28 16:25 GMT+8
 * 
 * 功能: 自动遍历vaults/子目录，读取MD头部的YAML ID和STATUS，生成侧边栏导航菜单
 * 意义: 主编未来新增一个公式MD，页面会自动出现对应链接，无需再改一行代码
 */

// 错误报告
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 配置
$VAULTS_DIR = '/home/luckyelite/.openclaw/workspace/amber-engine/vaults';
$ARCHIVE_URL = 'https://gemini.googlemanager.cn:10168/archive_index.php';
$PARSEDOWN_PATH = __DIR__ . '/parsedown/Parsedown.php';

// 引入Parsedown
require_once $PARSEDOWN_PATH;

/**
 * 扫描vaults目录结构
 */
function scan_vaults_structure($base_dir) {
    $structure = [];
    
    // 扫描子目录
    $subdirs = ['manifest', 'data', 'reports', 'scripts', 'logs'];
    
    foreach ($subdirs as $subdir) {
        $dir_path = $base_dir . '/' . $subdir;
        if (!is_dir($dir_path)) {
            continue;
        }
        
        $structure[$subdir] = [
            'name' => ucfirst($subdir),
            'path' => $dir_path,
            'files' => []
        ];
        
        // 扫描文件
        $files = scandir($dir_path);
        foreach ($files as $file) {
            if ($file === '.' || $file === '..') {
                continue;
            }
            
            $file_path = $dir_path . '/' . $file;
            $file_info = [
                'name' => $file,
                'path' => $file_path,
                'type' => pathinfo($file, PATHINFO_EXTENSION),
                'size' => filesize($file_path),
                'modified' => date('Y-m-d H:i:s', filemtime($file_path))
            ];
            
            // 如果是Markdown文件，解析YAML头部
            if (strtolower(pathinfo($file, PATHINFO_EXTENSION)) === 'md') {
                $file_info['metadata'] = parse_markdown_yaml($file_path);
            }
            
            $structure[$subdir]['files'][] = $file_info;
        }
    }
    
    return $structure;
}

/**
 * 解析Markdown文件的YAML头部
 */
function parse_markdown_yaml($file_path) {
    $metadata = [
        'id' => '',
        'status' => '',
        'title' => '',
        'author' => '',
        'date' => '',
        'version' => ''
    ];
    
    $content = file_get_contents($file_path);
    if (!$content) {
        return $metadata;
    }
    
    // 检查YAML头部 (以---开始和结束)
    if (preg_match('/^---\s*(.*?)\s*---/s', $content, $matches)) {
        $yaml_content = $matches[1];
        $lines = explode("\n", $yaml_content);
        
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line)) {
                continue;
            }
            
            if (preg_match('/^([a-zA-Z_]+):\s*(.+)$/', $line, $key_match)) {
                $key = strtolower($key_match[1]);
                $value = trim($key_match[2]);
                
                if (isset($metadata[$key])) {
                    $metadata[$key] = $value;
                }
            }
        }
    }
    
    // 如果没有YAML头部，使用文件名作为标题
    if (empty($metadata['title'])) {
        $metadata['title'] = pathinfo($file_path, PATHINFO_FILENAME);
    }
    
    return $metadata;
}

/**
 * 生成侧边栏HTML
 */
function generate_sidebar($structure) {
    $html = '<div class="sidebar">';
    $html .= '<div class="sidebar-header">';
    $html .= '<h2>📚 琥珀引擎档案馆</h2>';
    $html .= '<p class="sidebar-subtitle">自动索引导航系统</p>';
    $html .= '</div>';
    
    $html .= '<div class="sidebar-section">';
    $html .= '<h3>🏛️ 档案馆结构</h3>';
    
    foreach ($structure as $section_name => $section) {
        $html .= '<div class="sidebar-category">';
        $html .= '<h4>' . $section['name'] . ' (' . count($section['files']) . ')</h4>';
        $html .= '<ul>';
        
        foreach ($section['files'] as $file) {
            $file_url = generate_file_url($file);
            $file_title = $file['name'];
            
            // 如果有metadata，使用metadata中的标题
            if (isset($file['metadata']['title']) && !empty($file['metadata']['title'])) {
                $file_title = $file['metadata']['title'];
            }
            
            // 添加状态标签
            $status_badge = '';
            if (isset($file['metadata']['status']) && !empty($file['metadata']['status'])) {
                $status_class = strtolower($file['metadata']['status']);
                $status_badge = '<span class="status-badge ' . $status_class . '">' . $file['metadata']['status'] . '</span>';
            }
            
            // 添加ID标签
            $id_badge = '';
            if (isset($file['metadata']['id']) && !empty($file['metadata']['id'])) {
                $id_badge = '<span class="id-badge">#' . $file['metadata']['id'] . '</span>';
            }
            
            $html .= '<li>';
            $html .= '<a href="' . $file_url . '" title="' . htmlspecialchars($file['name']) . '">';
            $html .= get_file_icon($file['type']) . ' ' . htmlspecialchars($file_title);
            $html .= '</a>';
            $html .= $status_badge . $id_badge;
            $html .= '<br><small>' . format_file_size($file['size']) . ' • ' . $file['modified'] . '</small>';
            $html .= '</li>';
        }
        
        $html .= '</ul>';
        $html .= '</div>';
    }
    
    $html .= '</div>';
    
    // 系统信息
    $html .= '<div class="sidebar-footer">';
    $html .= '<h3>🔄 系统状态</h3>';
    $html .= '<ul>';
    $html .= '<li>📅 更新时间: ' . date('Y-m-d H:i:s') . '</li>';
    $html .= '<li>📊 文件总数: ' . count_total_files($structure) . '</li>';
    $html .= '<li>📁 目录数量: ' . count($structure) . '</li>';
    $html .= '<li>🔍 自动索引: ✅ 已启用</li>';
    $html .= '</ul>';
    $html .= '</div>';
    
    $html .= '</div>';
    
    return $html;
}

/**
 * 生成文件URL
 */
function generate_file_url($file) {
    global $ARCHIVE_URL;
    
    $file_name = $file['name'];
    $file_type = $file['type'];
    
    // 如果是Markdown文件，使用md_viewer.html
    if (strtolower($file_type) === 'md') {
        return 'md_viewer.html?file=' . urlencode($file_name);
    }
    
    // 其他文件直接链接
    return $file_name;
}

/**
 * 获取文件图标
 */
function get_file_icon($file_type) {
    $icons = [
        'md' => '📝',
        'json' => '📊',
        'py' => '🐍',
        'sh' => '📟',
        'php' => '🐘',
        'html' => '🌐',
        'css' => '🎨',
        'js' => '⚡',
        'txt' => '📄',
        'log' => '📋',
        'pdf' => '📕',
        'jpg' => '🖼️',
        'png' => '🖼️',
        'gif' => '🖼️',
        'csv' => '📈',
        'xlsx' => '📊',
        'zip' => '📦',
        'default' => '📎'
    ];
    
    $type_lower = strtolower($file_type);
    return isset($icons[$type_lower]) ? $icons[$type_lower] : $icons['default'];
}

/**
 * 格式化文件大小
 */
function format_file_size($bytes) {
    if ($bytes >= 1073741824) {
        return number_format($bytes / 1073741824, 2) . ' GB';
    } elseif ($bytes >= 1048576) {
        return number_format($bytes / 1048576, 2) . ' MB';
    } elseif ($bytes >= 1024) {
        return number_format($bytes / 1024, 2) . ' KB';
    } else {
        return $bytes . ' B';
    }
}

/**
 * 计算文件总数
 */
function count_total_files($structure) {
    $total = 0;
    foreach ($structure as $section) {
        $total += count($section['files']);
    }
    return $total;
}

/**
 * 生成主内容区域
 */
function generate_main_content($structure) {
    $html = '<div class="main-content">';
    $html .= '<header class="main-header">';
    $html .= '<h1>🏛️ 琥珀引擎档案馆 V1.0</h1>';
    $html .= '<p class="subtitle">基于[2613-201号-B]档案馆效能增强令构建的自动索引系统</p>';
    $html .= '</header>';
    
    $html .= '<div class="stats-grid">';
    $html .= '<div class="stat-card">';
    $html .= '<h3>📊 数据统计</h3>';
    $html .= '<p>文件总数: ' . count_total_files($structure) . '</p>';
    $html .= '<p>目录数量: ' . count($structure) . '</p>';
    $html .= '<p>最后更新: ' . date('Y-m-d H:i:s') . '</p>';
    $html .= '</div>';
    
    $html .= '<div class="stat-card">';
    $html .= '<h3>🚀 系统特性</h3>';
    $html .= '<p>✅ 自动索引导航</p>';
    $html .= '<p>✅ YAML元数据解析</p>';
    $html .= '<p>✅ 实时文件扫描</p>';
    $html .= '<p>✅ 零配置部署</p>';
    $html .= '</div>';
    
    $html .= '<div class="stat-card">';
    $html .= '<h3>📈 数据装填器</h3>';
    $html .= '<p>状态: <span class="status-active">✅ 运行中</span></p>';
    $html .= '<p>频率: 每小时刷新</p>';
    $html .= '<p>标的: 518880等5支ETF</p>';
    $html .= '<p><a href="data_refresher.py" class="btn">查看脚本</a></p>';
    $html .= '</div>';
    
    $html .= '<div class="stat-card">';
    $html .= '<h3>🔗 快速链接</h3>';
    $html .= '<p><a href="md_viewer.html?file=PORTFOLIO.md">📊 演武场看板</a></p>';
    $html .= '<p><a href="md_viewer.html?file=RADAR.md">🎯 机会雷达</a></p>';
    $html .= '<p><a href="portfolio_dashboard.html">📈 投资组合</a></p>';
    $html .= '<p><a href="index.html">🏠 返回主页</a></p>';
    $html .= '</div>';
    $html .= '</div>';
    
    // 显示每个目录的详细内容
    foreach ($structure as $section_name => $section) {
        $html .= '<section class="content-section">';
        $html .= '<h2>' . get_file_icon('folder') . ' ' . $section['name'] . ' 目录</h2>';
        $html .= '<p>包含 ' . count($section['files']) . ' 个文件</p>';
        
        if (count($section['files']) > 0) {
            $html .= '<div class="file-table">';
            $html .= '<table>';
            $html .= '<thead>';
            $html .= '<tr>';
            $html .= '<th>文件</th>';
            $html .= '<th>类型</th>';
            $html .= '<th>大小</th>';
            $html .= '<th>修改时间</th>';
            $html .= '<th>状态/ID</th>';
            $html .= '<th>操作</th>';
            $html .= '</tr>';
            $html .= '</thead>';
            $html .= '<tbody>';
            
            foreach ($section['files'] as $file) {
                $file_url = generate_file_url($file);
                
                $html .= '<tr>';
                $html .= '<td>' . get_file_icon($file['type']) . ' ' . htmlspecialchars($file['name']) . '</td>';
                $html .= '<td><span class="file-type">' . strtoupper($file['type']) . '</span></td>';
                $html .= '<td>' . format_file_size($file['size']) . '</td>';
                $html .= '<td>' . $file['modified'] . '</td>';
                $html .= '<td>';
                
                if (isset($file['metadata'])) {
                    if (!empty($file['metadata']['status'])) {
                        $html .= '<span class="status-label">' . $file['metadata']['status'] . '</span>';
                    }
                    if (!empty($file['metadata']['id'])) {
                        $html .= '<span class="id-label">#' . $file['metadata']['id'] . '</span>';
                    }
                }
                
                $html .= '</td>';
                $html .= '<td>';
                $html .= '<a href="' . $file_url . '" class="btn-small">查看</a>';
                $html .= '</td>';
                $html .= '</tr>';
            }
            
            $html .= '</tbody>';
            $html .= '</table>';
            $html .= '</div>';
        } else {
            $html .= '<p class="empty-message">该目录暂无文件</p>';
        }
        
        $html .= '</section>';
    }
    
    $html .= '<footer class="main-footer">';
    $html .= '<p>📅 系统生成时间: ' . date('Y-m-d H:i:s') . ' | 🧀 工程师: Cheese | 📋 指令: [2613-201号-B]</p>';
    $html .= '<p>💡 提示: 在Markdown文件头部添加YAML元数据，系统会自动识别并生成导航</p>';
    $html .= '</footer>';
    
    $html .= '</div>';
    
    return $html;
}

// 主程序
try {
    // 扫描目录结构
    $structure = scan_vaults_structure($VAULTS_DIR);
    
    // 生成HTML
    $sidebar_html = generate_sidebar($structure);
    $main_content_html = generate_main_content($structure);
    
} catch (Exception $e) {
    $error_message = '档案馆扫描失败: ' . $e->getMessage();
    $sidebar_html = '<div class="error">' . $error_message . '</div>';
    $main_content_html = '<div class="error">' . $error_message . '</div>';
}

?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏛️ 琥珀引擎档案馆 - 自动索引系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 50px rgba(0,0,0,0.1);
        }
        
        .sidebar {
            width: 320px;
            background: #2c3e50;
            color: white;
            padding: 20px;
            overflow-y: auto;
            position: sticky;
            top: 0;
            height: 100vh;
        }
        
        .sidebar-header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .sidebar-header h2 {
            font-size: 24px;
            margin-bottom: 5px;
            color: #3498db;
        }
        
        .sidebar-subtitle {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .sidebar-section {
            margin-bottom: 30px;
        }
        
        .sidebar-section h3 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #