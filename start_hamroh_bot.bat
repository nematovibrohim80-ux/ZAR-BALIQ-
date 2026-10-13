@echo off
chcp 65001 > nul
title Hamroh AI — Samimiy Suhbatdosh Boti

:run
echo =================================================================
echo  🌸 HAMROH AI BOTI ISHGA TUSHMOQDA...
echo  Samimiy, do'stona va mehrli suhbatdosh AI assistenti
echo =================================================================
echo.

py -3 bot.py

echo.
echo [OGOHLANTIRISH] Bot to'xtadi yoki tarmoq uzildi. 3 soniyadan so'ng qayta ishga tushadi...
timeout /t 3 > nul
goto run
