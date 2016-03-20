rmdir C:\Users\dadasd\coquery\make\build /s /q
rmdir C:\Users\dadasd\coquery\make\dist /s /q
pyinstaller coquery_win.spec
"C:\Program Files\Inno Setup 5\Compil32.exe" /cc coquery.iss