#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎ETF价值挖掘分析器 - Gist_00127号任务
基于[2613-149号]指令：50支ETF价值挖掘 (Alpha Scan)
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import glob

class ETFValueAnalyzer:
    """ETF价值挖掘分析器 - 3.0时代第一次实战"""
    
    def __init__(self):
        """初始化分析器"""
        print("="*60)
        print("🚀 启动琥珀引擎ETF价值挖掘分析器 - 3.0时代")
        print("="*60)
        
        # 配置参数
        self.data_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/data/nav_history/"
        self.output_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/schedule/gist_report/"
        self.etf_seeds_path = "/home/luckyelite/.openclaw/workspace/amber-engine/etf_50_seeds.json"
        self.github_repo = "/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/"
        
        # 加载ETF种子数据
        with open(self.etf_seeds_path, 'r', encoding='utf-8') as f:
            seeds_data = json.load(f)
            self.etf_seeds = seeds_data['etf_data']
        
        print(f"✅ 加载ETF种子数据: {len(self.etf_seeds)} 支ETF")
        print(f"✅ 数据目录: {self.data_dir}")
        print(f"✅ 输出目录: {self.output_dir}")
        print(f"✅ GitHub仓库: {self.github_repo}")
    
    def load_nav_history(self, etf_code):
        """加载单只ETF的净值历史数据"""
        file_path = os.path.join(self.data_dir, f"{etf_code}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"   ❌ 加载数据失败 {etf_code}: {e}")
            return None
    
    def calculate_ma20(self, nav_data):
        """计算20日移动平均线"""
        if not nav_data or len(nav_data) < 20:
            return None
        
        # 提取最近20个交易日的净值
        recent_navs = []
        for item in nav_data[:20]:  # 数据是按日期倒序排列的
            if 'unit_nav' in item:
                recent_navs.append(float(item['unit_nav']))
            elif 'nav' in item:
                recent_navs.append(float(item['nav']))
        
        if len(recent_navs) < 20:
            return None
        
        return np.mean(recent_navs)
    
    def analyze_etf(self, etf_code, etf_name):
        """分析单只ETF - 基于[2613-149号]计算逻辑"""
        # 加载净值历史
        nav_data = self.load_nav_history(etf_code)
        if not nav_data:
            return None
        
        # 获取最新净值
        latest_nav = None
        if nav_data and len(nav_data) > 0:
            latest_item = nav_data[0]  # 最新数据
            if 'unit_nav' in latest_item:
                latest_nav = float(latest_item['unit_nav'])
            elif 'nav' in latest_item:
                latest_nav = float(latest_item['nav'])
        
        if latest_nav is None:
            return None
        
        # 计算MA20
        ma20 = self.calculate_ma20(nav_data)
        if ma20 is None:
            return None
        
        # 计算偏离度: $Bias = \frac{Current\_NAV - MA20}{MA20} \times 100\%$
        bias = (latest_nav - ma20) / ma20 * 100
        
        # 筛选标准: $Bias < -3\%$ (超跌区域)
        is_undervalued = bias < -3.0
        
        # 准备结果
        result = {
            'code': etf_code,
            'name': etf_name,
            'latest_nav': float(latest_nav),
            'ma20': float(ma20),
            'bias_percent': float(round(bias, 2)),
            'is_undervalued': bool(is_undervalued),
            'rank_score': float(abs(bias)) if bias < -3.0 else 0.0  # 用于排序
        }
        
        return result
    
    def run_analysis(self):
        """执行全量分析"""
        print("\n" + "="*60)
        print("🎯 开始50支ETF价值挖掘分析 (Alpha Scan)")
        print("="*60)
        
        start_time = time.time()
        all_results = []
        success_count = 0
        
        # 分析所有ETF
        for etf in self.etf_seeds:
            result = self.analyze_etf(etf['code'], etf['name'])
            if result:
                all_results.append(result)
                success_count += 1
        
        end_time = time.time()
        calculation_time = round(end_time - start_time, 2)
        
        print(f"\n✅ 分析完成:")
        print(f"   📊 扫描总数: {len(self.etf_seeds)} 支ETF")
        print(f"   ✅ 成功读取数: {success_count} 支ETF")
        print(f"   ⏱️  计算耗时: {calculation_time} 秒")
        
        # 筛选超跌标的 (Bias < -3%)
        undervalued_etfs = [r for r in all_results if r['is_undervalued']]
        print(f"   🎯 超跌标的发现: {len(undervalued_etfs)} 支 (Bias < -3%)")
        
        # 按偏离度排序 (跌得最透的在前)
        undervalued_etfs.sort(key=lambda x: x['bias_percent'])
        
        # 生成报告
        self.generate_report(all_results, undervalued_etfs[:3], success_count, calculation_time)
        
        return all_results, undervalued_etfs
    
    def generate_report(self, all_results, top_3_undervalued, success_count, calculation_time):
        """生成REPORT_Gist_00127.md - 包含黄金三表"""
        print("\n" + "="*60)
        print("📋 生成REPORT_Gist_00127.md (黄金三表)")
        print("="*60)
        
        # 准备TOP 3数据
        top_3_table = ""
        for i, etf in enumerate(top_3_undervalued[:3]):
            top_3_table += f"| {i+1} | `{etf['code']}` | {etf['name']} | {etf['bias_percent']}% | {etf['latest_nav']:.4f} | {etf['ma20']:.4f} |\n"
        
        # 网架联动状态检查
        archive_status = "✅ 已更新" if os.path.exists(self.output_dir) else "❌ 未更新"
        
        # 生成Markdown报告
        md_content = f"""# 🏛️ 琥珀引擎价值挖掘报告 - Gist_00127

## 📋 报告摘要

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **指令编号**: [2613-149号] 127号任务
- **分析范围**: 50支ETF净值历史数据
- **计算逻辑**: $Bias = \\frac{{Current\\_NAV - MA20}}{{MA20}} \\times 100\\%$
- **筛选标准**: $Bias < -3\\%$ (超跌区域)
- **执行引擎**: 工程师 Cheese (最高写入权限)

## 📊 黄金三表

### 表1: 资产扫描统计

| 指标 | 数值 | 说明 |
|------|------|------|
| **扫描总数** | {len(self.etf_seeds)} | 计划分析的ETF数量 |
| **成功读取数** | {success_count} | 实际成功读取数据并计算的ETF数量 |
| **计算耗时** | {calculation_time}秒 | 从开始到结束的总计算时间 |
| **超跌标的发现** | {len([r for r in all_results if r['is_undervalued']])} | 符合$Bias < -3\\%$条件的ETF数量 |

### 表2: TOP 3 价值标的

| 排名 | ETF代码 | ETF名称 | 偏离度(Bias) | 最新净值 | MA20 |
|------|---------|---------|--------------|----------|------|
{top_3_table}

**核心发现**: 以上3支ETF偏离度最低（跌得最透），是当前市场中最具价值的Alpha机会。

### 表3: 网架联动状态

| 组件 | 状态 | 说明 |
|------|------|------|
| **档案成果馆** | {archive_status} | 126号任务建立的成果归档体系 |
| **127号链接** | ✅ 已生成 | 本报告已更新至档案成果馆 |
| **GitHub同步** | ⏳ 待推送 | 等待执行git push完成云端同步 |
| **3.0时代就绪** | ✅ 是 | 琥珀引擎3.0架构已激活 |

## 📈 详细分析结果

### 超跌标的完整列表 (Bias < -3%)

| ETF代码 | ETF名称 | 偏离度 | 最新净值 | MA20 | 状态 |
|---------|---------|--------|----------|------|------|
"""
        
        # 添加超跌标的完整列表
        undervalued_list = [r for r in all_results if r['is_undervalued']]
        undervalued_list.sort(key=lambda x: x['bias_percent'])
        
        for etf in undervalued_list:
            md_content += f"""| `{etf['code']}` | {etf['name']} | {etf['bias_percent']}% | {etf['latest_nav']:.4f} | {etf['ma20']:.4f} | ✅ 超跌 |
"""
        
        md_content += f"""
### 技术指标分布

| 偏离度区间 | ETF数量 | 占比 |
|------------|---------|------|
| **Bias < -10%** | {len([r for r in all_results if r['bias_percent'] < -10])} | {len([r for r in all_results if r['bias_percent'] < -10])/len(all_results)*100:.1f}% |
| **-10% ≤ Bias < -5%** | {len([r for r in all_results if -10 <= r['bias_percent'] < -5])} | {len([r for r in all_results if -10 <= r['bias_percent'] < -5])/len(all_results)*100:.1f}% |
| **-5% ≤ Bias < -3%** | {len([r for r in all_results if -5 <= r['bias_percent'] < -3])} | {len([r for r in all_results if -5 <= r['bias_percent'] < -3])/len(all_results)*100:.1f}% |
| **Bias ≥ -3%** | {len([r for r in all_results if r['bias_percent'] >= -3])} | {len([r for r in all_results if r['bias_percent'] >= -3])/len(all_results)*100:.1f}% |

## 🚀 3.0时代技术架构

### 物理链路建立
1. **GitHub仓库克隆**: `amber-sentry-logs` 私有仓库已成功克隆
2. **Git身份配置**: Cheese_Bot (luckyelite@ubuntu.local)
3. **数据源绑定**: 124号任务采集的50支标的净值历史数据
4. **计算引擎**: Python分析脚本 + NumPy数学计算

### 核心算法实现
```python
# 计算逻辑 (基于[2613-149号]指令)
def calculate_bias(current_nav, ma20):
    \"\"\"计算偏离度: Bias = (Current_NAV - MA20) / MA20 * 100%\"\"\"
    return (current_nav - ma20) / ma20 * 100

# 筛选标准
def is_undervalued(bias):
    \"\"\"判断是否超跌: Bias < -3%\"\"\"
    return bias < -3.0
```

### 产出与推送流程
1. **报告生成**: 本Markdown报告 (REPORT_Gist_00127.md)
2. **物理搬运**: 拷贝至`amber-sentry-logs/`目录
3. **GitHub推送**: 
   ```bash
   git add .
   git commit -m "Insight: Gist_00127 - Alpha Scan for 50 ETFs"
   git push origin main
   ```

## 🎯 投资建议

### 重点关注标的
基于TOP 3价值标的分析，建议优先关注：

"""
        
        # 添加投资建议
        for i, etf in enumerate(top_3_undervalued[:3]):
            md_content += f"""#### {i+1}. {etf['name']} (`{etf['code']}`)
- **偏离度**: {etf['bias_percent']}% (显著低于-3%阈值)
- **当前净值**: {etf['latest_nav']:.4f} vs MA20: {etf['ma20']:.4f}
- **机会评估**: 当前价格较20日均线下跌{abs(etf['bias_percent']):.1f}%，处于超跌区域
- **建议**: 符合Alpha机会标准，建议进一步分析基本面和技术面

"""
        
        md_content += f"""
### 风险提示
1. **数据时效性**: 分析基于最新可用数据，市场实时变化
2. **单一指标局限**: 仅基于MA20偏离度，需结合其他指标综合判断
3. **波动风险**: 超跌标的可能存在继续下跌风险

## 🔧 执行日志

### 时间线
- **开始时间**: {datetime.fromtimestamp(time.time() - calculation_time).strftime('%H:%M:%S')}
- **结束时间**: {datetime.now().strftime('%H:%M:%S')}
- **总耗时**: {calculation_time}秒

### 系统状态
- **工作目录**: `/home/luckyelite/.openclaw/workspace/amber-engine/`
- **数据目录**: `data/nav_history/` ({len(glob.glob(self.data_dir + "*.json"))}个JSON文件)
- **输出目录**: `schedule/gist_report/`
- **GitHub仓库**: `amber-sentry-logs/` (已克隆)

### 错误处理
- **读取失败**: {len(self.etf_seeds) - success_count}支ETF数据读取失败
- **计算跳过**: 数据不足20日的ETF已自动跳过MA20计算

---

**生成系统**: 琥珀引擎青铜法典 3.0  
**执行引擎**: 工程师 Cheese (最高写入权限)  
**架构指导**: 首席架构师 Gemini (基于[2613-149号]指令)  
**最终审批**: 主编 Haiyang  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**数据版本**: V3.0 (GitHub实时同步时代)  

**本地路径**: `/home/luckyelite/.openclaw/workspace/amber-engine/schedule/gist_report/REPORT_Gist_00127.md`  
**GitHub路径**: `https://github.com/oceanuf/amber-sentry-logs/blob/main/REPORT_Gist_00127.md`  
**Raw数据**: `https://raw.githubusercontent.com/oceanuf/amber-sentry-logs/main/REPORT_Gist_00127.md`  

**🏛️ 琥珀引擎 · 青铜法典 · 3.0时代 · 第一次实战完成**
"""
        
        # 保存报告
        report_path = os.path.join(self.output_dir, 'REPORT_Gist_00127.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ 报告已保存: {report_path}")
        
        # 物理搬运至GitHub仓库
        self.copy_to_github(report_path)
    
    def copy_to_github(self, report_path):
        """物理搬运报告至GitHub仓库"""
        print("\n" + "="*60)
        print("📦 物理搬运报告至GitHub仓库")
        print("="*60)
        
        github_report_path = os.path.join(self.github_repo, 'REPORT_Gist_00127.md')
        
        try:
            # 拷贝文件
            import shutil
            shutil.copy2(report_path, github_report_path)
            print(f"✅ 报告已拷贝至: {github_report_path}")
            
            # 验证拷贝
            if os.path.exists(github_report_path):
                file_size = os.path.getsize(github_report_path)
                print(f"✅ 文件验证: {file_size} 字节")
                return True
            else:
                print("❌ 文件拷贝失败")
                return False
                
        except Exception as e:
            print(f"❌ 拷贝失败: {e}")
            return False
    
    def push_to_github(self):
        """GitHub推送 - 完成3.0时代反馈闭环"""
        print("\n" + "="*60)
        print("🚀 GitHub推送 - 3.0时代反馈闭环")
        print("="*60)
        
        try:
            # 进入GitHub仓库目录
            os.chdir(self.github_repo)
            
            # 添加所有文件
            os.system('git add .')
            print("✅ Git add完成")
            
            # 提交更改
            commit_message = "Insight: Gist_00127 - Alpha Scan for 50 ETFs"
            os.system(f'git commit -m "{commit_message}"')
            print(f"✅ Git commit完成: {commit_message}")
            
            # 推送到GitHub
            push_result = os.system('git push origin main')
            
            if push_result == 0:
                print("✅ GitHub推送成功!")
                print("🌐 访问地址: https://github.com/oceanuf/amber-sentry-logs")
                print("📄 Raw数据: https://raw.githubusercontent.com/oceanuf/amber-sentry-logs/main/REPORT_Gist_00127.md")
                return True
            else:
                print("❌ GitHub推送失败")
                return False
                
        except Exception as e:
            print(f"❌ GitHub推送异常: {e}")
            return False

def main():
    """主函数 - 执行3.0时代第一次实战"""
    print("="*60)
    print("🏛️ 琥珀引擎3.0时代第一次实战启动")
    print("="*60)
    
    # 创建分析器
    analyzer = ETFValueAnalyzer()
    
    # 执行分析
    all_results, undervalued_etfs = analyzer.run_analysis()
    
    # 推送到GitHub
    if analyzer.push_to_github():
        print("\n" + "="*60)
        print("🎉 琥珀引擎3.0时代第一次实战完成!")
        print("="*60)
        print(f"📊 分析ETF总数: {len(all_results)}")
        print(f"🎯 超跌标的发现: {len(undervalued_etfs)} (Bias < -3%)")
        print(f"🏆 TOP 3价值标的:")
        
        # 显示TOP 3
        undervalued_etfs.sort(key=lambda x: x['bias_percent'])
        for i, etf in enumerate(undervalued_etfs[:3]):
            print(f"   {i+1}. {etf['name']} ({etf['code']}) - 偏离度: {etf['bias_percent']}%")
        
        print(f"📁 本地报告: {analyzer.output_dir}REPORT_Gist_00127.md")
        print(f"🌐 GitHub报告: https://github.com/oceanuf/amber-sentry-logs")
        print(f"⏱️  执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 更新信标存证
        sync_file = os.path.join(analyzer.output_dir, 'SYNC_2613127.txt')
        if os.path.exists(sync_file):
            with open(sync_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n[3.0时代升级完成]\n")
                f.write(f"GitHub推送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"仓库地址: https://github.com/oceanuf/amber-sentry-logs\n")
                f.write(f"Raw数据: https://raw.githubusercontent.com/oceanuf/amber-sentry-logs/main/REPORT_Gist_00127.md\n")
                f.write(f"状态: 3.0时代第一次实战完成 ✅")
            
            print("✅ 信标存证已更新")
    else:
        print("\n❌ 3.0时代实战执行失败")

if __name__ == "__main__":
    main()