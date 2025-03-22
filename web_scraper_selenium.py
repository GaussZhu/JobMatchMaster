"""
AI简历职位匹配系统 - 网页抓取模块 (Streamlit Cloud兼容版)
使用Selenium和BeautifulSoup抓取招聘网站职位信息，添加了Streamlit Cloud兼容性
"""
import os
import re
import time
import random
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# 尝试导入Selenium相关库，如果失败则提供备用方案
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    
    SELENIUM_AVAILABLE = True
except ImportError:
    print("Selenium库不可用，将使用备用方案")
    SELENIUM_AVAILABLE = False

# 尝试导入BeautifulSoup，如果失败则提供备用方案
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    print("BeautifulSoup库不可用，将使用备用方案")
    BS4_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    """职位抓取器，使用Selenium和BeautifulSoup抓取招聘网站职位信息"""
    
    def __init__(self, headless: bool = True):
        """初始化职位抓取器
        
        Args:
            headless: 是否使用无头模式运行浏览器
        """
        self.headless = headless
        self.driver = None
        self.cache_dir = "./cache"
        self.cache_duration = 24 * 60 * 60  # 缓存有效期（秒）
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _init_driver(self) -> bool:
        """初始化Selenium WebDriver
        
        Returns:
            bool: 是否成功初始化
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium库不可用，无法初始化WebDriver")
            return False
        
        try:
            # 配置Chrome选项
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            
            # 在Streamlit Cloud环境中使用系统安装的ChromeDriver
            if "STREAMLIT_SHARING" in os.environ or "STREAMLIT_CLOUD" in os.environ:
                self.driver = webdriver.Chrome(options=chrome_options)
            else:
                # 在本地环境中使用webdriver_manager自动下载ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            return True
        except Exception as e:
            logger.error(f"初始化WebDriver失败: {str(e)}")
            return False
    
    def _close_driver(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def _get_cache_path(self, query: str, location: str, platform: str) -> str:
        """获取缓存文件路径
        
        Args:
            query: 搜索关键词
            location: 地点
            platform: 平台
        
        Returns:
            str: 缓存文件路径
        """
        # 规范化参数，移除特殊字符
        query = re.sub(r'[^\w\s]', '', query).strip().lower()
        location = re.sub(r'[^\w\s]', '', location).strip().lower()
        platform = re.sub(r'[^\w\s]', '', platform).strip().lower()
        
        # 生成缓存文件名
        cache_file = f"jobs_{platform}_{query}_{location}.json"
        return os.path.join(self.cache_dir, cache_file)
    
    def _load_from_cache(self, query: str, location: str, platform: str) -> Optional[List[Dict[str, Any]]]:
        """从缓存加载职位信息
        
        Args:
            query: 搜索关键词
            location: 地点
            platform: 平台
        
        Returns:
            Optional[List[Dict[str, Any]]]: 职位列表，如果缓存不存在或已过期则返回None
        """
        cache_path = self._get_cache_path(query, location, platform)
        
        if not os.path.exists(cache_path):
            return None
        
        # 检查缓存是否过期
        file_time = os.path.getmtime(cache_path)
        current_time = time.time()
        if current_time - file_time > self.cache_duration:
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def _save_to_cache(self, jobs: List[Dict[str, Any]], query: str, location: str, platform: str):
        """将职位信息保存到缓存
        
        Args:
            jobs: 职位列表
            query: 搜索关键词
            location: 地点
            platform: 平台
        """
        cache_path = self._get_cache_path(query, location, platform)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
    
    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机延迟，避免被反爬
        
        Args:
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _extract_job_details_from_html(self, html: str, platform: str) -> Dict[str, Any]:
        """从HTML中提取职位详情
        
        Args:
            html: HTML内容
            platform: 平台
        
        Returns:
            Dict[str, Any]: 职位详情
        """
        if not BS4_AVAILABLE:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        job_details = {}
        
        if platform == "智联招聘":
            # 提取职位标题
            title_elem = soup.select_one('.job-summary .summary-title h1')
            if title_elem:
                job_details['title'] = title_elem.text.strip()
            
            # 提取公司名称
            company_elem = soup.select_one('.company-name a')
            if company_elem:
                job_details['company'] = company_elem.text.strip()
            
            # 提取薪资范围
            salary_elem = soup.select_one('.job-summary .summary-salary')
            if salary_elem:
                job_details['salary_range'] = salary_elem.text.strip()
            
            # 提取工作地点
            location_elem = soup.select_one('.job-summary .summary-place')
            if location_elem:
                job_details['location'] = location_elem.text.strip()
            
            # 提取职位描述
            description_elem = soup.select_one('.describtion .describtion-text')
            if description_elem:
                job_details['description'] = description_elem.text.strip()
            
            # 提取要求技能
            skills = []
            skill_elems = soup.select('.pos-tag span')
            for skill_elem in skill_elems:
                skills.append(skill_elem.text.strip())
            job_details['required_skills'] = skills
            
            # 提取教育要求
            education_elem = soup.select_one('.job-qualifications span:nth-child(1)')
            if education_elem:
                job_details['education_requirement'] = education_elem.text.strip()
            
            # 提取经验要求
            experience_elem = soup.select_one('.job-qualifications span:nth-child(2)')
            if experience_elem:
                job_details['experience_requirement'] = experience_elem.text.strip()
        
        elif platform == "前程无忧":
            # 提取职位标题
            title_elem = soup.select_one('.tHeader .cn h1')
            if title_elem:
                job_details['title'] = title_elem.text.strip()
            
            # 提取公司名称
            company_elem = soup.select_one('.tHeader .cn .cname a')
            if company_elem:
                job_details['company'] = company_elem.text.strip()
            
            # 提取薪资范围
            salary_elem = soup.select_one('.tHeader .cn strong')
            if salary_elem:
                job_details['salary_range'] = salary_elem.text.strip()
            
            # 提取工作地点
            location_elem = soup.select_one('.tHeader .cn .msg .el')
            if location_elem:
                job_details['location'] = location_elem.text.strip()
            
            # 提取职位描述
            description_elem = soup.select_one('.job_msg')
            if description_elem:
                job_details['description'] = description_elem.text.strip()
            
            # 提取要求技能
            skills = []
            skill_elems = soup.select('.tBorderTop_box .mt10 span')
            for skill_elem in skill_elems:
                skills.append(skill_elem.text.strip())
            job_details['required_skills'] = skills
            
            # 提取教育要求
            job_request = soup.select('.tHeader .cn .msg')
            if len(job_request) >= 2:
                job_details['education_requirement'] = job_request[1].text.strip()
            
            # 提取经验要求
            if len(job_request) >= 3:
                job_details['experience_requirement'] = job_request[2].text.strip()
        
        # 如果没有提取到技能，尝试从描述中提取
        if 'required_skills' not in job_details or not job_details['required_skills']:
            job_details['required_skills'] = self._extract_skills_from_description(job_details.get('description', ''))
        
        return job_details
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """从职位描述中提取技能
        
        Args:
            description: 职位描述
        
        Returns:
            List[str]: 技能列表
        """
        if not description:
            return []
        
        # 常见技能关键词
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 
            'PHP', 'Ruby', 'Swift', 'Kotlin', 'Objective-C', 'Scala', 'R', 'Shell', 'Bash',
            'React', 'Vue', 'Angular', 'jQuery', 'HTML', 'CSS', 'SASS', 'LESS', 
            'Bootstrap', 'Tailwind', 'Webpack', 'Vite',
            'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Spring Boot', 
            'Laravel', 'ASP.NET',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 
            'SQL Server', 'SQLite',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 
            'GitLab', 'Terraform', 'Ansible', 'CI/CD',
            '机器学习', '深度学习', '人工智能', 'TensorFlow', 'PyTorch', 'Keras', 
            'Scikit-learn', 'Pandas', 'NumPy', 'SciPy', 'Matplotlib',
            'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin',
            'RESTful API', 'GraphQL', 'WebSocket', 'OAuth', 'JWT', '微服务', 'Serverless'
        ]
        
        # 提取技能
        skills = []
        for skill in skill_keywords:
            if skill.lower() in description.lower():
                skills.append(skill)
        
        return skills
    
    def search_jobs(self, query: str, location: str = "北京", platform: str = "智联招聘", limit: int = 10) -> List[Dict[str, Any]]:
        """搜索职位
        
        Args:
            query: 搜索关键词
            location: 地点
            platform: 平台
            limit: 结果数量限制
        
        Returns:
            List[Dict[str, Any]]: 职位列表
        """
        # 尝试从缓存加载
        cached_jobs = self._load_from_cache(query, location, platform)
        if cached_jobs:
            logger.info(f"从缓存加载到 {len(cached_jobs)} 个职位")
            return cached_jobs[:limit]
        
        # 如果Selenium不可用，返回模拟数据
        if not SELENIUM_AVAILABLE or not BS4_AVAILABLE:
            logger.warning("Selenium或BeautifulSoup不可用，返回模拟数据")
            return self._generate_mock_jobs(query, location, limit)
        
        # 初始化WebDriver
        if not self._init_driver():
            logger.error("初始化WebDriver失败，返回模拟数据")
            return self._generate_mock_jobs(query, location, limit)
        
        try:
            jobs = []
            
            if platform == "智联招聘":
                jobs = self._search_zhaopin(query, location, limit)
            elif platform == "前程无忧":
                jobs = self._search_51job(query, location, limit)
            else:
                # 默认使用智联招聘
                jobs = self._search_zhaopin(query, location, limit)
            
            # 保存到缓存
            if jobs:
                self._save_to_cache(jobs, query, location, platform)
            
            return jobs
        except Exception as e:
            logger.error(f"搜索职位失败: {str(e)}")
            return self._generate_mock_jobs(query, location, limit)
        finally:
            self._close_driver()
    
    def _search_zhaopin(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """在智联招聘搜索职位
        
        Args:
            query: 搜索关键词
            location: 地点
            limit: 结果数量限制
        
        Returns:
            List[Dict[str, Any]]: 职位列表
        """
        jobs = []
        
        try:
            # 构建搜索URL
            search_url = f"https://sou.zhaopin.com/?kw={query}&city={location}"
            self.driver.get(search_url)
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".positionlist .joblist-box__item"))
            )
            
            # 随机延迟
            self._random_delay()
            
            # 获取职位列表
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".positionlist .joblist-box__item")
            
            for i, job_element in enumerate(job_elements[:limit]):
                try:
                    # 提取职位信息
                    title_element = job_element.find_element(By.CSS_SELECTOR, ".iteminfo__line1__jobname")
                    company_element = job_element.find_element(By.CSS_SELECTOR, ".iteminfo__line1__compname")
                    salary_element = job_element.find_element(By.CSS_SELECTOR, ".iteminfo__line2__jobdesc .iteminfo__line2__jobdesc__salary")
                    location_element = job_element.find_element(By.CSS_SELECTOR, ".iteminfo__line2__jobdesc__city")
                    
                    title = title_element.text.strip()
                    company = company_element.text.strip()
                    salary_range = salary_element.text.strip()
                    job_location = location_element.text.strip()
                    
                    # 获取职位链接
                    job_link = title_element.get_attribute("href")
                    
                    # 创建职位对象
                    job = {
                        "id": f"zhaopin_{i}",
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary_range": salary_range,
                        "url": job_link,
                        "platform": "智联招聘",
                        "required_skills": []
                    }
                    
                    # 访问职位详情页
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.driver.get(job_link)
                    
                    # 等待职位详情加载
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-summary"))
                    )
                    
                    # 随机延迟
                    self._random_delay()
                    
                    # 获取页面HTML
                    page_html = self.driver.page_source
                    
                    # 提取职位详情
                    job_details = self._extract_job_details_from_html(page_html, "智联招聘")
                    
                    # 更新职位对象
                    job.update(job_details)
                    
                    # 关闭详情页
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    
                    # 添加到结果列表
                    jobs.append(job)
                    
                    # 随机延迟
                    self._random_delay(2.0, 5.0)
                    
                except Exception as e:
                    logger.error(f"提取职位信息失败: {str(e)}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
        
        except Exception as e:
            logger.error(f"搜索智联招聘失败: {str(e)}")
        
        return jobs
    
    def _search_51job(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """在前程无忧搜索职位
        
        Args:
            query: 搜索关键词
            location: 地点
            limit: 结果数量限制
        
        Returns:
            List[Dict[str, Any]]: 职位列表
        """
        jobs = []
        
        try:
            # 构建搜索URL
            search_url = f"https://search.51job.com/list/{location},000000,0000,00,9,99,{query},2,1.html"
            self.driver.get(search_url)
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".j_joblist .e"))
            )
            
            # 随机延迟
            self._random_delay()
            
            # 获取职位列表
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".j_joblist .e")
            
            for i, job_element in enumerate(job_elements[:limit]):
                try:
                    # 提取职位信息
                    title_element = job_element.find_element(By.CSS_SELECTOR, ".jname .e_l_b_t")
                    company_element = job_element.find_element(By.CSS_SELECTOR, ".cname .e_l_b_t")
                    salary_element = job_element.find_element(By.CSS_SELECTOR, ".sal")
                    location_element = job_element.find_element(By.CSS_SELECTOR, ".d_at")
                    
                    title = title_element.text.strip()
                    company = company_element.text.strip()
                    salary_range = salary_element.text.strip()
                    job_location = location_element.text.strip()
                    
                    # 获取职位链接
                    job_link = title_element.get_attribute("href")
                    
                    # 创建职位对象
                    job = {
                        "id": f"51job_{i}",
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary_range": salary_range,
                        "url": job_link,
                        "platform": "前程无忧",
                        "required_skills": []
                    }
                    
                    # 访问职位详情页
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.driver.get(job_link)
                    
                    # 等待职位详情加载
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".tHeader"))
                    )
                    
                    # 随机延迟
                    self._random_delay()
                    
                    # 获取页面HTML
                    page_html = self.driver.page_source
                    
                    # 提取职位详情
                    job_details = self._extract_job_details_from_html(page_html, "前程无忧")
                    
                    # 更新职位对象
                    job.update(job_details)
                    
                    # 关闭详情页
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    
                    # 添加到结果列表
                    jobs.append(job)
                    
                    # 随机延迟
                    self._random_delay(2.0, 5.0)
                    
                except Exception as e:
                    logger.error(f"提取职位信息失败: {str(e)}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
        
        except Exception as e:
            logger.error(f"搜索前程无忧失败: {str(e)}")
        
        return jobs
    
    def _generate_mock_jobs(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """生成模拟职位数据
        
        Args:
            query: 搜索关键词
            location: 地点
            limit: 结果数量限制
        
        Returns:
            List[Dict[str, Any]]: 职位列表
        """
        jobs = []
        
        # 根据查询关键词确定职位类型
        job_type = "开发工程师"
        if "python" in query.lower():
            job_type = "Python开发工程师"
        elif "java" in query.lower():
            job_type = "Java开发工程师"
        elif "前端" in query.lower() or "frontend" in query.lower():
            job_type = "前端开发工程师"
        elif "后端" in query.lower() or "backend" in query.lower():
            job_type = "后端开发工程师"
        elif "数据" in query.lower() or "data" in query.lower():
            job_type = "数据工程师"
        elif "算法" in query.lower() or "algorithm" in query.lower():
            job_type = "算法工程师"
        elif "产品" in query.lower() or "product" in query.lower():
            job_type = "产品经理"
        elif "设计" in query.lower() or "design" in query.lower():
            job_type = "UI设计师"
        elif "测试" in query.lower() or "test" in query.lower():
            job_type = "测试工程师"
        elif "运维" in query.lower() or "devops" in query.lower():
            job_type = "运维工程师"
        
        # 公司列表
        companies = [
            "阿里巴巴", "腾讯", "百度", "京东", "美团", "字节跳动", "滴滴", "小米", "华为", "网易",
            "搜狐", "新浪", "360", "携程", "爱奇艺", "哔哩哔哩", "拼多多", "快手", "蚂蚁金服", "微博"
        ]
        
        # 薪资范围
        salary_ranges = [
            "15K-20K", "20K-30K", "25K-35K", "30K-40K", "35K-50K", 
            "40K-60K", "50K-70K", "60K-80K", "70K-90K", "80K-100K"
        ]
        
        # 技能要求
        skill_sets = {
            "Python开发工程师": ["Python", "Django", "Flask", "FastAPI", "MySQL", "Redis", "MongoDB", "Docker", "Git"],
            "Java开发工程师": ["Java", "Spring", "Spring Boot", "MyBatis", "MySQL", "Redis", "Kafka", "Docker", "Git"],
            "前端开发工程师": ["JavaScript", "TypeScript", "HTML", "CSS", "React", "Vue.js", "Webpack", "Node.js", "Git"],
            "后端开发工程师": ["Java", "Python", "Go", "Spring Boot", "Django", "MySQL", "Redis", "Docker", "Git"],
            "数据工程师": ["Python", "SQL", "Spark", "Hadoop", "Hive", "Kafka", "ETL", "数据仓库", "Git"],
            "算法工程师": ["Python", "机器学习", "深度学习", "TensorFlow", "PyTorch", "NLP", "计算机视觉", "数据挖掘", "Git"],
            "产品经理": ["产品设计", "用户研究", "需求分析", "产品规划", "市场分析", "用户体验", "原型设计", "数据分析", "项目管理"],
            "UI设计师": ["UI设计", "视觉设计", "交互设计", "用户体验", "Sketch", "Figma", "Adobe XD", "Photoshop", "Illustrator"],
            "测试工程师": ["自动化测试", "接口测试", "性能测试", "安全测试", "Selenium", "JMeter", "Postman", "Python", "Git"],
            "运维工程师": ["Linux", "Shell", "Docker", "Kubernetes", "Jenkins", "Ansible", "监控", "日志", "Git"]
        }
        
        # 教育要求
        education_requirements = ["本科", "硕士", "大专", "学历不限"]
        
        # 经验要求
        experience_requirements = ["1-3年", "3-5年", "5-7年", "7-10年", "经验不限"]
        
        # 职位描述模板
        description_template = """
        岗位职责：
        1. 负责{job_type}相关的设计、开发和维护工作
        2. 参与项目需求分析、技术方案设计和系统架构优化
        3. 解决开发过程中的技术难题，确保代码质量和性能
        4. 与产品、设计、测试等团队协作，推动项目顺利进行
        5. 关注行业技术发展趋势，持续学习和应用新技术
        
        任职要求：
        1. {education}及以上学历，计算机相关专业，{experience}相关工作经验
        2. 熟练掌握{skills}等技术栈
        3. 具有良好的编码习惯和技术文档编写能力
        4. 具备较强的问题分析和解决能力
        5. 有良好的团队协作精神和沟通能力
        6. 有相关行业经验者优先
        """
        
        # 生成模拟职位
        for i in range(limit):
            company = random.choice(companies)
            salary_range = random.choice(salary_ranges)
            education = random.choice(education_requirements)
            experience = random.choice(experience_requirements)
            
            # 获取技能集
            skills = skill_sets.get(job_type, ["Python", "Java", "JavaScript"])
            # 随机选择5-8个技能
            selected_skills = random.sample(skills, min(random.randint(5, 8), len(skills)))
            skills_str = "、".join(selected_skills[:3])
            
            # 生成职位描述
            description = description_template.format(
                job_type=job_type,
                education=education,
                experience=experience,
                skills=skills_str
            )
            
            # 提取经验年限
            experience_years = 0
            if experience != "经验不限":
                experience_match = re.search(r'(\d+)-(\d+)年', experience)
                if experience_match:
                    experience_years = int(experience_match.group(2))
            
            # 创建职位对象
            job = {
                "id": f"mock_{i}",
                "title": f"{job_type}",
                "company": company,
                "location": location,
                "salary_range": salary_range,
                "url": "",
                "platform": "模拟数据",
                "description": description,
                "required_skills": selected_skills,
                "education_requirement": education,
                "experience_requirement": experience_years
            }
            
            jobs.append(job)
        
        return jobs

def search_jobs_with_selenium(keywords: str, location: str = "北京", limit: int = 10, platform: str = "智联招聘") -> List[Dict[str, Any]]:
    """使用Selenium搜索职位的便捷函数
    
    Args:
        keywords: 搜索关键词
        location: 地点
        limit: 结果数量限制
        platform: 平台
    
    Returns:
        List[Dict[str, Any]]: 职位列表
    """
    scraper = JobScraper(headless=True)
    return scraper.search_jobs(keywords, location, platform, limit)

# 导出函数
__all__ = ['JobScraper', 'search_jobs_with_selenium']
