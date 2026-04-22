@echo off
cd /d %~dp0
py -m streamlit run simulator.py 
pause