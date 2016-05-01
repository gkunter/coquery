set COQ_VERSION=0.9.2
rmdir "%HOMEPATH%\coquery-%COQ_VERSION%\make\build" /s /q
rmdir "%HOMEPATH%\coquery-%COQ_VERSION%\make\dist" /s /q
pyinstaller coquery_win.spec
"C:\Program Files\Inno Setup 5\Compil32.exe" /cc coquery.iss