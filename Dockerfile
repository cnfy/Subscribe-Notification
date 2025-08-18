# 使用官方 Python 镜像
FROM python:3.11-slim

# 安装 Playwright 所需的系统依赖
RUN apt-get update && apt-get install -y \
    libnss3 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libgtk-3-0 libxss1 libxtst6 \
    libenchant-2-2 libsecret-1-0 libmanette-0.2-0 libgstreamer-gl1.0-0 \
    libgstreamer-plugins-base1.0-0 libgles2 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN python -m playwright install

# 设置环境变量（Render 推荐）
ENV PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright

# 启动 Flask 应用（使用 gunicorn）
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
