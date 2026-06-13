## 项目结构
python 3.8

selenium + flask + sqlite

## 依赖安装
依赖安装查看 pip.txt

## 项目部署
目前部署在 59.77.7.17 的 /root/attendance/dist/ 目录

服务器已安装 chromedriver

运行命令：

1. 激活 conda，如果有的话
```
conda activate attendance
```
2. 开 4 个 worker 进程
```
nohup gunicorn -w 4 -b 0.0.0.0:5555 app:app > app.log 2>&1 &
```
3. 如果出现 SSL 报错
```html
python -m pip uninstall pyOpenSSL cryptography -y
python -m pip install pyOpenSSL==22.0.0 cryptography==36.0.2
```