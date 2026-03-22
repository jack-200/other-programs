Set WindowsShell = CreateObject("WScript.Shell")
Set FileSystem = CreateObject("Scripting.FileSystemObject")

shortcutsDir = FileSystem.GetParentFolderName(WScript.ScriptFullName)
projectRoot = FileSystem.GetParentFolderName(shortcutsDir)

WindowsShell.CurrentDirectory = projectRoot
WindowsShell.Run "uv run web-content-downloader\main.py", 0, True

Set WindowsShell = Nothing
Set FileSystem = Nothing