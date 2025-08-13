from flask import Flask, render_template, request, redirect, url_for
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from logger import upload_log_to_pcloud, download_file_from_pcloud, update_json_to_pcloud
from main import start
import json
import os
from logger import logger
from datetime import datetime

app = Flask(__name__)

# 初始化并启动定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(upload_log_to_pcloud, 'interval', minutes=15)
scheduler.start()

# 模拟任务存储（可替换为数据库）
tasks = {}

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/create', methods=['POST'])
def create_task():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        'name': request.form['name'],
        'url': request.form['url'],
        'xpath': request.form['xpath'],
        'email': request.form['email'],
        'target': request.form['target'],
        'status': 'running'
    }
    updateTaskStatus(task_id,tasks[task_id])
    scheduler.add_job(start, 'interval', minutes=1, args=[request.form['url'], request.form['xpath'], request.form['email'], request.form['target'], request.form['name'], task_id], id=task_id)
    logger.info(f'任务ID：{task_id}-任务名称:{tasks[task_id]["name"]}，任务已开始')
    return redirect(url_for('index'))

@app.route('/start/<task_id>')
def start_task(task_id):
    if task_id in tasks:
        tasks[task_id]['status'] = 'running'
        scheduler.resume_job(task_id)
        updateTaskStatus(task_id, {'status':'running'})
        logger.info(f'任务ID：{task_id}-任务名称:{tasks[task_id]["name"]}，任务已启动')
    return redirect(url_for('index'))

@app.route('/stop/<task_id>')
def stop_task(task_id):
    if task_id in tasks:
        tasks[task_id]['status'] = 'stopped'
        scheduler.pause_job(task_id)
        updateTaskStatus(task_id, {'status': 'stopped'})
        logger.info(f'任务ID：{task_id}-任务名称:{tasks[task_id]["name"]}，任务已暂停')
    return redirect(url_for('index'))

@app.route('/delete/<task_id>')
def delete_task(task_id):
    if task_id in tasks:
        del tasks[task_id]
        scheduler.remove_job(task_id)
        updateTaskStatus(task_id, {})
        logger.info(f'任务ID：{task_id}-任务名称:{tasks[task_id]["name"]}，任务已删除')
    return redirect(url_for('index'))

@app.route('/edit/<task_id>', methods=['POST'])
def edit_task(task_id):
    if task_id in tasks:
        stop_task(task_id)
        scheduler.remove_job(task_id)
        tasks[task_id]['name'] = request.form['name']
        tasks[task_id]['url'] = request.form['url']
        tasks[task_id]['xpath'] = request.form['xpath']
        tasks[task_id]['email'] = request.form['email']
        tasks[task_id]['target'] = request.form['target']
        tasks[task_id]['status'] = 'running'
        scheduler.add_job(start, 'interval', minutes=1,
                          args=[request.form['url'], request.form['xpath'], request.form['email'], request.form['target'], request.form['name'], task_id], id=task_id)
        logger.info(f'任务ID：{task_id}-任务名称:{tasks[task_id]["name"]}，任务已更新')
        updateTaskStatus(task_id, tasks[task_id])
    return '', 204  # 返回空响应即可

@app.route('/ping')
def ping():
    return f'pong - {datetime.utcnow().isoformat()}', 200

def updateTaskStatus(task_id,new_value):
    path = '/tmp/tasks.json'
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
    else:
        data_dict = {}

    if data_dict.get(task_id):
        pass
    else:
        data_dict[task_id] = {}

    if new_value:
        data_dict[task_id].update(new_value)
    else:
        del data_dict[task_id]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)
    update_json_to_pcloud()
        # 写入更新后的数据
def load_tasks_from_file():
    path = '/tmp/tasks.json'
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for task_id, task_info in data.items():
                    tasks[task_id] = task_info
                    if task_info.get('status') == 'running':
                        scheduler.add_job(
                            start,
                            'interval',
                            minutes=1,
                            args=[task_info['url'], task_info['xpath'], task_info['email'],task_info['target'], task_info['name'], task_id],
                            id=task_id
                        )
            except json.JSONDecodeError:
                logger.error("任务文件格式错误，无法加载")

from dotenv import load_dotenv
load_dotenv()

download_file_from_pcloud()
load_tasks_from_file()

if __name__ == '__main__':
    app.run(debug=True)
