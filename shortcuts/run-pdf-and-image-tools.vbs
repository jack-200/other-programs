Set WindowsShell = CreateObject("WScript.Shell")
Set FileSystem = CreateObject("Scripting.FileSystemObject")

shortcutsDir = FileSystem.GetParentFolderName(WScript.ScriptFullName)
projectRoot = FileSystem.GetParentFolderName(shortcutsDir)

venvActivatePath = projectRoot & "\.venv\Scripts\activate"
applicationPath = projectRoot & "\pdf-and-image-tools\main.pyw"

WindowsShell.Run "cmd /c " & venvActivatePath & " && pythonw " & applicationPath & " && deactivate", 0, True

Set WindowsShell = Nothing
Set FileSystem = Nothing