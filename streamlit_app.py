"""
AI简历职位匹配系统 - 极简版
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

# 设置缓存目录
if not os.path.exists("./cache"):
    os.makedirs("./cache")

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

def search_jobs(keywords, location='', limit=10):
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
            'keywords': [keywords] + required_skills[:3]
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
# 主应用部分
#################################################

def main():
    """主函数，运行Streamlit应用"""
    st.title("AI简历职位匹配系统")
    st.subheader("使用AI分析简历并匹配最适合的职位")
    
    # 创建示例简历
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    example_resume_path = os.path.join(data_dir, 'example_resume.txt')
    
    # 创建侧边栏
    st.sidebar.title("操作面板")
    
    # 上传简历
    st.sidebar.header("上传简历")
    uploaded_file = st.sidebar.file_uploader("选择简历文件", type=['pdf', 'docx', 'txt'])
    
    # 使用示例简历选项
    use_example = st.sidebar.checkbox("使用示例简历", value=True)
    
    # 职位搜索选项
    st.sidebar.header("职位搜索")
    job_keywords = st.sidebar.text_input("职位关键词", value="软件工程师")
    job_location = st.sidebar.text_input("工作地点", value="北京")
    job_limit = st.sidebar.slider("搜索结果数量", min_value=5, max_value=20, value=10)
    
    # 处理按钮
    if st.sidebar.button("开始匹配"):
        # 显示处理中提示
        with st.spinner("正在处理中..."):
            # 确定使用的简历文件
            resume_file_path = None
            if uploaded_file is not None:
                # 保存上传的文件
                temp_file_path = os.path.join("./cache", uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                resume_file_path = temp_file_path
                st.sidebar.success(f"已上传简历: {uploaded_file.name}")
            elif use_example:
                resume_file_path = example_resume_path
                st.sidebar.info("使用示例简历")
            
            if resume_file_path:
                try:
                    # 解析简历
                    resume_data = parse_resume(resume_file_path)
                    
                    # 搜索职位
                    jobs = search_jobs(job_keywords, job_location, job_limit)
                    
                    # 计算匹配度并排序
                    match_results = match_resume_to_jobs(resume_data, jobs)
                    
                    # 显示结果
                    display_results(resume_data, jobs, match_results)
                except Exception as e:
                    st.error(f"处理过程中出错: {str(e)}")
            else:
                st.error("请上传简历文件或选择使用示例简历")

def display_results(resume_data, jobs, match_results):
    """显示处理结果"""
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 1, 2])
    
    # 第一列：简历摘要
    with col1:
        st.header("简历摘要")
        
        # 个人信息
        if 'personal_info' in resume_data:
            personal = resume_data['personal_info']
            st.subheader("个人信息")
            st.write(f"姓名: {personal.get('name', '未知')}")
            st.write(f"电话: {personal.get('phone', '未知')}")
            st.write(f"邮箱: {personal.get('email', '未知')}")
        
        # 教育背景
        if 'education' in resume_data and resume_data['education']:
            st.subheader("教育背景")
            for edu in resume_data['education']:
                st.write(f"{edu.get('school', '未知')} - {edu.get('degree', '未知')} - {edu.get('major', '未知')}")
                st.write("---")
        
        # 技能
        if 'skills' in resume_data and resume_data['skills']:
            st.subheader("技能")
            st.write(", ".join(resume_data['skills'][:10]))
    
    # 第二列：搜索到的职位
    with col2:
        st.header("搜索到的职位")
        st.write(f"关键词: {jobs[0].get('keywords', ['无关键词'])[:3]}")
        st.write(f"共找到 {len(jobs)} 个职位")
        
        for i, job in enumerate(jobs[:3]):
            st.subheader(f"{i+1}. {job.get('title', '未知职位')}")
            st.write(f"公司: {job.get('company', '未知公司')}")
            st.write(f"地点: {job.get('location', '未知地点')}")
            st.write(f"要求技能: {', '.join(job.get('required_skills', ['无'])[:5])}")
            st.write("---")
        
        if len(jobs) > 3:
            st.write("...")
    
    # 第三列：匹配结果
    with col3:
        st.header("匹配结果")
        st.write("按匹配度排序的职位列表")
        
        for i, match in enumerate(match_results[:5]):
            # 创建可展开的部分
            with st.expander(f"{i+1}. {match.get('job_title', '未知职位')} - 匹配度: {match.get('overall_match', 0):.2f}"):
                st.write(f"公司: {match.get('company', '未知公司')}")
                
                # 显示匹配详情
                st.subheader("匹配详情")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"技能匹配: {match.get('skill_match', 0):.2f}")
                    st.write(f"关键词匹配: {match.get('keyword_match', 0):.2f}")
                with col_b:
                    st.write(f"教育背景匹配: {match.get('education_match', 0):.2f}")
                    st.write(f"工作经验匹配: {match.get('experience_match', 0):.2f}")
                
                # 显示匹配的技能
                if 'matched_skills' in match and match['matched_skills']:
                    st.subheader("匹配的技能")
                    st.write(", ".join(match['matched_skills']))
                
                # 添加申请按钮（示例功能）
                if st.button(f"申请该职位 #{i+1}"):
                    st.success("已发送申请！（示例功能）")
    
    # 添加下载结果按钮
    st.download_button(
        label="下载匹配结果",
        data=json.dumps(match_results, ensure_ascii=False, indent=4),
        file_name="match_results.json",
        mime="application/json",
    )

if __name__ == "__main__":
    main()
