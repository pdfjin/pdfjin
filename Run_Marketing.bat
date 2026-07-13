@echo off
title PDFjin Daily Marketing Routine
color 0A

echo ==================================================
echo         STARTING PDFJIN DAILY MARKETING
echo ==================================================
echo.

cd /d "%~dp0"

echo [1/2] RUNNING SOCIAL MEDIA POSTER...
python social_poster.py
echo.
echo Please copy your social media posts above!
pause
echo.

echo [2/2] RUNNING REDDIT FORUM MARKETER...
python forum_marketer.py
echo.

echo ==================================================
echo         MARKETING ROUTINE COMPLETE!
echo ==================================================
pause
