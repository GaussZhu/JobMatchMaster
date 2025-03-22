"""
AI简历职位匹配系统 - 简历分析增强模块 (Streamlit Cloud兼容版)
使用NLP技术提高简历分析的准确性和职位匹配度，添加了Streamlit Cloud兼容性
"""
import os
import re
import json
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from collections import Counter

# 尝试导入nltk，如果失败则使用备用方案
try:
    import nltk
    # 确保NLTK资源可用
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    NLTK_AVAILABLE = True
except ImportError:
    print("NLTK库不可用，将使用备用方案")
    NLTK_AVAILABLE = False

class ResumeAnalyzer:
    """增强版简历分析器"""
    
    def __init__(self):
        """初始化简历分析器"""
        self.stopwords = set()
        # 添加中文停用词
        self.chinese_stopwords = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '这', '那', '有', '在', '中', '为'}
        self.stopwords.update(self.chinese_stopwords)
        
        # 如果nltk可用，添加英文停用词
        if NLTK_AVAILABLE:
            try:
                self.stopwords.update(set(nltk.corpus.stopwords.words('english')))
            except:
                pass
        
        # 技能关键词映射，用于标准化技能名称
        self.skill_mapping = {
            # 编程语言
            'python': 'Python',
            'java': 'Java',
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'typescript': 'TypeScript',
            'ts': 'TypeScript',
            'c++': 'C++',
            'c#': 'C#',
            'golang': 'Go',
            'go': 'Go',
            'rust': 'Rust',
            'php': 'PHP',
            'ruby': 'Ruby',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'objective-c': 'Objective-C',
            'scala': 'Scala',
            'r': 'R',
            'shell': 'Shell',
            'bash': 'Bash',
            
            # 前端技术
            'react': 'React',
            'reactjs': 'React',
            'vue': 'Vue.js',
            'vuejs': 'Vue.js',
            'angular': 'Angular',
            'angularjs': 'Angular',
            'jquery': 'jQuery',
            'html': 'HTML',
            'html5': 'HTML',
            'css': 'CSS',
            'css3': 'CSS',
            'sass': 'SASS',
            'less': 'LESS',
            'bootstrap': 'Bootstrap',
            'tailwind': 'Tailwind CSS',
            'webpack': 'Webpack',
            'vite': 'Vite',
            
            # 后端技术
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'express': 'Express',
            'django': 'Django',
            'flask': 'Flask',
            'spring': 'Spring',
            'spring boot': 'Spring Boot',
            'springboot': 'Spring Boot',
            'laravel': 'Laravel',
            'asp.net': 'ASP.NET',
            'aspnet': 'ASP.NET',
            
            # 数据库
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'postgres': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'mongo': 'MongoDB',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'oracle': 'Oracle',
            'sql server': 'SQL Server',
            'sqlserver': 'SQL Server',
            'sqlite': 'SQLite',
            
            # 云服务和DevOps
            'aws': 'AWS',
            'azure': 'Azure',
            'gcp': 'GCP',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'jenkins': 'Jenkins',
            'git': 'Git',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'terraform': 'Terraform',
            'ansible': 'Ansible',
            
            # 数据科学和AI
            'machine learning': '机器学习',
            'ml': '机器学习',
            'deep learning': '深度学习',
            'dl': '深度学习',
            'artificial intelligence': '人工智能',
            'ai': '人工智能',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'keras': 'Keras',
            'scikit-learn': 'Scikit-learn',
            'sklearn': 'Scikit-learn',
            'pandas': 'Pandas',
            'numpy': 'NumPy',
            'scipy': 'SciPy',
            'matplotlib': 'Matplotlib',
            
            # 移动开发
            'android': 'Android',
            'ios': 'iOS',
            'react native': 'React Native',
            'reactnative': 'React Native',
            'flutter': 'Flutter',
            'xamarin': 'Xamarin',
            
            # 其他技术
            'restful': 'RESTful API',
            'rest': 'RESTful API',
            'graphql': 'GraphQL',
            'websocket': 'WebSocket',
            'oauth': 'OAuth',
            'jwt': 'JWT',
            'microservices': '微服务',
            'serverless': 'Serverless',
            'ci/cd': 'CI/CD',
            'cicd': 'CI/CD',
        }
        
        # 技能类别映射
        self.skill_categories = {
            'programming_languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 
                'PHP', 'Ruby', 'Swift', 'Kotlin', 'Objective-C', 'Scala', 'R', 'Shell', 'Bash'
            ],
            'frontend': [
                'React', 'Vue.js', 'Angular', 'jQuery', 'HTML', 'CSS', 'SASS', 'LESS', 
                'Bootstrap', 'Tailwind CSS', 'Webpack', 'Vite'
            ],
            'backend': [
                'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Spring Boot', 
                'Laravel', 'ASP.NET'
            ],
            'database': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 
                'SQL Server', 'SQLite'
            ],
            'devops': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 
                'GitLab', 'Terraform', 'Ansible', 'CI/CD'
            ],
            'data_science': [
                '机器学习', '深度学习', '人工智能', 'TensorFlow', 'PyTorch', 'Keras', 
                'Scikit-learn', 'Pandas', 'NumPy', 'SciPy', 'Matplotlib'
            ],
            'mobile': [
                'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin'
            ],
            'other': [
                'RESTful API', 'GraphQL', 'WebSocket', 'OAuth', 'JWT', '微服务', 'Serverless'
            ]
        }
        
        # 职业方向映射
        self.career_directions = {
            'frontend_developer': {
                'name': '前端开发工程师',
                'skills': ['JavaScript', 'HTML', 'CSS', 'React', 'Vue.js', 'Angular', 'TypeScript', 'Webpack']
            },
            'backend_developer': {
                'name': '后端开发工程师',
                'skills': ['Java', 'Python', 'Go', 'C#', 'Node.js', 'Spring', 'Django', 'Express']
            },
            'fullstack_developer': {
                'name': '全栈开发工程师',
                'skills': ['JavaScript', 'TypeScript', 'Python', 'Java', 'React', 'Vue.js', 'Node.js', 'Express', 'Django', 'Spring']
            },
            'data_scientist': {
                'name': '数据科学家',
                'skills': ['Python', 'R', '机器学习', '深度学习', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'SciPy']
            },
            'data_engineer': {
                'name': '数据工程师',
                'skills': ['Python', 'Spark', 'Hadoop', 'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'ETL']
            },
            'devops_engineer': {
                'name': 'DevOps工程师',
                'skills': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Jenkins', 'Terraform', 'Ansible', 'CI/CD']
            },
            'mobile_developer': {
                'name': '移动开发工程师',
                'skills': ['Android', 'iOS', 'Swift', 'Kotlin', 'React Native', 'Flutter']
            },
            'ai_engineer': {
                'name': 'AI工程师',
                'skills': ['Python', '机器学习', '深度学习', '人工智能', 'TensorFlow', 'PyTorch', 'NLP', '计算机视觉']
            },
            'security_engineer': {
                'name': '安全工程师',
                'skills': ['网络安全', '渗透测试', '安全审计', '密码学', 'OWASP', '风险评估']
            },
            'product_manager': {
                'name': '产品经理',
                'skills': ['产品设计', '用户研究', '需求分析', '产品规划', '市场分析', '用户体验']
            },
            'project_manager': {
                'name': '项目经理',
                'skills': ['项目管理', '敏捷开发', 'Scrum', 'Kanban', '风险管理', '资源规划']
            }
        }
        
        # 教育水平映射
        self.education_levels = {
            '博士': 5,
            '硕士': 4,
            '本科': 3,
            '大专': 2,
            '高中': 1,
            'phd': 5,
            'ph.d': 5,
            'ph.d.': 5,
            'doctor': 5,
            'doctoral': 5,
            'master': 4,
            'ms': 4,
            'msc': 4,
            'm.s.': 4,
            'm.sc.': 4,
            'bachelor': 3,
            'bs': 3,
            'bsc': 3,
            'b.s.': 3,
            'b.sc.': 3,
            'undergraduate': 3,
            'associate': 2,
            'college': 2,
            'diploma': 2,
            'high school': 1,
            'secondary': 1
        }
        
        # 知名大学列表
        self.top_universities = [
            '清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学', '南京大学', 
            '中国科学技术大学', '哈尔滨工业大学', '西安交通大学', '武汉大学',
            'harvard', 'stanford', 'mit', 'cambridge', 'oxford', 'caltech', 'princeton', 
            'yale', 'columbia', 'chicago', 'berkeley', 'ucla', 'michigan', 'toronto', 
            'eth zurich', 'imperial college', 'ucl', 'tsinghua', 'peking', 'tokyo'
        ]
    
    def tokenize_text(self, text: str) -> List[str]:
        """分词函数，支持中英文"""
        if not text:
            return []
        
        # 如果nltk可用，使用nltk分词
        if NLTK_AVAILABLE:
            try:
                # 对英文使用nltk分词
                words = nltk.word_tokenize(text)
                return [w.lower() for w in words if w.isalnum() and w.lower() not in self.stopwords]
            except:
                pass
        
        # 备用分词方案
        # 简单的按空格和标点符号分词
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w.lower() for w in words if w.lower() not in self.stopwords]
    
    def extract_skills(self, text: str) -> List[str]:
        """从文本中提取技能"""
        if not text:
            return []
        
        # 分词
        tokens = self.tokenize_text(text)
        
        # 提取技能
        skills = []
        for token in tokens:
            if token in self.skill_mapping:
                skills.append(self.skill_mapping[token])
        
        # 使用正则表达式匹配多词技能
        for skill_key, skill_value in self.skill_mapping.items():
            if ' ' in skill_key and skill_key.lower() in text.lower():
                skills.append(skill_value)
        
        # 去重
        return list(set(skills))
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, int]:
        """对技能进行分类"""
        categories = {}
        for category, category_skills in self.skill_categories.items():
            count = sum(1 for skill in skills if skill in category_skills)
            if count > 0:
                categories[category] = count
        return categories
    
    def analyze_skills(self, skills: List[str]) -> Dict[str, Any]:
        """分析技能"""
        if not skills:
            return {
                'skill_count': 0,
                'skill_level': '初级',
                'skill_categories': {},
                'primary_skills': []
            }
        
        # 技能数量
        skill_count = len(skills)
        
        # 技能水平
        skill_level = '初级'
        if skill_count >= 15:
            skill_level = '高级'
        elif skill_count >= 8:
            skill_level = '中级'
        
        # 技能分类
        skill_categories = self.categorize_skills(skills)
        
        # 主要技能（按类别排序）
        primary_skills = []
        for category, _ in sorted(skill_categories.items(), key=lambda x: x[1], reverse=True):
            category_skills = [skill for skill in skills if skill in self.skill_categories[category]]
            primary_skills.extend(category_skills)
        
        return {
            'skill_count': skill_count,
            'skill_level': skill_level,
            'skill_categories': skill_categories,
            'primary_skills': primary_skills
        }
    
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取教育经历"""
        if not text:
            return []
        
        education = []
        
        # 提取学校名称
        school_pattern = r'([\u4e00-\u9fa5a-zA-Z]+大学|[\u4e00-\u9fa5a-zA-Z]+学院|university\s+of\s+[\w\s]+|[\w\s]+\s+university|[\w\s]+\s+college|[\w\s]+\s+institute\s+of\s+[\w\s]+)'
        schools = re.findall(school_pattern, text, re.IGNORECASE)
        
        # 提取学位
        degree_pattern = r'(博士|硕士|本科|大专|高中|phd|ph\.d|doctor|doctoral|master|ms|msc|m\.s\.|m\.sc\.|bachelor|bs|bsc|b\.s\.|b\.sc\.|undergraduate|associate|college|diploma|high\s+school|secondary)'
        degrees = re.findall(degree_pattern, text, re.IGNORECASE)
        
        # 提取专业
        major_pattern = r'(计算机|软件|信息|通信|电子|自动化|人工智能|数据|网络|机械|土木|建筑|电气|能源|材料|化学|物理|数学|统计|金融|经济|管理|市场|人力资源|法律|医学|生物|环境|食品|农业|艺术|设计|音乐|文学|历史|哲学|心理|教育|体育|computer|software|information|communication|electronic|automation|artificial\s+intelligence|data|network|mechanical|civil|architecture|electrical|energy|material|chemical|physics|mathematics|statistics|finance|economics|management|marketing|human\s+resource|law|medicine|biology|environment|food|agriculture|art|design|music|literature|history|philosophy|psychology|education|sports)'
        majors = re.findall(major_pattern, text, re.IGNORECASE)
        
        # 提取日期
        date_pattern = r'(\d{4}[-/年]\d{1,2}[-/月]|\d{4}[-/年]|\d{4})'
        dates = re.findall(date_pattern, text)
        
        # 组合结果
        for i in range(min(len(schools), len(degrees) if degrees else 1)):
            edu = {
                'school': schools[i] if i < len(schools) else '',
                'degree': degrees[i] if i < len(degrees) else '',
                'major': majors[i] if i < len(majors) else '',
                'start_date': dates[i*2] if i*2 < len(dates) else '',
                'end_date': dates[i*2+1] if i*2+1 < len(dates) else ''
            }
            education.append(edu)
        
        return education
    
    def analyze_education(self, education: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析教育经历"""
        if not education:
            return {
                'education_level': '未知',
                'is_cs_related': False,
                'top_university': False
            }
        
        # 获取最高学历
        highest_level = 0
        highest_degree = '未知'
        for edu in education:
            degree = edu.get('degree', '').lower()
            for level_name, level_value in self.education_levels.items():
                if level_name in degree:
                    if level_value > highest_level:
                        highest_level = level_value
                        if level_value == 5:
                            highest_degree = '博士'
                        elif level_value == 4:
                            highest_degree = '硕士'
                        elif level_value == 3:
                            highest_degree = '本科'
                        elif level_value == 2:
                            highest_degree = '大专'
                        else:
                            highest_degree = '高中'
        
        # 判断是否计算机相关专业
        cs_related_keywords = ['计算机', '软件', '信息', '通信', '电子', '自动化', '人工智能', '数据', '网络',
                              'computer', 'software', 'information', 'communication', 'electronic', 
                              'automation', 'artificial intelligence', 'data', 'network']
        is_cs_related = False
        for edu in education:
            major = edu.get('major', '').lower()
            if any(keyword in major for keyword in cs_related_keywords):
                is_cs_related = True
                break
        
        # 判断是否知名大学
        top_university = False
        for edu in education:
            school = edu.get('school', '').lower()
            if any(univ.lower() in school for univ in self.top_universities):
                top_university = True
                break
        
        return {
            'education_level': highest_degree,
            'is_cs_related': is_cs_related,
            'top_university': top_university
        }
    
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取工作经验"""
        if not text:
            return []
        
        experience = []
        
        # 提取公司名称
        company_pattern = r'([\u4e00-\u9fa5a-zA-Z]+公司|[\u4e00-\u9fa5a-zA-Z]+集团|[\u4e00-\u9fa5a-zA-Z]+有限|[\w\s]+\s+inc|[\w\s]+\s+corporation|[\w\s]+\s+ltd|[\w\s]+\s+limited|[\w\s]+\s+co)'
        companies = re.findall(company_pattern, text, re.IGNORECASE)
        
        # 提取职位
        position_pattern = r'(工程师|开发|架构|设计|测试|运维|产品|项目|经理|主管|总监|专员|助理|顾问|分析师|工程师|研究员|实习|engineer|developer|architect|designer|tester|operations|product|project|manager|supervisor|director|specialist|assistant|consultant|analyst|engineer|researcher|intern)'
        positions = re.findall(position_pattern, text, re.IGNORECASE)
        
        # 提取日期
        date_pattern = r'(\d{4}[-/年]\d{1,2}[-/月]|\d{4}[-/年]|\d{4})'
        dates = re.findall(date_pattern, text)
        
        # 组合结果
        for i in range(min(len(companies), len(positions) if positions else 1)):
            exp = {
                'company': companies[i] if i < len(companies) else '',
                'position': positions[i] if i < len(positions) else '',
                'start_date': dates[i*2] if i*2 < len(dates) else '',
                'end_date': dates[i*2+1] if i*2+1 < len(dates) else ''
            }
            experience.append(exp)
        
        return experience
    
    def analyze_experience(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析工作经验"""
        if not experience:
            return {
                'years': 0,
                'company_tier': '未知',
                'position_level': '初级',
                'has_management_experience': False
            }
        
        # 计算工作年限
        years = 0
        for exp in experience:
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            if start_date:
                start_year = int(re.search(r'\d{4}', start_date).group(0))
                end_year = 0
                
                if end_date:
                    end_match = re.search(r'\d{4}', end_date)
                    if end_match:
                        end_year = int(end_match.group(0))
                else:
                    # 如果没有结束日期，假设工作至今
                    import datetime
                    end_year = datetime.datetime.now().year
                
                if end_year > start_year:
                    years += (end_year - start_year)
        
        # 判断公司层级
        top_companies = ['阿里', '腾讯', '百度', '华为', '字节', '美团', '京东', '滴滴', '小米', '网易',
                        'alibaba', 'tencent', 'baidu', 'huawei', 'bytedance', 'meituan', 'jd', 'didi', 'xiaomi', 'netease',
                        'google', 'microsoft', 'amazon', 'apple', 'facebook', 'meta', 'netflix', 'tesla', 'uber', 'airbnb']
        
        company_tier = '普通'
        for exp in experience:
            company = exp.get('company', '').lower()
            if any(top_company in company for top_company in top_companies):
                company_tier = '知名'
                break
        
        # 判断职位级别
        position_level = '初级'
        management_keywords = ['经理', '主管', '总监', '负责人', '管理', 'manager', 'supervisor', 'director', 'lead', 'management']
        senior_keywords = ['高级', '资深', '专家', 'senior', 'expert', 'staff', 'principal']
        
        has_management_experience = False
        for exp in experience:
            position = exp.get('position', '').lower()
            
            if any(keyword in position for keyword in management_keywords):
                position_level = '管理'
                has_management_experience = True
                break
            elif any(keyword in position for keyword in senior_keywords):
                position_level = '高级'
        
        # 如果工作年限大于5年但职位级别仍为初级，则调整为中级
        if years >= 5 and position_level == '初级':
            position_level = '中级'
        # 如果工作年限大于8年但职位级别为中级，则调整为高级
        elif years >= 8 and position_level == '中级':
            position_level = '高级'
        
        return {
            'years': years,
            'company_tier': company_tier,
            'position_level': position_level,
            'has_management_experience': has_management_experience
        }
    
    def determine_career_direction(self, skills: List[str]) -> Dict[str, Any]:
        """确定职业方向"""
        if not skills:
            return {
                'primary_direction': '未知',
                'primary_score': 0,
                'secondary_direction': '未知',
                'secondary_score': 0,
                'direction_confidence': 'low'
            }
        
        # 计算每个职业方向的匹配分数
        direction_scores = {}
        for direction_key, direction_info in self.career_directions.items():
            direction_skills = direction_info['skills']
            matched_skills = [skill for skill in skills if skill in direction_skills]
            score = len(matched_skills) / len(direction_skills) * 100 if direction_skills else 0
            direction_scores[direction_key] = score
        
        # 按分数排序
        sorted_directions = sorted(direction_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 获取主要和次要方向
        primary_direction = self.career_directions[sorted_directions[0][0]]['name'] if sorted_directions else '未知'
        primary_score = sorted_directions[0][1] if sorted_directions else 0
        
        secondary_direction = self.career_directions[sorted_directions[1][0]]['name'] if len(sorted_directions) > 1 else '未知'
        secondary_score = sorted_directions[1][1] if len(sorted_directions) > 1 else 0
        
        # 确定方向确定性
        direction_confidence = 'low'
        if primary_score >= 70:
            direction_confidence = 'high'
        elif primary_score >= 40:
            direction_confidence = 'medium'
        
        return {
            'primary_direction': primary_direction,
            'primary_score': primary_score,
            'secondary_direction': secondary_direction,
            'secondary_score': secondary_score,
            'direction_confidence': direction_confidence
        }
    
    def calculate_overall_score(self, skills_analysis: Dict[str, Any], education_analysis: Dict[str, Any], experience_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """计算综合评分"""
        # 技能评分 (40%)
        skill_score = 0
        skill_count = skills_analysis.get('skill_count', 0)
        if skill_count >= 15:
            skill_score = 100
        elif skill_count >= 10:
            skill_score = 80
        elif skill_count >= 5:
            skill_score = 60
        elif skill_count > 0:
            skill_score = 40
        
        # 教育评分 (30%)
        education_score = 0
        education_level = education_analysis.get('education_level', '未知')
        is_cs_related = education_analysis.get('is_cs_related', False)
        top_university = education_analysis.get('top_university', False)
        
        if education_level == '博士':
            education_score = 100
        elif education_level == '硕士':
            education_score = 80
        elif education_level == '本科':
            education_score = 60
        elif education_level == '大专':
            education_score = 40
        else:
            education_score = 20
        
        if is_cs_related:
            education_score += 10
        if top_university:
            education_score += 10
        
        education_score = min(100, education_score)
        
        # 经验评分 (30%)
        experience_score = 0
        years = experience_analysis.get('years', 0)
        company_tier = experience_analysis.get('company_tier', '未知')
        position_level = experience_analysis.get('position_level', '初级')
        
        if years >= 10:
            experience_score = 100
        elif years >= 5:
            experience_score = 80
        elif years >= 3:
            experience_score = 60
        elif years >= 1:
            experience_score = 40
        else:
            experience_score = 20
        
        if company_tier == '知名':
            experience_score += 10
        
        if position_level == '管理':
            experience_score += 20
        elif position_level == '高级':
            experience_score += 10
        
        experience_score = min(100, experience_score)
        
        # 综合评分
        overall_score = int(skill_score * 0.4 + education_score * 0.3 + experience_score * 0.3)
        
        # 级别
        level = '初级'
        if overall_score >= 85:
            level = '专家'
        elif overall_score >= 70:
            level = '高级'
        elif overall_score >= 50:
            level = '中级'
        
        return {
            'overall_score': overall_score,
            'level': level,
            'component_scores': {
                'skills': skill_score,
                'education': education_score,
                'experience': experience_score
            }
        }
    
    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析简历"""
        # 提取技能
        skills = resume_data.get('skills', [])
        
        # 提取教育经历
        education = resume_data.get('education', [])
        
        # 提取工作经验
        experience = resume_data.get('experience', [])
        
        # 分析技能
        skills_analysis = self.analyze_skills(skills)
        
        # 分析教育经历
        education_analysis = self.analyze_education(education)
        
        # 分析工作经验
        experience_analysis = self.analyze_experience(experience)
        
        # 确定职业方向
        career_direction = self.determine_career_direction(skills)
        
        # 计算综合评分
        overall_score = self.calculate_overall_score(skills_analysis, education_analysis, experience_analysis)
        
        # 个人总结
        personal_summary = {
            'name': resume_data.get('personal_info', {}).get('name', '未知'),
            'years_of_experience': experience_analysis.get('years', 0),
            'highest_education': education_analysis.get('education_level', '未知'),
            'skill_level': skills_analysis.get('skill_level', '初级'),
            'career_direction': career_direction.get('primary_direction', '未知')
        }
        
        return {
            'personal_summary': personal_summary,
            'skills_analysis': skills_analysis,
            'education_analysis': education_analysis,
            'experience_analysis': experience_analysis,
            'career_direction': career_direction,
            'overall_score': overall_score
        }

def parse_resume_enhanced(file_path: str) -> Dict[str, Any]:
    """增强版简历解析函数"""
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return {
            'personal_info': {'name': '未知', 'summary': '文件不存在'},
            'education': [],
            'experience': [],
            'skills': []
        }
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建简历分析器
    analyzer = ResumeAnalyzer()
    
    # 提取个人信息
    name_pattern = r'^([\u4e00-\u9fa5a-zA-Z]+)'
    name_match = re.search(name_pattern, content)
    name = name_match.group(1) if name_match else '未知'
    
    # 提取联系方式
    phone_pattern = r'电话[：:]\s*(\d{11}|\d{3}[-\s]\d{4}[-\s]\d{4})'
    phone_match = re.search(phone_pattern, content)
    phone = phone_match.group(1) if phone_match else '未知'
    
    email_pattern = r'邮箱[：:]\s*([\w.-]+@[\w.-]+\.\w+)'
    email_match = re.search(email_pattern, content)
    email = email_match.group(1) if email_match else '未知'
    
    # 提取地点
    location_pattern = r'([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区|[\u4e00-\u9fa5]+市|[\u4e00-\u9fa5]+省[\u4e00-\u9fa5]+市)'
    location_match = re.search(location_pattern, content)
    location = location_match.group(1) if location_match else '未知'
    
    # 提取个人简介
    summary_pattern = r'个人简介[：:]\s*(.*?)(?=\n\n|\n教育|\n工作|\n技能|$)'
    summary_match = re.search(summary_pattern, content, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ''
    
    # 提取教育经历
    education_pattern = r'教育经[历验].*?(?=\n\n|\n工作|\n技能|$)'
    education_match = re.search(education_pattern, content, re.DOTALL)
    education_text = education_match.group(0) if education_match else ''
    education = analyzer.extract_education(education_text)
    
    # 提取工作经验
    experience_pattern = r'工作经[历验].*?(?=\n\n|\n教育|\n技能|$)'
    experience_match = re.search(experience_pattern, content, re.DOTALL)
    experience_text = experience_match.group(0) if experience_match else ''
    experience = analyzer.extract_experience(experience_text)
    
    # 提取技能
    skills_pattern = r'技能.*?(?=\n\n|\n教育|\n工作|$)'
    skills_match = re.search(skills_pattern, content, re.DOTALL)
    skills_text = skills_match.group(0) if skills_match else ''
    skills = analyzer.extract_skills(content)
    
    # 构建简历数据
    resume_data = {
        'personal_info': {
            'name': name,
            'phone': phone,
            'email': email,
            'location': location,
            'summary': summary
        },
        'education': education,
        'experience': experience,
        'skills': skills
    }
    
    return resume_data

def match_resume_to_jobs_enhanced(resume_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """增强版简历与职位匹配函数"""
    if not resume_data or not jobs:
        return []
    
    # 创建简历分析器
    analyzer = ResumeAnalyzer()
    
    # 分析简历
    resume_analysis = analyzer.analyze_resume(resume_data)
    
    # 获取简历技能
    resume_skills = set(resume_data.get('skills', []))
    
    # 获取简历教育水平
    education_analysis = resume_analysis.get('education_analysis', {})
    resume_education_level = education_analysis.get('education_level', '未知')
    education_level_map = {'博士': 5, '硕士': 4, '本科': 3, '大专': 2, '高中': 1, '未知': 0}
    resume_education_value = education_level_map.get(resume_education_level, 0)
    
    # 获取简历工作经验
    experience_analysis = resume_analysis.get('experience_analysis', {})
    resume_experience_years = experience_analysis.get('years', 0)
    
    # 获取简历职业方向
    career_direction = resume_analysis.get('career_direction', {})
    resume_primary_direction = career_direction.get('primary_direction', '未知')
    
    # 匹配结果
    match_results = []
    
    for job in jobs:
        # 获取职位技能
        job_skills = set(job.get('required_skills', []))
        
        # 计算技能匹配度
        if job_skills:
            matched_skills = resume_skills.intersection(job_skills)
            skill_match = len(matched_skills) / len(job_skills) * 100
        else:
            matched_skills = set()
            skill_match = 0
        
        # 计算教育匹配度
        job_education = job.get('education_requirement', '未知')
        job_education_value = 0
        for level, value in education_level_map.items():
            if level in job_education:
                job_education_value = value
                break
        
        if job_education_value > 0:
            if resume_education_value >= job_education_value:
                education_match = 100
            else:
                education_match = (resume_education_value / job_education_value) * 100
        else:
            education_match = 100  # 如果职位没有明确教育要求，则默认匹配
        
        # 计算经验匹配度
        job_experience = job.get('experience_requirement', 0)
        if isinstance(job_experience, str):
            try:
                job_experience = int(re.search(r'\d+', job_experience).group(0))
            except:
                job_experience = 0
        
        if job_experience > 0:
            if resume_experience_years >= job_experience:
                experience_match = 100
            else:
                experience_match = (resume_experience_years / job_experience) * 100
        else:
            experience_match = 100  # 如果职位没有明确经验要求，则默认匹配
        
        # 计算方向匹配度
        job_title = job.get('title', '').lower()
        direction_match = 0
        
        for direction_key, direction_info in analyzer.career_directions.items():
            direction_name = direction_info['name']
            if direction_name == resume_primary_direction:
                direction_keywords = [keyword.lower() for keyword in direction_info['skills']]
                if any(keyword in job_title for keyword in direction_keywords):
                    direction_match = 100
                    break
        
        if direction_match == 0:
            # 如果没有直接匹配，使用技能相似度作为方向匹配度
            direction_match = skill_match
        
        # 计算总匹配度
        match_score = int(skill_match * 0.4 + education_match * 0.2 + experience_match * 0.2 + direction_match * 0.2)
        
        # 生成改进建议
        improvement_suggestions = []
        
        if skill_match < 70:
            missing_skills = job_skills - resume_skills
            if missing_skills:
                suggestion = f"建议学习以下技能: {', '.join(list(missing_skills)[:3])}"
                improvement_suggestions.append(suggestion)
        
        if education_match < 70:
            suggestion = f"职位要求{job_education}学历，而您的学历是{resume_education_level}"
            improvement_suggestions.append(suggestion)
        
        if experience_match < 70:
            suggestion = f"职位要求{job_experience}年经验，而您有{resume_experience_years}年经验"
            improvement_suggestions.append(suggestion)
        
        # 添加匹配结果
        match_result = {
            'job_id': job.get('id', ''),
            'match_score': match_score,
            'skill_match': int(skill_match),
            'education_match': int(education_match),
            'experience_match': int(experience_match),
            'direction_match': int(direction_match),
            'matched_skills': list(matched_skills),
            'improvement_suggestions': improvement_suggestions
        }
        
        match_results.append(match_result)
    
    # 按匹配度排序
    match_results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return match_results

# 导出函数
__all__ = ['ResumeAnalyzer', 'parse_resume_enhanced', 'match_resume_to_jobs_enhanced']
