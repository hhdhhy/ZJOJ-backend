# ZJOJ 自动部署脚本
$server = "101.35.233.33"
$user = "root"
$password = "Liu20040529"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ZJOJ 自动部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 使用 plink (PuTTY) 执行命令
$commands = @(
    "cd /home/zjoj/ZJOJ-backend",
    "git pull origin feature/ai-assistant-step1",
    "docker compose down",
    "docker compose up -d --build",
    "sleep 30",
    "docker ps | grep gojudge",
    "curl -s http://localhost:5050/run -X POST -H 'Content-Type: application/json' -d '{`"cmd`":[{`"args`":[`"/bin/echo`",`"test`"]}]}'"
)

Write-Host "正在连接服务器..." -ForegroundColor Yellow
Write-Host ""

# 逐条执行命令
foreach ($cmd in $commands) {
    Write-Host "执行: $cmd" -ForegroundColor Green
    ssh ${user}@${server} $cmd
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
