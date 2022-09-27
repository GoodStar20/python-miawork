REM Remove files older than 10 days
forfiles /p "C:\Users\batch_job\Desktop\miaworkcomp\tmp" /s /m *.* /c "cmd /c Del @path" /d -10