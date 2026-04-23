@echo off
echo Sudoku Solver - Command Line Version
echo ====================================
cd /d "%~dp0"
python sudoku.py --inputFile data/euler.txt
echo.
echo Press any key to exit...
pause >nul