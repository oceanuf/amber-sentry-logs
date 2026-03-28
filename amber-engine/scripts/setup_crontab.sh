#!/bin/bash
# 配置琥珀引擎自动化重绘crontab定时任务

echo "🚀 配置琥珀引擎自动化重绘定时任务"
echo "=========================================="

# 获取脚本绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_RENDER_SCRIPT="$SCRIPT_DIR/auto_render_main.py"
PYTHON_PATH="$(which python3)"

echo "📁 脚本目录: $SCRIPT_DIR"
echo "🐍 Python路径: $PYTHON_PATH"
echo "📜 主脚本: $AUTO_RENDER_SCRIPT"

# 检查脚本是否存在
if [ ! -f "$AUTO_RENDER_SCRIPT" ]; then
    echo "❌ 错误: 主脚本不存在: $AUTO_RENDER_SCRIPT"
    exit 1
fi

# 创建crontab配置
CRON_CONFIG="# 🎖️ 琥珀引擎自动化重绘定时任务
# 配置时间: $(date '+%Y-%m-%d %H:%M:%S')

# A股市场: 每个交易日 15:10 (北京时间)
10 15 * * 1-5 $PYTHON_PATH $AUTO_RENDER_SCRIPT >> $SCRIPT_DIR/../logs/cron_ah_$(date +\%Y\%m\%d).log 2>&1

# 港股市场: 每个交易日 16:10 (北京时间)
10 16 * * 1-5 $PYTHON_PATH $AUTO_RENDER_SCRIPT >> $SCRIPT_DIR/../logs/cron_hk_$(date +\%Y\%m\%d).log 2>&1

# 美股市场: 次日 06:10 (北京时间)
10 6 * * 2-6 $PYTHON_PATH $AUTO_RENDER_SCRIPT >> $SCRIPT_DIR/../logs/cron_us_$(date +\%Y\%m\%d).log 2>&1

# 周末数据验证: 每周六 10:00
0 10 * * 6 $PYTHON_PATH $SCRIPT_DIR/assert_data_integrity.py >> $SCRIPT_DIR/../logs/cron_weekend_$(date +\%Y\%m\%d).log 2>&1

# 系统健康检查: 每天 08:00
0 8 * * * $PYTHON_PATH $SCRIPT_DIR/check_system_health.py >> $SCRIPT_DIR/../logs/cron_health_$(date +\%Y\%m\%d).log 2>&1"

echo ""
echo "📋 生成的crontab配置:"
echo "=========================================="
echo "$CRON_CONFIG"
echo "=========================================="

# 询问是否安装
read -p "是否安装到当前用户的crontab? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份现有crontab
    CRON_BACKUP="$SCRIPT_DIR/../backups/crontab_backup_$(date +%Y%m%d_%H%M%S).bak"
    mkdir -p "$(dirname "$CRON_BACKUP")"
    crontab -l > "$CRON_BACKUP" 2>/dev/null || true
    echo "💾 现有crontab已备份到: $CRON_BACKUP"
    
    # 安装新配置
    (crontab -l 2>/dev/null; echo "$CRON_CONFIG") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ crontab配置安装成功"
        
        # 显示当前crontab
        echo ""
        echo "📋 当前crontab配置:"
        echo "=========================================="
        crontab -l
        echo "=========================================="
        
        # 创建系统健康检查脚本
        create_health_check_script
        
        echo ""
        echo "🎉 琥珀引擎自动化重绘定时任务配置完成"
        echo "📅 定时任务安排:"
        echo "   A股: 周一至周五 15:10 (北京时间)"
        echo "   港股: 周一至周五 16:10 (北京时间)"
        echo "   美股: 周二至周六 06:10 (北京时间)"
        echo "   周末验证: 周六 10:00"
        echo "   健康检查: 每天 08:00"
        echo ""
        echo "📁 日志目录: $SCRIPT_DIR/../logs/"
        echo "💾 备份目录: $SCRIPT_DIR/../backups/"
    else
        echo "❌ crontab配置安装失败"
        exit 1
    fi
else
    echo "⚠️ 已取消安装"
    echo ""
    echo "💡 手动安装方法:"
    echo "1. 将上面的配置保存到文件"
    echo "2. 运行: crontab < 配置文件"
    echo "3. 验证: crontab -l"
fi

create_health_check_script() {
    # 创建系统健康检查脚本
    HEALTH_CHECK_SCRIPT="$SCRIPT_DIR/check_system_health.py"
    
    cat > "$HEALTH_CHECK_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
琥珀引擎系统健康检查脚本
每天08:00自动运行，检查系统状态
"""

import os
import sys
import subprocess
from datetime import datetime

def check_disk_space():
    """检查磁盘空间"""
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 5:
                used_percent = parts[4].replace('%', '')
                return float(used_percent)
    except:
        pass
    return None

def check_nginx_status():
    """检查Nginx状态"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except:
        return False

def check_script_permissions():
    """检查脚本权限"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = ['auto_render_main.py', 'assert_data_integrity.py', 
               'get_hs300_pro.py', 'valuation_cloud.py']
    
    results = {}
    for script in scripts:
        script_path = os.path.join(script_dir, script)
        if os.path.exists(script_path):
            results[script] = os.access(script_path, os.X_OK)
        else:
            results[script] = False
    
    return results

def generate_health_report():
    """生成健康检查报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 执行检查
    disk_usage = check_disk_space()
    nginx_active = check_nginx_status()
    script_perms = check_script_permissions()
    
    # 生成报告
    report = f"""# 琥珀引擎系统健康检查报告

## 检查时间
{timestamp}

## 系统状态
- 磁盘使用率: {disk_usage if disk_usage else "未知"}%
- Nginx状态: {'✅ 运行中' if nginx_active else '❌ 未运行'}
- Python版本: {sys.version.split()[0]}

## 脚本权限状态
"""
    
    for script, has_perm in script_perms.items():
        status = '✅ 可执行' if has_perm else '❌ 不可执行'
        report += f"- {script}: {status}\n"
    
    # 添加建议
    report += f"""
## 健康建议
"""
    
    if disk_usage and disk_usage > 80:
        report += "- ⚠️ 磁盘使用率超过80%，建议清理日志文件\n"
    
    if not nginx_active:
        report += "- ⚠️ Nginx未运行，网站无法访问\n"
    
    if all(script_perms.values()):
        report += "- ✅ 所有脚本权限正常\n"
    else:
        report += "- ⚠️ 部分脚本权限异常，请检查\n"
    
    report += f"""
## 下次检查
明天 08:00 (北京时间)

---
*琥珀引擎自动化健康监控系统*
"""
    
    return report

def main():
    """主函数"""
    print("🔍 开始琥珀引擎系统健康检查...")
    
    report = generate_health_report()
    print(report)
    
    # 保存报告
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports", "health")
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"health_check_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 健康报告已保存: {report_file}")
    
    # 设置脚本权限
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = ['auto_render_main.py', 'assert_data_integrity.py', 
               'get_hs300_pro.py', 'valuation_cloud.py', 'check_system_health.py']
    
    for script in scripts:
        script_path = os.path.join(script_dir, script)
        if os.path.exists(script_path):
            os.chmod(script_path, 0o755)
    
    print("✅ 脚本权限已设置")

if __name__ == "__main__":
    main()
EOF
    
    # 设置执行权限
    os.chmod(HEALTH_CHECK_SCRIPT, 0o755)
    echo "✅ 系统健康检查脚本已创建: $HEALTH_CHECK_SCRIPT"
}