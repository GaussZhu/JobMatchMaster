"""
AI简历职位匹配系统 - 网页抓取模块
使用Firecrawl MCP Server抓取招聘网站职位信息
"""
import os
import json
import time
import subprocess
import requests
from typing import List, Dict, Any, Optional, Union

class JobScraper:
    """招聘网站职位信息抓取类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化职位抓取器
        
        Args:
            api_key: Firecrawl API密钥，如果为None则尝试从环境变量获取
        """
        self.api_key = api_key or os.environ.get("FIRECRAWL_API_KEY")
        self.mcp_process = None
        self.mcp_url = "http://localhost:8787"  # MCP服务器默认地址
        
    def start_mcp_server(self) -> bool:
        """
        启动MCP服务器
        
        Returns:
            bool: 是否成功启动
        """
        if self.mcp_process is not None:
            print("MCP服务器已经在运行")
            return True
            
        try:
            # 使用subprocess启动MCP服务器
            env = os.environ.copy()
            env["FIRECRAWL_API_KEY"] = self.api_key
            
            self.mcp_process = subprocess.Popen(
                ["npx", "-y", "firecrawl-mcp"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            time.sleep(5)
            
            # 检查服务器是否正常运行
            try:
                response = requests.get(f"{self.mcp_url}/health")
                if response.status_code == 200:
                    print("MCP服务器启动成功")
                    return True
                else:
                    print(f"MCP服务器启动失败: {response.status_code}")
                    self.stop_mcp_server()
                    return False
            except requests.RequestException as e:
                print(f"无法连接到MCP服务器: {e}")
                self.stop_mcp_server()
                return False
                
        except Exception as e:
            print(f"启动MCP服务器时出错: {e}")
            return False
    
    def stop_mcp_server(self) -> None:
        """停止MCP服务器"""
        if self.mcp_process is not None:
            self.mcp_process.terminate()
            self.mcp_process = None
            print("MCP服务器已停止")
    
    def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        使用Firecrawl搜索工具搜索职位信息
        
        Args:
            keywords: 搜索关键词
            location: 位置信息
            limit: 结果数量限制
            
        Returns:
            List[Dict[str, Any]]: 职位信息列表
        """
        search_query = f"{keywords} {location} 招聘"
        
        # 构建搜索请求
        search_request = {
            "name": "firecrawl_search",
            "arguments": {
                "query": search_query,
                "limit": limit,
                "lang": "zh",
                "country": "cn",
                "scrapeOptions": {
                    "formats": ["markdown"],
                    "onlyMainContent": True
                }
            }
        }
        
        try:
            # 发送请求到MCP服务器
            response = requests.post(
                f"{self.mcp_url}/mcp",
                json=search_request
            )
            
            if response.status_code != 200:
                print(f"搜索请求失败: {response.status_code}")
                return []
                
            search_results = response.json()
            
            # 处理搜索结果
            job_listings = []
            
            if "content" in search_results and isinstance(search_results["content"], list):
                for item in search_results["content"]:
                    if "url" in item and "text" in item:
                        # 抓取每个搜索结果的详细内容
                        job_details = self.scrape_job_page(item["url"])
                        if job_details:
                            job_listings.append(job_details)
            
            return job_listings
            
        except Exception as e:
            print(f"搜索职位时出错: {e}")
            return []
    
    def scrape_job_page(self, url: str) -> Dict[str, Any]:
        """
        抓取职位详情页面
        
        Args:
            url: 职位页面URL
            
        Returns:
            Dict[str, Any]: 职位详情信息
        """
        # 构建抓取请求
        scrape_request = {
            "name": "firecrawl_scrape",
            "arguments": {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "waitFor": 1000,
                "timeout": 30000,
                "mobile": False,
                "includeTags": ["article", "main", "div.job-description", "div.job-detail"],
                "excludeTags": ["nav", "footer", "header", "aside"],
                "skipJsVerification": False
            }
        }
        
        try:
            # 发送请求到MCP服务器
            response = requests.post(
                f"{self.mcp_url}/mcp",
                json=scrape_request
            )
            
            if response.status_code != 200:
                print(f"抓取请求失败: {response.status_code}")
                return {}
                
            scrape_result = response.json()
            
            # 解析抓取结果，提取职位信息
            job_info = self._parse_job_content(scrape_result, url)
            return job_info
            
        except Exception as e:
            print(f"抓取职位页面时出错: {e}")
            return {}
    
    def batch_scrape_jobs(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        批量抓取多个职位页面
        
        Args:
            urls: 职位页面URL列表
            
        Returns:
            List[Dict[str, Any]]: 职位信息列表
        """
        if not urls:
            return []
            
        # 构建批量抓取请求
        batch_request = {
            "name": "firecrawl_batch_scrape",
            "arguments": {
                "urls": urls,
                "options": {
                    "formats": ["markdown"],
                    "onlyMainContent": True
                }
            }
        }
        
        try:
            # 发送请求到MCP服务器
            response = requests.post(
                f"{self.mcp_url}/mcp",
                json=batch_request
            )
            
            if response.status_code != 200:
                print(f"批量抓取请求失败: {response.status_code}")
                return []
                
            batch_result = response.json()
            
            # 获取批量操作ID
            if "content" in batch_result and isinstance(batch_result["content"], list):
                for item in batch_result["content"]:
                    if "text" in item and "batch_" in item["text"]:
                        batch_id = item["text"].split("batch_")[1].split(".")[0]
                        return self._check_batch_status(batch_id, urls)
            
            return []
            
        except Exception as e:
            print(f"批量抓取职位时出错: {e}")
            return []
    
    def _check_batch_status(self, batch_id: str, urls: List[str]) -> List[Dict[str, Any]]:
        """
        检查批量抓取状态并获取结果
        
        Args:
            batch_id: 批量操作ID
            urls: 原始URL列表，用于关联结果
            
        Returns:
            List[Dict[str, Any]]: 职位信息列表
        """
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # 构建状态检查请求
                status_request = {
                    "name": "firecrawl_check_batch_status",
                    "arguments": {
                        "id": f"batch_{batch_id}"
                    }
                }
                
                # 发送请求到MCP服务器
                response = requests.post(
                    f"{self.mcp_url}/mcp",
                    json=status_request
                )
                
                if response.status_code != 200:
                    print(f"批量状态检查请求失败: {response.status_code}")
                    time.sleep(2)
                    attempt += 1
                    continue
                    
                status_result = response.json()
                
                # 检查是否完成
                if "status" in status_result and status_result["status"] == "completed":
                    # 处理结果
                    job_listings = []
                    
                    if "results" in status_result and isinstance(status_result["results"], list):
                        for i, result in enumerate(status_result["results"]):
                            if i < len(urls):
                                job_info = self._parse_job_content(result, urls[i])
                                if job_info:
                                    job_listings.append(job_info)
                    
                    return job_listings
                
                # 如果还在处理中，等待后重试
                time.sleep(2)
                attempt += 1
                
            except Exception as e:
                print(f"检查批量状态时出错: {e}")
                time.sleep(2)
                attempt += 1
        
        print("批量抓取超时")
        return []
    
    def _parse_job_content(self, content: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        从抓取内容中解析职位信息
        
        Args:
            content: 抓取的内容
            url: 职位页面URL
            
        Returns:
            Dict[str, Any]: 解析后的职位信息
        """
        job_info = {
            'id': f"job_{hash(url) % 10000}",
            'url': url,
            'platform': self._extract_platform_from_url(url),
            'title': '',
            'company': '',
            'location': '',
            'description': '',
            'required_skills': [],
            'education_requirement': '',
            'experience_requirement': 0,
            'salary_range': '',
            'keywords': []
        }
        
        # 提取正文内容
        text_content = ""
        if "content" in content and isinstance(content["content"], list):
            for item in content["content"]:
                if "text" in item:
                    text_content += item["text"] + "\n"
        
        # 解析职位标题
        job_info['title'] = self._extract_job_title(text_content)
        
        # 解析公司名称
        job_info['company'] = self._extract_company_name(text_content)
        
        # 解析工作地点
        job_info['location'] = self._extract_location(text_content)
        
        # 解析职位描述
        job_info['description'] = self._extract_description(text_content)
        
        # 解析技能要求
        job_info['required_skills'] = self._extract_skills(text_content)
        
        # 解析教育要求
        job_info['education_requirement'] = self._extract_education(text_content)
        
        # 解析经验要求
        job_info['experience_requirement'] = self._extract_experience(text_content)
        
        # 解析薪资范围
        job_info['salary_range'] = self._extract_salary(text_content)
        
        # 提取关键词
        job_info['keywords'] = job_info['required_skills'][:3]
        
        return job_info
    
    def _extract_platform_from_url(self, url: str) -> str:
        """从URL中提取平台名称"""
        if "zhaopin.com" in url:
            return "智联招聘"
        elif "51job.com" in url:
            return "前程无忧"
        elif "liepin.com" in url:
            return "猎聘网"
        elif "lagou.com" in url:
            return "拉勾网"
        elif "boss.com" in url or "zhipin.com" in url:
            return "BOSS直聘"
        else:
            return "其他招聘平台"
    
    def _extract_job_title(self, text: str) -> str:
        """从文本中提取职位标题"""
        # 简单实现，实际应用中可以使用更复杂的NLP技术
        lines = text.split('\n')
        for line in lines[:10]:  # 通常标题在前几行
            line = line.strip()
            if len(line) > 0 and len(line) < 50:  # 标题通常不会太长
                return line
        return "未知职位"
    
    def _extract_company_name(self, text: str) -> str:
        """从文本中提取公司名称"""
        # 查找常见的公司名称标识
        company_indicators = ["公司：", "公司:", "企业名称：", "企业名称:"]
        for indicator in company_indicators:
            if indicator in text:
                start_idx = text.find(indicator) + len(indicator)
                end_idx = text.find("\n", start_idx)
                if end_idx > start_idx:
                    return text[start_idx:end_idx].strip()
        
        # 如果没有找到明确标识，尝试从前几行提取
        lines = text.split('\n')
        for line in lines[1:15]:  # 跳过第一行（可能是标题）
            line = line.strip()
            if len(line) > 0 and len(line) < 50 and "招聘" not in line and "职位" not in line:
                return line
        
        return "未知公司"
    
    def _extract_location(self, text: str) -> str:
        """从文本中提取工作地点"""
        # 查找常见的地点标识
        location_indicators = ["工作地点：", "工作地点:", "地点：", "地点:", "工作城市：", "工作城市:"]
        for indicator in location_indicators:
            if indicator in text:
                start_idx = text.find(indicator) + len(indicator)
                end_idx = text.find("\n", start_idx)
                if end_idx > start_idx:
                    return text[start_idx:end_idx].strip()
        
        # 如果没有找到明确标识，尝试识别常见城市名称
        common_cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "苏州", "天津", "重庆"]
        for city in common_cities:
            if city in text[:500]:  # 只在前面部分查找
                return city
        
        return "未知地点"
    
    def _extract_description(self, text: str) -> str:
        """从文本中提取职位描述"""
        # 查找常见的描述标识
        desc_indicators = ["职位描述", "工作职责", "岗位职责", "工作内容", "岗位描述"]
        for indicator in desc_indicators:
            if indicator in text:
                start_idx = text.find(indicator)
                # 找到下一个主要部分的开始
                next_sections = ["任职要求", "岗位要求", "职位要求", "技能要求", "薪资福利"]
                end_idx = len(text)
                for section in next_sections:
                    section_idx = text.find(section, start_idx)
                    if section_idx > start_idx and section_idx < end_idx:
                        end_idx = section_idx
                
                description = text[start_idx:end_idx].strip()
                if len(description) > 10:  # 确保描述不是太短
                    return description
        
        # 如果没有找到明确标识，返回前300个字符作为描述
        if len(text) > 300:
            return text[:300] + "..."
        return text
    
    def _extract_skills(self, text: str) -> List[str]:
        """从文本中提取技能要求"""
        skills = []
        
        # 常见技术技能列表
        common_skills = [
            "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring", "Spring Boot",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Git",
            "HTML", "CSS", "TypeScript", "Swift", "Kotlin", "Objective-C",
            "TensorFlow", "PyTorch", "机器学习", "深度学习", "人工智能", "数据分析",
            "微服务", "RESTful API", "GraphQL", "DevOps", "CI/CD"
        ]
        
        # 在文本中查找这些技能
        for skill in common_skills:
            if skill in text:
                skills.append(skill)
        
        # 如果没有找到任何技能，尝试从要求部分提取
        if not skills:
            req_indicators = ["任职要求", "岗位要求", "职位要求", "技能要求"]
            for indicator in req_indicators:
                if indicator in text:
                    start_idx = text.find(indicator)
                    # 提取要求部分的前300个字符
                    req_text = text[start_idx:start_idx+300]
                    # 按行分割并查找可能的技能
                    for line in req_text.split('\n'):
                        if line.strip().startswith("- ") or line.strip().startswith("• "):
                            skill_candidate = line.strip()[2:].split("，")[0].split(",")[0]
                            if len(skill_candidate) < 20:  # 技能名称通常不会太长
                                skills.append(skill_candidate)
        
        # 如果仍然没有找到技能，返回一些通用技能
        if not skills:
            return ["沟通能力", "团队协作", "解决问题能力"]
        
        return skills[:10]  # 限制最多返回10个技能
    
    def _extract_education(self, text: str) -> str:
        """从文本中提取教育要求"""
        # 查找常见的教育要求标识
        edu_indicators = ["学历要求", "学历：", "学历:", "教育背景", "教育经历"]
        for indicator in edu_indicators:
            if indicator in text:
                start_idx = text.find(indicator) + len(indicator)
                end_idx = text.find("\n", start_idx)
                if end_idx > start_idx:
                    edu_text = text[start_idx:end_idx].strip()
                    # 提取学历级别
                    edu_levels = ["博士", "硕士", "本科", "大专", "高中"]
                    for level in edu_levels:
                        if level in edu_text:
                            return level
        
        # 直接在文本中查找学历级别
        edu_levels = ["博士", "硕士", "本科", "大专", "高中"]
        for level in edu_levels:
            if level in text:
                return level
        
        return "本科"  # 默认返回本科
    
    def _extract_experience(self, text: str) -> int:
        """从文本中提取经验要求，返回年数"""
        # 查找常见的经验要求标识
        exp_indicators = ["经验要求", "工作经验", "经验：", "经验:"]
        for indicator in exp_indicators:
            if indicator in text:
                start_idx = text.find(indicator) + len(indicator)
                end_idx = text.find("\n", start_idx)
                if end_idx > start_idx:
                    exp_text = text[start_idx:end_idx].strip()
                    # 提取数字
                    import re
                    numbers = re.findall(r'\d+', exp_text)
                    if numbers:
                        return int(numbers[0])
        
        # 直接在文本中查找经验年数模式
        import re
        patterns = [
            r'(\d+)[年|+]以上经验',
            r'(\d+)年以上',
            r'经验(\d+)年以上',
            r'至少(\d+)年'
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                return int(matches.group(1))
        
        # 查找经验范围
        range_pattern = r'(\d+)-(\d+)年'
        matches = re.search(range_pattern, text)
        if matches:
            # 取范围的平均值
            min_years = int(matches.group(1))
            max_years = int(matches.group(2))
            return (min_years + max_years) // 2
        
        return 1  # 默认返回1年经验
    
    def _extract_salary(self, text: str) -> str:
        """从文本中提取薪资范围"""
        # 查找常见的薪资标识
        salary_indicators = ["薪资：", "薪资:", "月薪：", "月薪:", "薪资范围", "薪酬：", "薪酬:"]
        for indicator in salary_indicators:
            if indicator in text:
                start_idx = text.find(indicator) + len(indicator)
                end_idx = text.find("\n", start_idx)
                if end_idx > start_idx:
                    salary_text = text[start_idx:end_idx].strip()
                    return salary_text
        
        # 直接在文本中查找薪资模式
        import re
        patterns = [
            r'(\d+)k-(\d+)k',
            r'(\d+)-(\d+)k',
            r'(\d+)K-(\d+)K',
            r'(\d+)-(\d+)K',
            r'(\d+)万-(\d+)万',
            r'月薪(\d+)-(\d+)',
            r'(\d+)000-(\d+)000'
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                min_salary = matches.group(1)
                max_salary = matches.group(2)
                return f"{min_salary}k-{max_salary}k"
        
        return "面议"  # 默认返回面议


# 适配现有应用的接口
def search_jobs_with_mcp(keywords: str, location: str = "", limit: int = 10, platform: str = "MCP抓取") -> List[Dict[str, Any]]:
    """
    使用MCP抓取招聘网站职位信息的接口函数，适配现有应用
    
    Args:
        keywords: 搜索关键词
        location: 位置信息
        limit: 结果数量限制
        platform: 平台标识
        
    Returns:
        List[Dict[str, Any]]: 职位信息列表
    """
    # 获取API密钥
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("警告: 未设置FIRECRAWL_API_KEY环境变量，将使用模拟数据")
        # 导入原始模拟数据生成函数
        from streamlit_app import search_jobs as search_jobs_mock
        return search_jobs_mock(keywords, location, limit, platform)
    
    # 创建抓取器实例
    scraper = JobScraper(api_key)
    
    # 启动MCP服务器
    if not scraper.start_mcp_server():
        print("启动MCP服务器失败，将使用模拟数据")
        # 导入原始模拟数据生成函数
        from streamlit_app import search_jobs as search_jobs_mock
        return search_jobs_mock(keywords, location, limit, platform)
    
    try:
        # 搜索职位
        jobs = scraper.search_jobs(keywords, location, limit)
        
        # 如果没有找到职位，使用模拟数据
        if not jobs:
            print("未找到职位信息，将使用模拟数据")
            # 导入原始模拟数据生成函数
            from streamlit_app import search_jobs as search_jobs_mock
            return search_jobs_mock(keywords, location, limit, platform)
        
        return jobs
    finally:
        # 确保停止MCP服务器
        scraper.stop_mcp_server()


if __name__ == "__main__":
    # 测试代码
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if api_key:
        scraper = JobScraper(api_key)
        if scraper.start_mcp_server():
            try:
                print("测试搜索职位...")
                jobs = scraper.search_jobs("Python开发", "北京", 3)
                print(f"找到{len(jobs)}个职位")
                for job in jobs:
                    print(f"标题: {job['title']}")
                    print(f"公司: {job['company']}")
                    print(f"地点: {job['location']}")
                    print(f"技能: {job['required_skills']}")
                    print("---")
            finally:
                scraper.stop_mcp_server()
    else:
        print("请设置FIRECRAWL_API_KEY环境变量进行测试")
