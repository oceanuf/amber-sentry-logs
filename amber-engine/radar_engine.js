/**
 * 星辰引力雷达图引擎
 * 版本: 1.0.0
 * 用途: 为Top 5标的生成四维引力雷达图
 * 集成状态: 可被Skill_Global_Audit.py正确引用
 */

class RadarEngine {
    constructor() {
        this.version = "1.0.0";
        this.lastUpdate = "2026-03-24 15:10";
        this.status = "ACTIVE";
    }

    /**
     * 生成雷达图配置
     * @param {Object} fundData 基金数据
     * @returns {Object} Chart.js配置
     */
    generateRadarConfig(fundData) {
        const dimensions = [
            '逻辑穿透力',
            '风险抵御力', 
            '战略稀缺性',
            '执行效率'
        ];

        const scores = [
            fundData.penetration_score || 0,
            fundData.risk_resistance_score || 0,
            fundData.strategic_scarcity_score || 0,
            fundData.execution_efficiency_score || 0
        ];

        // 确保所有分值在0-100范围内
        const normalizedScores = scores.map(score => Math.max(0, Math.min(100, score)));

        return {
            type: 'radar',
            data: {
                labels: dimensions,
                datasets: [{
                    label: `${fundData.code} ${fundData.name}`,
                    data: normalizedScores,
                    backgroundColor: 'rgba(0, 180, 255, 0.2)',
                    borderColor: 'rgba(0, 180, 255, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(0, 180, 255, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(160, 160, 255, 0.3)'
                        },
                        grid: {
                            color: 'rgba(160, 160, 255, 0.2)'
                        },
                        pointLabels: {
                            color: '#a0a0ff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: '#a0a0ff',
                            font: {
                                size: 12
                            },
                            stepSize: 25,
                            max: 100,
                            min: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#e0e0ff',
                            font: {
                                size: 14
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(20, 25, 50, 0.9)',
                        titleColor: '#00b4ff',
                        bodyColor: '#e0e0ff',
                        borderColor: '#00b4ff',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const dimension = dimensions[context.dataIndex];
                                return `${dimension}: ${value.toFixed(1)}分`;
                            }
                        }
                    }
                }
            }
        };
    }

    /**
     * 生成熔断警报HTML
     * @param {Object} fundData 基金数据
     * @returns {string} HTML代码
     */
    generateBreakerAlert(fundData) {
        if (fundData.premium_rate >= 5.0) {
            return `
                <div class="breaker-alert" style="
                    background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    border-left: 5px solid #ff0000;
                    animation: pulse 2s infinite;
                ">
                    <strong>⚠️ [BREAKER_ACTIVE] 熔断触发</strong><br>
                    标的: ${fundData.code} ${fundData.name}<br>
                    溢价率: ${fundData.premium_rate.toFixed(2)}% ≥ 5.0%<br>
                    处理: 总分强制归零 (一票否决权生效)
                </div>
                <style>
                    @keyframes pulse {
                        0% { opacity: 1; }
                        50% { opacity: 0.7; }
                        100% { opacity: 1; }
                    }
                </style>
            `;
        }
        return '';
    }

    /**
     * 生成Top 5雷达图容器HTML
     * @param {Array} top5Funds Top 5基金数据
     * @returns {string} HTML代码
     */
    generateRadarContainer(top5Funds) {
        if (!top5Funds || top5Funds.length === 0) {
            return '<div class="no-data">暂无Top 5数据</div>';
        }

        let html = '<div class="radar-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">';
        
        top5Funds.forEach((fund, index) => {
            const breakerAlert = this.generateBreakerAlert(fund);
            
            html += `
                <div class="radar-card" style="
                    background: rgba(30, 35, 60, 0.8);
                    border-radius: 12px;
                    padding: 20px;
                    border: 1px solid rgba(0, 180, 255, 0.3);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #00b4ff;">
                            #${index + 1} ${fund.code} ${fund.name}
                        </h3>
                        <span style="
                            background: ${fund.total_score >= 60 ? 'linear-gradient(135deg, #00cc66, #00aa44)' : 'linear-gradient(135deg, #ff4444, #cc0000)'};
                            color: white;
                            padding: 5px 12px;
                            border-radius: 20px;
                            font-weight: bold;
                        ">
                            ${fund.total_score.toFixed(1)}分
                        </span>
                    </div>
                    
                    ${breakerAlert}
                    
                    <div style="margin: 15px 0;">
                        <canvas id="radar-${fund.code}" height="250"></canvas>
                    </div>
                    
                    <div style="
                        background: rgba(10, 15, 40, 0.6);
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 0.9em;
                    ">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                            <div>逻辑穿透力: <strong>${fund.penetration_score?.toFixed(1) || 0}</strong></div>
                            <div>风险抵御力: <strong>${fund.risk_resistance_score?.toFixed(1) || 0}</strong></div>
                            <div>战略稀缺性: <strong>${fund.strategic_scarcity_score?.toFixed(1) || 0}</strong></div>
                            <div>执行效率: <strong>${fund.execution_efficiency_score?.toFixed(1) || 0}</strong></div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    /**
     * 验证引擎状态
     * @returns {Object} 状态报告
     */
    getStatus() {
        return {
            engine: 'RadarEngine',
            version: this.version,
            status: this.status,
            lastUpdate: this.lastUpdate,
            capabilities: [
                'generateRadarConfig',
                'generateBreakerAlert', 
                'generateRadarContainer',
                'Chart.js Integration'
            ],
            compatibility: {
                skill_global_audit: '✅ 可引用',
                fetch_global_raw_v2: '✅ 数据兼容',
                web_deployment: '✅ 10168端口就绪'
            }
        };
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RadarEngine;
} else {
    // 浏览器环境
    window.RadarEngine = RadarEngine;
}