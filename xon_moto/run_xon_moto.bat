@echo off
chcp 65001 >nul
title XON_MOTO - Mashinalar va Mototsikllar Bozori

echo ========================================================
echo        XON_MOTO - Avto va Moto Bozori Web Sayti
echo ========================================================
echo.
echo Server ishga tushmoqda...
echo Brauzerda ochish: http://127.0.0.1:5000
echo Serverni to'xtatish uchun: Ctrl + C
echo.

py app.py

pause
