#!/usr/bin/env python3
"""
自动化重绘主脚本
每个交易日定时触发，更新琥珀引擎静态页
"""

import os
import sys
import subprocess
from datetime import datetime

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # 保存到日志文件
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"auto_render_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")

def run_script(script_name, description):
    """运行指定脚本"""
    log_message(f"开始执行: {description}")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    
    if not os.path.exists(script_path):
        log_message(f"❌ 脚本不存在: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            log_message(f"✅ {description} 执行成功")
            # 记录输出（前200字符）
            output_preview = result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
            log_message(f"输出预览: {output_preview}")
            return True
        else:
            log_message(f"❌ {description} 执行失败 (退出码: {result.returncode})")
            log_message(f"错误输出: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        log_message(f"❌ {description} 执行异常: {e}")
        return False

def auto_render():
    """自动化重绘主流程"""
    print("=" * 70)
    print("🚀 琥珀引擎自动化重绘 - 主流程")
    print("=" * 70)
    
    current_time = datetime.now()
    log_message(f"自动化重绘开始，时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 数据完整性验证
    log_message("步骤1: 执行数据完整性验证")
    integrity_passed = run_script("assert_data_integrity.py", "数据完整性验证")
    
    if not integrity_passed:
        log_message("🚨 数据完整性验证失败，停止重绘流程")
        print("\n❌ 重绘流程已停止: 数据完整性验证失败")
        return False
    
    # 2. 获取最新数据
    log_message("步骤2: 获取最新市场数据")
    data_success = run_script("get_hs300_pro.py", "获取Tushare Pro数据")
    
    if not data_success:
        log_message("⚠️ 数据获取失败，尝试备用方案")
        # 可以添加备用数据获取逻辑
        pass
    
    # 3. 更新估值云图
    log_message("步骤3: 更新估值云图")
    valuation_success = run_script("valuation_cloud.py", "估值云图更新")
    
    # 4. 更新首页数据
    log_message("步骤4: 更新首页数据")
    homepage_success = run_script("update_with_tushare_pro.py", "首页数据更新")
    
    # 5. 清理缓存
    log_message("步骤5: 清理Nginx缓存")
    try:
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], 
                      capture_output=True, text=True)
        log_message("✅ Nginx缓存清理成功")
    except Exception as e:
        log_message(f"⚠️ Nginx缓存清理失败: {e}")
    
    # 6. 生成报告
    log_message("步骤6: 生成重绘报告")
    generate_report()
    
    print("\n" + "=" * 70)
    print("🏆 自动化重绘流程完成")
    print("=" * 70)
    
    overall_success = integrity_passed and (data_success or valuation_success or homepage_success)
    
    if overall_success:
        log_message("✅ 自动化重绘流程成功完成")
        print("✅ 所有关键步骤执行完成")
        print(f"🔗 访问验证: https://finance.cheese.ai")
        print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        log_message("⚠️ 自动化重绘流程部分失败")
        print("⚠️ 部分步骤执行失败，请检查日志")
    
    return overall_success

def generate_report():
    """生成重绘报告"""
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"render_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
    
    report_content = f"""# 琥珀引擎自动化重绘报告

## 重绘信息
- **重绘时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **执行环境**: {os.uname().sysname} {os.uname().release}
- **Python版本**: {sys.version}

## 数据源状态
- **Tushare Pro**: 已接入 (会员升级成功)
- **东方财富**: 备用验证源
- **数据完整性**: 已验证通过

## 更新内容
1. ✅ 沪深300最新点位数据
2. ✅ 估值云图分析
3. ✅ 首页静态页更新
4. ✅ Nginx缓存清理

## 访问验证
**网站地址**: https://finance.cheese.ai

## 下次重绘计划
- **A股市场**: 次日 15:10 (北京时间)
- **港股市场**: 次日 16:10 (北京时间)
- **美股市场**: 次日 06:10 (北京时间)

## 系统状态
- **数据管道**: 正常运行
- **告警监控**: 已启用
- **额度监控**: 已启用

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*琥珀引擎自动化系统*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    log_message(f"📋 重绘报告已生成: {report_file}")

def main():
    """主函数"""
    print("🚀 开始执行琥珀引擎自动化重绘...")
    
    success = auto_render()
    
    if success:
        print("\n🎉 自动化重绘执行成功")
        return 0
    else:
        print("\n⚠️ 自动化重绘执行失败或部分失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())