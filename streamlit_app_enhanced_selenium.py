"""
AI简历职位匹配系统 - 增强版Streamlit应用 (Streamlit Cloud兼容版)
使用Selenium和BeautifulSoup抓取招聘网站职位信息，添加了Streamlit Cloud兼容性
"""
import os
import time
import json
import base64
import streamlit as st
import pandas as pd
import datetime

# 尝试导入集成模块 (使用Selenium版本)
try:
    from job_search_integration_selenium import JobSearchIntegration, get_enhanced_functions
    INTEGRATION_AVAILABLE = True
except ImportError:
    st.error("集成模块导入失败，某些功能可能不可用")
    INTEGRATION_AVAILABLE = False

# 配置页面
st.set_page_config(
    page_title="AI简历职位匹配系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0277BD;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .match-score {
        font-size: 1.8rem;
        font-weight: bold;
        text-align: center;
    }
    .match-score-high {
        color: #2E7D32;
    }
    .match-score-medium {
        color: #F57F17;
    }
    .match-score-low {
        color: #C62828;
    }
</style>
""", unsafe_allow_html=True)

# 创建数据目录
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 示例简历文件
example_resume_path = os.path.join(data_dir, "example_resume.txt")
if not os.path.exists(example_resume_path):
    with open(example_resume_path, "w", encoding="utf-8") as f:
        f.write("""张三
电话: 13800138000
邮箱: zhangsan@example.com
北京市海淀区

个人简介: 5年Python开发经验，熟悉Web开发和数据分析，有大型项目经验。

教育经历
清华大学 计算机科学与技术 本科 2015-2019

工作经验
阿里巴巴 高级Python开发工程师 2019-至今
- 负责电商平台后端API开发
- 优化数据处理流程，提高系统性能30%
- 带领5人小组完成核心模块重构

百度 Python开发实习生 2018-2019
- 参与搜索引擎数据分析项目
- 开发数据可视化工具

技能
Python, Django, Flask, RESTful API, MySQL, Redis, MongoDB, Docker, Git, Linux, JavaScript, HTML, CSS, Vue.js, 数据分析, 机器学习
""")

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """生成文件下载链接"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

def main():
    """主函数"""
    # 显示标题
    st.markdown('<h1 class="main-header">AI简历职位匹配系统</h1>', unsafe_allow_html=True)
    
    # 初始化会话状态
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'resume_analysis' not in st.session_state:
        st.session_state.resume_analysis = None
    if 'jobs' not in st.session_state:
        st.session_state.jobs = None
    if 'match_results' not in st.session_state:
        st.session_state.match_results = None
    if 'integration' not in st.session_state:
        if INTEGRATION_AVAILABLE:
            try:
                st.session_state.integration = JobSearchIntegration()
            except Exception as e:
                st.error(f"初始化集成模块失败: {str(e)}")
                st.session_state.integration = None
        else:
            st.session_state.integration = None
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 设置")
        
        # 上传简历
        st.markdown("### 上传简历")
        resume_file = st.file_uploader("选择简历文件", type=["txt", "pdf", "docx"])
        
        # 或者使用示例简历
        use_example = st.checkbox("使用示例简历", value=True)
        
        # 职位搜索设置
        st.markdown("### 职位搜索设置")
        keywords = st.text_input("关键词", value="Python 开发工程师")
        location = st.text_input("地点", value="北京")
        platform = st.selectbox("数据来源", ["模拟数据", "智联招聘", "前程无忧"])
        limit = st.slider("结果数量", min_value=5, max_value=20, value=10)
        
        # 开始分析按钮
        start_button = st.button("开始分析")
    
    # 主界面
    if start_button:
        # 显示加载状态
        with st.spinner("正在处理中..."):
            # 确定简历文件路径
            resume_path = example_resume_path if use_example else None
            
            if resume_file is not None:
                # 保存上传的文件
                resume_path = os.path.join(data_dir, resume_file.name)
                with open(resume_path, "wb") as f:
                    f.write(resume_file.getbuffer())
            
            if resume_path:
                try:
                    # 如果集成模块可用，使用集成模块处理
                    if INTEGRATION_AVAILABLE and st.session_state.integration:
                        # 处理简历并搜索职位
                        results = st.session_state.integration.process_resume_and_search_jobs(
                            resume_path, keywords, location, limit, platform
                        )
                        
                        # 更新会话状态
                        st.session_state.resume_data = results.get('resume_data')
                        st.session_state.resume_analysis = results.get('resume_analysis')
                        st.session_state.jobs = results.get('jobs')
                        st.session_state.match_results = results.get('match_results')
                        
                        # 保存结果
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        result_file = f"match_results_{timestamp}.json"
                        result_path = st.session_state.integration.save_results(results, result_file)
                    else:
                        # 如果集成模块不可用，显示错误信息
                        st.error("集成模块不可用，无法处理简历和搜索职位")
                except Exception as e:
                    st.error(f"处理失败: {str(e)}")
    
    # 显示结果
    if st.session_state.resume_data and st.session_state.resume_analysis:
        # 显示简历分析结果
        st.markdown('<h2 class="sub-header">简历分析结果</h2>', unsafe_allow_html=True)
        
        # 个人信息
        personal_info = st.session_state.resume_data.get('personal_info', {})
        personal_summary = st.session_state.resume_analysis.get('personal_summary', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"### {personal_info.get('name', '未知')}")
            st.markdown(f"**联系方式:** {personal_info.get('phone', '未知')} | {personal_info.get('email', '未知')}")
            st.markdown(f"**地点:** {personal_info.get('location', '未知')}")
            st.markdown(f"**工作经验:** {personal_summary.get('years_of_experience', 0)}年")
            st.markdown(f"**最高学历:** {personal_summary.get('highest_education', '未知')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # 综合评分
            overall_score = st.session_state.resume_analysis.get('overall_score', {})
            score = overall_score.get('overall_score', 0)
            level = overall_score.get('level', '初级')
            
            score_class = "match-score-low"
            if score >= 80:
                score_class = "match-score-high"
            elif score >= 60:
                score_class = "match-score-medium"
            
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="match-score {score_class}">{score}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center;">综合评分 ({level})</div>', unsafe_allow_html=True)
            
            # 组件评分
            component_scores = overall_score.get('component_scores', {})
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f'<div style="text-align: center;"><b>技能</b><br>{component_scores.get("skills", 0)}</div>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<div style="text-align: center;"><b>教育</b><br>{component_scores.get("education", 0)}</div>', unsafe_allow_html=True)
            with col_c:
                st.markdown(f'<div style="text-align: center;"><b>经验</b><br>{component_scores.get("experience", 0)}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 技能分析
        st.markdown('<h3 class="sub-header">技能分析</h3>', unsafe_allow_html=True)
        skills_analysis = st.session_state.resume_analysis.get('skills_analysis', {})
        skills = st.session_state.resume_data.get('skills', [])
        
        if skills:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"**技能数量:** {skills_analysis.get('skill_count', 0)}")
            st.markdown(f"**技能水平:** {skills_analysis.get('skill_level', '初级')}")
            
            # 显示技能标签
            st.markdown("**技能列表:**")
            skill_html = ""
            for skill in skills:
                skill_html += f'<span style="background-color: #E1F5FE; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 0.5rem; display: inline-block;">{skill}</span>'
            st.markdown(skill_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 职业方向
        st.markdown('<h3 class="sub-header">职业方向</h3>', unsafe_allow_html=True)
        career_direction = st.session_state.resume_analysis.get('career_direction', {})
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown(f"**主要方向:** {career_direction.get('primary_direction', '未知')} (匹配度: {career_direction.get('primary_score', 0):.1f}%)")
        st.markdown(f"**次要方向:** {career_direction.get('secondary_direction', '未知')} (匹配度: {career_direction.get('secondary_score', 0):.1f}%)")
        st.markdown(f"**方向确定性:** {career_direction.get('direction_confidence', 'low')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示职位匹配结果
    if st.session_state.jobs and st.session_state.match_results:
        st.markdown('<h2 class="sub-header">职位匹配结果</h2>', unsafe_allow_html=True)
        
        # 获取职位和匹配结果
        jobs = st.session_state.jobs
        match_results = st.session_state.match_results
        
        # 创建职位ID到职位的映射
        job_map = {job['id']: job for job in jobs}
        
        # 显示匹配结果
        for match in match_results[:5]:  # 只显示前5个匹配结果
            job_id = match.get('job_id', '')
            job = job_map.get(job_id, {})
            
            if not job:
                continue
            
            # 匹配分数
            match_score = match.get('match_score', 0)
            score_class = "match-score-low"
            if match_score >= 80:
                score_class = "match-score-high"
            elif match_score >= 60:
                score_class = "match-score-medium"
            
            # 创建可展开的职位卡片
            with st.expander(f"{job.get('title', '未知职位')} - {job.get('company', '未知公司')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**公司:** {job.get('company', '未知')}")
                    st.markdown(f"**地点:** {job.get('location', '未知')}")
                    st.markdown(f"**薪资:** {job.get('salary_range', '未知')}")
                    st.markdown(f"**来源:** {job.get('platform', '未知')}")
                    
                    # 显示职位描述
                    st.markdown("**职位描述:**")
                    st.markdown(job.get('description', '无描述'))
                    
                    # 显示要求技能
                    required_skills = job.get('required_skills', [])
                    if required_skills:
                        st.markdown("**要求技能:**")
                        skill_html = ""
                        for skill in required_skills:
                            skill_html += f'<span style="background-color: #E1F5FE; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 0.5rem; display: inline-block;">{skill}</span>'
                        st.markdown(skill_html, unsafe_allow_html=True)
                    
                    # 显示匹配的技能
                    matched_skills = match.get('matched_skills', [])
                    if matched_skills:
                        st.markdown("**匹配的技能:**")
                        skill_html = ""
                        for skill in matched_skills:
                            skill_html += f'<span style="background-color: #E8F5E9; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 0.5rem; display: inline-block;">{skill}</span>'
                        st.markdown(skill_html, unsafe_allow_html=True)
                    
                    # 显示改进建议
                    improvement_suggestions = match.get('improvement_suggestions', [])
                    if improvement_suggestions:
                        st.markdown("**改进建议:**")
                        for suggestion in improvement_suggestions:
                            st.markdown(f"- {suggestion}")
                
                with col2:
                    # 显示匹配分数
                    st.markdown(f'<div class="match-score {score_class}">{match_score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">匹配度</div>', unsafe_allow_html=True)
                    
                    # 显示各维度匹配度
                    st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
                    st.markdown(f"技能匹配: {match.get('skill_match', 0)}%")
                    st.progress(match.get('skill_match', 0) / 100)
                    st.markdown(f"教育匹配: {match.get('education_match', 0)}%")
                    st.progress(match.get('education_match', 0) / 100)
                    st.markdown(f"经验匹配: {match.get('experience_match', 0)}%")
                    st.progress(match.get('experience_match', 0) / 100)
                    st.markdown(f"方向匹配: {match.get('direction_match', 0)}%")
                    st.progress(match.get('direction_match', 0) / 100)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # 显示更多匹配结果
        if len(match_results) > 5:
            with st.expander("显示更多匹配结果"):
                for match in match_results[5:]:
                    job_id = match.get('job_id', '')
                    job = job_map.get(job_id, {})
                    
                    if not job:
                        continue
                    
                    st.markdown(f"**{job.get('title', '未知职位')} - {job.get('company', '未知公司')}** (匹配度: {match.get('match_score', 0)}%)")
                    st.markdown(f"地点: {job.get('location', '未知')} | 薪资: {job.get('salary_range', '未知')}")
                    st.markdown("---")
        
        # 提供下载结果的链接
        if hasattr(st.session_state, 'integration') and st.session_state.integration:
            result_files = [f for f in os.listdir(st.session_state.integration.cache_dir) if f.startswith('match_results_')]
            if result_files:
                latest_file = sorted(result_files)[-1]
                result_path = os.path.join(st.session_state.integration.cache_dir, latest_file)
                st.markdown(
                    get_binary_file_downloader_html(result_path, '下载匹配结果'),
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"应用运行出错: {str(e)}")
        st.info("如果您看到此错误，请尝试刷新页面或联系管理员。")
