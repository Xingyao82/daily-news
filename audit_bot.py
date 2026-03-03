#!/usr/bin/env python3
"""
OpenClaw 文章审核机器人 (Article Audit Bot)
版本: 1.0
功能: 自动审核文章，确保数据准确、格式规范、内容合规
"""

import json
import re
import sys
import os
from datetime import datetime

class ArticleAuditor:
    """文章审核器"""
    
    def __init__(self, article_path):
        self.article_path = article_path
        self.issues = []
        self.warnings = []
        self.passed = True
        self.content = ""
        
    def load_article(self):
        """加载文章"""
        try:
            with open(self.article_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            self.issues.append(f"无法加载文章: {e}")
            self.passed = False
            return False
    
    def check_data_accuracy(self):
        """检查数据准确性 - 关键财务数据核实"""
        print("🔍 检查数据准确性...")
        
        # NVIDIA财务数据检查
        if 'NVIDIA' in self.content or '英伟达' in self.content:
            # 检查总营收
            if '$393亿' in self.content or '$393 billion' in self.content:
                self.issues.append("🔴 严重错误: NVIDIA总营收应为$681亿，不是$393亿")
                self.passed = False
            
            if '$356亿' in self.content or '$356 billion' in self.content:
                self.issues.append("🔴 严重错误: NVIDIA数据中心收入应为$623亿，不是$356亿")
                self.passed = False
                
            if '$0.89' in self.content and 'EPS' in self.content:
                self.issues.append("🔴 严重错误: NVIDIA EPS应为$1.62，不是$0.89")
                self.passed = False
        
        # OpenAI/GPT数据检查
        if 'GPT-5' in self.content and '2026年2月' in self.content and '发布' in self.content:
            if 'MMLU' in self.content and '92.3%' in self.content:
                self.warnings.append("🟡 需核实: GPT-5的MMLU 92.3%数据需确认来源")
        
        # 阿里Qwen数据检查
        if 'Qwen 3.5' in self.content or 'Qwen3.5' in self.content:
            if '3970亿' in self.content or '397B' in self.content:
                # 这是一个真实发布的模型，数据基本正确
                pass
            else:
                self.warnings.append("🟡 需核实: Qwen 3.5参数数据需确认")
    
    def check_format(self):
        """检查格式规范"""
        print("🔍 检查格式规范...")
        
        # 检查标题
        if not self.content.startswith('# '):
            self.issues.append("❌ 格式错误: 文章必须以#开头的一级标题")
            self.passed = False
        
        # 检查发布时间
        if '发布时间' not in self.content and '**发布时间**' not in self.content:
            self.warnings.append("⚠️ 格式警告: 建议添加发布时间")
        
        # 检查来源声明
        if '来源' not in self.content and '来源声明' not in self.content:
            self.warnings.append("⚠️ 格式警告: 建议添加来源声明")
        
        # 检查免责声明
        if '免责声明' not in self.content:
            self.warnings.append("⚠️ 格式警告: 建议添加免责声明")
        
        # 检查字数
        char_count = len(self.content)
        if char_count < 1000:
            self.issues.append(f"❌ 内容过短: 仅{char_count}字符，建议至少1500字")
            self.passed = False
        elif char_count < 3000:
            self.warnings.append(f"⚠️ 内容偏短: 仅{char_count}字符，建议扩展")
    
    def check_safety(self):
        """安全检查"""
        print("🔍 安全检查...")
        
        # 检查代码块
        if '```' in self.content:
            self.warnings.append("⚠️ 发现代码块符号(```)，发布到公众号前需去除")
        
        # 检查JSON花括号
        if '{"' in self.content or '}' in self.content:
            self.warnings.append("⚠️ 发现JSON花括号，可能引起微信解析错误")
        
        # 检查敏感词
        sensitive_words = ['政治', '独裁', '共产党', '反动']
        for word in sensitive_words:
            if word in self.content:
                self.issues.append(f"🔴 敏感内容: 发现敏感词'{word}'")
                self.passed = False
    
    def check_structure(self):
        """检查文章结构"""
        print("🔍 检查文章结构...")
        
        # 检查标题层级
        h1_count = len(re.findall(r'^# ', self.content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', self.content, re.MULTILINE))
        
        if h1_count != 1:
            self.issues.append(f"❌ 结构错误: 应有1个H1标题，实际有{h1_count}个")
            self.passed = False
        
        if h2_count < 3:
            self.warnings.append(f"⚠️ 结构建议: 建议至少3个H2副标题，实际有{h2_count}个")
        
        # 检查表格
        if '|' in self.content and '---' in self.content:
            print("  ✓ 发现表格")
        
        # 检查列表
        if '- ' in self.content:
            print("  ✓ 发现列表")
    
    def generate_report(self):
        """生成审核报告"""
        report = []
        report.append("=" * 60)
        report.append("📋 文章审核报告")
        report.append("=" * 60)
        report.append(f"文章: {os.path.basename(self.article_path)}")
        report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"字数: {len(self.content)} 字符")
        report.append("-" * 60)
        
        if self.passed and not self.issues:
            report.append("\n✅ 审核结果: 通过")
        elif self.issues:
            report.append("\n🔴 审核结果: 未通过（有严重错误）")
        else:
            report.append("\n🟡 审核结果: 有条件通过（有警告）")
        
        if self.issues:
            report.append("\n🔴 严重错误（必须修复）:")
            for i, issue in enumerate(self.issues, 1):
                report.append(f"  {i}. {issue}")
        
        if self.warnings:
            report.append("\n🟡 警告建议（可选修复）:")
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"  {i}. {warning}")
        
        if not self.issues and not self.warnings:
            report.append("\n✅ 完美！未发现任何问题")
        
        report.append("\n" + "=" * 60)
        
        return '\n'.join(report)
    
    def audit(self):
        """执行完整审核"""
        print(f"\n🔎 开始审核: {self.article_path}")
        print("-" * 60)
        
        if not self.load_article():
            return False, self.generate_report()
        
        self.check_data_accuracy()
        self.check_format()
        self.check_safety()
        self.check_structure()
        
        report = self.generate_report()
        return self.passed, report


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 audit_bot.py <文章路径>")
        print("示例: python3 audit_bot.py 20260226-NVIDIA财报.md")
        sys.exit(1)
    
    article_path = sys.argv[1]
    
    auditor = ArticleAuditor(article_path)
    passed, report = auditor.audit()
    
    print(report)
    
    # 保存报告
    report_path = article_path.replace('.md', '.audit.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 审核报告已保存: {report_path}")
    
    # 返回状态码
    if passed:
        print("\n✅ 审核通过，可以发布！")
        sys.exit(0)
    else:
        print("\n❌ 审核未通过，请修复问题后重新审核！")
        sys.exit(1)


if __name__ == "__main__":
    main()
