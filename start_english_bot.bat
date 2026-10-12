@echo off
chcp 65001 > nul
title Ingliz Tili Uy Vazifasi Boti (@uy_vazifa_bot)

:run
echo =================================================================
echo  🇬🇧 INGLIZ TILI UY VAZIFASI BOTI ISHGA TUSHMOQDA...
echo  Telegram: @uy_vazifa_bot
echo =================================================================
echo.

py -3 bot.py

echo.
echo [OGOHLANTIRISH] Bot to'xtadi yoki tarmoq uzildi. 3 soniyadan so'ng qayta ulanadi...
timeout /t 3 > nul
goto run
