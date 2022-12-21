@REM PART 1: actions that are more commonly used and have little to no execution time
@REM terminate user-defined programs (minimize memory usage, terminate unresponsive programs)
@REM by default, no programs have been set for termination
@REM taskkill /f /im chrome.exe

@REM restart windows explorer (fix black background, broken search)
taskkill /f /im explorer.exe & start explorer.exe

@REM run disk cleanup with the default settings to clean up files
start cleanmgr.exe /verylowdisk

@REM timeout to allow user to manually quit before running comprehensive optimizations
timeout 30

@REM Scan for windows updates using WSUS and install updates
wuauclt.exe /SelfUpdateManaged
wuauclt.exe /updatenow

@REM python: update pip and setuptools. By default, this is disabled for systems without python
@REM python -m pip install --upgrade pip
@REM pip install -U setuptools

@REM restart network adapter
@REM ipconfig /release
@REM ipconfig /renew
@REM ipconfig /flushdns
@REM netsh winsock reset

@REM Repair Windows Image
DISM /Online /Cleanup-Image /RestoreHealth

@REM Scans the integrity of all protected system files and repairs files with problems when possible
sfc /scannow

@REM Defrag the volume on drive C while providing progress and verbose output
defrag c: /u /v

@REM timeout to allow user to cancel restart
timeout 30
shutdown /r
