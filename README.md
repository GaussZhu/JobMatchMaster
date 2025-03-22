# JobMatchMaster - AI简历职位匹配系统

JobMatchMaster是一个基于AI的简历分析与招聘精准匹配系统，它能够分析用户的简历，从招聘网站抓取真实职位信息，并计算简历与职位的匹配度，提供个性化的改进建议。

## 主要功能

1. **简历解析与分析**：自动提取简历中的关键信息，包括个人信息、教育背景、工作经验和技能
2. **职位信息抓取**：使用Selenium和BeautifulSoup从招聘网站抓取真实职位信息
3. **多维度匹配计算**：从技能、教育、经验和职业方向多个维度计算匹配度
4. **个性化改进建议**：为每个匹配的职位提供针对性的简历改进建议
5. **美观的用户界面**：提供直观、美观的交互体验

## 安装指南

### 环境要求

- Python 3.8+
- Chrome浏览器（用于Selenium网页抓取）

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/GaussZhu/JobMatchMaster.git
cd JobMatchMaster
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
streamlit run streamlit_app_enhanced_selenium.py
```

## 使用方法

1. 启动应用后，在浏览器中打开显示的URL
2. 上传您的简历或使用示例简历
3. 设置职位搜索条件（关键词、地点、数据来源等）
4. 点击"开始分析"按钮
5. 查看分析结果和匹配职位

## 文件说明

- `streamlit_app_enhanced_selenium.py`: 主应用文件，包含Streamlit界面代码
- `web_scraper_selenium.py`: 网页抓取模块，使用Selenium和BeautifulSoup抓取招聘网站信息
- `resume_analyzer.py`: 简历分析模块，提供简历解析和分析功能
- `job_search_integration_selenium.py`: 集成模块，将网页抓取和简历分析功能结合
- `requirements.txt`: 依赖列表
- `config.toml`: Streamlit配置文件

## 在Streamlit Cloud上部署

1. 登录[Streamlit Cloud](https://streamlit.io/cloud)
2. 点击"New app"按钮
3. 选择您的GitHub仓库、分支和主应用文件(`streamlit_app_enhanced_selenium.py`)
4. 点击"Deploy"按钮

注意：在Streamlit Cloud上部署时，可能需要添加一些环境变量或secrets，具体取决于您的配置。

## 注意事项

- 首次搜索职位时可能需要较长时间，因为系统需要启动Chrome浏览器并抓取网页
- 为避免被招聘网站封锁，系统会在请求之间添加随机延迟
- 抓取结果会缓存24小时，以提高性能并减少对招聘网站的请求

## 贡献指南

欢迎提交问题报告和功能请求！如果您想贡献代码，请遵循以下步骤：

1. Fork仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件
