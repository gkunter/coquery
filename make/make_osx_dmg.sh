rm -rf build dist
pyinstaller coquery_osx.spec
cp -a dist/Coquery/ dist/Coquery.app/Contents/MacOS/
hdiutil create -srcfolder dist/Coquery.app dist/coquery-0.9-osx-el-capitan
