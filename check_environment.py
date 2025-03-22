#!/usr/bin/env python3
"""
检查环境配置和必要库的安装情况
"""
import sys
import importlib.util
import os

def check_module(module_name):
    """检查模块是否已安装"""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"- {module_name} 未安装")
        return False
    else:
        print(f"- {module_name} 已安装")
        return True

def main():
    """主函数"""
    print("Python版本:", sys.version)
    print("\n检查必要库:")
    
    # 检查核心库
    required_modules = [
        "streamlit",
        "selenium",
        "bs4",  # BeautifulSoup
        "pandas",
        "numpy",
        "webdriver_manager"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    # 检查项目文件
    print("\n检查项目文件:")
    required_files = [
        "streamlit_app_enhanced_selenium.py",
        "web_scraper_selenium.py",
        "resume_analyzer.py",
        "job_search_integration_selenium.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"- {file} 存在")
        else:
            print(f"- {file} 不存在")
    
    # 总结
    if missing_modules:
        print("\n缺少以下库，请安装:")
        for module in missing_modules:
            print(f"  pip install {module}")
    else:
        print("\n所有必要库已安装")

if __name__ == "__main__":
    main()
