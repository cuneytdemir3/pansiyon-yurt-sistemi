@echo off
title SBL Pansiyon - WhatsApp ve Tunel Baslatici
cd /d "%~dp0"

echo ===================================================
echo 1. Eski acik kalan bot ve tunel islemleri temizleniyor...
echo ===================================================
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 >nul

if exist "tunnel.log" del /f /q "tunnel.log"

echo.
echo ===================================================
echo 2. Canli Cloudflare Tuneli arka planda baslatiliyor...
echo ===================================================
start "Cloudflare Tuneli (Kapatmayin)" /min cmd /c "cloudflared.exe tunnel --url http://127.0.0.1:3001 --logfile tunnel.log"

echo Tunel adresinin olusmasi icin 5 saniye bekleniyor...
timeout /t 5 >nul

echo.
echo ===================================================
echo 3. WhatsApp Botu baslatiliyor...
echo ===================================================
node whatsapp-bot.js

echo.
echo [!] Bot durdu. Kapatmak icin bir tusa basin...
pause