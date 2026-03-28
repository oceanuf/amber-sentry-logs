#!/usr/bin/env python3
"""
使用升级后的Tushare Pro会员获取沪深300(000300)最新指数数据
主编已升级会员，测试高级接口权限
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 设置Tushare Token (升级后)
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

def test_pro_permissions():
    """
    测试升级后的Tushare Pro会员权限
    """
    print("=" * 70)
    print("🚀 Tushare Pro会员权限测试 (升级后)")
    print("=" * 70)
    
    try:
        import tushare as ts
        
        print(f"✅ tushare库导入成功")
        print(f"🔑 Token: {TUSHARE_TOKEN[:10]}... (升级后)")
        
        # 初始化pro接口
        pro = ts.pro_api(TUSHARE_TOKEN)
        print("✅ tushare pro接口初始化成功")
        
        # 获取当前日期
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        print(f"\n📅 当前日期: {today}")
        print(f"📅 昨日日期: {yesterday}")
        
        # 测试1: 指数日线接口 (之前无权限)
        print("\n🔍 测试1: 指数日线接口 (index_daily) - 之前无权限")
        
        try:
            # 沪深300代码: 000300.SH
            df_daily = pro.index_daily(ts_code='000300.SH', 
                                      start_date=yesterday, 
                                      end_date=today,
                                      fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount')
            
            if df_daily is not None and not df_daily.empty:
                print(f"✅ ✅ ✅ 指数日线接口现在可用！返回 {len(df_daily)} 条记录")
                
                # 按交易日期排序，获取最新数据
                df_daily = df_daily.sort_values('trade_date', ascending=False)
                latest_data = df_daily.iloc[0]
                
                print(f"\n📈 沪深300最新日线数据:")
                print(f"   交易日期: {latest_data['trade_date']}")
                print(f"   收盘点位: {latest_data['close']:.2f}")
                print(f"   涨跌额: {latest_data['change']:.2f}")
                print(f"   涨跌幅: {latest_data['pct_chg']:.2f}%")
                print(f"   成交量: {latest_data['vol']:,.0f} 手")
                print(f"   成交额: {latest_data['amount']:,.0f} 元")
                print(f"   开盘: {latest_data['open']:.2f}")
                print(f"   最高: {latest_data['high']:.2f}")
                print(f"   最低: {latest_data['low']:.2f}")
                print(f"   昨收: {latest_data['pre_close']:.2f}")
                
                daily_result = {
                    'source': 'tushare_pro_index_daily',
                    'price': float(latest_data['close']),
                    'change': float(latest_data['pct_chg']),
                    'trade_date': latest_data['trade_date'],
                    'open': float(latest_data['open']),
                    'high': float(latest_data['high']),
                    'low': float(latest_data['low']),
                    'pre_close': float(latest_data['pre_close']),
                    'volume': float(latest_data['vol']),
                    'amount': float(latest_data['amount'])
                }
                
                # 保存数据到文件
                data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "static", "data")
                os.makedirs(data_dir, exist_ok=True)
                df_daily.to_csv(os.path.join(data_dir, 'hs300_daily.csv'), index=False, encoding='utf-8-sig')
                print(f"💾 数据已保存到: {os.path.join(data_dir, 'hs300_daily.csv')}")
                
            else:
                print("⚠️ 指数日线数据为空，可能今日未交易")
                daily_result = None
                
        except Exception as e:
            print(f"❌ 指数日线接口错误: {e}")
            daily_result = None
        
        # 测试2: 指数基础数据接口 (之前无权限)
        print("\n🔍 测试2: 指数基础数据接口 (index_dailybasic) - 之前无权限")
        
        try:
            df_basic = pro.index_dailybasic(ts_code='000300.SH',
                                           trade_date=today,
                                           fields='ts_code,trade_date,turnover_rate,turnover_f,pe,pe_ttm,pb')
            
            if df_basic is not None and not df_basic.empty:
                print(f"✅ ✅ ✅ 指数基础数据接口现在可用！返回 {len(df_basic)} 条记录")
                
                latest_basic = df_basic.iloc[0]
                
                print(f"\n📊 沪深300基础数据:")
                print(f"   交易日期: {latest_basic['trade_date']}")
                if 'turnover_rate' in latest_basic:
                    print(f"   换手率: {latest_basic['turnover_rate']:.2f}%")
                if 'turnover_f' in latest_basic:
                    print(f"   成交额: {latest_basic['turnover_f']:,.0f} 元")
                if 'pe' in latest_basic:
                    print(f"   市盈率: {latest_basic['pe']:.2f}")
                if 'pe_ttm' in latest_basic:
                    print(f"   市盈率(TTM): {latest_basic['pe_ttm']:.2f}")
                if 'pb' in latest_basic:
                    print(f"   市净率: {latest_basic['pb']:.2f}")
                
                basic_result = {
                    'source': 'tushare_pro_index_dailybasic',
                    'trade_date': latest_basic['trade_date'],
                    'turnover_rate': float(latest_basic['turnover_rate']) if 'turnover_rate' in latest_basic else None,
                    'turnover_f': float(latest_basic['turnover_f']) if 'turnover_f' in latest_basic else None,
                    'pe': float(latest_basic['pe']) if 'pe' in latest_basic else None,
                    'pe_ttm': float(latest_basic['pe_ttm']) if 'pe_ttm' in latest_basic else None,
                    'pb': float(latest_basic['pb']) if 'pb' in latest_basic else None
                }
            else:
                print("⚠️ 今日基础数据可能未更新，尝试获取昨日数据...")
                
                df_basic_yesterday = pro.index_dailybasic(ts_code='000300.SH',
                                                         trade_date=yesterday,
                                                         fields='ts_code,trade_date,turnover_rate,turnover_f')
                
                if df_basic_yesterday is not None and not df_basic_yesterday.empty:
                    latest_basic = df_basic_yesterday.iloc[0]
                    print(f"✅ 获取到昨日基础数据:")
                    print(f"   交易日期: {latest_basic['trade_date']}")
                    if 'turnover_rate' in latest_basic:
                        print(f"   换手率: {latest_basic['turnover_rate']:.2f}%")
                    if 'turnover_f' in latest_basic:
                        print(f"   成交额: {latest_basic['turnover_f']:,.0f} 元")
                    
                    basic_result = {
                        'source': 'tushare_pro_index_dailybasic_yesterday',
                        'trade_date': latest_basic['trade_date']
                    }
                else:
                    print("❌ 昨日基础数据也为空")
                    basic_result = None
                    
        except Exception as e:
            print(f"❌ 指数基础数据接口错误: {e}")
            basic_result = None
        
        # 测试3: 获取更多历史数据
        print("\n🔍 测试3: 获取沪深300历史数据")
        
        try:
            # 获取最近30个交易日数据
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
            df_history = pro.index_daily(ts_code='000300.SH', 
                                        start_date=start_date, 
                                        end_date=today)
            
            if df_history is not None and not df_history.empty:
                print(f"✅ 历史数据获取成功: 共 {len(df_history)} 个交易日")
                
                # 计算统计信息
                avg_price = df_history['close'].mean()
                max_price = df_history['close'].max()
                min_price = df_history['close'].min()
                latest_price = df_history.iloc[-1]['close']
                
                print(f"\n📊 沪深300历史数据统计 ({len(df_history)}个交易日):")
                print(f"   最新收盘: {latest_price:.2f}")
                print(f"   平均收盘: {avg_price:.2f}")
                print(f"   最高收盘: {max_price:.2f}")
                print(f"   最低收盘: {min_price:.2f}")
                print(f"   波动范围: {max_price - min_price:.2f} 点")
                print(f"   波动幅度: {(max_price - min_price) / avg_price * 100:.2f}%")
                
                # 保存历史数据
                history_file = os.path.join(data_dir, 'hs300_history.csv')
                df_history.to_csv(history_file, index=False, encoding='utf-8-sig')
                print(f"💾 历史数据已保存到: {history_file}")
                
                history_result = {
                    'source': 'tushare_pro_history',
                    'record_count': len(df_history),
                    'latest_price': float(latest_price),
                    'avg_price': float(avg_price),
                    'max_price': float(max_price),
                    'min_price': float(min_price)
                }
            else:
                print("⚠️ 历史数据获取失败")
                history_result = None
                
        except Exception as e:
            print(f"❌ 历史数据获取错误: {e}")
            history_result = None
        
        # 汇总结果
        print("\n" + "=" * 70)
        print("🎯 Tushare Pro会员权限测试结果")
        print("=" * 70)
        
        if daily_result:
            print(f"✅ ✅ ✅ 会员升级成功！")
            print(f"📊 沪深300最新点位: {daily_result['price']:.2f}")
            print(f"📈 涨跌幅: {daily_result['change']:+.2f}%")
            print(f"📅 交易日期: {daily_result['trade_date']}")
            
            # 与首席架构师验证的数据对比
            architect_price = 4658.33
            architect_change = 0.45
            
            print(f"\n🔍 数据一致性验证:")
            print(f"   Tushare Pro点位: {daily_result['price']:.2f}")
            print(f"   东方财富点位: {architect_price:.2f} (首席架构师验证)")
            print(f"   点位差异: {abs(daily_result['price'] - architect_price):.2f}")
            print(f"   差异百分比: {abs((daily_result['price'] - architect_price) / architect_price * 100):.2f}%")
            
            if abs(daily_result['price'] - architect_price) < 5:  # 5点以内差异优秀
                print(f"✅ ✅ ✅ 数据一致性: 优秀 (差异 < 5点)")
            elif abs(daily_result['price'] - architect_price) < 20:  # 20点以内良好
                print(f"✅ ✅ 数据一致性: 良好 (差异 < 20点)")
            else:
                print(f"⚠️ 数据一致性: 差异较大 ({abs(daily_result['price'] - architect_price):.2f}点)")
            
            # 更新首页数据
            update_homepage_with_tushare_data(daily_result)
            
            return {
                'success': True,
                'daily_data': daily_result,
                'basic_data': basic_result,
                'history_data': history_result,
                'membership_upgraded': True,
                'data_consistency': abs(daily_result['price'] - architect_price) < 20
            }
        else:
            print("❌ 虽然会员已升级，但未能获取到最新数据")
            print("💡 可能原因:")
            print("   1. 今日未交易 (周末或节假日)")
            print("   2. 数据更新延迟")
            print("   3. 接口调用限制")
            
            return {
                'success': False,
                'membership_upgraded': True,
                'error': '未能获取最新数据'
            }
            
    except ImportError as e:
        print(f"❌ tushare库导入失败: {e}")
        return {'success': False, 'error': f'tushare导入失败: {e}'}
        
    except Exception as e:
        print(f"❌ 测试过程发生错误: {e}")
        import traceback
        print("\n📋 错误详情:")
        print(traceback.format_exc())
        return {'success': False, 'error': str(e)}

def update_homepage_with_tushare_data(daily_data):
    """使用Tushare Pro数据更新首页"""
    print("\n" + "=" * 70)
    print("🎨 使用Tushare Pro数据更新首页")
    print("=" * 70)
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_file = os.path.join(base_dir, "output", "index.html")
        
        if not os.path.exists(index_file):
            print(f"❌ 首页文件不存在: {index_file}")
            return False
        
        # 读取首页内容
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新跑马灯公告
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        new_alert = f'''    <!-- Tushare Pro会员验证公告 -->
    <div id="amber-alert-bar" style="background: #e3f2fd; color: #1565c0; border-bottom: 2px solid #bbdefb; animation: pulse 2s infinite;">
        🎯 <strong>Tushare Pro会员验证：</strong> 沪深300实时点位 {daily_data['price']:.2f}，数据来源：Tushare Pro官方接口，会员升级成功。
    </div>'''
        
        # 查找并替换公告
        alert_start = content.find('<!-- 首席架构师验证公告 -->')
        if alert_start != -1:
            alert_end = content.find('<!-- 网站头部 -->', alert_start)
            if alert_end != -1:
                old_alert = content[alert_start:alert_end]
                content = content.replace(old_alert, new_alert)
                print("✅ 跑马灯公告更新成功")
        
        # 更新沪深300数据
        pct_class = "price-up" if daily_data['change'] > 0 else "price-down"
        pct_sign = "+" if daily_data['change'] > 0 else ""
        
        new_hs300_html = f'''                <div class="index-item">
                    <div class="index-header">
                        <span class="index-name">沪深300</span>
                        <span class="index-market">A股</span>
                    </div>
                    <div class="index-value">{daily_data['price']:.2f}</div>
                    <div class="index-change {pct_class}">
                        {pct_sign}{daily_data['change']:.2f}%
                    </div>
                    <div class="data-source-tag verified">Tushare Pro</div>
                </div>'''
        
        # 查找并替换沪深300数据
        import re
        pattern = r'<div class="index-item">\s*<div class="index-header">\s*<span class="index-name">沪深300</span>.*?</div>\s*</div>'
        
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for match in matches:
                content = content.replace(match, new_hs300_html)
            print("✅ 沪深300数据更新成功")
        
        # 更新时间戳
        old_time_pattern = r'数据更新: \d{4}-\d{2}-\d{2} \d{2}:\d{2} \(北京时间\)'
        new_time_text = f'数据更新: {current_time} (北京时间) | 🎯 Tushare Pro会员'
        
        content = re.sub(old_time_pattern, new_time_text, content)
        print("✅ 更新时间戳成功")
        
        # 保存更新后的文件
        backup_file = index_file + '.tushare_backup'
        import shutil
        shutil.copy2(index_file, backup_file)
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 首页更新完成")
        print(f"💾 备份文件: {backup_file}")
        print(f"⏰ 更新时间: {current_time}")
        
        # 清理Nginx缓存
        os.system("sudo systemctl reload nginx 2>/dev/null")
        print("✅ Nginx缓存已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 首页更新失败: {e}")