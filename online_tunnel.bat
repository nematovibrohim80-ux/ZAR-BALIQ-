@echo off
chcp 65001 >nul
title BARAKA MARKET - Internetga Uzatish Tizimi
echo ==========================================================
echo    BARAKA MARKET - Onlayn Do'kon Tizimi
echo    Aloqa: +998 33 354 87 88 | Telegram: @nematvv1
echo ==========================================================
echo.
echo [MUHIM ESLATMA]
echo Sizning DOIMIY, 24/7 ishlaydigan rasmiy havolangiz:
echo 👉 https://nematovibrohim80-ux.github.io/ZAR-BALIQ-/
echo (Bu havola kompyuteringiz o'chiq bo'lsa ham butun dunyoda ishlaydi!)
echo.
echo ----------------------------------------------------------
echo Mahalliy (kompyuteringizdagi) server ishga tushirilmoqda...
start /B py -m http.server 8080 --bind 0.0.0.0 >nul 2>&1
timeout /t 2 >nul
echo Cloudflare orqali vaqtinchalik tunnel ochilmoqda:
echo.
.\cloudflared.exe tunnel --url http://localhost:8080
pause
