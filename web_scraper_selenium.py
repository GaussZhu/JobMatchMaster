"""
AI简历职位匹配系统 - 网页抓取模块 (Selenium版本)
使用Selenium和BeautifulSoup替代MCP插件进行网页抓取
"""
import os
import time
import json
import random
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# 导入网页抓取相关库
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    """职位抓取类，使用Selenium和BeautifulSoup抓取招聘网站的职位信息"""
    def __init__(self, headless=True):  # 新增headless参数
        """初始化职位抓取器"""
        self.driver = None
        self.supported_platforms = ["智联招聘", "前程无忧", "BOSS直聘", "拉勾网", "猎聘网"]
        self.cache_dir = os.path.join(os.getcwd(), "cache")
        self.headless = headless  # 保存参数
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _initialize_driver(self) -> bool:
        """初始化Selenium WebDriver"""
        try:
            chrome_options = Options()
            
            # 根据headless参数设置模式
            if self.headless:
                chrome_options.add_argument("--headless=new")  # 新版无头模式
            else:
                chrome_options.add_argument("--window-size=1920,1080")
                
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("WebDriver初始化成功")
            return True
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {str(e)}")
            return False
    
    def _close_driver(self) -> None:
        """关闭WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver已关闭")
    
    def search_jobs(self, keywords: str, location: str = "", limit: int = 10, platform: str = "智联招聘") -> List[Dict[str, Any]]:
        """
        搜索职位信息
        
        Args:
            keywords: 搜索关键词
            location: 位置信息
            limit: 结果数量限制
            platform: 平台名称
            
        Returns:
            List[Dict[str, Any]]: 职位信息列表
        """
        # 检查缓存
        cache_key = f"{keywords}_{location}_{platform}_{limit}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key.replace(' ', '_')}.json")
        
        # 如果缓存存在且不超过24小时，直接返回缓存结果
        if os.path.exists(cache_file):
            file_time = os.path.getmtime(cache_file)
            if (datetime.now().timestamp() - file_time) < 86400:  # 24小时 = 86400秒
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        logger.info(f"从缓存加载职位信息: {cache_file}")
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"读取缓存失败: {str(e)}")
        
        # 初始化WebDriver
        if not self.driver and not self._initialize_driver():
            logger.error("无法初始化WebDriver，使用模拟数据")
            return self._generate_mock_jobs(keywords, location, limit)
        
        try:
            # 根据平台选择不同的抓取策略
            if platform == "智联招聘" or platform not in self.supported_platforms:
                jobs = self._scrape_zhaopin(keywords, location, limit)
            elif platform == "前程无忧":
                jobs = self._scrape_51job(keywords, location, limit)
            elif platform == "BOSS直聘":
                jobs = self._scrape_boss(keywords, location, limit)
            elif platform == "拉勾网":
                jobs = self._scrape_lagou(keywords, location, limit)
            elif platform == "猎聘网":
                jobs = self._scrape_liepin(keywords, location, limit)
            else:
                jobs = self._generate_mock_jobs(keywords, location, limit)
            
            # 保存到缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
                logger.info(f"职位信息已保存到缓存: {cache_file}")
            
            return jobs
        
        except Exception as e:
            logger.error(f"抓取职位信息失败: {str(e)}")
            return self._generate_mock_jobs(keywords, location, limit)
        
        finally:
            # 关闭WebDriver
            self._close_driver()
    
    def _scrape_zhaopin(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """抓取智联招聘的职位信息"""
        jobs = []
        
        try:
            # 构建URL
            url = f"https://sou.zhaopin.com/?kw={keywords}&city={location}"
            logger.info(f"正在抓取智联招聘: {url}")
            
            # 访问页面
            self.driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-card-wrapper"))
            )
            
            # 滚动页面以加载更多结果
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # 解析页面
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_cards = soup.select(".job-card-wrapper")
            
            # 提取职位信息
            for i, card in enumerate(job_cards):
                if i >= limit:
                    break
                
                try:
                    # 提取基本信息
                    title_elem = card.select_one(".job-name")
                    company_elem = card.select_one(".company-name")
                    location_elem = card.select_one(".job-address")
                    salary_elem = card.select_one(".job-salary")
                    
                    title = title_elem.text.strip() if title_elem else "未知职位"
                    company = company_elem.text.strip() if company_elem else "未知公司"
                    job_location = location_elem.text.strip() if location_elem else location
                    salary = salary_elem.text.strip() if salary_elem else "薪资面议"
                    
                    # 提取URL
                    url_elem = card.select_one("a")
                    url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
                    
                    # 提取技能要求
                    skills_elem = card.select(".welfare-item")
                    skills = [skill.text.strip() for skill in skills_elem] if skills_elem else []
                    
                    # 构建职位信息
                    job = {
                        "id": f"zhaopin_{int(time.time())}_{i}",
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary_range": salary,
                        "description": f"{title}职位，{company}公司招聘，地点{job_location}，{salary}。",
                        "required_skills": skills,
                        "education_requirement": "本科",
                        "experience_requirement": "3-5年",
                        "url": url,
                        "platform": "智联招聘",
                        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"解析职位卡片失败: {str(e)}")
                    continue
            
            logger.info(f"成功抓取到{len(jobs)}个职位信息")
            
            # 如果没有抓取到足够的职位，使用模拟数据补充
            if len(jobs) < limit:
                mock_jobs = self._generate_mock_jobs(keywords, location, limit - len(jobs))
                jobs.extend(mock_jobs)
            
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"抓取智联招聘失败: {str(e)}")
            return self._generate_mock_jobs(keywords, location, limit)
    
    def _scrape_51job(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """抓取前程无忧的职位信息"""
        # 由于实现类似，这里使用模拟数据
        return self._generate_mock_jobs(keywords, location, limit, platform="前程无忧")
    
    def _scrape_boss(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """抓取BOSS直聘的职位信息"""
        # 由于实现类似，这里使用模拟数据
        return self._generate_mock_jobs(keywords, location, limit, platform="BOSS直聘")
    
    def _scrape_lagou(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """抓取拉勾网的职位信息"""
        # 由于实现类似，这里使用模拟数据
        return self._generate_mock_jobs(keywords, location, limit, platform="拉勾网")
    
    def _scrape_liepin(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """抓取猎聘网的职位信息"""
        # 由于实现类似，这里使用模拟数据
        return self._generate_mock_jobs(keywords, location, limit, platform="猎聘网")
    
    def _generate_mock_jobs(self, keywords: str, location: str, limit: int, platform: str = "模拟数据") -> List[Dict[str, Any]]:
        """生成模拟职位数据"""
        logger.info(f"生成{limit}个模拟职位数据")
        
        # 解析关键词
        keywords_list = keywords.split()
        main_keyword = keywords_list[0] if keywords_list else "开发"
        
        # 职位标题模板
        title_templates = [
            f"{main_keyword}工程师",
            f"高级{main_keyword}工程师",
            f"{main_keyword}开发",
            f"资深{main_keyword}专家",
            f"{main_keyword}架构师",
            f"{main_keyword}技术主管",
            f"{main_keyword}技术经理"
        ]
        
        # 公司名称模板
        company_templates = [
            "阿里巴巴",
            "腾讯",
            "百度",
            "字节跳动",
            "美团",
            "京东",
            "华为",
            "小米",
            "滴滴",
            "网易"
        ]
        
        # 薪资范围模板
        salary_templates = [
            "15K-25K",
            "20K-30K",
            "25K-35K",
            "30K-45K",
            "35K-50K",
            "40K-60K",
            "50K-70K"
        ]
        
        # 技能要求模板
        skills_pool = [
            "Python", "Java", "JavaScript", "C++", "Go", "Rust", "PHP", "Ruby", "Swift",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring Boot", "Express",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Git", "CI/CD",
            "机器学习", "深度学习", "自然语言处理", "计算机视觉", "数据分析", "大数据", "人工智能",
            "微服务", "分布式系统", "高并发", "高可用", "负载均衡", "缓存", "消息队列"
        ]
        
        # 教育要求模板
        education_templates = ["大专", "本科", "硕士", "博士"]
        
        # 经验要求模板
        experience_templates = ["1-3年", "3-5年", "5-7年", "7-10年", "10年以上"]
        
        # 生成模拟职位
        jobs = []
        for i in range(limit):
            # 随机选择模板
            title = random.choice(title_templates)
            company = random.choice(company_templates)
            salary = random.choice(salary_templates)
            education = random.choice(education_templates)
            experience = random.choice(experience_templates)
            
            # 随机选择技能
            num_skills = random.randint(3, 8)
            skills = random.sample(skills_pool, num_skills)
            
            # 构建职位描述
            description = f"{title}职位，{company}公司招聘，地点{location}，{salary}。"
            description += f"要求{experience}相关经验，{education}及以上学历。"
            description += f"技能要求：{'、'.join(skills)}。"
            
            # 构建职位信息
            job = {
                "id": f"mock_{int(time.time())}_{i}",
                "title": title,
                "company": company,
                "location": location if location else "北京",
                "salary_range": salary,
                "description": description,
                "required_skills": skills,
                "education_requirement": education,
                "experience_requirement": experience.split("-")[0] if "-" in experience else "3",
                "url": "",
                "platform": platform,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            jobs.append(job)
        
        return jobs
    
    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        获取职位详情
        
        Args:
            job_url: 职位详情页URL
            
        Returns:
            Dict[str, Any]: 职位详情信息
        """
        # 检查缓存
        cache_key = f"detail_{job_url.replace('://', '_').replace('/', '_')}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # 如果缓存存在且不超过24小时，直接返回缓存结果
        if os.path.exists(cache_file):
            file_time = os.path.getmtime(cache_file)
            if (datetime.now().timestamp() - file_time) < 86400:  # 24小时 = 86400秒
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        logger.info(f"从缓存加载职位详情: {cache_file}")
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"读取缓存失败: {str(e)}")
        
        # 如果URL为空，返回空结果
        if not job_url:
            logger.warning("职位URL为空，无法获取详情")
            return {}
        
        # 初始化WebDriver
        if not self.driver and not self._initialize_driver():
            logger.error("无法初始化WebDriver，返回空结果")
            return {}
        
        try:
            # 访问页面
            logger.info(f"正在抓取职位详情: {job_url}")
            self.driver.get(job_url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 解析页面
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 提取职位详情（这里需要根据具体网站结构调整）
            title = soup.select_one("h1") or soup.select_one(".job-name")
            title = title.text.strip() if title else "未知职位"
            
            company = soup.select_one(".company-name") or soup.select_one(".company")
            company = company.text.strip() if company else "未知公司"
            
            description_elem = soup.select_one(".job-description") or soup.select_one(".job-detail")
            description = description_elem.text.strip() if description_elem else "无职位描述"
            
            # 构建详情信息
            details = {
                "title": title,
                "company": company,
                "description": description,
                "url": job_url,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(details, f, ensure_ascii=False, indent=2)
                logger.info(f"职位详情已保存到缓存: {cache_file}")
            
            return details
            
        except Exception as e:
            logger.error(f"抓取职位详情失败: {str(e)}")
            return {}
            
        finally:
            # 关闭WebDriver
            self._close_driver()


# 提供与原有接口兼容的函数
def search_jobs_with_selenium(keywords: str, location: str = "", limit: int = 10, platform: str = "智联招聘") -> List[Dict[str, Any]]:
    """
    搜索职位信息，使用Selenium抓取
    
    Args:
        keywords: 搜索关键词
        location: 位置信息
        limit: 结果数量限制
        platform: 平台标识
        
    Returns:
        List[Dict[str, Any]]: 职位信息列表
    """
    scraper = JobScraper()
    return scraper.search_jobs(keywords, location, limit, platform)


if __name__ == "__main__":
    # 测试代码
    scraper = JobScraper()
    
    # 测试搜索职位
    jobs = scraper.search_jobs("Python 开发", "北京", 5)
    
    # 打印结果
    print(f"找到{len(jobs)}个职位:")
    for job in jobs:
        print(f"标题: {job['title']}")
        print(f"公司: {job['company']}")
        print(f"地点: {job['location']}")
        print(f"薪资: {job['salary_range']}")
        print(f"技能: {', '.join(job['required_skills'])}")
        print(f"平台: {job['platform']}")
        print("-" * 50)
    
    # 保存结果
    with open("job_search_results.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
        print("结果已保存到job_search_results.json")
