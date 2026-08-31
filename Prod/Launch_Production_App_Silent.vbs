Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory & "\Prod\Launch_Production_App.bat"
WshShell.Run chr(34) & strPath & chr(34), 0
Set WshShell = Nothing
