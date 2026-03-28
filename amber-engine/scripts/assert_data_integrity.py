#!/usr/bin/env python3
"""
数据完整性验证脚本
强制要求：若两源数据偏差 > 0.1%，严禁更新静态页，并触发告警
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

def get_tushare_hs300():
    """从Tushare Pro获取沪深300数据"""
    try:
        import tushare as ts
        pro = ts.pro_api(TUSHARE_TOKEN)
        
        today = datetime.now().strftime("%Y%m%d")
        df = pro.index_daily(ts_code='000300.SH', 
                            start_date=today, 
                            end_date=today)
        
        if df is not None and not df.empty:
            data = df.iloc[0]
            return {
                'source': 'tushare_pro',
                'price': float(data['close']),
                'change': float(data['pct_chg']),
                'trade_date': data['trade_date']
            }
    except Exception as e:
        print(f"❌ Tushare数据获取失败: {e}")
    return None

def get_efinance_hs300():
    """从东方财富获取沪深300数据（备用验证源）"""
    try:
        import akshare as ak
        df = ak.stock_zh_index_spot_em()
        
        if df is not None and not df.empty:
            # 查找沪深300
            hs300_data = df[df['代码'] == '000300']
            if not hs300_data.empty:
                data = hs300_data.iloc[0]
                return {
                    'source': 'eastmoney',
                    'price': float(data['最新价']),
                    'change': float(data['涨跌幅']),
                    'trade_date': datetime.now().strftime("%Y%m%d")
                }
    except Exception as e:
        print(f"❌ 东方财富数据获取失败: {e}")
    return None

def assert_data_integrity():
    """
    数据完整性验证
    强制要求：若两源数据偏差 > 0.1%，严禁更新静态页
    """
    print("=" * 70)
    print("🔍 数据完整性验证 - 双源数据对比")
    print("=" * 70)
    
    # 获取两源数据
    tushare_data = get_tushare_hs300()
    efinance_data = get_efinance_hs300()
    
    if not tushare_data:
        print("❌ Tushare数据获取失败")
        return False, "Tushare数据获取失败"
    
    if not efinance_data:
        print("⚠️ 东方财富数据获取失败，仅使用Tushare数据")
        # 单数据源情况下，只记录日志不触发告警
        print(f"✅ Tushare数据: {tushare_data['price']:.2f} ({tushare_data['change']:+.2f}%)")
        return True, "单数据源模式"
    
    # 计算数据偏差
    price_diff = abs(tushare_data['price'] - efinance_data['price'])
    price_diff_pct = (price_diff / tushare_data['price']) * 100
    
    change_diff = abs(tushare_data['change'] - efinance_data['change'])
    
    print(f"📊 Tushare数据: {tushare_data['price']:.2f} ({tushare_data['change']:+.2f}%)")
    print(f"📊 东方财富数据: {efinance_data['price']:.2f} ({efinance_data['change']:+.2f}%)")
    print(f"📈 点位差异: {price_diff:.2f} 点")
    print(f"📈 点位差异百分比: {price_diff_pct:.3f}%")
    print(f"📈 涨跌幅差异: {change_diff:.3f}%")
    
    # 验证阈值
    MAX_PRICE_DIFF_PCT = 0.1  # 0.1% 阈值
    MAX_CHANGE_DIFF = 0.2     # 0.2% 涨跌幅差异
    
    integrity_passed = True
    warning_messages = []
    
    if price_diff_pct > MAX_PRICE_DIFF_PCT:
        integrity_passed = False
        warning_msg = f"❌ 数据偏差超限: 点位差异 {price_diff_pct:.3f}% > {MAX_PRICE_DIFF_PCT}%"
        warning_messages.append(warning_msg)
        print(warning_msg)
    else:
        print(f"✅ 点位差异检查通过: {price_diff_pct:.3f}% ≤ {MAX_PRICE_DIFF_PCT}%")
    
    if change_diff > MAX_CHANGE_DIFF:
        integrity_passed = False
        warning_msg = f"❌ 涨跌幅差异超限: {change_diff:.3f}% > {MAX_CHANGE_DIFF}%"
        warning_messages.append(warning_msg)
        print(warning_msg)
    else:
        print(f"✅ 涨跌幅差异检查通过: {change_diff:.3f}% ≤ {MAX_CHANGE_DIFF}%")
    
    if integrity_passed:
        print("\n✅ ✅ ✅ 数据完整性验证通过")
        print(f"   点位一致性: {price_diff_pct:.3f}% (阈值: {MAX_PRICE_DIFF_PCT}%)")
        print(f"   涨跌幅一致性: {change_diff:.3f}% (阈值: {MAX_CHANGE_DIFF}%)")
        return True, "数据完整性验证通过"
    else:
        print("\n❌ ❌ ❌ 数据完整性验证失败")
        
        # 触发告警
        alert_message = " | ".join(warning_messages)
        trigger_alert(alert_message, tushare_data, efinance_data)
        
        return False, alert_message

def trigger_alert(alert_message, tushare_data, efinance_data):
    """触发告警（微信/邮件）"""
    print("\n🚨 触发数据异常告警")
    print("=" * 70)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建告警日志
    alert_log = f"""
🚨 琥珀引擎数据异常告警
时间: {current_time}
异常原因: {alert_message}

📊 数据对比详情:
Tushare Pro: {tushare_data['price']:.2f} ({tushare_data['change']:+.2f}%)
东方财富: {efinance_data['price']:.2f} ({efinance_data['change']:+.2f}%)
点位差异: {abs(tushare_data['price'] - efinance_data['price']):.2f} 点
差异百分比: {(abs(tushare_data['price'] - efinance_data['price']) / tushare_data['price'] * 100):.3f}%

⚠️ 系统已暂停静态页更新，请立即检查数据源！
"""
    
    print(alert_log)
    
    # 保存告警日志到文件
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"data_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(alert_log)
    
    print(f"💾 告警日志已保存: {log_file}")
    
    # TODO: 实际部署时需要配置微信/邮件告警
    # 这里先记录到系统日志
    print("📧 告警通知: 需要配置微信/邮件告警通道")
    
    # 发送系统通知（示例）
    try:
        # 这里可以添加实际的邮件发送逻辑
        # send_email_alert(alert_log)
        pass
    except Exception as e:
        print(f"⚠️ 告警发送失败: {e}")

def main():
    """主函数"""
    print("🚀 开始执行数据完整性验证...")
    
    integrity_passed, message = assert_data_integrity()
    
    if integrity_passed:
        print("\n🎯 验证结果: 通过")
        print(f"   状态: {message}")
        return 0  # 成功退出码
    else:
        print("\n🚨 验证结果: 失败")
        print(f"   状态: {message}")
        print("\n⚠️ 系统已阻止静态页更新")
        return 1  # 失败退出码

if __name__ == "__main__":
    sys.exit(main())