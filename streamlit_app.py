"""
AI简历职位匹配系统 - 优化前端版本
专为Streamlit Cloud部署优化
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import random

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
    .custom-button {
        background-color: #2E7D32;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
        font-weight: 500;
        display: inline-block;
        margin-top: 1rem;
        border: none;
    }
    
    .custom-button:hover {
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
    </style>
    """, unsafe_allow_html=True)

#################################################
# 简历解析器部分 - 简化版
#################################################

def parse_resume(file_path):
    """模拟简历解析，返回示例数据"""
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

def get_resume_summary(resume_data):
    """获取简历摘要"""
    return {
        'name': resume_data['personal_info'].get('name', '未知'),
        'latest_position': resume_data['work_experience'][0].get('position', '未知') if resume_data['work_experience'] else '未知',
        'latest_company': resume_data['work_experience'][0].get('company', '未知') if resume_data['work_experience'] else '未知',
        'experience_years': len(resume_data['work_experience']) * 2,
        'highest_education': f"{resume_data['education'][0].get('degree', '未知')} - {resume_data['education'][0].get('major', '未知')}" if resume_data['education'] else '未知',
        'top_skills': resume_data['skills'][:5] if len(resume_data['skills']) > 5 else resume_data['skills']
    }

#################################################
# 职位搜索部分 - 简化版
#################################################

def search_jobs(keywords, location='', limit=10, platform="模拟数据"):
    """模拟职位搜索，返回示例数据"""
    jobs = []
    
    # 职位标题模板
    job_titles = [
        "软件工程师", "高级软件工程师", "前端开发工程师", "后端开发工程师", 
        "全栈工程师", "数据工程师", "产品经理", "UI/UX设计师"
    ]
    
    # 公司名称模板
    companies = [
        "阿里巴巴", "腾讯", "百度", "字节跳动", "华为", "小米", 
        "京东", "美团", "网易", "微软", "谷歌", "亚马逊"
    ]
    
    # 技能模板
    all_skills = [
        "Python", "Java", "JavaScript", "C++", "React", "Vue", "Angular", 
        "Node.js", "Spring Boot", "MySQL", "MongoDB", "Docker", "Git"
    ]
    
    # 生成职位列表
    for i in range(min(limit, 20)):
        # 根据关键词调整职位标题
        if "前端" in keywords:
            job_title = random.choice(["前端开发工程师", "高级前端工程师", "Web前端开发", "UI开发工程师"])
        elif "后端" in keywords:
            job_title = random.choice(["后端开发工程师", "高级后端工程师", "服务端开发", "Java开发工程师"])
        elif "全栈" in keywords:
            job_title = random.choice(["全栈工程师", "全栈开发工程师", "Web全栈开发"])
        else:
            job_title = random.choice(job_titles)
        
        # 选择相关技能
        required_skills = random.sample(all_skills, k=random.randint(4, 6))
        
        # 生成职位描述
        description = f"{job_title}职位描述：我们正在寻找一位经验丰富的{job_title}加入我们的团队。"
        
        # 生成职位数据
        job = {
            'id': f"job_{i+1}",
            'title': job_title,
            'company': random.choice(companies),
            'location': location if location else random.choice(["北京", "上海", "深圳", "杭州", "广州"]),
            'description': description,
            'required_skills': required_skills,
            'education_requirement': random.choice(["本科", "硕士"]),
            'experience_requirement': random.randint(1, 5),
            'salary_range': random.choice(["15k-25k", "20k-35k", "30k-50k"]),
            'keywords': [keywords] + required_skills[:3],
            'platform': platform
        }
        
        jobs.append(job)
    
    return jobs

#################################################
# 职位匹配部分 - 简化版
#################################################

def match_resume_to_jobs(resume_data, jobs):
    """计算简历与职位的匹配度并排序"""
    match_results = []
    
    for job in jobs:
        # 计算技能匹配
        resume_skills = set(resume_data['skills'])
        job_skills = set(job['required_skills'])
        matched_skills = list(resume_skills.intersection(job_skills))
        skill_match = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # 计算教育匹配
        degree_level = {'博士': 4, '硕士': 3, '本科': 2, '大专': 1, '高中': 0, '': 0}
        resume_highest_degree = resume_data['education'][0].get('degree', '') if resume_data['education'] else ''
        job_required_degree = job.get('education_requirement', '')
        
        resume_level = degree_level.get(resume_highest_degree, 0)
        job_level = degree_level.get(job_required_degree, 0)
        
        education_match = 1.0 if resume_level >= job_level else resume_level / job_level if job_level > 0 else 0
        
        # 计算经验匹配
        resume_experience_years = len(resume_data['work_experience']) * 2
        job_required_years = job.get('experience_requirement', 0)
        
        experience_match = 1.0 if resume_experience_years >= job_required_years else resume_experience_years / job_required_years if job_required_years > 0 else 0
        
        # 计算关键词匹配（简化版）
        keyword_match = random.uniform(0.5, 0.9)  # 简化为随机值
        
        # 计算综合匹配分数
        overall_match = (skill_match * 0.4 + education_match * 0.2 + experience_match * 0.2 + keyword_match * 0.2)
        
        # 添加匹配结果
        match_results.append({
            'job_id': job.get('id', ''),
            'job_title': job.get('title', '未知职位'),
            'company': job.get('company', '未知公司'),
            'overall_match': overall_match,
            'skill_match': skill_match,
            'education_match': education_match,
            'experience_match': experience_match,
            'keyword_match': keyword_match,
            'matched_skills': matched_skills
        })
    
    # 按匹配度降序排序
    match_results.sort(key=lambda x: x['overall_match'], reverse=True)
    
    return match_results

#################################################
# 美化的UI组件
#################################################

def display_resume_summary(resume_data):
    """显示美化的简历摘要"""
    st.markdown('<h3 class="subtitle">简历摘要</h3>', unsafe_allow_html=True)
    
    # 个人信息卡片
    if 'personal_info' in resume_data:
        personal = resume_data['personal_info']
        st.markdown(f"""
        <div class="card">
            <h4 style="color: #2E7D32; margin-top: 0;">个人信息</h4>
            <p><strong>姓名:</strong> {personal.get('name', '未知')}</p>
            <p><strong>电话:</strong> {personal.get('phone', '未知')}</p>
            <p><strong>邮箱:</strong> {personal.get('email', '未知')}</p>
            <p><strong>地点:</strong> {personal.get('location', '未知')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 教育背景卡片
    if 'education' in resume_data and resume_data['education']:
        st.markdown('<h4 style="color: #2E7D32;">教育背景</h4>', unsafe_allow_html=True)
        for edu in resume_data['education']:
            st.markdown(f"""
            <div class="card" style="border-left-color: #1976D2;">
                <h4 style="color: #1976D2; margin-top: 0;">{edu.get('school', '未知')}</h4>
                <p><strong>{edu.get('degree', '未知')} - {edu.get('major', '未知')}</strong></p>
                <p>{edu.get('start_date', '')} 至 {edu.get('end_date', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 技能标签
    if 'skills' in resume_data and resume_data['skills']:
        st.markdown('<h4 style="color: #2E7D32;">技能</h4>', unsafe_allow_html=True)
        skills_html = ""
        for skill in resume_data['skills'][:10]:
            skills_html += f'<span class="tag">{skill}</span>'
        st.markdown(f"""
        <div class="card" style="border-left-color: #FF9800;">
            {skills_html}
        </div>
        """, unsafe_allow_html=True)

def display_job_matches(match_results, jobs):
    """显示美化的职位匹配结果"""
    st.markdown('<h3 class="subtitle">最佳匹配职位</h3>', unsafe_allow_html=True)
    
    for i, match in enumerate(match_results[:5]):
        job = next((j for j in jobs if j.get('id') == match.get('job_id')), {})
        
        # 计算百分比
        match_percent = int(match.get('overall_match', 0) * 100)
        skill_percent = int(match.get('skill_match', 0) * 100)
        edu_percent = int(match.get('education_match', 0) * 100)
        exp_percent = int(match.get('experience_match', 0) * 100)
        
        # 构建技能标签HTML
        skills_html = ""
        for skill in match.get('matched_skills', []):
            skills_html += f'<span class="tag">{skill}</span>'
        
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: #1976D2; margin-top: 0;">{match.get('job_title', '未知职位')}</h3>
                    <p style="color: #455A64;">{match.get('company', '未知公司')} | {job.get('location', '未知地点')}</p>
                </div>
                <div class="match-score-container">
                    <div class="match-score">{match_percent}%</div>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <h4 style="color: #455A64;">匹配详情</h4>
            
            <p><strong>技能匹配</strong></p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {skill_percent}%"></div>
            </div>
            
            <p><strong>教育背景匹配</strong></p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {edu_percent}%"></div>
            </div>
            
            <p><strong>工作经验匹配</strong></p>
            <div class="progress-container">
                <div class="progress-bar" style="width: {exp_percent}%"></div>
            </div>
            
            <div class="divider"></div>
            
            <h4 style="color: #455A64;">匹配的技能</h4>
            <div>
                {skills_html if skills_html else '<p>无匹配技能</p>'}
            </div>
            
            <button class="custom-button" onclick="alert('申请功能示例')">申请该职位</button>
        </div>
        """, unsafe_allow_html=True)

def create_sidebar():
    """创建美化的侧边栏"""
    st.sidebar.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #F5F5F5;
    }
    
    .sidebar-header {
        color: #2E7D32;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .sidebar-subheader {
        color: #455A64;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown('<h2 class="sidebar-header">操作面板</h2>', unsafe_allow_html=True)
    
    # 简历上传部分
    st.sidebar.markdown('<h3 class="sidebar-subheader">上传简历</h3>', unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("选择简历文件", type=['pdf', 'docx', 'txt'])
    use_example = st.sidebar.checkbox("使用示例简历", value=True)
    
    # 职位搜索部分
    st.sidebar.markdown('<h3 class="sidebar-subheader">职位搜索</h3>', unsafe_allow_html=True)
    
    # 添加平台选择
    platform = st.sidebar.selectbox(
        "选择招聘平台",
        ["模拟数据", "Boss直聘", "脉脉"]
    )
    
    job_keywords = st.sidebar.text_input("职位关键词", value="软件工程师")
    job_location = st.sidebar.text_input("工作地点", value="北京")
    job_limit = st.sidebar.slider("搜索结果数量", min_value=5, max_value=20, value=10)
    
    # AI增强选项
    st.sidebar.markdown('<h3 class="sidebar-subheader">AI增强</h3>', unsafe_allow_html=True)
    use_ai = st.sidebar.checkbox("使用AI增强分析", value=False)
    
    # 处理按钮
    start_button = st.sidebar.button("开始匹配")
    
    return {
        "uploaded_file": uploaded_file,
        "use_example": use_example,
        "platform": platform,
        "job_keywords": job_keywords,
        "job_location": job_location,
        "job_limit": job_limit,
        "use_ai": use_ai,
        "start_button": start_button
    }

def display_welcome():
    """显示欢迎信息和功能介绍"""
    st.markdown("""
    <div class="info-panel">
        <h3 style="margin-top: 0;">欢迎使用AI简历职位匹配系统</h3>
        <p>本系统可以帮助您：</p>
        <ul>
            <li>分析简历中的关键信息</li>
            <li>在多个招聘平台搜索职位</li>
            <li>计算简历与职位的匹配度</li>
            <li>提供精准的职位推荐</li>
        </ul>
        <p>请在左侧面板上传您的简历或使用示例简历，然后点击"开始匹配"按钮。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示功能介绍
    st.markdown('<h3 class="subtitle">功能介绍</h3>', unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div class="card" style="height: 200px;">
            <h4 style="color: #2E7D32; margin-top: 0;">简历解析</h4>
            <p>自动提取简历中的个人信息、教育背景、工作经验和技能等关键信息。</p>
        </div>
        """, unsafe_allow_html=True)
        
    with feature_col2:
        st.markdown("""
        <div class="card" style="height: 200px;">
            <h4 style="color: #2E7D32; margin-top: 0;">职位匹配</h4>
            <p>通过多维度分析计算简历与职位的匹配度，找到最适合您的工作机会。</p>
        </div>
        """, unsafe_allow_html=True)
        
    with feature_col3:
        st.markdown("""
        <div class="card" style="height: 200px;">
            <h4 style="color: #2E7D32; margin-top: 0;">AI增强分析</h4>
            <p>使用先进的AI技术提供更深入的匹配分析和个性化的求职建议。</p>
        </div>
        """, unsafe_allow_html=True)

#################################################
# 主应用部分
#################################################

def main():
    """主函数，运行Streamlit应用"""
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
                    # 解析简历
                    resume_data = parse_resume(resume_file_path)
                    
                    # 搜索职位
                    jobs = search_jobs(
                        sidebar_inputs["job_keywords"], 
                        sidebar_inputs["job_location"], 
                        sidebar_inputs["job_limit"],
                        platform=sidebar_inputs["platform"]
                    )
                    
                    # 计算匹配度并排序
                    match_results = match_resume_to_jobs(resume_data, jobs)
                    
                    # 创建两列布局
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # 显示简历摘要
                        display_resume_summary(resume_data)
                    
                    with col2:
                        # 显示匹配结果
                        display_job_matches(match_results, jobs)
                    
                    # 如果启用AI增强分析
                    if sidebar_inputs["use_ai"]:
                        st.markdown('<h3 class="subtitle">AI增强分析</h3>', unsafe_allow_html=True)
                        with st.spinner("正在使用AI分析..."):
                            st.info("AI分析功能需要配置API密钥才能使用。")
                    
                    # 添加下载结果按钮
                    st.download_button(
                        label="下载匹配结果",
                        data=json.dumps(match_results, ensure_ascii=False, indent=4),
                        file_name="match_results.json",
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
