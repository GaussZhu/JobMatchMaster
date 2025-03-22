"""
AI简历职位匹配系统 - 简历分析增强模块
使用NLP技术提高简历分析的准确性和职位匹配度
"""
import os
import re
import json
import nltk
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from collections import Counter

# 确保NLTK资源可用
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeAnalyzer:
    """增强版简历分析器"""
    
    def __init__(self):
        """初始化简历分析器"""
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        # 添加中文停用词
        self.chinese_stopwords = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '这', '那', '有', '在', '中', '为'}
        self.stopwords.update(self.chinese_stopwords)
        
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
            
            # 其他技能
            'restful': 'RESTful API',
            'rest': 'RESTful API',
            'graphql': 'GraphQL',
            'microservices': '微服务',
            'agile': '敏捷开发',
            'scrum': 'Scrum',
            'kanban': 'Kanban',
            'ci/cd': 'CI/CD',
            'cicd': 'CI/CD',
            'testing': '自动化测试',
            'unit testing': '单元测试',
            'ui/ux': 'UI/UX设计',
            'uiux': 'UI/UX设计',
        }
        
        # 学历等级映射
        self.education_levels = {
            '博士': 5,
            'phd': 5,
            'ph.d': 5,
            'doctor': 5,
            '硕士': 4,
            'master': 4,
            'msc': 4,
            'mba': 4,
            '本科': 3,
            'bachelor': 3,
            'bs': 3,
            'ba': 3,
            'bsc': 3,
            '大专': 2,
            'associate': 2,
            'college': 2,
            'diploma': 2,
            '高中': 1,
            'high school': 1,
            'secondary': 1,
        }
        
        # 职位类型映射
        self.job_categories = {
            '前端': ['前端', '前端开发', 'web前端', 'frontend', 'front-end', 'html', 'css', 'javascript', 'react', 'vue', 'angular'],
            '后端': ['后端', '后端开发', 'backend', 'back-end', 'java', 'python', 'c++', 'go', 'php', 'node.js', 'spring', 'django'],
            '全栈': ['全栈', '全栈开发', 'fullstack', 'full-stack', 'full stack'],
            '移动端': ['移动端', '移动开发', 'mobile', 'android', 'ios', 'flutter', 'react native'],
            '数据': ['数据', '数据分析', '数据工程', 'data', 'data engineer', 'data analyst', 'data scientist'],
            '人工智能': ['人工智能', 'ai', '机器学习', 'ml', '深度学习', 'dl', 'artificial intelligence', 'machine learning', 'deep learning'],
            '运维': ['运维', 'devops', 'sre', '系统工程师', 'system engineer', 'operations'],
            '测试': ['测试', 'qa', '质量', 'quality', 'test', 'testing'],
            '产品': ['产品', '产品经理', 'product', 'product manager', 'pm'],
            '设计': ['设计', 'ui', 'ux', '交互设计', 'design', 'designer'],
            '项目管理': ['项目管理', '项目经理', 'project', 'project manager', 'pmo'],
        }
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件，提取关键信息
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            Dict[str, Any]: 解析后的简历数据
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"简历文件不存在: {file_path}")
        
        # 根据文件扩展名选择解析方法
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 这里简化处理，实际应用中应该使用专业的简历解析库
        # 如pyresparser, resume-parser等
        if file_ext == '.pdf':
            return self._parse_pdf_resume(file_path)
        elif file_ext == '.docx':
            return self._parse_docx_resume(file_path)
        elif file_ext == '.txt':
            return self._parse_txt_resume(file_path)
        elif file_ext == '.json':
            return self._parse_json_resume(file_path)
        else:
            # 对于不支持的格式，返回模拟数据
            return self._generate_mock_resume_data()
    
    def _parse_pdf_resume(self, file_path: str) -> Dict[str, Any]:
        """解析PDF格式简历"""
        # 实际应用中应使用pdfminer, PyPDF2等库
        # 这里简化处理，返回模拟数据
        return self._generate_mock_resume_data()
    
    def _parse_docx_resume(self, file_path: str) -> Dict[str, Any]:
        """解析DOCX格式简历"""
        # 实际应用中应使用python-docx等库
        # 这里简化处理，返回模拟数据
        return self._generate_mock_resume_data()
    
    def _parse_txt_resume(self, file_path: str) -> Dict[str, Any]:
        """解析纯文本格式简历"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的文本解析逻辑
            lines = content.split('\n')
            
            # 提取个人信息
            name = lines[0].strip() if lines else "未知"
            email = self._extract_email(content)
            phone = self._extract_phone(content)
            
            # 提取教育经历
            education = self._extract_education_from_text(content)
            
            # 提取工作经历
            work_experience = self._extract_work_experience_from_text(content)
            
            # 提取技能
            skills = self._extract_skills_from_text(content)
            
            # 构建简历数据
            resume_data = {
                'personal_info': {
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'location': self._extract_location_from_text(content),
                    'summary': self._extract_summary_from_text(content)
                },
                'education': education,
                'work_experience': work_experience,
                'skills': skills
            }
            
            return resume_data
            
        except Exception as e:
            print(f"解析文本简历时出错: {e}")
            return self._generate_mock_resume_data()
    
    def _parse_json_resume(self, file_path: str) -> Dict[str, Any]:
        """解析JSON格式简历"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_data = json.load(f)
            
            # 验证JSON结构
            required_keys = ['personal_info', 'education', 'work_experience', 'skills']
            for key in required_keys:
                if key not in resume_data:
                    print(f"JSON简历缺少必要字段: {key}")
                    return self._generate_mock_resume_data()
            
            return resume_data
            
        except Exception as e:
            print(f"解析JSON简历时出错: {e}")
            return self._generate_mock_resume_data()
    
    def _generate_mock_resume_data(self) -> Dict[str, Any]:
        """生成模拟简历数据"""
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
                },
                {
                    'school': '清华大学',
                    'degree': '学士',
                    'major': '软件工程',
                    'start_date': '2011-09',
                    'end_date': '2015-07',
                }
            ],
            'work_experience': [
                {
                    'company': '阿里巴巴',
                    'position': '高级软件工程师',
                    'start_date': '2020-06',
                    'end_date': '至今',
                    'description': '负责电商平台的后端开发，使用Java和Spring Boot构建微服务架构。'
                },
                {
                    'company': '腾讯',
                    'position': '软件工程师',
                    'start_date': '2018-07',
                    'end_date': '2020-05',
                    'description': '参与社交应用的前端开发，使用React和Redux构建用户界面。'
                }
            ],
            'skills': [
                'Python', 'Java', 'JavaScript', 'React', 'Node.js', 
                'Spring Boot', 'MySQL', 'MongoDB', 'Docker', 'Git'
            ]
        }
    
    def _extract_email(self, text: str) -> str:
        """从文本中提取邮箱地址"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "未知"
    
    def _extract_phone(self, text: str) -> str:
        """从文本中提取电话号码"""
        # 中国手机号码模式
        phone_pattern = r'1[3-9]\d{9}'
        match = re.search(phone_pattern, text)
        if match:
            return match.group(0)
        
        # 一般电话号码模式
        phone_pattern = r'\d{3,4}[-\s]?\d{7,8}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else "未知"
    
    def _extract_location_from_text(self, text: str) -> str:
        """从文本中提取位置信息"""
        # 常见城市列表
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '苏州', '天津', '重庆']
        for city in cities:
            if city in text:
                # 尝试提取更详细的地址
                city_idx = text.find(city)
                end_idx = text.find('\n', city_idx)
                if end_idx > city_idx and end_idx - city_idx < 50:
                    return text[city_idx:end_idx].strip()
                return city
        
        return "未知"
    
    def _extract_summary_from_text(self, text: str) -> str:
        """从文本中提取个人总结"""
        # 查找常见的总结标识
        summary_indicators = ['个人简介', '自我介绍', '个人概况', '职业概述', '个人总结']
        for indicator in summary_indicators:
            if indicator in text:
                start_idx = text.find(indicator) + len(indicator)
                end_idx = text.find('\n\n', start_idx)
                if end_idx > start_idx:
                    return text[start_idx:end_idx].strip()
        
        # 如果没有找到明确标识，尝试使用前100个字符
        lines = text.split('\n')
        if len(lines) > 2:  # 跳过姓名和联系方式
            for line in lines[2:10]:
                if len(line.strip()) > 20:  # 较长的行可能是总结
                    return line.strip()
        
        return "未提供个人总结"
    
    def _extract_education_from_text(self, text: str) -> List[Dict[str, str]]:
        """从文本中提取教育经历"""
        education = []
        
        # 查找教育经历部分
        edu_indicators = ['教育经历', '教育背景', '学历', '教育']
        edu_section = ""
        for indicator in edu_indicators:
            if indicator in text:
                start_idx = text.find(indicator)
                # 找到下一个主要部分
                next_sections = ['工作经历', '工作经验', '项目经历', '技能', '技术栈']
                end_idx = len(text)
                for section in next_sections:
                    section_idx = text.find(section, start_idx)
                    if section_idx > start_idx and section_idx < end_idx:
                        end_idx = section_idx
                
                edu_section = text[start_idx:end_idx]
                break
        
        if not edu_section:
            return []
        
        # 解析教育经历
        # 这里使用简化的解析逻辑，实际应用中应该使用更复杂的模式匹配
        lines = edu_section.split('\n')
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的教育经历条目
            if any(school in line for school in ['大学', '学院', 'University', 'College', 'Institute']):
                if current_edu and 'school' in current_edu:
                    education.append(current_edu)
                current_edu = {'school': line}
            elif '学位' in line or '学历' in line or 'degree' in line.lower():
                for degree in ['博士', '硕士', '本科', '大专', '高中', 'PhD', 'Master', 'Bachelor']:
                    if degree in line:
                        current_edu['degree'] = degree
                        break
            elif '专业' in line or 'major' in line.lower():
                major_match = re.search(r'专业[：:]\s*(.+)', line)
                if major_match:
                    current_edu['major'] = major_match.group(1)
                else:
                    current_edu['major'] = line.replace('专业', '').strip()
            elif '时间' in line or '日期' in line or 'date' in line.lower():
                dates = re.findall(r'\d{4}[-/\.年]\d{1,2}', line)
                if len(dates) >= 2:
                    current_edu['start_date'] = dates[0]
                    current_edu['end_date'] = dates[1]
                elif len(dates) == 1:
                    current_edu['start_date'] = dates[0]
                    if '至今' in line or 'present' in line.lower():
                        current_edu['end_date'] = '至今'
                    else:
                        current_edu['end_date'] = '未知'
        
        # 添加最后一个教育经历
        if current_edu and 'school' in current_edu:
            education.append(current_edu)
        
        return education
    
    def _extract_work_experience_from_text(self, text: str) -> List[Dict[str, str]]:
        """从文本中提取工作经历"""
        work_experience = []
        
        # 查找工作经历部分
        work_indicators = ['工作经历', '工作经验', '职业经历', '工作']
        work_section = ""
        for indicator in work_indicators:
            if indicator in text:
                start_idx = text.find(indicator)
                # 找到下一个主要部分
                next_sections = ['教育经历', '教育背景', '项目经历', '技能', '技术栈']
                end_idx = len(text)
                for section in next_sections:
                    section_idx = text.find(section, start_idx)
                    if section_idx > start_idx and section_idx < end_idx:
                        end_idx = section_idx
                
                work_section = text[start_idx:end_idx]
                break
        
        if not work_section:
            return []
        
        # 解析工作经历
        # 这里使用简化的解析逻辑，实际应用中应该使用更复杂的模式匹配
        lines = work_section.split('\n')
        current_work = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的工作经历条目
            if any(company in line for company in ['公司', '企业', 'Company', 'Corp', 'Inc', 'Ltd']):
                if current_work and 'company' in current_work:
                    work_experience.append(current_work)
                current_work = {'company': line}
            elif '职位' in line or '岗位' in line or 'position' in line.lower() or 'title' in line.lower():
                position_match = re.search(r'[职位岗位][：:]\s*(.+)', line)
                if position_match:
                    current_work['position'] = position_match.group(1)
                else:
                    current_work['position'] = line
            elif '时间' in line or '日期' in line or 'date' in line.lower():
                dates = re.findall(r'\d{4}[-/\.年]\d{1,2}', line)
                if len(dates) >= 2:
                    current_work['start_date'] = dates[0]
                    current_work['end_date'] = dates[1]
                elif len(dates) == 1:
                    current_work['start_date'] = dates[0]
                    if '至今' in line or 'present' in line.lower():
                        current_work['end_date'] = '至今'
                    else:
                        current_work['end_date'] = '未知'
            elif '描述' in line or '职责' in line or '工作内容' in line or 'description' in line.lower() or 'responsibility' in line.lower():
                desc_match = re.search(r'[描述职责][：:]\s*(.+)', line)
                if desc_match:
                    current_work['description'] = desc_match.group(1)
                else:
                    # 收集接下来的几行作为描述
                    description = []
                    i = lines.index(line) + 1
                    while i < len(lines) and i < lines.index(line) + 5:
                        if lines[i].strip() and not any(keyword in lines[i] for keyword in ['公司', '职位', '时间', '日期']):
                            description.append(lines[i].strip())
                        i += 1
                    current_work['description'] = ' '.join(description)
        
        # 添加最后一个工作经历
        if current_work and 'company' in current_work:
            work_experience.append(current_work)
        
        return work_experience
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """从文本中提取技能"""
        skills = set()
        
        # 查找技能部分
        skill_indicators = ['技能', '技术栈', '专业技能', '技术技能', 'skills', 'technologies']
        skill_section = ""
        for indicator in skill_indicators:
            if indicator in text:
                start_idx = text.find(indicator)
                # 找到下一个主要部分
                next_sections = ['教育经历', '工作经历', '项目经历', '自我评价', '兴趣爱好']
                end_idx = len(text)
                for section in next_sections:
                    section_idx = text.find(section, start_idx)
                    if section_idx > start_idx and section_idx < end_idx:
                        end_idx = section_idx
                
                skill_section = text[start_idx:end_idx]
                break
        
        # 如果找不到明确的技能部分，使用整个文本
        if not skill_section:
            skill_section = text
        
        # 从技能部分提取技能
        # 1. 查找常见技能关键词
        for skill_key, skill_name in self.skill_mapping.items():
            # 使用单词边界确保匹配整个单词
            pattern = r'\b' + re.escape(skill_key) + r'\b'
            if re.search(pattern, skill_section.lower()):
                skills.add(skill_name)
        
        # 2. 查找列表形式的技能
        list_patterns = [
            r'•\s*([^•\n]+)',  # 以•开头的列表项
            r'[\-\*]\s*([^\-\*\n]+)',  # 以-或*开头的列表项
            r'\d+\.\s*([^\d\.\n]+)',  # 以数字开头的列表项
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, skill_section)
            for match in matches:
                skill = match.strip()
                # 过滤掉太长的项（可能不是技能）和太短的项
                if 2 < len(skill) < 30:
                    # 检查是否匹配已知技能
                    skill_lower = skill.lower()
                    if skill_lower in self.skill_mapping:
                        skills.add(self.skill_mapping[skill_lower])
                    else:
                        skills.add(skill)
        
        # 3. 查找逗号分隔的技能列表
        comma_separated = re.findall(r'技能[：:]\s*(.+)', skill_section)
        if comma_separated:
            for skill_list in comma_separated:
                for skill in re.split(r'[,，、/\s]+', skill_list):
                    skill = skill.strip()
                    if 2 < len(skill) < 30:
                        skill_lower = skill.lower()
                        if skill_lower in self.skill_mapping:
                            skills.add(self.skill_mapping[skill_lower])
                        else:
                            skills.add(skill)
        
        return list(skills)
    
    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析简历数据，提取关键特征
        
        Args:
            resume_data: 简历数据
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        analysis = {}
        
        # 提取个人信息摘要
        analysis['personal_summary'] = self.get_resume_summary(resume_data)
        
        # 分析技能
        analysis['skills_analysis'] = self.analyze_skills(resume_data['skills'])
        
        # 分析教育背景
        analysis['education_analysis'] = self.analyze_education(resume_data['education'])
        
        # 分析工作经验
        analysis['experience_analysis'] = self.analyze_experience(resume_data['work_experience'])
        
        # 确定职业方向
        analysis['career_direction'] = self.determine_career_direction(resume_data)
        
        # 计算综合评分
        analysis['overall_score'] = self.calculate_overall_score(resume_data)
        
        return analysis
    
    def get_resume_summary(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取简历摘要"""
        return {
            'name': resume_data['personal_info'].get('name', '未知'),
            'latest_position': resume_data['work_experience'][0].get('position', '未知') if resume_data['work_experience'] else '未知',
            'latest_company': resume_data['work_experience'][0].get('company', '未知') if resume_data['work_experience'] else '未知',
            'experience_years': self.calculate_experience_years(resume_data['work_experience']),
            'highest_education': self.get_highest_education(resume_data['education']),
            'top_skills': resume_data['skills'][:5] if len(resume_data['skills']) > 5 else resume_data['skills']
        }
    
    def calculate_experience_years(self, work_experience: List[Dict[str, str]]) -> float:
        """计算工作经验年限"""
        if not work_experience:
            return 0
        
        total_months = 0
        import datetime
        
        for job in work_experience:
            # 解析开始日期
            start_date_str = job.get('start_date', '')
            if not start_date_str:
                continue
            
            # 处理不同的日期格式
            start_date = None
            date_formats = ['%Y-%m', '%Y/%m', '%Y.%m', '%Y年%m月']
            for fmt in date_formats:
                try:
                    start_date = datetime.datetime.strptime(start_date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not start_date:
                continue
            
            # 解析结束日期
            end_date_str = job.get('end_date', '')
            if end_date_str == '至今' or end_date_str == 'present':
                end_date = datetime.datetime.now()
            else:
                end_date = None
                for fmt in date_formats:
                    try:
                        end_date = datetime.datetime.strptime(end_date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            if not end_date:
                continue
            
            # 计算月数差异
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
        
        # 转换为年
        return round(total_months / 12, 1)
    
    def get_highest_education(self, education: List[Dict[str, str]]) -> str:
        """获取最高学历"""
        if not education:
            return '未知'
        
        highest_level = 0
        highest_edu = None
        
        for edu in education:
            degree = edu.get('degree', '')
            major = edu.get('major', '')
            
            # 查找学历等级
            level = 0
            for key, value in self.education_levels.items():
                if key in degree.lower():
                    level = value
                    break
            
            if level > highest_level:
                highest_level = level
                highest_edu = edu
        
        if highest_edu:
            return f"{highest_edu.get('degree', '未知')} - {highest_edu.get('major', '未知')}"
        
        return education[0].get('degree', '未知') + ' - ' + education[0].get('major', '未知')
    
    def analyze_skills(self, skills: List[str]) -> Dict[str, Any]:
        """分析技能集"""
        if not skills:
            return {
                'skill_count': 0,
                'skill_categories': {},
                'primary_skills': [],
                'skill_level': '初级'
            }
        
        # 技能分类
        categories = {
            '编程语言': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin'],
            '前端技术': ['HTML', 'CSS', 'React', 'Vue.js', 'Angular', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'Webpack'],
            '后端技术': ['Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Spring Boot', 'Laravel', 'ASP.NET'],
            '数据库': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server', 'SQLite'],
            '云服务和DevOps': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab'],
            '数据科学和AI': ['机器学习', '深度学习', '人工智能', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy'],
            '移动开发': ['Android', 'iOS', 'React Native', 'Flutter', 'Xamarin'],
            '其他技能': ['RESTful API', 'GraphQL', '微服务', '敏捷开发', 'Scrum', 'Kanban', 'CI/CD', '自动化测试', 'UI/UX设计']
        }
        
        # 统计各类别的技能数量
        skill_categories = {}
        for category, category_skills in categories.items():
            category_count = sum(1 for skill in skills if skill in category_skills)
            if category_count > 0:
                skill_categories[category] = category_count
        
        # 确定主要技能领域
        primary_category = max(skill_categories.items(), key=lambda x: x[1])[0] if skill_categories else '其他技能'
        primary_skills = [skill for skill in skills if any(skill in category_skills for category, category_skills in categories.items() if category == primary_category)]
        
        # 确定技能水平
        skill_level = '初级'
        if len(skills) >= 10:
            skill_level = '高级'
        elif len(skills) >= 5:
            skill_level = '中级'
        
        return {
            'skill_count': len(skills),
            'skill_categories': skill_categories,
            'primary_skills': primary_skills,
            'skill_level': skill_level
        }
    
    def analyze_education(self, education: List[Dict[str, str]]) -> Dict[str, Any]:
        """分析教育背景"""
        if not education:
            return {
                'education_level': '未知',
                'education_score': 0,
                'is_cs_related': False,
                'top_university': False
            }
        
        # 获取最高学历
        highest_level = 0
        highest_edu = None
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            
            # 查找学历等级
            level = 0
            for key, value in self.education_levels.items():
                if key in degree:
                    level = value
                    break
            
            if level > highest_level:
                highest_level = level
                highest_edu = edu
        
        if not highest_edu:
            highest_edu = education[0]
        
        # 判断是否是计算机相关专业
        cs_related_majors = [
            '计算机', '软件', '信息', '网络', '人工智能', '数据', '电子', '通信',
            'computer', 'software', 'information', 'network', 'artificial intelligence', 'data', 'electronic', 'communication'
        ]
        
        major = highest_edu.get('major', '').lower()
        is_cs_related = any(keyword in major for keyword in cs_related_majors)
        
        # 判断是否是顶尖大学
        top_universities = [
            '清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学', '南京大学', '中国科学技术大学',
            '哈尔滨工业大学', '西安交通大学', '华中科技大学', '武汉大学', '同济大学', '北京航空航天大学',
            'tsinghua', 'peking', 'fudan', 'shanghai jiao tong', 'zhejiang', 'nanjing', 'ustc',
            'harbin institute of technology', 'xian jiaotong', 'huazhong', 'wuhan', 'tongji', 'beihang'
        ]
        
        school = highest_edu.get('school', '').lower()
        top_university = any(university.lower() in school for university in top_universities)
        
        # 计算教育评分
        education_score = highest_level * 20  # 最高100分
        if is_cs_related:
            education_score += 10
        if top_university:
            education_score += 10
        
        education_score = min(100, education_score)
        
        return {
            'education_level': highest_edu.get('degree', '未知'),
            'education_score': education_score,
            'is_cs_related': is_cs_related,
            'top_university': top_university
        }
    
    def analyze_experience(self, work_experience: List[Dict[str, str]]) -> Dict[str, Any]:
        """分析工作经验"""
        if not work_experience:
            return {
                'years': 0,
                'experience_score': 0,
                'company_tier': '普通',
                'position_level': '初级',
                'has_management_experience': False
            }
        
        # 计算总工作年限
        years = self.calculate_experience_years(work_experience)
        
        # 判断公司层级
        top_companies = [
            '阿里巴巴', '腾讯', '百度', '字节跳动', '华为', '小米', '京东', '美团', '网易', '滴滴', '拼多多', '快手',
            '微软', '谷歌', '亚马逊', '苹果', 'Facebook', 'IBM', '英特尔', '甲骨文', 'SAP',
            'alibaba', 'tencent', 'baidu', 'bytedance', 'huawei', 'xiaomi', 'jd', 'meituan', 'netease', 'didi', 'pinduoduo', 'kuaishou',
            'microsoft', 'google', 'amazon', 'apple', 'facebook', 'ibm', 'intel', 'oracle', 'sap'
        ]
        
        latest_company = work_experience[0].get('company', '').lower()
        company_tier = '一线' if any(company.lower() in latest_company for company in top_companies) else '普通'
        
        # 判断职位级别
        position = work_experience[0].get('position', '').lower()
        
        senior_keywords = ['高级', '资深', '专家', '架构师', '经理', '主管', '总监', '负责人',
                          'senior', 'lead', 'architect', 'manager', 'director', 'head']
        mid_keywords = ['中级', '工程师', '开发者', '分析师',
                       'engineer', 'developer', 'analyst']
        
        if any(keyword in position for keyword in senior_keywords):
            position_level = '高级'
        elif any(keyword in position for keyword in mid_keywords):
            position_level = '中级'
        else:
            position_level = '初级'
        
        # 判断是否有管理经验
        management_keywords = ['经理', '主管', '总监', '负责人', '管理', '团队', '领导',
                              'manager', 'director', 'head', 'lead', 'management', 'team', 'leadership']
        
        has_management_experience = any(
            any(keyword in job.get('position', '').lower() or keyword in job.get('description', '').lower() 
                for keyword in management_keywords)
            for job in work_experience
        )
        
        # 计算经验评分
        experience_score = min(100, years * 10)  # 10年及以上满分
        if company_tier == '一线':
            experience_score += 10
        if position_level == '高级':
            experience_score += 10
        elif position_level == '中级':
            experience_score += 5
        if has_management_experience:
            experience_score += 10
        
        experience_score = min(100, experience_score)
        
        return {
            'years': years,
            'experience_score': experience_score,
            'company_tier': company_tier,
            'position_level': position_level,
            'has_management_experience': has_management_experience
        }
    
    def determine_career_direction(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """确定职业方向"""
        # 提取所有文本内容
        all_text = ""
        
        # 添加工作经历
        for job in resume_data['work_experience']:
            all_text += job.get('position', '') + ' '
            all_text += job.get('description', '') + ' '
        
        # 添加技能
        all_text += ' '.join(resume_data['skills']) + ' '
        
        # 添加个人总结
        all_text += resume_data['personal_info'].get('summary', '') + ' '
        
        # 统计各职位类型的关键词出现次数
        category_scores = {}
        for category, keywords in self.job_categories.items():
            score = sum(all_text.lower().count(keyword.lower()) for keyword in keywords)
            if score > 0:
                category_scores[category] = score
        
        # 找出得分最高的职位类型
        if category_scores:
            primary_direction = max(category_scores.items(), key=lambda x: x[1])[0]
            direction_score = category_scores[primary_direction] / sum(category_scores.values()) * 100
        else:
            primary_direction = '未确定'
            direction_score = 0
        
        # 获取次要方向
        if len(category_scores) > 1:
            sorted_directions = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            secondary_direction = sorted_directions[1][0]
            secondary_score = sorted_directions[1][1] / sum(category_scores.values()) * 100
        else:
            secondary_direction = '未确定'
            secondary_score = 0
        
        return {
            'primary_direction': primary_direction,
            'primary_score': direction_score,
            'secondary_direction': secondary_direction,
            'secondary_score': secondary_score,
            'direction_confidence': 'high' if direction_score > 50 else 'medium' if direction_score > 30 else 'low'
        }
    
    def calculate_overall_score(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算简历综合评分"""
        # 分析各部分
        skills_analysis = self.analyze_skills(resume_data['skills'])
        education_analysis = self.analyze_education(resume_data['education'])
        experience_analysis = self.analyze_experience(resume_data['work_experience'])
        
        # 计算各部分权重
        weights = {
            'skills': 0.4,
            'education': 0.2,
            'experience': 0.4
        }
        
        # 计算技能评分（满分100）
        skill_score = min(100, skills_analysis['skill_count'] * 10)  # 10个及以上技能满分
        
        # 计算综合评分
        overall_score = (
            skill_score * weights['skills'] +
            education_analysis['education_score'] * weights['education'] +
            experience_analysis['experience_score'] * weights['experience']
        )
        
        # 确定级别
        if overall_score >= 80:
            level = '高级'
        elif overall_score >= 60:
            level = '中级'
        else:
            level = '初级'
        
        return {
            'overall_score': round(overall_score, 1),
            'level': level,
            'component_scores': {
                'skills': skill_score,
                'education': education_analysis['education_score'],
                'experience': experience_analysis['experience_score']
            }
        }
    
    def match_resume_to_job(self, resume_data: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, float]:
        """
        计算简历与职位的匹配度
        
        Args:
            resume_data: 简历数据
            job: 职位数据
            
        Returns:
            Dict[str, float]: 匹配度评分
        """
        # 计算技能匹配
        resume_skills = set(s.lower() for s in resume_data['skills'])
        job_skills = set(s.lower() for s in job['required_skills'])
        
        matched_skills = []
        for job_skill in job_skills:
            for resume_skill in resume_skills:
                # 使用部分匹配，因为技能名称可能有细微差别
                if job_skill in resume_skill or resume_skill in job_skill:
                    matched_skills.append(job_skill)
                    break
        
        skill_match = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # 计算教育匹配
        degree_level = {'博士': 4, '硕士': 3, '本科': 2, '大专': 1, '高中': 0, '': 0}
        resume_highest_degree = resume_data['education'][0].get('degree', '') if resume_data['education'] else ''
        job_required_degree = job.get('education_requirement', '')
        
        resume_level = 0
        for key, value in degree_level.items():
            if key in resume_highest_degree:
                resume_level = value
                break
        
        job_level = 0
        for key, value in degree_level.items():
            if key in job_required_degree:
                job_level = value
                break
        
        education_match = 1.0 if resume_level >= job_level else resume_level / job_level if job_level > 0 else 0
        
        # 计算经验匹配
        resume_experience_years = self.calculate_experience_years(resume_data['work_experience'])
        job_required_years = job.get('experience_requirement', 0)
        
        experience_match = 1.0 if resume_experience_years >= job_required_years else resume_experience_years / job_required_years if job_required_years > 0 else 0
        
        # 计算职位方向匹配
        career_direction = self.determine_career_direction(resume_data)
        job_title = job.get('title', '').lower()
        
        direction_match = 0.0
        for category, keywords in self.job_categories.items():
            if any(keyword.lower() in job_title for keyword in keywords):
                if category == career_direction['primary_direction']:
                    direction_match = 1.0
                elif category == career_direction['secondary_direction']:
                    direction_match = 0.7
                break
        
        # 如果没有明确匹配，使用关键词匹配
        if direction_match == 0.0:
            # 提取简历中的所有文本
            resume_text = resume_data['personal_info'].get('summary', '') + ' '
            for job in resume_data['work_experience']:
                resume_text += job.get('position', '') + ' ' + job.get('description', '') + ' '
            resume_text += ' '.join(resume_data['skills'])
            
            # 提取职位中的关键词
            job_text = job.get('title', '') + ' ' + job.get('description', '')
            
            # 计算关键词匹配
            job_words = set(self._tokenize(job_text))
            resume_words = set(self._tokenize(resume_text))
            
            common_words = job_words.intersection(resume_words)
            direction_match = len(common_words) / len(job_words) if job_words else 0
        
        # 计算综合匹配分数
        weights = {
            'skill': 0.4,
            'education': 0.1,
            'experience': 0.2,
            'direction': 0.3
        }
        
        match_score = (
            skill_match * weights['skill'] +
            education_match * weights['education'] +
            experience_match * weights['experience'] +
            direction_match * weights['direction']
        )
        
        # 转换为百分比
        match_percentage = round(match_score * 100)
        
        return {
            'match_score': match_percentage,
            'skill_match': round(skill_match * 100),
            'education_match': round(education_match * 100),
            'experience_match': round(experience_match * 100),
            'direction_match': round(direction_match * 100),
            'matched_skills': matched_skills
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """分词并去除停用词"""
        # 对中英文混合文本进行简单分词
        # 实际应用中应使用更复杂的分词算法，如jieba
        words = []
        
        # 英文分词
        english_words = nltk.word_tokenize(text)
        words.extend([word.lower() for word in english_words if word.isalpha() and word.lower() not in self.stopwords])
        
        # 中文分词（简化处理）
        chinese_text = ''.join(char for char in text if '\u4e00' <= char <= '\u9fff')
        for i in range(len(chinese_text) - 1):
            word = chinese_text[i:i+2]  # 简单的二字词切分
            if word not in self.chinese_stopwords:
                words.append(word)
        
        return words
    
    def match_resume_to_jobs(self, resume_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        计算简历与多个职位的匹配度并排序
        
        Args:
            resume_data: 简历数据
            jobs: 职位列表
            
        Returns:
            List[Dict[str, Any]]: 匹配结果列表
        """
        match_results = []
        
        for job in jobs:
            # 计算匹配度
            match_scores = self.match_resume_to_job(resume_data, job)
            
            # 添加到结果列表
            match_results.append({
                'job_id': job['id'],
                'match_score': match_scores['match_score'],
                'skill_match': match_scores['skill_match'],
                'education_match': match_scores['education_match'],
                'experience_match': match_scores['experience_match'],
                'direction_match': match_scores['direction_match'],
                'matched_skills': match_scores['matched_skills']
            })
        
        # 按匹配度排序
        match_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return match_results
    
    def generate_improvement_suggestions(self, resume_data: Dict[str, Any], job: Dict[str, Any]) -> List[str]:
        """
        根据简历和目标职位生成改进建议
        
        Args:
            resume_data: 简历数据
            job: 目标职位
            
        Returns:
            List[str]: 改进建议列表
        """
        suggestions = []
        
        # 计算匹配度
        match_scores = self.match_resume_to_job(resume_data, job)
        
        # 技能建议
        if match_scores['skill_match'] < 70:
            missing_skills = set(s.lower() for s in job['required_skills']) - set(s.lower() for s in resume_data['skills'])
            if missing_skills:
                suggestions.append(f"建议添加以下技能: {', '.join(missing_skills)}")
        
        # 教育建议
        if match_scores['education_match'] < 70:
            degree_level = {'博士': 4, '硕士': 3, '本科': 2, '大专': 1, '高中': 0, '': 0}
            resume_highest_degree = resume_data['education'][0].get('degree', '') if resume_data['education'] else ''
            job_required_degree = job.get('education_requirement', '')
            
            resume_level = 0
            for key, value in degree_level.items():
                if key in resume_highest_degree:
                    resume_level = value
                    break
            
            job_level = 0
            for key, value in degree_level.items():
                if key in job_required_degree:
                    job_level = value
                    break
            
            if resume_level < job_level:
                for key, value in degree_level.items():
                    if value == job_level:
                        suggestions.append(f"该职位要求{key}学历，建议提升教育背景")
                        break
        
        # 经验建议
        if match_scores['experience_match'] < 70:
            resume_experience_years = self.calculate_experience_years(resume_data['work_experience'])
            job_required_years = job.get('experience_requirement', 0)
            
            if resume_experience_years < job_required_years:
                suggestions.append(f"该职位要求{job_required_years}年经验，建议积累更多相关工作经验")
        
        # 职位方向建议
        if match_scores['direction_match'] < 70:
            job_title = job.get('title', '')
            suggestions.append(f"您的经历与{job_title}职位方向匹配度不高，建议积累更多相关领域的经验")
        
        # 如果没有具体建议，添加一般性建议
        if not suggestions:
            suggestions.append("您的简历与该职位匹配度较高，可以考虑在个人总结中突出与该职位相关的经验和技能")
        
        return suggestions


# 适配现有应用的接口
def parse_resume_enhanced(file_path: str) -> Dict[str, Any]:
    """
    增强版简历解析接口函数，适配现有应用
    
    Args:
        file_path: 简历文件路径
        
    Returns:
        Dict[str, Any]: 解析后的简历数据
    """
    analyzer = ResumeAnalyzer()
    return analyzer.parse_resume(file_path)

def match_resume_to_jobs_enhanced(resume_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    增强版简历职位匹配接口函数，适配现有应用
    
    Args:
        resume_data: 简历数据
        jobs: 职位列表
        
    Returns:
        List[Dict[str, Any]]: 匹配结果列表
    """
    analyzer = ResumeAnalyzer()
    return analyzer.match_resume_to_jobs(resume_data, jobs)

def analyze_resume_enhanced(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    增强版简历分析接口函数，适配现有应用
    
    Args:
        resume_data: 简历数据
        
    Returns:
        Dict[str, Any]: 分析结果
    """
    analyzer = ResumeAnalyzer()
    return analyzer.analyze_resume(resume_data)

def generate_improvement_suggestions_enhanced(resume_data: Dict[str, Any], job: Dict[str, Any]) -> List[str]:
    """
    增强版简历改进建议接口函数，适配现有应用
    
    Args:
        resume_data: 简历数据
        job: 目标职位
        
    Returns:
        List[str]: 改进建议列表
    """
    analyzer = ResumeAnalyzer()
    return analyzer.generate_improvement_suggestions(resume_data, job)


if __name__ == "__main__":
    # 测试代码
    analyzer = ResumeAnalyzer()
    
    # 测试简历解析
    resume_data = analyzer.parse_resume("example_resume.txt")
    print("简历解析结果:")
    print(f"姓名: {resume_data['personal_info']['name']}")
    print(f"技能: {resume_data['skills']}")
    
    # 测试简历分析
    analysis = analyzer.analyze_resume(resume_data)
    print("\n简历分析结果:")
    print(f"综合评分: {analysis['overall_score']['overall_score']}")
    print(f"职业方向: {analysis['career_direction']['primary_direction']}")
    
    # 测试职位匹配
    job = {
        'id': 'job_1',
        'title': '高级Python开发工程师',
        'company': '某科技公司',
        'required_skills': ['Python', 'Django', 'Flask', 'MySQL', 'Redis', 'Docker'],
        'education_requirement': '本科',
        'experience_requirement': 3
    }
    
    match_scores = analyzer.match_resume_to_job(resume_data, job)
    print("\n职位匹配结果:")
    print(f"匹配度: {match_scores['match_score']}%")
    print(f"技能匹配: {match_scores['skill_match']}%")
    print(f"匹配的技能: {match_scores['matched_skills']}")
    
    # 测试改进建议
    suggestions = analyzer.generate_improvement_suggestions(resume_data, job)
    print("\n改进建议:")
    for suggestion in suggestions:
        print(f"- {suggestion}")
