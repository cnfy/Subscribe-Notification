# 使用官方 Playwright 镜像（包含 Python 和浏览器）
FROM mcr.microsoft.com/playwright/python:v1.48.0

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . .

ENV TZ=Asia/Tokyo
RUN apt-get update && apt-get install -y tzdata
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Playwright 浏览器路径（Render 推荐）
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 启动 Flask 应用（使用 gunicorn）
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]