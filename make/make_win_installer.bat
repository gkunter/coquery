rmdir "%HOMEPATH%\coquery-release\make\build" /s /q
rmdir "%HOMEPATH%\coquery-release\make\dist" /s /q
pyinstaller coquery_win.spec
"C:\Program Files\Inno Setup 5\Compil32.exe" /cc coquery.iss