# 使用 Python 3.10 slim 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制并安装项目依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器
COPY . .

# 赋予验证脚本执行权限
RUN chmod +x validate_tests.sh

# 设置环境变量，以便在运行时可以传入实际的 API Key
ENV LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# 在构建过程中运行单元测试
RUN ./validate_tests.sh

# 设置容器的入口点，默认运行 ChatPPT Gradio Server
CMD ["python", "src/gradio_server.py"]