"""
测试修复后的web_scraper_selenium模块
"""
import os
import sys
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入修复后的模块
sys.path.append('/home/ubuntu')
try:
    from web_scraper_selenium_fixed import JobScraper, search_jobs_with_selenium
    logger.info("成功导入修复后的web_scraper_selenium模块")
except ImportError as e:
    logger.error(f"导入修复后的web_scraper_selenium模块失败: {str(e)}")
    sys.exit(1)

def test_job_scraper():
    """测试JobScraper类"""
    logger.info("开始测试JobScraper类")
    
    # 创建JobScraper实例
    try:
        scraper = JobScraper(headless=True)
        logger.info("成功创建JobScraper实例")
    except Exception as e:
        logger.error(f"创建JobScraper实例失败: {str(e)}")
        return False
    
    # 测试WebDriver初始化
    try:
        success = scraper._init_driver()
        if success:
            logger.info("WebDriver初始化成功")
        else:
            logger.error("WebDriver初始化失败")
            return False
    except Exception as e:
        logger.error(f"WebDriver初始化异常: {str(e)}")
        return False
    
    # 关闭WebDriver
    try:
        scraper._close_driver()
        logger.info("WebDriver关闭成功")
    except Exception as e:
        logger.error(f"WebDriver关闭异常: {str(e)}")
    
    return True

def test_search_jobs(platform="智联招聘", keywords="Python", location="北京", limit=3):
    """测试搜索职位功能"""
    logger.info(f"开始测试搜索职位功能 - 平台: {platform}, 关键词: {keywords}, 地点: {location}, 数量: {limit}")
    
    try:
        # 创建JobScraper实例
        scraper = JobScraper(headless=True)
        
        # 搜索职位
        jobs = scraper.search_jobs(keywords, location, platform, limit)
        
        if not jobs:
            logger.warning("未找到职位")
            return False
        
        logger.info(f"找到{len(jobs)}个职位")
        
        # 检查第一个职位的字段
        first_job = jobs[0]
        logger.info(f"第一个职位: {first_job.get('title')} - {first_job.get('company')}")
        logger.info(f"薪资范围: {first_job.get('salary_range')}")
        logger.info(f"经验要求: {first_job.get('experience_requirement')}")
        logger.info(f"经验年限: {first_job.get('experience_years')}")
        logger.info(f"平台: {first_job.get('platform')}")
        
        # 检查是否为模拟数据
        if first_job.get('platform') == "模拟数据":
            logger.warning("返回的是模拟数据，而不是实际抓取的数据")
            return False
        
        # 保存结果到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"test_results_{platform}_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到文件: {result_file}")
        
        return True
    except Exception as e:
        logger.error(f"测试搜索职位功能失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始测试修复后的web_scraper_selenium模块")
    
    # 测试JobScraper类
    if not test_job_scraper():
        logger.error("JobScraper类测试失败")
        return
    
    # 测试搜索职位功能 - 智联招聘
    if test_search_jobs(platform="智联招聘", keywords="Python", location="北京", limit=3):
        logger.info("智联招聘搜索测试成功")
    else:
        logger.warning("智联招聘搜索测试失败，尝试其他平台")
    
    # 测试搜索职位功能 - 前程无忧
    if test_search_jobs(platform="前程无忧", keywords="Java", location="上海", limit=3):
        logger.info("前程无忧搜索测试成功")
    else:
        logger.warning("前程无忧搜索测试失败，尝试其他平台")
    
    # 测试搜索职位功能 - BOSS直聘
    if test_search_jobs(platform="BOSS直聘", keywords="前端", location="深圳", limit=3):
        logger.info("BOSS直聘搜索测试成功")
    else:
        logger.warning("BOSS直聘搜索测试失败，尝试其他平台")
    
    # 测试搜索职位功能 - 拉勾网
    if test_search_jobs(platform="拉勾网", keywords="数据分析", location="杭州", limit=3):
        logger.info("拉勾网搜索测试成功")
    else:
        logger.warning("拉勾网搜索测试失败，尝试其他平台")
    
    # 测试搜索职位功能 - 猎聘网
    if test_search_jobs(platform="猎聘网", keywords="产品经理", location="广州", limit=3):
        logger.info("猎聘网搜索测试成功")
    else:
        logger.warning("猎聘网搜索测试失败")
    
    logger.info("测试完成")

if __name__ == "__main__":
    main()
