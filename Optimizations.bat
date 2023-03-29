@REM taskkill /f /im chrome.exe

@REM restart windows explorer (fix black background, broken search, etc)
taskkill /f /im explorer.exe & start explorer.exe

@REM python: upgrade pip, update setuptools + wheel
@REM python.exe -m ensurepip --upgrade
@REM python.exe -m pip install --upgrade setuptools wheel

@REM run disk cleanup with the options checked
@REM cleanmgr /sageset:1
cleanmgr /sagerun:1

@REM restart network adapter
@REM ipconfig /release
@REM ipconfig /renew
@REM ipconfig /flushdns
@REM netsh winsock reset

@REM defrag the volume on drive C while providing progress and verbose output
defrag c: /u /v

@REM repair windows image
DISM /Online /Cleanup-Image /RestoreHealth

@REM scan and repair protected system files
sfc /scannow

@REM run full Microsoft Defender Antivirus scan
cd "%ProgramFiles%\Windows Defender"
MpCmdRun.exe -SignatureUpdate
MpCmdRun.exe -Scan -ScanType 2

shutdown /r