' Create necessary objects
Set Shell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get script directory
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Construct paths
venvPath = scriptDir & "\..\venv\Scripts\activate"
pythonScriptPath = scriptDir & "\..\content-tools\pdf_and_image_tools.pyw"

' Run the command
Shell.Run "cmd /c " & venvPath & " && pythonw " & pythonScriptPath & " && deactivate", 0, True

' Clean up
Set Shell = Nothing
Set FSO = Nothing