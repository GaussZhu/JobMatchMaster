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
                # 修复Python 3.11兼容性问题
                try:
                    # 新版webdriver_manager的用法
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e:
                    logger.warning(f"使用新版webdriver_manager失败: {str(e)}，尝试使用备用方法")
                    try:
                        # 直接使用Chrome，让系统自动查找ChromeDriver
                        self.driver = webdriver.Chrome(options=chrome_options)
                    except Exception as e2:
                        logger.error(f"备用方法也失败: {str(e2)}")
                        return False
            
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
                # 尝试提取经验年限数字
                if job_details['experience_requirement']:
                    experience_match = re.search(r'(\d+)-(\d+)年', job_details['experience_requirement'])
                    if experience_match:
                        job_details['experience_years'] = int(experience_match.group(2))
                    else:
                        job_details['experience_years'] = 0
        
        elif platform == "前程无忧":
            # 提取职位标题
            title_elem = soup.select_one('.cn h1')
            if title_elem:
                job_details['title'] = title_elem.text.strip()
            
            # 提取公司名称
            company_elem = soup.select_one('.cn .cname a')
            if company_elem:
                job_details['company'] = company_elem.text.strip()
            
            # 提取薪资范围
            salary_elem = soup.select_one('.cn .salary')
            if salary_elem:
                job_details['salary_range'] = salary_elem.text.strip()
            
            # 提取工作地点
            location_elem = soup.select_one('.cn .lname')
            if location_elem:
                job_details['location'] = location_elem.text.strip()
            
            # 提取职位描述
            description_elem = soup.select_one('.job_msg')
            if description_elem:
                job_details['description'] = description_elem.text.strip()
            
            # 提取要求技能
            skills = []
            skill_elems = soup.select('.sp4 span')
            for skill_elem in skill_elems:
                skills.append(skill_elem.text.strip())
            job_details['required_skills'] = skills
            
            # 提取教育和经验要求
            job_request = soup.select('.msg.ltype')
            if len(job_request) >= 3:
                job_details['education_requirement'] = job_request[0].text.strip()
                job_details['experience_requirement'] = job_request[1].text.strip()
                # 尝试提取经验年限数字
                if job_details['experience_requirement']:
                    experience_match = re.search(r'(\d+)-(\d+)年', job_details['experience_requirement'])
                    if experience_match:
                        job_details['experience_years'] = int(experience_match.group(2))
                    else:
                        job_details['experience_years'] = 0
        
        elif platform == "BOSS直聘":
            # 提取职位标题
            title_elem = soup.select_one('.job-banner .name')
            if title_elem:
                job_details['title'] = title_elem.text.strip()
            
            # 提取公司名称
            company_elem = soup.select_one('.company-info .name')
            if company_elem:
                job_details['company'] = company_elem.text.strip()
            
            # 提取薪资范围
            salary_elem = soup.select_one('.job-banner .salary')
            if salary_elem:
                job_details['salary_range'] = salary_elem.text.strip()
            
            # 提取工作地点
            location_elem = soup.select_one('.job-banner .location')
            if location_elem:
                job_details['location'] = location_elem.text.strip()
            
            # 提取职位描述
            description_elem = soup.select_one('.job-sec .text')
            if description_elem:
                job_details['description'] = description_elem.text.strip()
            
            # 提取要求技能
            skills = []
            skill_elems = soup.select('.job-tags span')
            for skill_elem in skill_elems:
                skills.append(skill_elem.text.strip())
            job_details['required_skills'] = skills
            
            # 提取教育和经验要求
            job_request = soup.select('.job-banner .info-primary p')
            if len(job_request) >= 2:
                requirements = job_request[0].text.strip().split('/')
                if len(requirements) >= 3:
                    job_details['experience_requirement'] = requirements[0].strip()
                    job_details['education_requirement'] = requirements[1].strip()
                    # 尝试提取经验年限数字
                    if job_details['experience_requirement']:
                        experience_match = re.search(r'(\d+)-(\d+)年', job_details['experience_requirement'])
                        if experience_match:
                            job_details['experience_years'] = int(experience_match.group(2))
                        else:
                            job_details['experience_years'] = 0
        
        elif platform == "拉勾网":
            # 提取职位标题
            title_elem = soup.select_one('.job-name')
            if title_elem:
                job_details['title'] = title_elem.text.strip()
            
            # 提取公司名称
            company_elem = soup.select_one('.company')
            if company_elem:
                job_details['company'] = company_elem.text.strip()
            
            # 提取薪资范围
            salary_elem = soup.select_one('.salary')
            if salary_elem:
                job_details['salary_range'] = salary_elem.text.strip()
            
            # 提取工作地点
            location_elem = soup.select_one('.work_addr')
            if location_elem:
                job_details['location'] = location_elem.text.strip().replace('查看地图', '')
            
            # 提取职位描述
            description_elem = soup.select_one('.job_bt div')
            if description_elem:
                job_details['description'] = description_elem.text.strip()
            
            # 提取要求技能
            skills = []
            skill_elems = soup.select('.job_request .labels li')
            for skill_elem in skill_elems:
                skills.append(skill_elem.text.strip())
            job_details['required_skills'] = skills
            
            # 提取教育和经验要求
            job_request = soup.select('.job_request p')
            if len(job_request) >= 1:
                requirements = job_request[0].text.strip().split('/')
                if len(requirements) >= 3:
                    job_details['experience_requirement'] = requirements[0].strip()
                    job_details['education_requirement'] = requirements[1].strip()
                    # 尝试提取经验年限数字
                    if job_details['experience_requirement']:
                        experience_match = re.search(r'(\d+)-(\d+)年', job_details['experience_requirement'])
                        if experience_match:
                            job_details['experience_years'] = int(experience_match.group(2))
                        else:
                            job_details['experience_years'] = 0
        
        elif platform == "猎聘网":
            # 提取职位标题
            title_elem = soup.select_one('.title-info h1')
            if title_elem:
                job_details['title'] = title_elem.text.strip()
            
            # 提取公司名称
            company_elem = soup.select_one('.company-name')
            if company_elem:
                job_details['company'] = company_elem.text.strip()
            
            # 提取薪资范围
            salary_elem = soup.select_one('.job-item-title')
            if salary_elem:
                job_details['salary_range'] = salary_elem.text.strip()
            
            # 提取工作地点
            location_elem = soup.select_one('.basic-infor span')
            if location_el<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>