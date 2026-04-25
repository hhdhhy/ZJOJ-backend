import paramiko
import time

server = "101.35.233.33"
username = "root"
password = "Liu20040529"

commands = [
    "cd /home/zjoj/ZJOJ-backend",
    "git pull origin feature/ai-assistant-step1",
    "docker compose down",
    "docker compose up -d --build",
    "sleep 30",
    "docker ps | grep gojudge",
    "curl -s http://localhost:5050/run -X POST -H 'Content-Type: application/json' -d '{\"cmd\":[{\"args\":[\"/bin/echo\",\"test\"]}]}'"
]

print("=" * 50)
print("  ZJOJ 自动部署")
print("=" * 50)
print()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"连接到 {server}...")
    ssh.connect(
        hostname=server,
        username=username,
        password=password,
        port=22,
        timeout=10,
        allow_agent=False,
        look_for_keys=False
    )
    print("连接成功！\n")
    
    for cmd in commands:
        print(f"执行: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
        
        # 等待命令执行
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print(output)
        if error and exit_status != 0:
            print(f"错误: {error}")
        print()
    
    print("=" * 50)
    print("  部署完成！")
    print("=" * 50)
    
except Exception as e:
    print(f"错误: {e}")
finally:
    ssh.close()
