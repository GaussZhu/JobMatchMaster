# AI简历职位匹配系统 - 部署指南

本文档提供了将AI简历职位匹配系统部署到Streamlit Cloud的简要指南。

## 文件说明

此部署包包含以下文件：

- `streamlit_app.py`: 主应用程序文件（单文件版本，已整合所有组件）
- `requirements.txt`: 依赖项列表
- `.streamlit/config.toml`: Streamlit配置文件

## 部署步骤

### 1. 创建GitHub仓库

1. 登录您的GitHub账户
2. 创建一个新的公共仓库（例如：`resume-job-matcher`）
3. 不要初始化仓库（不添加README、.gitignore或许可证）

### 2. 上传文件

将部署包中的所有文件上传到GitHub仓库，保持相同的目录结构：

```
/
├── streamlit_app.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```

您可以通过GitHub网页界面上传文件：

1. 进入您的仓库页面
2. 点击"Add file" > "Upload files"
3. 拖拽文件或选择文件上传
4. 对于`.streamlit`目录，您需要先创建目录，然后上传`config.toml`文件

### 3. 部署到Streamlit Cloud

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 使用GitHub账户登录
3. 点击"New app"按钮
4. 选择您的仓库和分支（通常是`main`）
5. 将主文件路径设置为`streamlit_app.py`
6. 点击"Deploy!"按钮

部署过程通常需要几分钟。完成后，您将获得一个永久的URL，可以访问您的应用。

## 故障排除

如果您在部署过程中遇到问题：

1. 检查Streamlit Cloud的日志以获取详细错误信息
2. 确保所有文件都已正确上传到GitHub仓库
3. 验证`requirements.txt`中的依赖项是否兼容

## 更新应用

要更新已部署的应用，只需将更改推送到GitHub仓库。Streamlit Cloud会自动重新部署应用。
