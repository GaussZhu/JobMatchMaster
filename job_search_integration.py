"""
AI简历职位匹配系统 - 职位搜索抓取集成模块
将MCP网页抓取功能集成到现有应用中
"""
import os
import sys
import json
import time
from typing import List, Dict, Any, Optional, Union

# 导入网页抓取模块
from web_scraper import JobScraper, search_jobs_with_mcp

# 导入简历分析模块
from resume_analyzer import (
    ResumeAnalyzer, 
    parse_resume_enhanced, 
    match_resume_to_jobs_enhanced,
    analyze_resume_enhanced,
    generate_improvement_suggestions_enhanced
)

class JobSearchIntegration:
    """职位搜索抓取集成类，将MCP抓取功能集成到现有应用中"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化职位搜索集成器
        
        Args:
            api_key: Firecrawl API密钥，如果为None则尝试从环境变量获取
        """
        self.api_key = api_key or os.environ.get("FIRECRAWL_API_KEY")
        self.job_scraper = JobScraper(self.api_key)
        self.resume_analyzer = ResumeAnalyzer()
        
    def search_jobs(self, keywords: str, location: str = "", limit: int = 10, platform: str = "MCP抓取") -> List[Dict[str, Any]]:
        """
        搜索职位信息，优先使用MCP抓取，失败时回退到模拟数据
        
        Args:
            keywords: 搜索关键词
            location: 位置信息
            limit: 结果数量限制
            platform: 平台标识
            
        Returns:
            List[Dict[str, Any]]: 职位信息列表
        """
        # 使用MCP抓取职位信息
        return search_jobs_with_mcp(keywords, location, limit, platform)
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件，使用增强版简历分析
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            Dict[str, Any]: 解析后的简历数据
        """
        return parse_resume_enhanced(file_path)
    
    def match_resume_to_jobs(self, resume_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        计算简历与职位的匹配度，使用增强版匹配算法
        
        Args:
            resume_data: 简历数据
            jobs: 职位列表
            
        Returns:
            List[Dict[str, Any]]: 匹配结果列表
        """
        return match_resume_to_jobs_enhanced(resume_data, jobs)
    
    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析简历数据，使用增强版分析功能
        
        Args:
            resume_data: 简历数据
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        return analyze_resume_enhanced(resume_data)
    
    def generate_improvement_suggestions(self, resume_data: Dict[str, Any], job: Dict[str, Any]) -> List[str]:
        """
        生成简历改进建议，使用增强版建议功能
        
        Args:
            resume_data: 简历数据
            job: 目标职位
            
        Returns:
            List[str]: 改进建议列表
        """
        return generate_improvement_suggestions_enhanced(resume_data, job)
    
    def process_resume_and_search_jobs(self, resume_file_path: str, keywords: str, location: str = "", limit: int = 10) -> Dict[str, Any]:
        """
        处理简历并搜索匹配的职位，返回完整的处理结果
        
        Args:
            resume_file_path: 简历文件路径
            keywords: 搜索关键词
            location: 位置信息
            limit: 结果数量限制
            
        Returns:
            Dict[str, Any]: 处理结果，包含简历分析和职位匹配
        """
        # 解析简历
        resume_data = self.parse_resume(resume_file_path)
        
        # 分析简历
        resume_analysis = self.analyze_resume(resume_data)
        
        # 搜索职位
        jobs = self.search_jobs(keywords, location, limit)
        
        # 计算匹配度
        match_results = self.match_resume_to_jobs(resume_data, jobs)
        
        # 为每个职位生成改进建议
        for i, match in enumerate(match_results[:3]):  # 只为前3个最匹配的职位生成建议
            job_id = match['job_id']
            job = next((j for j in jobs if j['id'] == job_id), None)
            if job:
                suggestions = self.generate_improvement_suggestions(resume_data, job)
                match_results[i]['improvement_suggestions'] = suggestions
        
        # 返回完整结果
        return {
            'resume_data': resume_data,
            'resume_analysis': resume_analysis,
            'jobs': jobs,
            'match_results': match_results
        }
    
    def save_results_to_file(self, results: Dict[str, Any], output_file: str) -> None:
        """
        将处理结果保存到文件
        
        Args:
            results: 处理结果
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {output_file}")


# 替换原有应用中的函数
def get_enhanced_functions():
    """
    获取增强版函数，用于替换原有应用中的函数
    
    Returns:
        Dict: 包含增强版函数的字典
    """
    return {
        'search_jobs': search_jobs_with_mcp,
        'parse_resume': parse_resume_enhanced,
        'match_resume_to_jobs': match_resume_to_jobs_enhanced,
        'analyze_resume': analyze_resume_enhanced,
        'generate_improvement_suggestions': generate_improvement_suggestions_enhanced
    }


if __name__ == "__main__":
    # 测试代码
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("警告: 未设置FIRECRAWL_API_KEY环境变量，将使用模拟数据")
    
    integration = JobSearchIntegration(api_key)
    
    # 测试简历处理和职位搜索
    resume_file = "example_resume.txt"
    if not os.path.exists(resume_file):
        # 创建示例简历文件
        with open(resume_file, "w", encoding="utf-8") as f:
            f.write("张明\n")
            f.write("电话: 13812345678 邮箱: zhangming@example.com\n")
            f.write("北京市海淀区\n\n")
            f.write("个人简介: 有5年软件开发经验的全栈工程师，专注于Web应用开发和人工智能应用。\n\n")
            f.write("教育经历\n")
            f.write("北京大学 硕士 计算机科学 2015-09 - 2018-07\n")
            f.write("清华大学 学士 软件工程 2011-09 - 2015-07\n\n")
            f.write("工作经历\n")
            f.write("阿里巴巴 高级软件工程师 2020-06 - 至今\n")
            f.write("负责电商平台的后端开发，使用Java和Spring Boot构建微服务架构。\n\n")
            f.write("腾讯 软件工程师 2018-07 - 2020-05\n")
            f.write("参与社交应用的前端开发，使用React和Redux构建用户界面。\n\n")
            f.write("技能\n")
            f.write("Python, Java, JavaScript, React, Node.js, Spring Boot, MySQL, MongoDB, Docker, Git")
    
    try:
        print("开始处理简历和搜索职位...")
        results = integration.process_resume_and_search_jobs(
            resume_file_path=resume_file,
            keywords="Python开发",
            location="北京",
            limit=5
        )
        
        # 保存结果
        integration.save_results_to_file(results, "job_search_results.json")
        
        # 打印匹配结果
        print("\n职位匹配结果:")
        for i, match in enumerate(results['match_results']):
            job = next((j for j in results['jobs'] if j['id'] == match['job_id']), None)
            if job:
                print(f"{i+1}. {job['title']} - {job['company']} - 匹配度: {match['match_score']}%")
                if 'improvement_suggestions' in match:
                    print("   改进建议:")
                    for suggestion in match['improvement_suggestions']:
                        print(f"   - {suggestion}")
                print()
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
