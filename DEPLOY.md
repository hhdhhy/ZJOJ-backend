# ZJOJ 生产环境部署指南

## 📋 前置要求

- Ubuntu 20.04/22.04 服务器
- SSH访问权限
- 至少 2GB RAM（AI功能需要更多）
- 至少 20GB 磁盘空间

## 🚀 快速部署

### 方法1：自动部署脚本（推荐）

在**本地机器**上执行：

```bash
# Windows (Git Bash)
chmod +x quick_deploy.sh
./quick_deploy.sh

# Linux/Mac
chmod +x quick_deploy.sh
./quick_deploy.sh
```

### 方法2：手动部署

#### 1. SSH登录服务器

```bash
ssh ubuntu@101.35.233.33
# 密码: Liu2004hd
```

#### 2. 上传代码

```bash
# 在本地执行
scp -r ./* ubuntu@101.35.233.33:/home/ubuntu/ZJOJ/
```

#### 3. 在服务器上执行部署

```bash
# SSH登录后执行
cd /home/ubuntu/ZJOJ
chmod +x deploy.sh
bash deploy.sh
```

## 🔧 部署后配置

### 1. 生成安全的SECRET_KEY

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

复制输出的密钥，然后编辑环境变量：

```bash
echo 'export DJANGO_SECRET_KEY="你的密钥"' >> ~/.bashrc
source ~/.bashrc
```

### 2. 创建超级用户

```bash
cd /home/ubuntu/ZJOJ
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
python manage.py createsuperuser
```

### 3. 重启服务

```bash
sudo supervisorctl restart zjoj
sudo systemctl restart nginx
```

## 📊 服务管理

### 查看状态

```bash
# 查看Django应用状态
sudo supervisorctl status zjoj

# 查看Nginx状态
sudo systemctl status nginx

# 查看MySQL状态
sudo systemctl status mysql
```

### 重启服务

```bash
# 重启Django
sudo supervisorctl restart zjoj

# 重启Nginx
sudo systemctl restart nginx

# 重启MySQL
sudo systemctl restart mysql
```

### 查看日志

```bash
# Django/Gunicorn日志
tail -f /var/log/zjoj/gunicorn_error.log
tail -f /var/log/zjoj/gunicorn_access.log

# Supervisor日志
tail -f /var/log/zjoj/supervisor_err.log
tail -f /var/log/zjoj/supervisor_out.log

# Nginx日志
tail -f /var/log/nginx/zjoj_error.log
tail -f /var/log/nginx/zjoj_access.log

# Django应用日志
tail -f /var/log/zjoj/django.log
```

## 🔒 安全建议

### 1. 修改默认密码

```bash
# 修改MySQL密码
sudo mysql -u root -p
ALTER USER 'zjoj_user'@'localhost' IDENTIFIED BY '新密码';
FLUSH PRIVILEGES;
```

然后更新 `ZJOJ/settings_production.py` 中的数据库密码。

### 2. 配置防火墙

部署脚本已自动配置UFW防火墙：
- 允许 80 (HTTP)
- 允许 443 (HTTPS)
- 允许 22 (SSH)

查看规则：
```bash
sudo ufw status
```

### 3. 启用HTTPS（推荐）

使用Let's Encrypt免费证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 4. 定期备份

```bash
# 备份数据库
mysqldump -u zjoj_user -p zjoj_db > backup_$(date +%Y%m%d).sql

# 备份媒体文件
tar -czf media_backup_$(date +%Y%m%d).tar.gz /home/ubuntu/ZJOJ/media/
```

## 🐛 故障排查

### 问题1：502 Bad Gateway

**原因**：Gunicorn未运行

**解决**：
```bash
sudo supervisorctl status zjoj
sudo supervisorctl restart zjoj
tail -f /var/log/zjoj/gunicorn_error.log
```

### 问题2：数据库连接失败

**检查**：
```bash
# MySQL是否运行
sudo systemctl status mysql

# 测试连接
mysql -u zjoj_user -p zjoj_db
```

### 问题3：静态文件404

**解决**：
```bash
cd /home/ubuntu/ZJOJ
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### 问题4：权限错误

**解决**：
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/ZJOJ
sudo chmod -R 755 /home/ubuntu/ZJOJ
```

## 📝 更新部署

当代码有更新时：

```bash
# 方法1：使用快速部署脚本
./quick_deploy.sh

# 方法2：手动更新
cd /home/ubuntu/ZJOJ
git pull
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=ZJOJ.settings_production
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart zjoj
```

## 🎯 性能优化

### 1. 增加Gunicorn Workers

编辑 `gunicorn_config.py`：

```python
workers = 4  # 根据CPU核心数调整：(2 * CPU核心数) + 1
```

### 2. 使用Redis缓存（可选）

```bash
sudo apt install redis-server
pip install redis django-redis
```

更新 `settings_production.py`：

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. 数据库优化

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：

```ini
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 512M
query_cache_size = 64M
```

## 📞 技术支持

遇到问题？检查：
1. 日志文件（见上方"查看日志"部分）
2. 服务状态
3. 防火墙规则
4. 数据库连接

---

**部署完成后访问**: http://101.35.233.33
