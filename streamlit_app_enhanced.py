"""
AI简历职位匹配系统 - 增强版
集成MCP网页抓取和增强版简历分析功能
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import random
import time
import datetime

# 导入集成模块
from job_search_integration import JobSearchIntegration, get_enhanced_functions

# 配置页面
st.set_page_config(
    page_title="AI简历职位匹配系统",
    page_icon="📝",
    layout="wide"
)

#################################################
# 自定义CSS样式
#################################################

def apply_custom_css():
    """应用自定义CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式 */
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* 标题样式 */
    .title {
        color: #2E7D32;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E0E0E0;
    }
    
    .subtitle {
        color: #455A64;
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    /* 卡片样式 */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #2E7D32;
    }
    
    .job-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
        border-left: 5px solid #1976D2;
    }
    
    .job-card:hover {
        transform: translateY(-5px);
    }
    
    /* 匹配分数样式 */
    .match-score {
        font-size: 2rem;
        font-weight: 700;
        color: #2E7D32;
        text-align: center;
        margin: 1rem 0;
    }
    
    .match-score-container {
        background-color: #F1F8E9;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background-color: #E0E0E0;
        margin: 1rem 0;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        font-weight: 500;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin-top: 1rem;
    }
    
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    
    /* 信息面板 */
    .info-panel {
        background-color: #E3F2FD;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1976D2;
    }
    
    /* 进度条样式 */
    .progress-container {
        width: 100%;
        background-color: #E0E0E0;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 10px;
        border-radius: 10px;
        background-color: #2E7D32;
    }
    
    /* 响应式布局调整 */
    @media (max-width: 768px) {
        .title {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1.2rem;
        }
        
        .card, .job-card {
            padding: 1rem;
        }
    }
    
    /* 新增样式 - 建议面板 */
    .suggestion-panel {
        background-color: #FFF8E1;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 5px solid #FFA000;
    }
    
    /* 新增样式 - 分析结果面板 */
    .analysis-panel {
        background-color: #F3E5F5;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #7B1FA2;
    }
    
    /* 新增样式 - 职业方向标签 */
    .direction-tag {
        display: inline-block;
        background-color: #E1F5FE;
        color: #0288D1;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* 新增样式 - 技能类别标签 */
    .skill-category-tag {
        display: inline-block;
        background-color: #F1F8E9;
        color: #558B2F;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* 新增样式 - 加载动画 */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    
    /* 新增样式 - 职位URL链接 */
    .job-url {
        color: #1976D2;
        text-decoration: none;
        font-weight: 500;
    }
    
    .job-url:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

#################################################
# 侧边栏和配置
#################################################

def create_sidebar():
    """创建侧边栏配置"""
    with st.sidebar:
        st.markdown("### 配置")
        
        # 上传简历
        uploaded_file = st.file_uploader("上传简历", type=["pdf", "docx", "txt", "json"])
        
        # 使用示例简历
        use_example = st.checkbox("使用示例简历", value=not bool(uploaded_file))
        
        # 职位搜索配置
        st.markdown("### 职位搜索")
        job_keywords = st.text_input("职位关键词", value="Python 开发")
        job_location = st.text_input("地点", value="北京")
        job_limit = st.slider("搜索结果数量", min_value=5, max_value=20, value=10, step=5)
        
        # 搜索平台选择
        platform_options = ["MCP抓取", "模拟数据"]
        platform = st.selectbox("数据来源", options=platform_options)
        
        # 高级选项
        st.markdown("### 高级选项")
        use_ai = st.checkbox("启用AI增强分析", value=True)
        
        # 显示API密钥配置
        show_api_config = st.checkbox("显示API配置", value=False)
        if show_api_config:
            api_key = st.text_input("Firecrawl API密钥", type="password")
            if api_key:
                os.environ["FIRECRAWL_API_KEY"] = api_key
                st.success("API密钥已设置")
        
        # 开始按钮
        start_button = st.button("开始分析")
        
        return {
            "uploaded_file": uploaded_file,
            "use_example": use_example,
            "job_keywords": job_keywords,
            "job_location": job_location,
            "job_limit": job_limit,
            "platform": platform,
            "use_ai": use_ai,
            "start_button": start_button
        }

#################################################
# 显示函数
#################################################

def display_welcome():
    """显示欢迎信息"""
    st.markdown("""
    <div class="card">
        <h3>欢迎使用AI简历职位匹配系统</h3>
        <p>本系统可以帮助您：</p>
        <ul>
            <li>分析简历，提取关键信息</li>
            <li>搜索匹配的职位信息</li>
            <li>计算简历与职位的匹配度</li>
            <li>提供针对性的简历改进建议</li>
        </ul>
        <p>开始使用：</p>
        <ol>
            <li>上传您的简历或使用示例简历</li>
            <li>设置职位搜索条件</li>
            <li>点击"开始分析"按钮</li>
        </ol>
        <div class="info-panel">
            <p><strong>新功能：</strong> 现在支持从真实招聘网站抓取职位信息，提供更准确的匹配结果！</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_resume_summary(resume_data):
    """显示简历摘要"""
    resume_summary = resume_data['personal_info']
    
    st.markdown('<h3 class="subtitle">简历摘要</h3>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="card">
        <h4>{resume_summary.get('name', '未知')}</h4>
        <p>{resume_summary.get('summary', '')}</p>
        <div class="divider"></div>
        <p><strong>联系方式：</strong> {resume_summary.get('phone', '未知')} | {resume_summary.get('email', '未知')}</p>
        <p><strong>地点：</strong> {resume_summary.get('location', '未知')}</p>
        <div class="divider"></div>
        <p><strong>技能：</strong></p>
        <div>
            {''.join(f'<span class="tag">{skill}</span>' for skill in resume_data['skills'][:10])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_resume_analysis(analysis_results):
    """显示简历分析结果"""
    st.markdown('<h3 class="subtitle">简历分析</h3>', unsafe_allow_html=True)
    
    # 提取分析结果
    personal_summary = analysis_results['personal_summary']
    skills_analysis = analysis_results['skills_analysis']
    education_analysis = analysis_results['education_analysis']
    experience_analysis = analysis_results['experience_analysis']
    career_direction = analysis_results['career_direction']
    overall_score = analysis_results['overall_score']
    
    # 显示综合评分
    st.markdown(f"""
    <div class="analysis-panel">
        <h4>综合评分: {overall_score['overall_score']}/100</h4>
        <p><strong>级别:</strong> {overall_score['level']}</p>
        <div class="progress-container">
            <div class="progress-bar" style="width: {overall_score['overall_score']}%;"></div>
        </div>
        <div class="divider"></div>
        <p><strong>技能评分:</strong> {overall_score['component_scores']['skills']}/100</p>
        <div class="progress-container">
            <div class="progress-bar" style="width: {overall_score['component_scores']['skills']}%;"></div>
        </div>
        <p><strong>教育评分:</strong> {overall_score['component_scores']['education']}/100</p>
        <div class="progress-container">
            <div class="progress-bar" style="width: {overall_score['component_scores']['education']}%;"></div>
        </div>
        <p><strong>经验评分:</strong> {overall_score['component_scores']['experience']}/100</p>
        <div class="progress-container">
            <div class="progress-bar" style="width: {overall_score['component_scores']['experience']}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示职业方向
    st.markdown(f"""
    <div class="analysis-panel">
        <h4>职业方向分析</h4>
        <p><strong>主要方向:</strong> <span class="direction-tag">{career_direction['primary_direction']}</span> ({career_direction['primary_score']:.1f}%)</p>
        <p><strong>次要方向:</strong> <span class="direction-tag">{career_direction['secondary_direction']}</span> ({career_direction['secondary_score']:.1f}%)</p>
        <p><strong>方向确定性:</strong> {
            "高" if career_direction['direction_confidence'] == 'high' else 
            "中" if career_direction['direction_confidence'] == 'medium' else "低"
        }</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示技能分析
    skill_categories_html = ""
    for category, count in skills_analysis['skill_categories'].items():
        skill_categories_html += f'<span class="skill-category-tag">{category} ({count})</span>'
    
    st.markdown(f"""
    <div class="analysis-panel">
        <h4>技能分析</h4>
        <p><strong>技能数量:</strong> {skills_analysis['skill_count']}</p>
        <p><strong>技能水平:</strong> {skills_analysis['skill_level']}</p>
        <p><strong>主要技能:</strong> {', '.join(skills_analysis['primary_skills'][:5])}</p>
        <p><strong>技能类别:</strong></p>
        <div>{skill_categories_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示教育和经验分析
    st.markdown(f"""
    <div class="analysis-panel">
        <h4>教育与经验</h4>
        <p><strong>最高学历:</strong> {education_analysis['education_level']}</p>
        <p><strong>是否计算机相关专业:</strong> {"是" if education_analysis['is_cs_related'] else "否"}</p>
        <p><strong>是否知名院校:</strong> {"是" if education_analysis['top_university'] else "否"}</p>
        <div class="divider"></div>
        <p><strong>工作年限:</strong> {experience_analysis['years']}年</p>
        <p><strong>公司层级:</strong> {experience_analysis['company_tier']}</p>
        <p><strong>职位级别:</strong> {experience_analysis['position_level']}</p>
        <p><strong>是否有管理经验:</strong> {"是" if experience_analysis['has_management_experience'] else "否"}</p>
    </div>
    """, unsafe_allow_html=True)

def display_job_matches(match_results, jobs):
    """显示职位匹配结果"""
    st.markdown('<h3 class="subtitle">职位匹配结果</h3>', unsafe_allow_html=True)
    
    for match in match_results:
        job_id = match['job_id']
        job = next((j for j in jobs if j['id'] == job_id), None)
        
        if not job:
            continue
        
        # 计算各项匹配度的进度条宽度
        match_score = match['match_score']
        skill_match = match.get('skill_match', 0)
        education_match = match.get('education_match', 0)
        experience_match = match.get('experience_match', 0)
        direction_match = match.get('direction_match', 0)
        
        # 构建匹配的技能标签
        matched_skills_html = ""
        if 'matched_skills' in match and match['matched_skills']:
            for skill in match['matched_skills']:
                matched_skills_html += f'<span class="tag">{skill}</span>'
        
        # 构建职位URL链接
        job_url_html = ""
        if 'url' in job and job['url']:
            job_url_html = f'<a href="{job["url"]}" target="_blank" class="job-url">查看职位详情</a>'
        
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>{job['title']}</h4>
                <div class="match-score-container">
                    <div class="match-score">{match_score}%</div>
                </div>
            </div>
            <p><strong>{job['company']}</strong> | {job['location']} | {job.get('salary_range', '薪资面议')}</p>
            <p>{job_url_html}</p>
            <div class="divider"></div>
            <p><strong>职位描述:</strong></p>
            <p>{job.get('description', '无描述')}</p>
            <div class="divider"></div>
            <p><strong>要求技能:</strong></p>
            <div>
                {''.join(f'<span class="tag">{skill}</span>' for skill in job['required_skills'])}
            </div>
            <p><strong>学历要求:</strong> {job.get('education_requirement', '未知')}</p>
            <p><strong>经验要求:</strong> {job.get('experience_requirement', '未知')}年</p>
            <div class="divider"></div>
            <p><strong>匹配详情:</strong></p>
            <p>技能匹配: {skill_match}%</p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {skill_match}%;"></div>
            </div>
            <p>教育匹配: {education_match}%</p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {education_match}%;"></div>
            </div>
            <p>经验匹配: {experience_match}%</p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {experience_match}%;"></div>
            </div>
            <p>方向匹配: {direction_match}%</p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {direction_match}%;"></div>
            </div>
            
            {f'''
            <div class="suggestion-panel">
                <h4>改进建议:</h4>
                <ul>
                    {''.join(f'<li>{suggestion}</li>' for suggestion in match['improvement_suggestions'])}
                </ul>
            </div>
            ''' if 'improvement_suggestions' in match and match['improvement_suggestions'] else ''}
        </div>
        """, unsafe_allow_html=True)

def display_loading_animation():
    """显示加载动画"""
    with st.spinner("正在处理中..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.05)
            progress_bar.progress(i + 1)

#################################################
# 主应用
#################################################

def main():
    """主Streamlit应用"""
    apply_custom_css()
    
    # 使用自定义标题
    st.markdown('<h1 class="title">AI简历职位匹配系统</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subtitle">智能分析简历，精准匹配职位</h2>', unsafe_allow_html=True)
    
    # 创建侧边栏
    sidebar_inputs = create_sidebar()
    
    # 设置缓存目录
    if not os.path.exists("./cache"):
        os.makedirs("./cache")
    
    # 创建示例简历
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    example_resume_path = os.path.join(data_dir, 'example_resume.txt')
    if not os.path.exists(example_resume_path):
        # 创建示例简历文件
        with open(example_resume_path, "w", encoding="utf-8") as f:
            f.write("张明\n")
            f.write("电话: 13812345678 邮箱: zhangming@example.com\n")
            f.write("北京市海淀区\n\n")
            f.write("个人简介: 有5年软件开发经验的全栈工程师，专注于Web应用开发和人工智能应用。\n\n")
            f.write("教育经历\n")
            f.write("北京大学 硕士 计算机科学 2015-09 - 2018-07\n")
            f.write("清华大学 学士 软件工程 2011-09 - 2015-07\n\n")
            f.write("工作经历\n")
            f.write("阿里巴巴 高级软件工程师 2020-06 - 至今\n")
            f.write("负责电商平台的后端开发，使用Java和Spring Boot构建微服务架构。\n\n")
            f.write("腾讯 软件工程师 2018-07 - 2020-05\n")
            f.write("参与社交应用的前端开发，使用React和Redux构建用户界面。\n\n")
            f.write("技能\n")
            f.write("Python, Java, JavaScript, React, Node.js, Spring Boot, MySQL, MongoDB, Docker, Git")
    
    # 处理按钮
    if sidebar_inputs["start_button"]:
        # 显示处理中提示
        with st.spinner("正在处理中..."):
            # 确定使用的简历文件
            resume_file_path = None
            if sidebar_inputs["uploaded_file"] is not None:
                # 保存上传的文件
                temp_file_path = os.path.join("./cache", sidebar_inputs["uploaded_file"].name)
                with open(temp_file_path, "wb") as f:
                    f.write(sidebar_inputs["uploaded_file"].getbuffer())
                resume_file_path = temp_file_path
                st.sidebar.success(f"已上传简历: {sidebar_inputs['uploaded_file'].name}")
            elif sidebar_inputs["use_example"]:
                resume_file_path = example_resume_path
                st.sidebar.info("使用示例简历")
            
            if resume_file_path:
                try:
                    # 创建集成对象
                    integration = JobSearchIntegration()
                    
                    # 处理简历并搜索职位
                    results = integration.process_resume_and_search_jobs(
                        resume_file_path=resume_file_path,
                        keywords=sidebar_inputs["job_keywords"],
                        location=sidebar_inputs["job_location"],
                        limit=sidebar_inputs["job_limit"]
                    )
                    
                    # 提取结果
                    resume_data = results['resume_data']
                    resume_analysis = results['resume_analysis']
                    jobs = results['jobs']
                    match_results = results['match_results']
                    
                    # 创建两列布局
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # 显示简历摘要
                        display_resume_summary(resume_data)
                        
                        # 如果启用AI增强分析
                        if sidebar_inputs["use_ai"]:
                            # 显示简历分析结果
                            display_resume_analysis(resume_analysis)
                    
                    with col2:
                        # 显示匹配结果
                        display_job_matches(match_results, jobs)
                    
                    # 保存结果
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    result_file = f"./cache/match_results_{timestamp}.json"
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    
                    # 添加下载结果按钮
                    with open(result_file, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="下载匹配结果",
                            data=f,
                            file_name=f"match_results_{timestamp}.json",
                            mime="application/json",
                        )
                    
                except Exception as e:
                    st.error(f"处理过程中出错: {str(e)}")
            else:
                st.error("请上传简历文件或选择使用示例简历")
    else:
        # 显示欢迎信息
        display_welcome()

if __name__ == "__main__":
    main()
