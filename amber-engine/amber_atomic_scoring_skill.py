#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎原子化打分Skill (模拟版)
协议：MEMORY.md Section 5.1 (Weight 0.3 Override)
唯一合法的计算逻辑，工程师Cheese必须且只能通过此Skill进行ETF评分
"""

import json
import hashlib
from datetime import datetime

print("="*60)
print("🔐 琥珀引擎原子化打分Skill")
print("协议：MEMORY.md Section 5.1 (Weight 0.3 Override)")
print("唯一合法的计算逻辑")
print("="*60)

class AmberAtomicScoringSkill:
    """琥珀引擎原子化打分Skill"""
    
    def __init__(self):
        """初始化Skill"""
        # 核心加权矩阵 (V4.1 主编审计版)
        self.weights = {
            "S_D_Performance": 0.30,   # 基金表现
            "S_A_Liquidity": 0.25,     # 流动性
            "S_C_Cost": 0.20,          # 费率成本
            "S_B_Correlation": 0.125,  # 相关性
            "S_E_Management": 0.125    # 管理模式
        }
        
        print("✅ 加载核心加权矩阵:")
        for dim, weight in self.weights.items():
            print(f"   {dim}: {weight}")
    
    def calculate_final_score(self, p_raw, l_raw, c_raw, b_raw, m_raw):
        """
        计算最终分数
        公式：Final_Score = (p_raw*0.30 + l_raw*0.25 + c_raw*0.20 + b_raw*0.125 + m_raw*0.125) * 10
        """
        # 严格执行公式
        raw_weighted_score = (
            p_raw * self.weights["S_D_Performance"] +
            l_raw * self.weights["S_A_Liquidity"] +
            c_raw * self.weights["S_C_Cost"] +
            b_raw * self.weights["S_B_Correlation"] +
            m_raw * self.weights["S_E_Management"]
        )
        
        # 强制从10分制映射至100分制
        final_score = round(raw_weighted_score * 10, 2)
        
        return final_score
    
    def generate_audit_hash(self, input_data, final_score):
        """生成审计哈希（由输入数据和主编私钥生成的指纹）"""
        # 模拟主编私钥
        chief_private_key = "AMBER_ENGINE_V4_1_CHIEF_AUDIT_KEY_20260322"
        
        # 构建哈希字符串
        hash_string = f"{json.dumps(input_data, sort_keys=True)}|{final_score}|{chief_private_key}"
        
        # 生成SHA256哈希
        audit_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()[:16]
        
        return audit_hash
    
    def get_rating_category(self, final_score):
        """获取评级分类"""
        if final_score >= 85.0:
            return "🏆 核心观察池", "琥珀金", "#ff9800"
        elif final_score >= 70.0:
            return "🥈 备选观察池", "浅金", "#ffb74d"
        else:
            return "❌ 淘汰区", "灰度", "#9e9e9e"
    
    def process_etf(self, etf_data):
        """处理单只ETF"""
        print(f"\n📊 处理ETF: {etf_data['name']} ({etf_data['code']})")
        
        # 提取原始分
        p_raw = etf_data.get("p_raw", 0)
        l_raw = etf_data.get("l_raw", 0)
        c_raw = etf_data.get("c_raw", 0)
        b_raw = etf_data.get("b_raw", 0)
        m_raw = etf_data.get("m_raw", 0)
        
        print(f"   原始分: P:{p_raw} L:{l_raw} C:{c_raw} B:{b_raw} M:{m_raw}")
        
        # 计算最终分数
        final_score = self.calculate_final_score(p_raw, l_raw, c_raw, b_raw, m_raw)
        
        # 获取评级
        rating, rating_label, rating_color = self.get_rating_category(final_score)
        
        # 生成审计哈希
        audit_hash = self.generate_audit_hash(etf_data, final_score)
        
        print(f"   最终分数: {final_score}/100")
        print(f"   评级: {rating}")
        print(f"   审计哈希: {audit_hash}")
        
        return {
            "etf_info": {
                "code": etf_data["code"],
                "name": etf_data["name"]
            },
            "raw_scores": {
                "p_raw": p_raw,
                "l_raw": l_raw,
                "c_raw": c_raw,
                "b_raw": b_raw,
                "m_raw": m_raw
            },
            "final_score": final_score,
            "rating_info": {
                "rating": rating,
                "label": rating_label,
                "color": rating_color
            },
            "audit_hash": audit_hash,
            "calculation_time": datetime.now().isoformat()
        }
    
    def process_batch(self, input_file, output_file):
        """批量处理ETF数据"""
        print(f"\n📁 读取输入文件: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            
            print(f"✅ 读取成功，共 {len(input_data['etf_data'])} 只ETF")
            
            # 验证协议
            if input_data.get("protocol") != "MEMORY.md Section 5.1 (Weight 0.3 Override)":
                print("❌ 协议验证失败：输入文件协议不匹配")
                return False
            
            if input_data.get("executor_required") != "Engineer Cheese":
                print("❌ 执行者验证失败：必须由Engineer Cheese执行")
                return False
            
            print("✅ 协议验证通过")
            
        except Exception as e:
            print(f"❌ 读取输入文件失败: {e}")
            return False
        
        # 处理所有ETF
        print(f"\n🔧 开始批量处理...")
        results = []
        
        for etf in input_data["etf_data"]:
            result = self.process_etf(etf)
            results.append(result)
        
        # 按最终分数降序排序
        results.sort(key=lambda x: x["final_score"], reverse=True)
        
        # 构建输出数据
        output_data = {
            "task": input_data["task"],
            "protocol": input_data["protocol"],
            "executor": "工程师 Cheese (Audited by Chief)",
            "description": "琥珀引擎原子化打分Skill计算结果",
            "calculation_time": datetime.now().isoformat(),
            "weight_matrix": self.weights,
            "total_count": len(results),
            "summary": self.generate_summary(results),
            "detailed_results": results
        }
        
        # 保存输出文件
        print(f"\n💾 保存输出文件: {output_file}")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 输出文件保存成功")
            
            # 显示摘要
            self.display_summary(output_data["summary"])
            
            return True
            
        except Exception as e:
            print(f"❌ 保存输出文件失败: {e}")
            return False
    
    def generate_summary(self, results):
        """生成摘要统计"""
        rating_counts = {"🏆 核心观察池": 0, "🥈 备选观察池": 0, "❌ 淘汰区": 0}
        total_scores = []
        
        for result in results:
            rating = result["rating_info"]["rating"]
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
            total_scores.append(result["final_score"])
        
        # 计算统计指标
        avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
        max_score = max(total_scores) if total_scores else 0
        min_score = min(total_scores) if total_scores else 0
        
        return {
            "rating_counts": rating_counts,
            "score_statistics": {
                "average": round(avg_score, 2),
                "maximum": round(max_score, 2),
                "minimum": round(min_score, 2),
                "range": round(max_score - min_score, 2)
            },
            "top_3": results[:3] if len(results) >= 3 else results
        }
    
    def display_summary(self, summary):
        """显示摘要信息"""
        print(f"\n" + "="*60)
        print("📋 计算结果摘要")
        print("="*60)
        
        print(f"\n📊 评级分布:")
        for rating, count in summary["rating_counts"].items():
            print(f"   {rating}: {count}只")
        
        stats = summary["score_statistics"]
        print(f"\n📈 分数统计:")
        print(f"   平均分: {stats['average']}/100")
        print(f"   最高分: {stats['maximum']}/100")
        print(f"   最低分: {stats['minimum']}/100")
        print(f"   分数范围: {stats['range']}")
        
        print(f"\n🏆 Top 3 ETF:")
        for i, result in enumerate(summary["top_3"]):
            etf = result["etf_info"]
            score = result["final_score"]
            rating = result["rating_info"]["rating"]
            print(f"   {i+1}. {etf['name']} ({etf['code']}) - {score}/100 | {rating}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 琥珀引擎原子化打分Skill启动")
    print("="*60)
    
    # 创建Skill实例
    skill = AmberAtomicScoringSkill()
    
    # 处理输入文件
    input_file = "/home/luckyelite/.openclaw/workspace/amber-engine/CHEESE_INPUT_RAW_COMPLETED.json"
    output_file = "/home/luckyelite/.openclaw/workspace/amber-engine/AMBER_ATOMIC_SCORING_RESULTS.json"
    
    print(f"\n🎯 执行原子化打分...")
    print(f"   输入文件: {input_file}")
    print(f"   输出文件: {output_file}")
    
    success = skill.process_batch(input_file, output_file)
    
    if success:
        print(f"\n" + "="*60)
        print("✅ 琥珀引擎原子化打分Skill执行完成")
        print("="*60)
        print(f"\n📄 输出文件: {output_file}")
        print(f"🏢 执行者: 工程师 Cheese (Audited by Chief)")
        print(f"🔒 审计哈希: 已生成并嵌入结果文件")
    else:
        print(f"\n❌ 原子化打分执行失败")
    
    return success

if __name__ == "__main__":
    main()