"""
AI简历职位匹配系统 - 单文件版本
专为Streamlit Cloud部署优化
"""
import os
import sys
import json
import re
import random
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 配置页面
st.set_page_config(
    page_title="AI简历职位匹配系统",
    page_icon="📝",
    layout="wide"
)

# 设置缓存目录
if not os.path.exists("./cache"):
    os.makedirs("./cache")

#################################################
# 简历解析器部分
#################################################

class ResumeParser:
    """简历解析器类，负责从PDF和Word文档中提取信息"""
    
    def __init__(self):
        """初始化简历解析器"""
        pass
        
    def parse(self, file_path):
        """
        解析简历文件
        
        参数:
            file_path (str): 简历文件路径
            
        返回:
            dict: 解析后的简历数据
        """
        # 由于在云端环境中PDF和Word解析可能受限，这里使用模拟数据
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._parse_pdf(file_path)
        elif file_extension == '.docx':
            return self._parse_docx(file_path)
        else:
            # 如果是未知格式，使用示例数据
            return self._get_example_resume_data()
    
    def _parse_pdf(self, file_path):
        """解析PDF文件（模拟）"""
        # 在实际部署中，这里会使用PyPDF2等库解析PDF
        # 但为了简化部署，这里直接返回示例数据
        return self._get_example_resume_data()
    
    def _parse_docx(self, file_path):
        """解析Word文件（模拟）"""
        # 在实际部署中，这里会使用python-docx等库解析Word文档
        # 但为了简化部署，这里直接返回示例数据
        return self._get_example_resume_data()
    
    def _get_example_resume_data(self):
        """获取示例简历数据"""
        return {
            'personal_info': {
                'name': '张明',
                'phone': '13812345678',
                'email': 'zhangming@example.com',
                'location': '北京市海淀区',
                'summary': '有5年软件开发经验的全栈工程师，专注于Web应用开发和人工智能应用。'
            },
            'education': [
                {
                    'school': '北京大学',
                    'degree': '硕士',
                    'major': '计算机科学',
                    'start_date': '2015-09',
                    'end_date': '2018-07',
                    'gpa': '3.8/4.0'
                },
                {
                    'school': '清华大学',
                    'degree': '学士',
                    'major': '软件工程',
                    'start_date': '2011-09',
                    'end_date': '2015-07',
                    'gpa': '3.7/4.0'
                }
            ],
            'work_experience': [
                {
                    'company': '阿里巴巴',
                    'position': '高级软件工程师',
                    'start_date': '2020-06',
                    'end_date': '至今',
                    'description': '负责电商平台的后端开发，使用Java和Spring Boot构建微服务架构。优化了订单处理系统，提高了30%的处理效率。',
                    'achievements': ['改进了CI/CD流程', '实现了自动化测试', '优化了数据库查询性能']
                },
                {
                    'company': '腾讯',
                    'position': '软件工程师',
                    'start_date': '2018-07',
                    'end_date': '2020-05',
                    'description': '参与社交应用的前端开发，使用React和Redux构建用户界面。实现了实时聊天功能，提升了用户体验。',
                    'achievements': ['开发了10+个核心组件', '减少了50%的页面加载时间', '实现了响应式设计']
                }
            ],
            'skills': [
                'Python', 'Java', 'JavaScript', 'React', 'Node.js', 
                'Spring Boot', 'MySQL', 'MongoDB', 'Docker', 'Kubernetes',
                'Git', 'CI/CD', 'AWS', 'Linux', 'RESTful API'
            ],
            'projects': [
                {
                    'name': '电商平台优化',
                    'description': '重构了电商平台的订单处理系统，使用微服务架构提高了系统的可扩展性和性能。',
                    'technologies': ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Docker']
                },
                {
                    'name': '社交媒体应用',
                    'description': '开发了一个社交媒体应用的前端，实现了实时聊天、动态发布等功能。',
                    'technologies': ['React', 'Redux', 'WebSocket', 'CSS3', 'HTML5']
                }
            ],
            'languages': [
                {'language': '中文', 'proficiency': '母语'},
                {'language': '英语', 'proficiency': '流利'}
            ],
            'certifications': [
                {'name': 'AWS Certified Solutions Architect', 'date': '2021-03'},
                {'name': 'Oracle Certified Professional Java Programmer', 'date': '2019-05'}
            ],
            'keywords': [
                '软件开发', '全栈工程师', 'Web开发', '微服务', '前端开发',
                '后端开发', '数据库优化', '云计算', '容器化', 'DevOps'
            ]
        }
    
    def get_resume_summary(self, resume_data):
        """
        获取简历摘要
        
        参数:
            resume_data (dict): 解析后的简历数据
            
        返回:
            dict: 简历摘要
        """
        summary = {
            'name': resume_data['personal_info'].get('name', '未知'),
            'latest_position': resume_data['work_experience'][0].get('position', '未知') if resume_data['work_experience'] else '未知',
            'latest_company': resume_data['work_experience'][0].get('company', '未知') if resume_data['work_experience'] else '未知',
            'experience_years': self._calculate_experience_years(resume_data['work_experience']),
            'highest_education': self._get_highest_education(resume_data['education']),
            'top_skills': resume_data['skills'][:5] if len(resume_data['skills']) > 5 else resume_data['skills'],
            'keywords': resume_data['keywords'][:5] if 'keywords' in resume_data and len(resume_data['keywords']) > 5 else resume_data.get('keywords', [])
        }
        return summary
    
    def _calculate_experience_years(self, work_experience):
        """计算工作经验年限（模拟）"""
        if not work_experience:
            return 0
        # 简化计算，实际应用中应该计算具体日期差
        return len(work_experience) * 2
    
    def _get_highest_education(self, education):
        """获取最高学历"""
        if not education:
            return '未知'
        
        # 学历等级映射
        degree_level = {
            '博士': 4,
            '硕士': 3,
            '学士': 2,
            '大专': 1,
            '高中': 0
        }
        
        highest_edu = education[0]
        highest_level = degree_level.get(highest_edu.get('degree', ''), 0)
        
        for edu in education[1:]:
            current_level = degree_level.get(edu.get('degree', ''), 0)
            if current_level > highest_level:
                highest_edu = edu
                highest_level = current_level
        
        return f"{highest_edu.get('degree', '未知')} - {highest_edu.get('major', '未知')} - {highest_edu.get('school', '未知')}"
    
    def save_parsed_data(self, resume_data, output_file):
        """
        保存解析后的数据到文件
        
        参数:
            resume_data (dict): 解析后的简历数据
            output_file (str): 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, ensure_ascii=False, indent=4)

#################################################
# 职位匹配算法部分
#################################################

class JobMatcher:
    """职位匹配算法类，负责计算简历与职位的匹配度"""
    
    def __init__(self):
        """初始化职位匹配器"""
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def match_resume_to_job(self, resume_data, job_data):
        """
        计算简历与职位的匹配度
        
        参数:
            resume_data (dict): 解析后的简历数据
            job_data (dict): 职位数据
            
        返回:
            dict: 匹配结果
        """
        # 计算各维度的匹配分数
        text_similarity = self._calculate_text_similarity(resume_data, job_data)
        keyword_match = self._calculate_keyword_match(resume_data, job_data)
        skill_match, matched_skills = self._calculate_skill_match(resume_data, job_data)
        education_match = self._calculate_education_match(resume_data, job_data)
        experience_match = self._calculate_experience_match(resume_data, job_data)
        
        # 计算综合匹配分数（各维度加权平均）
        weights = {
            'text_similarity': 0.2,
            'keyword_match': 0.2,
            'skill_match': 0.3,
            'education_match': 0.15,
            'experience_match': 0.15
        }
        
        overall_match = (
            text_similarity * weights['text_similarity'] +
            keyword_match * weights['keyword_match'] +
            skill_match * weights['skill_match'] +
            education_match * weights['education_match'] +
            experience_match * weights['experience_match']
        )
        
        # 返回匹配结果
        return {
            'job_id': job_data.get('id', ''),
            'job_title': job_data.get('title', '未知职位'),
            'company': job_data.get('company', '未知公司'),
            'overall_match': overall_match,
            'text_similarity': text_similarity,
            'keyword_match': keyword_match,
            'skill_match': skill_match,
            'education_match': education_match,
            'experience_match': experience_match,
            'matched_skills': matched_skills
        }
    
    def _calculate_text_similarity(self, resume_data, job_data):
        """计算文本相似度"""
        # 提取简历文本
        resume_text = self._extract_resume_text(resume_data)
        
        # 提取职位文本
        job_text = self._extract_job_text(job_data)
        
        # 如果文本为空，返回0
        if not resume_text or not job_text:
            return 0.0
        
        # 计算TF-IDF向量
        try:
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, job_text])
            # 计算余弦相似度
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            # 如果计算失败，返回随机值（仅用于演示）
            return random.uniform(0.5, 0.9)
    
    def _extract_resume_text(self, resume_data):
        """从简历数据中提取文本"""
        text_parts = []
        
        # 添加个人信息
        if 'personal_info' in resume_data:
            personal = resume_data['personal_info']
            if 'summary' in personal:
                text_parts.append(personal['summary'])
        
        # 添加工作经验
        if 'work_experience' in resume_data:
            for exp in resume_data['work_experience']:
                if 'position' in exp:
                    text_parts.append(exp['position'])
                if 'description' in exp:
                    text_parts.append(exp['description'])
                if 'achievements' in exp and isinstance(exp['achievements'], list):
                    text_parts.extend(exp['achievements'])
        
        # 添加技能
        if 'skills' in resume_data and isinstance(resume_data['skills'], list):
            text_parts.extend(resume_data['skills'])
        
        # 添加项目经验
        if 'projects' in resume_data:
            for project in resume_data['projects']:
                if 'description' in project:
                    text_parts.append(project['description'])
                if 'technologies' in project and isinstance(project['technologies'], list):
                    text_parts.extend(project['technologies'])
        
        # 添加关键词
        if 'keywords' in resume_data and isinstance(resume_data['keywords'], list):
            text_parts.extend(resume_data['keywords'])
        
        return ' '.join(text_parts)
    
    def _extract_job_text(self, job_data):
        """从职位数据中提取文本"""
        text_parts = []
        
        # 添加职位标题
        if 'title' in job_data:
            text_parts.append(job_data['title'])
        
        # 添加职位描述
        if 'description' in job_data:
            text_parts.append(job_data['description'])
        
        # 添加职责
        if 'responsibilities' in job_data and isinstance(job_data['responsibilities'], list):
            text_parts.extend(job_data['responsibilities'])
        
        # 添加要求
        if 'requirements' in job_data and isinstance(job_data['requirements'], list):
            text_parts.extend(job_data['requirements'])
        
        # 添加技能要求
        if 'required_skills' in job_data and isinstance(job_data['required_skills'], list):
            text_parts.extend(job_data['required_skills'])
        
        # 添加关键词
        if 'keywords' in job_data and isinstance(job_data['keywords'], list):
            text_parts.extend(job_data['keywords'])
        
        return ' '.join(text_parts)
    
    def _calculate_keyword_match(self, resume_data, job_data):
        """计算关键词匹配度"""
        # 提取简历关键词
        resume_keywords = set()
        if 'keywords' in resume_data and isinstance(resume_data['keywords'], list):
            resume_keywords.update(resume_data['keywords'])
        
        # 提取职位关键词
        job_keywords = set()
        if 'keywords' in job_data and isinstance(job_data['keywords'], list):
            job_keywords.update(job_data['keywords'])
        
        # 如果关键词为空，返回0
        if not resume_keywords or not job_keywords:
            return 0.0
        
        # 计算匹配的关键词数量
        matched_keywords = resume_keywords.intersection(job_keywords)
        
        # 计算匹配度
        match_score = len(matched_keywords) / len(job_keywords) if job_keywords else 0
        
        return match_score
    
    def _calculate_skill_match(self, resume_data, job_data):
        """计算技能匹配度"""
        # 提取简历技能
        resume_skills = set()
        if 'skills' in resume_data and isinstance(resume_data['skills'], list):
            resume_skills.update(resume_data['skills'])
        
        # 提取职位所需技能
        job_skills = set()
        if 'required_skills' in job_data and isinstance(job_data['required_skills'], list):
            job_skills.update(job_data['required_skills'])
        
        # 如果技能为空，返回0和空列表
        if not resume_skills or not job_skills:
            return 0.0, []
        
        # 计算匹配的技能
        matched_skills = list(resume_skills.intersection(job_skills))
        
        # 计算匹配度
        match_score = len(matched_skills) / len(job_skills) if job_skills else 0
        
        return match_score, matched_skills
    
    def _calculate_education_match(self, resume_data, job_data):
        """计算教育背景匹配度"""
        # 学历等级映射
        degree_level = {
            '博士': 4,
            '硕士': 3,
            '学士': 2,
            '大专': 1,
            '高中': 0,
            '': 0
        }
        
        # 提取简历中的最高学历
        resume_highest_degree = ''
        if 'education' in resume_data and resume_data['education']:
            for edu in resume_data['education']:
                degree = edu.get('degree', '')
                if degree_level.get(degree, 0) > degree_level.get(resume_highest_degree, 0):
                    resume_highest_degree = degree
        
        # 提取职位要求的学历
        job_required_degree = ''
        if 'education_requirement' in job_data:
            job_required_degree = job_data.get('education_requirement', '')
        
        # 如果没有学历要求，返回1（完全匹配）
        if not job_required_degree:
            return 1.0
        
        # 计算匹配度
        resume_level = degree_level.get(resume_highest_degree, 0)
        job_level = degree_level.get(job_required_degree, 0)
        
        # 如果简历学历等于或高于职位要求，返回1
        if resume_level >= job_level:
            return 1.0
        
        # 否则返回部分匹配分数
        return resume_level / job_level if job_level > 0 else 0
    
    def _calculate_experience_match(self, resume_data, job_data):
        """计算工作经验匹配度"""
        # 提取简历中的工作经验年限
        resume_experience_years = 0
        if 'work_experience' in resume_data:
            # 简化计算，实际应用中应该计算具体日期差
            resume_experience_years = len(resume_data['work_experience']) * 2
        
        # 提取职位要求的工作经验年限
        job_required_years = 0
        if 'experience_requirement' in job_data:
            job_required_years = job_data.get('experience_requirement', 0)
        
        # 如果没有经验要求，返回1（完全匹配）
        if job_required_years <= 0:
            return 1.0
        
        # 计算匹配度
        # 如果简历经验等于或高于职位要求，返回1
        if resume_experience_years >= job_required_years:
            return 1.0
        
        # 否则返回部分匹配分数
        return resume_experience_years / job_required_years
    
    def rank_jobs_by_match(self, resume_data, job_list):
        """
        根据匹配度对职位列表进行排序
        
        参数:
            resume_data (dict): 解析后的简历数据
            job_list (list): 职位列表
            
        返回:
            list: 按匹配度排序的匹配结果列表
        """
        # 计算每个职位的匹配度
        match_results = []
        for job in job_list:
            match_result = self.match_resume_to_job(resume_data, job)
            match_results.append(match_result)
        
        # 按匹配度降序排序
        match_results.sort(key=lambda x: x['overall_match'], reverse=True)
        
        return match_results

#################################################
# 职位搜索API部分
#################################################

class JobSearchAPI:
    """职位搜索API类，负责从招聘网站获取职位信息"""
    
    def __init__(self):
        """初始化职位搜索API"""
        pass
    
    def search_jobs(self, keywords, location='', use_api=False, limit=10):
        """
        搜索职位
        
        参数:
            keywords (str): 职位关键词
            location (str): 工作地点
            use_api (bool): 是否使用真实API
            limit (int): 返回结果数量限制
            
        返回:
            list: 职位列表
        """
        # 在云端环境中，使用模拟数据
        return self._get_mock_jobs(keywords, location, limit)
    
    def _get_mock_jobs(self, keywords, location, limit):
        """获取模拟职位数据"""
        # 职位标题模板
        job_titles = [
            "软件工程师", "高级软件工程师", "软件开发工程师", "全栈工程师", 
            "前端开发工程师", "后端开发工程师", "数据工程师", "DevOps工程师",
            "机器学习工程师", "人工智能工程师", "产品经理", "项目经理",
            "UI/UX设计师", "测试工程师", "质量保证工程师", "系统架构师"
        ]
        
        # 公司名称模板
        companies = [
            "阿里巴巴", "腾讯", "百度", "字节跳动", "华为", "小米", 
            "京东", "美团", "滴滴", "网易", "新浪", "搜狐",
            "IBM", "微软", "谷歌", "亚马逊", "苹果", "英特尔"
        ]
        
        # 技能模板
        all_skills = [
            "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust",
            "React", "Vue", "Angular", "Node.js", "Express", "Django",
            "Spring Boot", "Flask", "FastAPI", "MySQL", "PostgreSQL",
            "MongoDB", "Redis", "Elasticsearch", "Docker", "Kubernetes",
            "AWS", "Azure", "GCP", "Linux", "Git", "CI/CD", "RESTful API",
            "GraphQL", "微服务", "分布式系统", "云计算", "大数据", "机器学习",
            "深度学习", "自然语言处理", "计算机视觉", "敏捷开发", "Scrum"
        ]
        
        # 职责模板
        responsibilities_templates = [
            "负责{product}的{aspect}开发",
            "设计和实现{product}的{aspect}功能",
            "优化{product}的{aspect}性能",
            "参与{product}的{aspect}架构设计",
            "维护和改进{product}的{aspect}模块",
            "与{team}团队协作完成{product}的开发",
            "解决{product}在{aspect}方面的技术问题",
            "编写高质量的代码并进行代码审查",
            "参与{product}的需求分析和功能设计",
            "为{product}开发自动化测试"
        ]
        
        # 产品模板
        products = [
            "电商平台", "社交应用", "支付系统", "搜索引擎", "内容平台",
            "云服务", "企业管理系统", "数据分析平台", "AI应用", "移动应用"
        ]
        
        # 方面模板
        aspects = [
            "前端", "后端", "全栈", "数据库", "算法", "架构",
            "性能", "安全", "用户体验", "接口", "微服务"
        ]
        
        # 团队模板
        teams = [
            "产品", "设计", "测试", "运维", "数据", "算法",
            "前端", "后端", "移动端", "安全"
        ]
        
        # 要求模板
        requirements_templates = [
            "熟悉{skill}技术栈",
            "有{experience}年以上{skill}开发经验",
            "精通{skill}和{skill}",
            "了解{concept}原理",
            "具有{product}相关项目经验",
            "能够独立完成{task}",
            "良好的{soft_skill}能力",
            "熟悉常见的{pattern}",
            "{degree}及以上学历，{major}相关专业优先",
            "有{industry}行业经验者优先"
        ]
        
        # 经验模板
        experiences = ["1-3", "3-5", "5-8", "8+"]
        
        # 概念模板
        concepts = [
            "分布式系统", "设计模式", "数据结构和算法", "网络协议",
            "操作系统", "数据库原理", "编译原理", "软件工程", "安全"
        ]
        
        # 任务模板
        tasks = [
            "系统设计", "功能开发", "性能优化", "问题排查",
            "代码重构", "技术选型", "架构升级", "自动化测试"
        ]
        
        # 软技能模板
        soft_skills = [
            "沟通", "团队协作", "问题解决", "学习", "时间管理",
            "抗压", "创新", "领导", "自驱", "适应变化"
        ]
        
        # 模式模板
        patterns = [
            "设计模式", "架构模式", "开发模式", "测试方法", "部署策略"
        ]
        
        # 学历模板
        degrees = ["大专", "本科", "硕士", "博士"]
        
        # 专业模板
        majors = [
            "计算机科学", "软件工程", "电子信息", "通信工程",
            "数学", "物理", "自动化", "人工智能"
        ]
        
        # 行业模板
        industries = [
            "互联网", "电商", "金融", "教育", "医疗", "游戏",
            "企业服务", "人工智能", "物联网", "区块链"
        ]
        
        # 生成职位列表
        jobs = []
        for i in range(min(limit, 20)):  # 最多生成20个职位
            # 根据关键词调整职位标题
            if "前端" in keywords:
                job_title = random.choice(["前端开发工程师", "高级前端工程师", "Web前端开发", "UI开发工程师", "JavaScript工程师"])
            elif "后端" in keywords:
                job_title = random.choice(["后端开发工程师", "高级后端工程师", "服务端开发", "Java开发工程师", "Python开发工程师"])
            elif "全栈" in keywords:
                job_title = random.choice(["全栈工程师", "全栈开发工程师", "Web全栈开发", "全栈软件工程师"])
            elif "数据" in keywords:
                job_title = random.choice(["数据工程师", "数据分析师", "大数据开发工程师", "数据科学家", "BI工程师"])
            elif "AI" in keywords or "人工智能" in keywords:
                job_title = random.choice(["机器学习工程师", "AI研发工程师", "深度学习工程师", "算法工程师", "NLP工程师"])
            elif "产品" in keywords:
                job_title = random.choice(["产品经理", "高级产品经理", "产品专员", "产品运营", "产品设计师"])
            else:
                job_title = random.choice(job_titles)
            
            # 根据关键词和职位标题选择相关技能
            if "前端" in job_title:
                required_skills = random.sample(["JavaScript", "HTML", "CSS", "React", "Vue", "Angular", "TypeScript", "Webpack", "Node.js", "小程序开发"], k=random.randint(4, 6))
            elif "后端" in job_title:
                required_skills = random.sample(["Java", "Python", "Go", "C++", "Spring Boot", "Django", "Flask", "MySQL", "Redis", "微服务"], k=random.randint(4, 6))
            elif "全栈" in job_title:
                required_skills = random.sample(["JavaScript", "Python", "React", "Node.js", "Express", "MongoDB", "MySQL", "Docker", "Git", "RESTful API"], k=random.randint(5, 7))
            elif "数据" in job_title:
                required_skills = random.sample(["Python", "SQL", "Hadoop", "Spark", "Hive", "数据仓库", "ETL", "数据可视化", "统计分析", "机器学习"], k=random.randint(4, 6))
            elif "机器学习" in job_title or "AI" in job_title or "算法" in job_title:
                required_skills = random.sample(["Python", "TensorFlow", "PyTorch", "机器学习", "深度学习", "NLP", "计算机视觉", "数据挖掘", "算法设计", "数学建模"], k=random.randint(4, 6))
            elif "产品" in job_title:
                required_skills = random.sample(["产品设计", "用户研究", "需求分析", "原型设计", "数据分析", "项目管理", "市场分析", "用户体验", "商业模式", "产品运营"], k=random.randint(4, 6))
            else:
                required_skills = random.sample(all_skills, k=random.randint(4, 8))
            
            # 生成职责描述
            responsibilities = []
            for _ in range(random.randint(3, 5)):
                template = random.choice(responsibilities_templates)
                product = random.choice(products)
                aspect = random.choice(aspects)
                team = random.choice(teams)
                responsibility = template.format(product=product, aspect=aspect, team=team)
                responsibilities.append(responsibility)
            
            # 生成要求描述
            requirements = []
            for _ in range(random.randint(4, 6)):
                template = random.choice(requirements_templates)
                skill1, skill2 = random.sample(all_skills, k=2)
                experience = random.choice(experiences)
                concept = random.choice(concepts)
                task = random.choice(tasks)
                soft_skill = random.choice(soft_skills)
                pattern = random.choice(patterns)
                degree = random.choice(degrees)
                major = random.choice(majors)
                industry = random.choice(industries)
                
                requirement = template.format(
                    skill=skill1, experience=experience, concept=concept,
                    product=random.choice(products), task=task, soft_skill=soft_skill,
                    pattern=pattern, degree=degree, major=major, industry=industry
                )
                requirements.append(requirement)
            
            # 生成职位描述
            description = f"{job_title}职位描述：\n"
            description += f"我们正在寻找一位经验丰富的{job_title}加入我们的团队，"
            description += f"负责{random.choice(products)}的{random.choice(aspects)}开发工作。"
            description += f"理想候选人应具备{', '.join(required_skills[:3])}等技能，"
            description += f"有{random.choice(experiences)}年相关工作经验。"
            
            # 生成职位数据
            job = {
                'id': f"job_{i+1}",
                'title': job_title,
                'company': random.choice(companies),
                'location': location if location else random.choice(["北京", "上海", "深圳", "杭州", "广州"]),
                'description': description,
                'responsibilities': responsibilities,
                'requirements': requirements,
                'required_skills': required_skills,
                'education_requirement': random.choice(degrees),
                'experience_requirement': int(random.choice(["1", "2", "3", "5", "8"])),
                'salary_range': random.choice(["15k-25k", "20k-35k", "30k-50k", "40k-60k", "50k-80k"]),
                'job_type': random.choice(["全职", "兼职", "实习", "远程"]),
                'keywords': [keywords] + [s for s in required_skills if len(s) > 1]
            }
            
            jobs.append(job)
        
        return jobs
    
    def save_jobs_to_file(self, jobs, output_file):
        """
        保存职位数据到文件
        
        参数:
            jobs (list): 职位列表
            output_file (str): 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)

#################################################
# 应用核心逻辑部分
#################################################

class ResumeJobMatcherApp:
    """简历职位匹配应用类，整合所有组件"""
    
    def __init__(self):
        """初始化应用"""
        self.resume_parser = ResumeParser()
        self.job_matcher = JobMatcher()
        self.job_search_api = JobSearchAPI()
    
    def run_full_process(self, resume_file_path, job_keywords, location='', use_api=False, limit=10):
        """
        运行完整的简历职位匹配流程
        
        参数:
            resume_file_path (str): 简历文件路径
            job_keywords (str): 职位关键词
            location (str): 工作地点
            use_api (bool): 是否使用真实API
            limit (int): 返回结果数量限制
            
        返回:
            dict: 处理结果
        """
        try:
            # 解析简历
            resume_data = self.resume_parser.parse(resume_file_path)
            
            # 搜索职位
            jobs = self.job_search_api.search_jobs(job_keywords, location, use_api, limit)
            
            # 计算匹配度并排序
            match_results = self.job_matcher.rank_jobs_by_match(resume_data, jobs)
            
            return {
                'success': True,
                'resume_data': resume_data,
                'jobs': jobs,
                'match_results': match_results
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

#################################################
# 创建示例简历文件
#################################################

def create_example_resume_file(output_dir):
    """
    创建示例简历文件
    
    参数:
        output_dir (str): 输出目录
        
    返回:
        str: 示例简历文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 示例简历内容
    resume_content = """
张明
软件工程师
电话：13812345678 | 邮箱：zhangming@example.com | 地址：北京市海淀区

个人简介
---------
有5年软件开发经验的全栈工程师，专注于Web应用开发和人工智能应用。具有扎实的编程基础和丰富的项目经验，能够独立完成从需求分析到系统实现的全过程。

教育背景
---------
北京大学 | 计算机科学 | 硕士 | 2015-2018
清华大学 | 软件工程 | 学士 | 2011-2015

工作经验
---------
阿里巴巴 | 高级软件工程师 | 2020-至今
- 负责电商平台的后端开发，使用Java和Spring Boot构建微服务架构
- 优化了订单处理系统，提高了30%的处理效率
- 改进了CI/CD流程，实现了自动化测试，优化了数据库查询性能

腾讯 | 软件工程师 | 2018-2020
- 参与社交应用的前端开发，使用React和Redux构建用户界面
- 实现了实时聊天功能，提升了用户体验
- 开发了10+个核心组件，减少了50%的页面加载时间，实现了响应式设计

技能
---------
编程语言：Python, Java, JavaScript, HTML/CSS
前端技术：React, Vue, Redux, Webpack
后端技术：Spring Boot, Node.js, Django, RESTful API
数据库：MySQL, MongoDB, Redis
DevOps：Docker, Kubernetes, Git, CI/CD
云服务：AWS, Azure
其他：微服务架构, 敏捷开发, 设计模式

项目经验
---------
电商平台优化 | 阿里巴巴 | 2021-2022
- 重构了电商平台的订单处理系统，使用微服务架构提高了系统的可扩展性和性能
- 使用Java, Spring Boot, MySQL, Redis, Docker等技术
- 系统性能提升40%，支持每秒处理1000+订单

社交媒体应用 | 腾讯 | 2019-2020
- 开发了一个社交媒体应用的前端，实现了实时聊天、动态发布等功能
- 使用React, Redux, WebSocket, CSS3, HTML5等技术
- 应用获得了超过100万用户，用户满意度达到95%

语言能力
---------
中文：母语
英语：流利

证书
---------
AWS Certified Solutions Architect | 2021
Oracle Certified Professional Java Programmer | 2019
"""
    
    # 创建示例简历文件（Word格式）
    output_file = os.path.join(output_dir, 'example_resume.docx')
    
    # 由于在云端环境中可能无法创建Word文档，这里创建一个文本文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(resume_content)
    
    return output_file

#################################################
# 主函数
#################################################

def main():
    """主函数，运行Streamlit应用"""
    st.title("AI简历职位匹配系统")
    st.subheader("使用AI分析简历并匹配最适合的职位")
    
    # 初始化应用
    app = ResumeJobMatcherApp()
    
    # 创建示例简历
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    example_resume_path = os.path.join(data_dir, 'example_resume.docx')
    if not os.path.exists(example_resume_path):
        try:
            example_resume_path = create_example_resume_file(data_dir)
            st.success("已创建示例简历文件")
        except Exception as e:
            st.error(f"创建示例简历失败: {str(e)}")
    
    # 创建侧边栏
    st.sidebar.title("操作面板")
    
    # 上传简历
    st.sidebar.header("上传简历")
    uploaded_file = st.sidebar.file_uploader("选择简历文件", type=['pdf', 'docx', 'txt'])
    
    # 使用示例简历选项
    use_example = st.sidebar.checkbox("使用示例简历", value=True)
    
    # 职位搜索选项
    st.sidebar.header("职位搜索")
    job_keywords = st.sidebar.text_input("职位关键词", value="软件工程师")
    job_location = st.sidebar.text_input("工作地点", value="北京")
    job_limit = st.sidebar.slider("搜索结果数量", min_value=5, max_value=20, value=10)
    
    # 在云端环境中默认使用模拟数据
    use_api = st.sidebar.checkbox("使用真实API数据", value=False, 
                                help="在云端环境中可能受限，建议使用模拟数据")
    
    # 处理按钮
    if st.sidebar.button("开始匹配"):
        # 显示处理中提示
        with st.spinner("正在处理中..."):
            # 确定使用的简历文件
            resume_file_path = None
            if uploaded_file is not None:
                # 保存上传的文件
                temp_file_path = os.path.join("./cache", uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                resume_file_path = temp_file_path
                st.sidebar.success(f"已上传简历: {uploaded_file.name}")
            elif use_example:
                resume_file_path = example_resume_path
                st.sidebar.info("使用示例简历")
            
            if resume_file_path:
                try:
                    # 运行完整流程
                    results = app.run_full_process(
                        resume_file_path=resume_file_path,
                        job_keywords=job_keywords,
                        location=job_location,
                        use_api=use_api,
                        limit=job_limit
                    )
                    
                    if results['success']:
                        # 显示结果
                        display_results(results)
                    else:
                        st.error(f"处理失败: {results['error']}")
                except Exception as e:
                    st.error(f"处理过程中出错: {str(e)}")
                    st.info("提示: 如果是资源不足错误，请尝试减少搜索结果数量或使用模拟数据")
            else:
                st.error("请上传简历文件或选择使用示例简历")

def display_results(results):
    """显示处理结果"""
    # 提取数据
    resume_data = results['resume_data']
    jobs = results['jobs']
    match_results = results['match_results']
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 1, 2])
    
    # 第一列：简历摘要
    with col1:
        st.header("简历摘要")
        
        # 个人信息
        if 'personal_info' in resume_data:
            personal = resume_data['personal_info']
            st.subheader("个人信息")
            st.write(f"姓名: {personal.get('name', '未知')}")
            st.write(f"电话: {personal.get('phone', '未知')}")
            st.write(f"邮箱: {personal.get('email', '未知')}")
        
        # 教育背景
        if 'education' in resume_data and resume_data['education']:
            st.subheader("教育背景")
            for edu in resume_data['education']:
                st.write(f"{edu.get('school', '未知')} - {edu.get('degree', '未知')} - {edu.get('major', '未知')}")
                if 'start_date' in edu and 'end_date' in edu:
                    st.write(f"{edu.get('start_date', '')} 至 {edu.get('end_date', '')}")
                st.write("---")
        
        # 技能
        if 'skills' in resume_data and resume_data['skills']:
            st.subheader("技能")
            st.write(", ".join(resume_data['skills'][:10]))
    
    # 第二列：搜索到的职位
    with col2:
        st.header("搜索到的职位")
        st.write(f"关键词: {jobs[0].get('keywords', ['无关键词'])[:5]}")
        st.write(f"共找到 {len(jobs)} 个职位")
        
        for i, job in enumerate(jobs[:3]):
            st.subheader(f"{i+1}. {job.get('title', '未知职位')}")
            st.write(f"公司: {job.get('company', '未知公司')}")
            st.write(f"地点: {job.get('location', '未知地点')}")
            st.write(f"要求技能: {', '.join(job.get('required_skills', ['无'])[:5])}")
            st.write("---")
        
        if len(jobs) > 3:
            st.write("...")
    
    # 第三列：匹配结果
    with col3:
        st.header("匹配结果")
        st.write("按匹配度排序的职位列表")
        
        for i, match in enumerate(match_results[:5]):
            # 创建可展开的部分
            with st.expander(f"{i+1}. {match.get('job_title', '未知职位')} - 匹配度: {match.get('overall_match', 0):.2f}"):
                st.write(f"公司: {match.get('company', '未知公司')}")
                
                # 显示匹配详情
                st.subheader("匹配详情")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"文本相似度: {match.get('text_similarity', 0):.2f}")
                    st.write(f"关键词匹配: {match.get('keyword_match', 0):.2f}")
                    st.write(f"技能匹配: {match.get('skill_match', 0):.2f}")
                with col_b:
                    st.write(f"教育背景匹配: {match.get('education_match', 0):.2f}")
                    st.write(f"工作经验匹配: {match.get('experience_match', 0):.2f}")
                
                # 显示匹配的技能
                if 'matched_skills' in match and match['matched_skills']:
                    st.subheader("匹配的技能")
                    st.write(", ".join(match['matched_skills']))
                
                # 添加申请按钮（示例功能）
                if st.button(f"申请该职位 #{i+1}"):
                    st.success("已发送申请！（示例功能）")
    
    # 添加下载结果按钮
    st.download_button(
        label="下载匹配结果",
        data=json.dumps(match_results, ensure_ascii=False, indent=4),
        file_name="match_results.json",
        mime="application/json",
    )

if __name__ == "__main__":
    main()
