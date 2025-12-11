@echo off
powershell.exe -Command "Remove-Item -Path mir_commander -Include *.cpp -Recurse -Force"
powershell.exe -Command "Remove-Item -Path plugins -Include *.cpp -Recurse -Force"
powershell.exe -Command "Remove-Item -Path mir_commander -Include *.pyd -Recurse -Force"
powershell.exe -Command "Remove-Item -Path plugins -Include *.pyd -Recurse -Force"
rmdir build /s /q
rmdir dist /s /q
