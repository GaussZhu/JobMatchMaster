"""
AI简历职位匹配系统 - 集成模块 (Streamlit Cloud兼容版)
集成网页抓取和简历分析功能，添加了Streamlit Cloud兼容性
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

# 尝试导入网页抓取模块，如果失败则使用备用方案
try:
    from web_scraper_selenium import JobScraper, search_jobs_with_selenium
    SCRAPER_AVAILABLE = True
except ImportError:
    print("网页抓取模块不可用，将使用备用方案")
    SCRAPER_AVAILABLE = False

# 导入简历分析模块
from resume_analyzer import (
    ResumeAnalyzer,
    parse_resume_enhanced,
    match_resume_to_jobs_enhanced
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobSearchIntegration:
    """职位搜索集成类，整合网页抓取和简历分析功能"""
    
    def __init__(self):
        """初始化职位搜索集成类"""
        self.resume_analyzer = ResumeAnalyzer()
        self.job_scraper = None
        if SCRAPER_AVAILABLE:
            try:
                self.job_scraper = JobScraper(headless=True)
            except Exception as e:
                logger.error(f"初始化JobScraper失败: {str(e)}")
        
        self.cache_dir = "./cache"
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def search_jobs(self, keywords: str, location: str = "北京", limit: int = 10, platform: str = "智联招聘") -> List[Dict[str, Any]]:
        """搜索职位
        
        Args:
            keywords: 搜索关键词
            location: 地点
            limit: 结果数量限制
            platform: 平台
        
        Returns:
            List[Dict[str, Any]]: 职位列表
        """
        # 如果平台是"模拟数据"或者网页抓取模块不可用，使用模拟数据
        if platform == "模拟数据" or not SCRAPER_AVAILABLE or not self.job_scraper:
            logger.info("使用模拟数据生成职位")
            return self._generate_mock_jobs(keywords, location, limit)
        
        try:
            # 使用网页抓取模块搜索职位
            jobs = self.job_scraper.search_jobs(keywords, location, platform, limit)
            if not jobs:
                logger.warning("未找到职位，使用模拟数据")
                return self._generate_mock_jobs(keywords, location, limit)
            return jobs
        except Exception as e:
            logger.error(f"搜索职位失败: {str(e)}")
            return self._generate_mock_jobs(keywords, location, limit)
    
    def _generate_mock_jobs(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """生成模拟职位数据
        
        Args:
            keywords: 搜索关键词
            location: 地点
            limit: 结果数量限制
        
        Returns:
            List[Dict[str, Any]]: 职位列表
        """
        # 如果网页抓取模块可用，使用其模拟数据生成功能
        if SCRAPER_AVAILABLE and self.job_scraper:
            return self.job_scraper._generate_mock_jobs(keywords, location, limit)
        
        # 否则使用简单的模拟数据
        import random
        import re
        
        jobs = []
        
        # 根据查询关键词确定职位类型
        job_type = "开发工程师"
        if "python" in keywords.lower():
            job_type = "Python开发工程师"
        elif "java" in keywords.lower():
            job_type = "Java开发工程师"
        elif "前端" in keywords.lower() or "frontend" in keywords.lower():
            job_type = "前端开发工程师"
        
        # 公司列表
        companies = ["阿里巴巴", "腾讯", "百度", "京东", "美团", "字节跳动", "滴滴", "小米", "华为", "网易"]
        
        # 薪资范围
        salary_ranges = ["15K-20K", "20K-30K", "25K-35K", "30K-40K", "35K-50K"]
        
        # 技能要求
        skill_sets = {
            "Python开发工程师": ["Python", "Django", "Flask", "MySQL", "Redis", "Docker", "Git"],
            "Java开发工程师": ["Java", "Spring", "Spring Boot", "MySQL", "Redis", "Docker", "Git"],
            "前端开发工程师": ["JavaScript", "HTML", "CSS", "React", "Vue.js", "Node.js", "Git"]
        }
        
        # 生成模拟职位
        for i in range(limit):
            company = random.choice(companies)
            salary_range = random.choice(salary_ranges)
            
            # 获取技能集
            skills = skill_sets.get(job_type, ["Python", "Java", "JavaScript"])
            
            # 创建职位对象
            job = {
                "id": f"mock_{i}",
                "title": f"{job_type}",
                "company": company,
                "location": location,
                "salary_range": salary_range,
                "url": "",
                "platform": "模拟数据",
                "description": f"这是一个{job_type}职位，需要{', '.join(skills[:3])}等技能。",
                "required_skills": skills,
                "education_requirement": "本科",
                "experience_requirement": 3
            }
            
            jobs.append(job)
        
        return jobs
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """解析简历
        
        Args:
            file_path: 简历文件路径
        
        Returns:
            Dict[str, Any]: 简历数据
        """
        try:
            return parse_resume_enhanced(file_path)
        except Exception as e:
            logger.error(f"解析简历失败: {str(e)}")
            return {
                'personal_info': {'name': '未知', 'summary': '解析失败'},
                'education': [],
                'experience': [],
                'skills': []
            }
    
    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析简历
        
        Args:
            resume_data: 简历数据
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            return self.resume_analyzer.analyze_resume(resume_data)
        except Exception as e:
            logger.error(f"分析简历失败: {str(e)}")
            return {
                'personal_summary': {
                    'name': resume_data.get('personal_info', {}).get('name', '未知'),
                    'years_of_experience': 0,
                    'highest_education': '未知',
                    'skill_level': '初级',
                    'career_direction': '未知'
                },
                'skills_analysis': {'skill_count': 0, 'skill_level': '初级', 'skill_categories': {}, 'primary_skills': []},
                'education_analysis': {'education_level': '未知', 'is_cs_related': False, 'top_university': False},
                'experience_analysis': {'years': 0, 'company_tier': '未知', 'position_level': '初级', 'has_management_experience': False},
                'career_direction': {'primary_direction': '未知', 'primary_score': 0, 'secondary_direction': '未知', 'secondary_score': 0, 'direction_confidence': 'low'},
                'overall_score': {'overall_score': 0, 'level': '初级', 'component_scores': {'skills': 0, 'education': 0, 'experience': 0}}
            }
    
    def match_resume_to_jobs(self, resume_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """匹配简历与职位
        
        Args:
            resume_data: 简历数据
            jobs: 职位列表
        
        Returns:
            List[Dict[str, Any]]: 匹配结果
        """
        try:
            return match_resume_to_jobs_enhanced(resume_data, jobs)
        except Exception as e:
            logger.error(f"匹配简历与职位失败: {str(e)}")
            return []
    
    def process_resume_and_search_jobs(self, resume_file_path: str, keywords: str, location: str = "北京", limit: int = 10, platform: str = "智联招聘") -> Dict[str, Any]:
        """处理简历并搜索职位
        
        Args:
            resume_file_path: 简历文件路径
            keywords: 搜索关键词
            location: 地点
            limit: 结果数量限制
            platform: 平台
        
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 解析简历
        resume_data = self.parse_resume(resume_file_path)
        
        # 分析简历
        resume_analysis = self.analyze_resume(resume_data)
        
        # 搜索职位
        jobs = self.search_jobs(keywords, location, limit, platform)
        
        # 匹配简历与职位
        match_results = self.match_resume_to_jobs(resume_data, jobs)
        
        # 返回结果
        return {
            'resume_data': resume_data,
            'resume_analysis': resume_analysis,
            'jobs': jobs,
            'match_results': match_results
        }
    
    def save_results(self, results: Dict[str, Any], file_name: str = "match_results.json") -> str:
        """保存结果
        
        Args:
            results: 处理结果
            file_name: 文件名
        
        Returns:
            str: 文件路径
        """
        file_path = os.path.join(self.cache_dir, file_name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return file_path
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")
            return ""

def get_enhanced_functions():
    """获取增强版函数
    
    Returns:
        Tuple: (parse_resume_enhanced, match_resume_to_jobs_enhanced)
    """
    return parse_resume_enhanced, match_resume_to_jobs_enhanced

# 导出函数
__all__ = ['JobSearchIntegration', 'get_enhanced_functions']
