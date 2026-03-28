                    <th>星级</th>
                    <th>区间表现</th>
                    <th>超额收益</th>
                    <th>最新净值</th>
                </tr>
            </thead>
            <tbody>
                {etf_rows}
            </tbody>
        </table>
        
        <div class="investment-advice">
            <h3 class="advice-title">🎯 投资建议</h3>
            <p>基于十五五规划三大主线，建议配置权重如下：</p>
            
            <div class="theme-weight">
                {theme_stats_html}
            </div>
            
            <h4>🏆 表现最强ETF Top 3 (架构师要求汇报)</h4>
            <ul class="recommendation-list">
'''

    # 添加Top 3 ETF
    top_3 = results[:3]
    for i, etf in enumerate(top_3):
        html_content += f'<li><strong>{etf["name"]}</strong> ({etf["ts_code"]}) - {etf["theme"]}主题，超额收益: {etf["alpha"]}% ({etf["star"]})</li>\n'
    
    html_content += '''            </ul>
            
            <h4>📋 核心观察池（三星级ETF）</h4>
            <ul class="recommendation-list">
'''
    
    # 添加三星级ETF
    three_star_etfs = [etf for etf in results if etf['star'] == '★★★']
    for etf in three_star_etfs[:5]:
        html_content += f'<li><strong>{etf["name"]}</strong> ({etf["ts_code"]}) - {etf["theme"]}主题，超额收益: {etf["alpha"]}%</li>\n'
    
    html_content += '''            </ul>
            
            <h4>⚡ 配置策略建议</h4>
            <ul class="recommendation-list">
                <li><strong>科技自立 (40%)</strong>: 长期持有，关注技术创新和政策红利</li>
                <li><strong>绿色转型 (35%)</strong>: 趋势跟踪，把握能源革命机遇</li>
                <li><strong>安全韧性 (25%)</strong>: 防御配置，对冲系统性风险</li>
                <li><strong>动态调整</strong>: 每月复盘，根据市场变化调整权重</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>© 2026 琥珀引擎 - 十五五规划主题ETF研究中心</p>
            <p>技术架构: V3.3.1 数据补盲引擎 | 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>免责声明: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
        </div>
    </div>
</body>
</html>'''
    
    return html_content

def main():
    """主函数"""
    # 执行分析
    results = analyze_etfs()
    
    # 保存JSON数据
    analysis_data = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period': f'{START_DATE} 至 {END_DATE}',
        'hs300_performance': {'change_pct': BENCHMARK_CHANGE},
        'etfs': results
    }
    
    with open('fifteen_five_analysis_final.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    print("✅ 分析数据已保存到 fifteen_five_analysis_final.json")
    
    # 显示分析结果摘要
    print("\n📊 分析结果摘要:")
    print(f"分析时段: {analysis_data['period']}")
    print(f"沪深300基准: {BENCHMARK_CHANGE}%")
    print(f"分析ETF数量: {len(results)}")
    
    # 按主题统计
    theme_counts = {}
    for etf in results:
        theme = etf['theme']
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    print("\n🎯 主题分布:")
    for theme, count in theme_counts.items():
        print(f"  {theme}: {count}只")
    
    # 显示表现最好的5只ETF
    print("\n🏆 表现最强ETF Top 5:")
    for i, etf in enumerate(results[:5]):
        print(f"{i+1}. {etf['name']} ({etf['ts_code']})")
        print(f"   主题: {etf['theme']} | 星级: {etf['star']}")
        print(f"   超额收益: {etf['alpha']}% | 跑赢基准: {'✅' if etf['outperforms'] else '❌'}")
    
    # 生成HTML报告
    print("\n📄 生成HTML报告...")
    html_content = generate_html_report(results)
    
    # 保存HTML文件
    output_path = "/home/luckyelite/.openclaw/workspace/amber-engine/output/etf/report/fifteen-five-plan.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML报告已保存到: {output_path}")
    
    # 设置权限
    os.system(f"chmod 644 {output_path}")
    
    print("\n" + "="*60)
    print("🎉 V3.3.1 数据补盲指令执行完成!")
    print("="*60)
    
    # 最终汇报
    print("\n📋 最终执行成果:")
    print(f"1. 技术架构: V3.3.1 数据补盲引擎")
    print(f"2. 分析范围: 15只核心主题ETF")
    print(f"3. 时间窗口: {START_DATE} 至 {END_DATE}")
    print(f"4. 基准锚定: 沪深300ETF (-2.70%)")
    print(f"5. 报告位置: /etf/report/fifteen-five-plan.html")
    print(f"6. 导航集成: V3.2.9 导航条已挂载")
    
    print("\n🔗 访问链接:")
    print("https://amber.googlemanager.cn:10123/etf/report/fifteen-five-plan.html")
    
    print("\n🏆 表现最强ETF Top 3 (架构师要求):")
    for i, etf in enumerate(results[:3]):
        print(f"{i+1}. {etf['name']} ({etf['ts_code']})")
        print(f"   主题: {etf['theme']} | 星级: {etf['star']}")
        print(f"   超额收益: {etf['alpha']}%")

if __name__ == "__main__":
    main()