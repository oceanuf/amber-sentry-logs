#!/usr/bin/env python3
"""
估值云图注入脚本
使用Tushare Pro index_dailybasic接口获取沪深300估值数据
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

def get_hs300_valuation():
    """
    获取沪深300估值数据并计算历史百分位
    """
    print("=" * 70)
    print("💎 估值云图注入 - 沪深300估值分析")
    print("=" * 70)
    
    try:
        import tushare as ts
        
        # 初始化pro接口
        pro = ts.pro_api(TUSHARE_TOKEN)
        
        # 获取当前日期
        today = datetime.now().strftime("%Y%m%d")
        
        # 1. 获取当前估值数据
        print("🔍 获取当前沪深300估值数据...")
        
        try:
            df_current = pro.index_dailybasic(ts_code='000300.SH',
                                             trade_date=today,
                                             fields='ts_code,trade_date,pe,pe_ttm,pb')
            
            if df_current is not None and not df_current.empty:
                current_data = df_current.iloc[0]
                current_pe = float(current_data['pe']) if 'pe' in current_data and pd.notna(current_data['pe']) else None
                current_pe_ttm = float(current_data['pe_ttm']) if 'pe_ttm' in current_data and pd.notna(current_data['pe_ttm']) else None
                current_pb = float(current_data['pb']) if 'pb' in current_data and pd.notna(current_data['pb']) else None
                
                print(f"✅ 当前估值数据获取成功:")
                if current_pe:
                    print(f"   市盈率(PE): {current_pe:.2f}")
                if current_pe_ttm:
                    print(f"   市盈率(TTM): {current_pe_ttm:.2f}")
                if current_pb:
                    print(f"   市净率(PB): {current_pb:.2f}")
            else:
                print("⚠️ 今日估值数据未更新，尝试获取昨日数据...")
                
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
                df_yesterday = pro.index_dailybasic(ts_code='000300.SH',
                                                   trade_date=yesterday,
                                                   fields='ts_code,trade_date,pe,pe_ttm,pb')
                
                if df_yesterday is not None and not df_yesterday.empty:
                    current_data = df_yesterday.iloc[0]
                    current_pe = float(current_data['pe']) if 'pe' in current_data and pd.notna(current_data['pe']) else None
                    current_pe_ttm = float(current_data['pe_ttm']) if 'pe_ttm' in current_data and pd.notna(current_data['pe_ttm']) else None
                    current_pb = float(current_data['pb']) if 'pb' in current_data and pd.notna(current_data['pb']) else None
                    
                    print(f"✅ 获取到昨日估值数据:")
                    if current_pe:
                        print(f"   市盈率(PE): {current_pe:.2f} (昨日)")
                    if current_pe_ttm:
                        print(f"   市盈率(TTM): {current_pe_ttm:.2f} (昨日)")
                    if current_pb:
                        print(f"   市净率(PB): {current_pb:.2f} (昨日)")
                else:
                    print("❌ 无法获取估值数据")
                    return None
                    
        except Exception as e:
            print(f"❌ 估值数据获取失败: {e}")
            return None
        
        # 2. 获取历史估值数据计算百分位
        print("\n📊 获取历史估值数据计算百分位...")
        
        try:
            # 获取最近250个交易日数据（约1年）
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
            df_history = pro.index_dailybasic(ts_code='000300.SH',
                                             start_date=start_date,
                                             end_date=today,
                                             fields='trade_date,pe,pe_ttm,pb')
            
            if df_history is not None and not df_history.empty:
                print(f"✅ 历史估值数据获取成功: {len(df_history)} 个交易日")
                
                # 计算PE历史百分位
                if current_pe and 'pe' in df_history.columns:
                    pe_history = df_history['pe'].dropna().astype(float)
                    if len(pe_history) > 0:
                        pe_percentile = (pe_history < current_pe).sum() / len(pe_history) * 100
                        print(f"   PE历史百分位: {pe_percentile:.1f}%")
                        
                        # 判断估值状态
                        if pe_percentile <= 20:
                            valuation_status = "💎 极度低估"
                            valuation_class = "valuation-extreme-low"
                            print(f"   💎 估值状态: 极度低估 (PE处于历史{pe_percentile:.1f}%分位)")
                        elif pe_percentile <= 80:
                            valuation_status = "⚖️ 合理估值"
                            valuation_class = "valuation-reasonable"
                            print(f"   ⚖️ 估值状态: 合理估值 (PE处于历史{pe_percentile:.1f}%分位)")
                        else:
                            valuation_status = "⚠️ 高估风险"
                            valuation_class = "valuation-high"
                            print(f"   ⚠️ 估值状态: 高估风险 (PE处于历史{pe_percentile:.1f}%分位)")
                        
                        # 计算TTM百分位
                        if current_pe_ttm and 'pe_ttm' in df_history.columns:
                            pe_ttm_history = df_history['pe_ttm'].dropna().astype(float)
                            if len(pe_ttm_history) > 0:
                                pe_ttm_percentile = (pe_ttm_history < current_pe_ttm).sum() / len(pe_ttm_history) * 100
                                print(f"   PE(TTM)历史百分位: {pe_ttm_percentile:.1f}%")
                        
                        # 计算PB百分位
                        if current_pb and 'pb' in df_history.columns:
                            pb_history = df_history['pb'].dropna().astype(float)
                            if len(pb_history) > 0:
                                pb_percentile = (pb_history < current_pb).sum() / len(pb_history) * 100
                                print(f"   PB历史百分位: {pb_percentile:.1f}%")
                        
                        return {
                            'current_pe': current_pe,
                            'current_pe_ttm': current_pe_ttm,
                            'current_pb': current_pb,
                            'pe_percentile': pe_percentile,
                            'valuation_status': valuation_status,
                            'valuation_class': valuation_class,
                            'data_date': current_data['trade_date'],
                            'history_count': len(df_history)
                        }
                    else:
                        print("⚠️ 历史PE数据不足")
                else:
                    print("⚠️ 当前PE数据不可用")
            else:
                print("❌ 历史估值数据获取失败")
                
        except Exception as e:
            print(f"❌ 历史数据计算失败: {e}")
            return None
            
    except ImportError as e:
        print(f"❌ tushare库导入失败: {e}")
        return None
        
    except Exception as e:
        print(f"❌ 估值分析过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_homepage_with_valuation(valuation_data):
    """
    将估值云图注入首页
    """
    print("\n" + "=" * 70)
    print("🎨 将估值云图注入琥珀引擎首页")
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
        
        # 创建估值云图HTML
        valuation_html = f'''
                <!-- 估值云图注入 -->
                <div class="index-item {valuation_data['valuation_class']}">
                    <div class="index-header">
                        <span class="index-name">估值云图</span>
                        <span class="index-market">沪深300</span>
                    </div>
                    <div class="index-value">{valuation_data['valuation_status']}</div>
                    <div class="index-detail">
                        PE: {valuation_data['current_pe']:.2f} | 历史百分位: {valuation_data['pe_percentile']:.1f}%
                    </div>
                    <div class="data-source-tag">Tushare Pro</div>
                </div>'''
        
        # 查找沪深300数据行的位置
        hs300_pattern = r'<div class="index-item">\s*<div class="index-header">\s*<span class="index-name">沪深300</span>.*?</div>\s*</div>'
        
        import re
        match = re.search(hs300_pattern, content, re.DOTALL)
        if match:
            # 在沪深300数据行后插入估值云图
            hs300_end = match.end()
            new_content = content[:hs300_end] + valuation_html + content[hs300_end:]
            
            # 保存更新后的文件
            backup_file = index_file + '.valuation_backup'
            import shutil
            shutil.copy2(index_file, backup_file)
            
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 估值云图注入成功")
            print(f"💾 备份文件: {backup_file}")
            print(f"📊 估值状态: {valuation_data['valuation_status']}")
            print(f"📈 PE百分位: {valuation_data['pe_percentile']:.1f}%")
            
            # 清理Nginx缓存
            os.system("sudo systemctl reload nginx 2>/dev/null")
            print("✅ Nginx缓存已清理")
            
            return True
        else:
            print("❌ 未找到沪深300数据行")
            return False
            
    except Exception as e:
        print(f"❌ 首页更新失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始执行估值云图注入...")
    
    # 获取估值数据
    valuation_data = get_hs300_valuation()
    
    if valuation_data:
        print(f"\n🎯 估值分析完成:")
        print(f"   当前PE: {valuation_data['current_pe']:.2f}")
        print(f"   历史百分位: {valuation_data['pe_percentile']:.1f}%")
        print(f"   估值状态: {valuation_data['valuation_status']}")
        print(f"   数据日期: {valuation_data['data_date']}")
        
        # 更新首页
        success = update_homepage_with_valuation(valuation_data)
        
        if success:
            print("\n" + "=" * 70)
            print("🏆 估值云图注入完成")
            print("=" * 70)
            print(f"✅ 估值状态: {valuation_data['valuation_status']}")
            print(f"✅ PE百分位: {valuation_data['pe_percentile']:.1f}%")
            print(f"✅ 数据日期: {valuation_data['data_date']}")
            print(f"🔗 访问验证: https://finance.cheese.ai")
            print("=" * 70)
        else:
            print("\n❌ 首页更新失败")
    else:
        print("\n❌ 估值数据获取失败")

if __name__ == "__main__":
    main()