#!/usr/bin/env python3
"""
添加黄金指标到琥珀引擎
基于主编要求添加国际金价和国内金价
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# 配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")
CSS_FILE = os.path.join(BASE_DIR, "output", "static", "css", "amber-v2.2.min.css")
DATA_CACHE_FILE = os.path.join(BASE_DIR, "output", "static", "data", "unified_data_cache.json")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoldDataFetcher:
    """黄金数据获取器"""
    
    def __init__(self, tushare_token: str):
        os.environ['TUSHARE_TOKEN'] = tushare_token
        self.tushare_token = tushare_token
        self.today = datetime.now().strftime("%Y%m%d")
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
    def fetch_international_gold(self) -> Optional[Dict]:
        """获取国际金价 (XAUUSD)"""
        try:
            import tushare as ts
            pro = ts.pro_api()
            
            # 尝试XAUUSD.FXCM
            df = pro.fx_daily(ts_code='XAUUSD.FXCM', trade_date=self.yesterday)
            if df.empty:
                # 尝试更早日期
                df = pro.fx_daily(ts_code='XAUUSD.FXCM', start_date=self.get_previous_date(5), end_date=self.yesterday)
                if df.empty:
                    logger.warning("⚠️ 未找到XAUUSD.FXCM数据")
                    return None
            
            latest = df.iloc[0]
            bid_close = float(latest['bid_close'])
            bid_open = float(latest['bid_open'])
            
            # 计算涨跌幅
            if bid_open > 0:
                pct_change = (bid_close - bid_open) / bid_open * 100
            else:
                pct_change = 0.0
            
            return {
                "name": "国际金价",
                "code": "XAUUSD.FXCM",
                "price": bid_close,
                "change_pct": pct_change,
                "trade_date": latest['trade_date'],
                "unit": "USD/oz",
                "source": "Tushare Pro"
            }
            
        except Exception as e:
            logger.error(f"❌ 获取国际金价失败: {e}")
            return None
    
    def fetch_domestic_gold(self) -> Optional[Dict]:
        """获取国内金价 (黄金期货)"""
        try:
            import tushare as ts
            pro = ts.pro_api()
            
            # 尝试AU.SHF (上海期货交易所黄金)
            df = pro.fut_daily(ts_code='AU.SHF', trade_date=self.yesterday)
            if df.empty:
                # 尝试更早日期
                df = pro.fut_daily(ts_code='AU.SHF', start_date=self.get_previous_date(5), end_date=self.yesterday)
                if df.empty:
                    logger.warning("⚠️ 未找到AU.SHF数据")
                    return None
            
            latest = df.iloc[0]
            close_price = float(latest['close'])
            pre_close = float(latest['pre_close'])
            
            # 计算涨跌幅
            if pre_close > 0:
                pct_change = (close_price - pre_close) / pre_close * 100
            else:
                pct_change = 0.0
            
            return {
                "name": "国内金价",
                "code": "AU.SHF",
                "price": close_price,
                "change_pct": pct_change,
                "trade_date": latest['trade_date'],
                "unit": "CNY/g",
                "source": "Tushare Pro"
            }
            
        except Exception as e:
            logger.error(f"❌ 获取国内金价失败: {e}")
            return None
    
    def get_previous_date(self, days_back: int = 1) -> str:
        """获取之前日期的字符串"""
        date_obj = datetime.now() - timedelta(days=days_back)
        return date_obj.strftime("%Y%m%d")
    
    def fetch_all_gold_data(self) -> Dict:
        """获取所有黄金数据"""
        logger.info("📡 开始获取黄金数据...")
        
        results = {
            "international_gold": self.fetch_international_gold(),
            "domestic_gold": self.fetch_domestic_gold(),
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fetch_date": self.today
        }
        
        # 统计
        success_count = sum(1 for v in results.values() if isinstance(v, dict))
        logger.info(f"✅ 黄金数据获取完成: {success_count}/2 成功")
        
        if results["international_gold"]:
            gold = results["international_gold"]
            logger.info(f"  国际金价: {gold['price']} {gold['unit']} ({gold['change_pct']:+.2f}%)")
        
        if results["domestic_gold"]:
            gold = results["domestic_gold"]
            logger.info(f"  国内金价: {gold['price']} {gold['unit']} ({gold['change_pct']:+.2f}%)")
        
        return results

class GoldHTMLUpdater:
    """HTML更新器"""
    
    def __init__(self):
        self.index_file = INDEX_FILE
        
    def read_html(self) -> str:
        """读取HTML文件"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_html(self, content: str):
        """保存HTML文件"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"✅ HTML文件已更新: {self.index_file}")
    
    def add_gold_to_macro_anchors(self, gold_data: Dict) -> bool:
        """添加黄金指标到宏观双锚"""
        try:
            html_content = self.read_html()
            
            # 找到宏观双锚部分
            macro_anchor_start = html_content.find('<div class="amber-macro-anchors">')
            if macro_anchor_start == -1:
                logger.error("❌ 未找到宏观双锚部分")
                return False
            
            # 找到anchors-container内部
            anchors_container_start = html_content.find('<div class="anchors-container">', macro_anchor_start)
            if anchors_container_start == -1:
                logger.error("❌ 未找到anchors-container")
                return False
            
            # 找到arch-insight开始位置（在anchor-item之后）
            arch_insight_start = html_content.find('<div class="arch-insight">', anchors_container_start)
            if arch_insight_start == -1:
                logger.error("❌ 未找到arch-insight")
                return False
            
            # 准备黄金锚点HTML
            gold_anchors_html = ""
            
            # 国际金价
            intl_gold = gold_data.get("international_gold")
            if intl_gold:
                change_class = "change-up" if intl_gold["change_pct"] > 0 else "change-down"
                change_symbol = "↑" if intl_gold["change_pct"] > 0 else "↓"
                
                gold_anchors_html += f'''
 <div class="anchor-item">
 <span class="anchor-label">🌍 国际金价 (XAUUSD)</span>
 <span class="anchor-value">{intl_gold["price"]:.2f}</span>
 <span class="anchor-change {change_class}">{change_symbol} {abs(intl_gold["change_pct"]):.2f}%</span>
 </div>
'''
            
            # 国内金价
            domestic_gold = gold_data.get("domestic_gold")
            if domestic_gold:
                change_class = "change-up" if domestic_gold["change_pct"] > 0 else "change-down"
                change_symbol = "↑" if domestic_gold["change_pct"] > 0 else "↓"
                
                gold_anchors_html += f'''
 <div class="anchor-item">
 <span class="anchor-label">🇨🇳 国内金价 (AU.SHF)</span>
 <span class="anchor-value">{domestic_gold["price"]:.2f}</span>
 <span class="anchor-change {change_class}">{change_symbol} {abs(domestic_gold["change_pct"]):.2f}%</span>
 </div>
'''
            
            if not gold_anchors_html:
                logger.warning("⚠️ 无黄金数据可添加")
                return False
            
            # 插入黄金锚点到arch-insight之前
            new_html = (
                html_content[:arch_insight_start] +
                gold_anchors_html +
                html_content[arch_insight_start:]
            )
            
            # 更新标题（从双锚改为四锚）
            new_html = new_html.replace(
                '<!-- V3.2物理并线：宏观双锚决策头 -->',
                '<!-- V3.2.7黄金扩展：宏观四锚决策头 -->'
            )
            
            self.save_html(new_html)
            
            # 统计添加的锚点
            added_count = (1 if intl_gold else 0) + (1 if domestic_gold else 0)
            logger.info(f"✅ 添加{added_count}个黄金锚点到宏观决策头")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新HTML失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_gold_hedge_section(self, gold_data: Dict):
        """更新黄金对冲部分的实时价格"""
        try:
            html_content = self.read_html()
            
            # 找到黄金对冲部分
            gold_section_start = html_content.find('<div class="gold-hedge-section">')
            if gold_section_start == -1:
                logger.warning("⚠️ 未找到黄金对冲部分")
                return False
            
            # 找到黄金对冲统计部分
            hedge_stats_start = html_content.find('<div class="hedge-stats">', gold_section_start)
            if hedge_stats_start == -1:
                logger.warning("⚠️ 未找到hedge-stats")
                return False
            
            # 在hedge-stats后添加实时价格展示
            hedge_stats_end = html_content.find('</div>', hedge_stats_start) + 6
            
            # 准备实时价格HTML
            realtime_price_html = '''
 <div class="hedge-stats" style="margin-top: 15px; border-top: 1px solid rgba(255, 152, 0, 0.2); padding-top: 15px;">
 <div class="hedge-stat">
 <div class="hedge-label">实时价格</div>
'''
            
            # 添加国际金价
            intl_gold = gold_data.get("international_gold")
            if intl_gold:
                change_class = "price-up" if intl_gold["change_pct"] > 0 else "price-down"
                realtime_price_html += f'''
 <div class="hedge-stat">
 <div class="hedge-value {change_class}">{intl_gold["price"]:.2f}</div>
 <div class="hedge-label">国际金价 (USD/oz)</div>
 </div>
'''
            
            # 添加国内金价
            domestic_gold = gold_data.get("domestic_gold")
            if domestic_gold:
                change_class = "price-up" if domestic_gold["change_pct"] > 0 else "price-down"
                realtime_price_html += f'''
 <div class="hedge-stat">
 <div class="hedge-value {change_class}">{domestic_gold["price"]:.2f}</div>
 <div class="hedge-label">国内金价 (CNY/g)</div>
 </div>
'''
            
            realtime_price_html += '</div>'
            
            # 插入实时价格
            new_html = (
                html_content[:hedge_stats_end] +
                realtime_price_html +
                html_content[hedge_stats_end:]
            )
            
            # 更新黄金对冲标题
            new_html = new_html.replace(
                '黄金对冲配置 · 透明化展示',
                '黄金对冲配置 · 实时价格监控'
            )
            
            self.save_html(new_html)
            logger.info("✅ 黄金对冲部分已更新实时价格")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新黄金对冲部分失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 70)
    print("🛠️ 添加黄金指标到琥珀引擎")
    print("=" * 70)
    print("执行内容:")
    print("1. 获取国际金价 (XAUUSD.FXCM)")
    print("2. 获取国内金价 (AU.SHF)")
    print("3. 添加到宏观四锚决策头")
    print("4. 更新黄金对冲部分实时价格")
    print("=" * 70)
    
    try:
        # 初始化
        tushare_token = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
        fetcher = GoldDataFetcher(tushare_token)
        updater = GoldHTMLUpdater()
        
        # 步骤1: 获取黄金数据
        logger.info("\n📡 步骤1: 获取黄金数据")
        gold_data = fetcher.fetch_all_gold_data()
        
        if not gold_data.get("international_gold") and not gold_data.get("domestic_gold"):
            logger.error("❌ 无法获取黄金数据，请检查Tushare权限或网络")
            return False
        
        # 步骤2: 添加到宏观决策头
        logger.info("\n🎯 步骤2: 添加到宏观决策头")
        if not updater.add_gold_to_macro_anchors(gold_data):
            logger.error("❌ 添加黄金锚点失败")
            return False
        
        # 步骤3: 更新黄金对冲部分
        logger.info("\n💰 步骤3: 更新黄金对冲部分")
        updater.update_gold_hedge_section(gold_data)
        
        # 步骤4: 重载Nginx
        logger.info("\n🔄 步骤4: 重载Nginx服务")
        os.system("sudo systemctl reload nginx 2>/dev/null || true")
        
        # 总结报告
        print("\n" + "=" * 70)
        print("🎉 黄金指标添加完成!")
        print("=" * 70)
        
        if gold_data.get("international_gold"):
            g = gold_data["international_gold"]
            print(f"✅ 国际金价: {g['price']:.2f} {g['unit']} ({g['change_pct']:+.2f}%)")
        
        if gold_data.get("domestic_gold"):
            g = gold_data["domestic_gold"]
            print(f"✅ 国内金价: {g['price']:.2f} {g['unit']} ({g['change_pct']:+.2f}%)")
        
        print(f"\n📊 添加位置:")
        print("  1. 宏观四锚决策头 (原双锚扩展)")
        print("  2. 黄金对冲部分实时价格")
        
        print(f"\n🔗 验证地址: https://amber.googlemanager.cn:10123/?v=3.2.7")
        print("🔄 强制刷新: Ctrl+F5")
        print("=" * 70)
        
        # 数据源说明
        print("\n📡 数据源信息:")
        print("  • 国际金价: Tushare Pro - XAUUSD.FXCM")
        print("  • 国内金价: Tushare Pro - AU.SHF (上海期货交易所)")
        print("  • 更新频率: 交易日自动更新")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)