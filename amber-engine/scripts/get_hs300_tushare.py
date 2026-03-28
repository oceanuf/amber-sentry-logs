#!/usr/bin/env python3
"""
使用tushare-data Skill获取沪深300(000300)最新指数数据
首席架构师验证后的数据交叉验证
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

def get_hs300_from_tushare():
    """
    使用tushare获取沪深300最新数据
    """
    print("=" * 70)
    print("📊 tushare-data Skill: 沪深300(000300)数据获取")
    print("=" * 70)
    
    try:
        # 导入tushare
        import tushare as ts
        
        print(f"✅ tushare库导入成功")
        print(f"🔑 Token: {TUSHARE_TOKEN[:10]}...")
        
        # 初始化pro接口
        pro = ts.pro_api(TUSHARE_TOKEN)
        print("✅ tushare pro接口初始化成功")
        
        # 获取当前日期
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        print(f"\n📅 数据查询时间范围:")
        print(f"   今天: {today}")
        print(f"   昨天: {yesterday}")
        
        # 方法1: 使用指数日线接口
        print("\n🔍 方法1: 使用指数日线接口 (index_daily)")
        
        try:
            # 沪深300在tushare中的代码是000300.SH
            df_daily = pro.index_daily(ts_code='000300.SH', 
                                      start_date=yesterday, 
                                      end_date=today)
            
            if df_daily is not None and not df_daily.empty:
                print(f"✅ 指数日线数据获取成功，共 {len(df_daily)} 条记录")
                
                # 按交易日期排序，获取最新数据
                df_daily = df_daily.sort_values('trade_date', ascending=False)
                latest_data = df_daily.iloc[0]
                
                print(f"\n📈 沪深300最新数据 (tushare index_daily):")
                print(f"   交易日期: {latest_data['trade_date']}")
                print(f"   收盘点位: {latest_data['close']:.2f}")
                print(f"   涨跌幅: {latest_data['pct_chg']:.2f}%")
                print(f"   成交量: {latest_data['vol']:,.0f} 手")
                print(f"   成交额: {latest_data['amount']:,.0f} 元")
                
                daily_result = {
                    'source': 'tushare_index_daily',
                    'price': float(latest_data['close']),
                    'change': float(latest_data['pct_chg']),
                    'trade_date': latest_data['trade_date'],
                    'volume': float(latest_data['vol']),
                    'amount': float(latest_data['amount'])
                }
            else:
                print("⚠️ 指数日线数据为空")
                daily_result = None
                
        except Exception as e:
            print(f"❌ 指数日线接口错误: {e}")
            daily_result = None
        
        # 方法2: 使用市场行情接口
        print("\n🔍 方法2: 使用市场行情接口 (index_dailybasic)")
        
        try:
            df_basic = pro.index_dailybasic(ts_code='000300.SH',
                                           trade_date=today,
                                           fields='ts_code,trade_date,close,pct_chg,turnover_rate,turnover_f,float_share')
            
            if df_basic is not None and not df_basic.empty:
                print(f"✅ 指数基础数据获取成功，共 {len(df_basic)} 条记录")
                
                latest_basic = df_basic.iloc[0]
                
                print(f"\n📊 沪深300基础数据 (tushare index_dailybasic):")
                print(f"   交易日期: {latest_basic['trade_date']}")
                print(f"   收盘点位: {latest_basic['close']:.2f}")
                print(f"   涨跌幅: {latest_basic['pct_chg']:.2f}%")
                if 'turnover_rate' in latest_basic:
                    print(f"   换手率: {latest_basic['turnover_rate']:.2f}%")
                if 'turnover_f' in latest_basic:
                    print(f"   成交额: {latest_basic['turnover_f']:,.0f} 元")
                
                basic_result = {
                    'source': 'tushare_index_dailybasic',
                    'price': float(latest_basic['close']),
                    'change': float(latest_basic['pct_chg']),
                    'trade_date': latest_basic['trade_date']
                }
            else:
                print("⚠️ 今日数据可能未更新，尝试获取昨日数据...")
                
                # 尝试获取昨日数据
                df_basic_yesterday = pro.index_dailybasic(ts_code='000300.SH',
                                                         trade_date=yesterday,
                                                         fields='ts_code,trade_date,close,pct_chg')
                
                if df_basic_yesterday is not None and not df_basic_yesterday.empty:
                    latest_basic = df_basic_yesterday.iloc[0]
                    print(f"✅ 获取到昨日数据:")
                    print(f"   交易日期: {latest_basic['trade_date']}")
                    print(f"   收盘点位: {latest_basic['close']:.2f}")
                    print(f"   涨跌幅: {latest_basic['pct_chg']:.2f}%")
                    
                    basic_result = {
                        'source': 'tushare_index_dailybasic_yesterday',
                        'price': float(latest_basic['close']),
                        'change': float(latest_basic['pct_chg']),
                        'trade_date': latest_basic['trade_date']
                    }
                else:
                    print("❌ 昨日数据也为空")
                    basic_result = None
                    
        except Exception as e:
            print(f"❌ 指数基础数据接口错误: {e}")
            basic_result = None
        
        # 方法3: 使用通用行情接口
        print("\n🔍 方法3: 使用通用行情接口 (daily)")
        
        try:
            df_general = pro.daily(ts_code='000300.SH',
                                  start_date=yesterday,
                                  end_date=today)
            
            if df_general is not None and not df_general.empty:
                print(f"✅ 通用行情数据获取成功，共 {len(df_general)} 条记录")
                
                df_general = df_general.sort_values('trade_date', ascending=False)
                latest_general = df_general.iloc[0]
                
                print(f"\n📊 沪深300通用行情数据 (tushare daily):")
                print(f"   交易日期: {latest_general['trade_date']}")
                print(f"   收盘点位: {latest_general['close']:.2f}")
                print(f"   涨跌幅: {((latest_general['close'] - latest_general['pre_close']) / latest_general['pre_close'] * 100):.2f}%")
                print(f"   成交量: {latest_general['vol']:,.0f} 手")
                print(f"   成交额: {latest_general['amount']:,.0f} 元")
                
                general_result = {
                    'source': 'tushare_daily',
                    'price': float(latest_general['close']),
                    'change': float((latest_general['close'] - latest_general['pre_close']) / latest_general['pre_close'] * 100),
                    'trade_date': latest_general['trade_date'],
                    'volume': float(latest_general['vol']),
                    'amount': float(latest_general['amount'])
                }
            else:
                print("⚠️ 通用行情数据为空")
                general_result = None
                
        except Exception as e:
            print(f"❌ 通用行情接口错误: {e}")
            general_result = None
        
        # 汇总结果
        print("\n" + "=" * 70)
        print("📋 数据汇总与验证")
        print("=" * 70)
        
        all_results = []
        if daily_result:
            all_results.append(daily_result)
            print(f"✅ index_daily: {daily_result['price']:.2f} ({daily_result['change']:+.2f}%)")
        
        if basic_result:
            all_results.append(basic_result)
            print(f"✅ index_dailybasic: {basic_result['price']:.2f} ({basic_result['change']:+.2f}%)")
        
        if general_result:
            all_results.append(general_result)
            print(f"✅ daily: {general_result['price']:.2f} ({general_result['change']:+.2f}%)")
        
        if not all_results:
            print("❌ 所有数据接口均失败")
            return None
        
        # 选择最可靠的数据
        # 优先选择index_dailybasic，其次index_daily，最后daily
        selected_result = None
        for source_priority in ['tushare_index_dailybasic', 'tushare_index_dailybasic_yesterday', 'tushare_index_daily', 'tushare_daily']:
            for result in all_results:
                if result['source'] == source_priority:
                    selected_result = result
                    break
            if selected_result:
                break
        
        if selected_result:
            print(f"\n🎯 选择数据源: {selected_result['source']}")
            print(f"   点位: {selected_result['price']:.2f}")
            print(f"   涨跌: {selected_result['change']:+.2f}%")
            print(f"   日期: {selected_result['trade_date']}")
            
            # 与首席架构师验证的数据对比
            architect_price = 4658.33
            architect_change = 0.45
            
            print(f"\n🔍 与首席架构师验证数据对比:")
            print(f"   tushare点位: {selected_result['price']:.2f}")
            print(f"   架构师点位: {architect_price:.2f} (东方财富实时)")
            print(f"   点位差异: {abs(selected_result['price'] - architect_price):.2f}")
            print(f"   差异百分比: {abs((selected_result['price'] - architect_price) / architect_price * 100):.2f}%")
            
            if abs(selected_result['price'] - architect_price) < 10:  # 10点以内差异可接受
                print(f"✅ 数据一致性: 通过 (差异 < 10点)")
            else:
                print(f"⚠️ 数据一致性: 差异较大 ({abs(selected_result['price'] - architect_price):.2f}点)")
            
            return selected_result
        else:
            print("❌ 无法选择有效数据源")
            return None
            
    except ImportError as e:
        print(f"❌ tushare库导入失败: {e}")
        print("\n💡 解决方案:")
        print("1. 安装tushare: pip install tushare --break-system-packages")
        print("2. 或使用系统包: sudo apt install python3-tushare")
        return None
        
    except Exception as e:
        print(f"❌ 数据获取过程发生错误: {e}")
        import traceback
        print("\n📋 错误详情:")
        print(traceback.format_exc())
        return None

def main():
    """主函数"""
    print("🚀 开始获取沪深300最新指数数据...")
    
    result = get_hs300_from_tushare()
    
    if result:
        print("\n" + "=" * 70)
        print("🏆 tushare-data Skill执行完成")
        print("=" * 70)
        print(f"📊 沪深300最新数据:")
        print(f"   点位: {result['price']:.2f}")
        print(f"   涨跌: {result['change']:+.2f}%")
        print(f"   日期: {result['trade_date']}")
        print(f"   数据源: {result['source']}")
        print(f"\n🔗 Token状态: 有效 ({TUSHARE_TOKEN[:10]}...)")
        print(f"⏰ 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("\n❌ 数据获取失败")

if __name__ == "__main__":
    main()