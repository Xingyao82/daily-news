#!/usr/bin/env python3
"""
三妹自我进化系统
分析运行数据，自动优化策略和参数
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

EVOLUTION_LOG = "/root/.openclaw/workspace/evolution_log.json"
PERFORMANCE_DB = "/root/.openclaw/workspace/performance_db.json"

class SelfEvolution:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        """加载进化数据"""
        if os.path.exists(EVOLUTION_LOG):
            with open(EVOLUTION_LOG, 'r') as f:
                self.log = json.load(f)
        else:
            self.log = {"generations": [], "current_params": {}}
            
        if os.path.exists(PERFORMANCE_DB):
            with open(PERFORMANCE_DB, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {"scans": [], "opportunities": [], "mistakes": []}
    
    def save_data(self):
        """保存进化数据"""
        with open(EVOLUTION_LOG, 'w') as f:
            json.dump(self.log, f, indent=2)
        with open(PERFORMANCE_DB, 'w') as f:
            json.dump(self.db, f, indent=2)
    
    def record_scan_result(self, markets_scanned, opportunities_found, duration):
        """记录每次扫描结果"""
        scan_record = {
            "timestamp": datetime.now().isoformat(),
            "markets_scanned": markets_scanned,
            "opportunities_found": opportunities_found,
            "duration_seconds": duration,
            "success_rate": opportunities_found / max(markets_scanned, 1)
        }
        self.db["scans"].append(scan_record)
        
        # 只保留最近1000条记录
        if len(self.db["scans"]) > 1000:
            self.db["scans"] = self.db["scans"][-1000:]
        
        self.save_data()
    
    def analyze_patterns(self):
        """分析数据模式，找出优化点"""
        if len(self.db["scans"]) < 10:
            return {"status": "insufficient_data", "recommendations": []}
        
        recent_scans = self.db["scans"][-100:]
        
        # 计算指标
        avg_opportunities = sum(s["opportunities_found"] for s in recent_scans) / len(recent_scans)
        avg_duration = sum(s["duration_seconds"] for s in recent_scans) / len(recent_scans)
        
        # 按小时统计发现率
        hourly_stats = defaultdict(lambda: {"scans": 0, "opportunities": 0})
        for scan in recent_scans:
            hour = datetime.fromisoformat(scan["timestamp"]).hour
            hourly_stats[hour]["scans"] += 1
            hourly_stats[hour]["opportunities"] += scan["opportunities_found"]
        
        # 找出最佳扫描时段
        best_hours = sorted(hourly_stats.items(), 
                           key=lambda x: x[1]["opportunities"]/max(x[1]["scans"],1), 
                           reverse=True)[:3]
        
        recommendations = []
        
        # 如果发现率太低，建议调整阈值
        if avg_opportunities < 0.01:
            recommendations.append({
                "type": "parameter_adjustment",
                "target": "polymarket_scanner",
                "action": "increase_threshold",
                "reason": "发现率过低，可能需要放宽阈值",
                "current_value": 0.99,
                "suggested_value": 0.995
            })
        
        # 如果扫描太慢，建议优化
        if avg_duration > 300:
            recommendations.append({
                "type": "performance_optimization",
                "target": "polymarket_scanner",
                "action": "increase_concurrency",
                "reason": f"扫描耗时过长 ({avg_duration:.0f}s)"
            })
        
        return {
            "status": "analyzed",
            "avg_opportunities_per_scan": avg_opportunities,
            "avg_scan_duration": avg_duration,
            "best_hours": [h[0] for h in best_hours],
            "recommendations": recommendations
        }
    
    def learn_from_mistake(self, mistake_type, details, correction):
        """记录错误并学习"""
        mistake = {
            "timestamp": datetime.now().isoformat(),
            "type": mistake_type,
            "details": details,
            "correction": correction,
            "learned": True
        }
        self.db["mistakes"].append(mistake)
        self.save_data()
    
    def generate_evolution_report(self):
        """生成进化报告"""
        analysis = self.analyze_patterns()
        
        report = f"""
🧬 三妹自我进化报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 性能数据:
- 总扫描次数: {len(self.db['scans'])}
- 总发现机会: {sum(s['opportunities_found'] for s in self.db['scans'])}
- 平均扫描耗时: {analysis.get('avg_scan_duration', 0):.1f}秒

🎯 优化建议:
"""
        if analysis.get('recommendations'):
            for i, rec in enumerate(analysis['recommendations'], 1):
                report += f"\n{i}. {rec['type']}: {rec['action']}"
                report += f"\n   原因: {rec['reason']}"
        else:
            report += "\n暂无优化建议，当前运行良好"
        
        return report
    
    def auto_optimize(self, dry_run=True):
        """自动执行优化"""
        analysis = self.analyze_patterns()
        changes_made = []
        
        for rec in analysis.get('recommendations', []):
            if rec['type'] == 'parameter_adjustment' and not dry_run:
                # 实际修改参数（谨慎执行）
                changes_made.append(rec)
                
        # 记录这一代进化
        generation = {
            "timestamp": datetime.now().isoformat(),
            "changes": changes_made,
            "metrics_before": analysis
        }
        self.log["generations"].append(generation)
        self.save_data()
        
        return changes_made

if __name__ == "__main__":
    evo = SelfEvolution()
    print(evo.generate_evolution_report())
