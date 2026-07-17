@echo off
echo ============================================================
echo 停止库存监控服务
echo ============================================================
echo.

taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq stock_monitor*"
taskkill /F /IM python.exe /FI "WINDOWTITLE eq stock_monitor*"

echo.
echo 服务已停止!
pause