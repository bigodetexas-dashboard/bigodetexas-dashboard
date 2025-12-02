Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "D:\dayz xbox\BigodeBot\BigodeTexas Launcher.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "D:\dayz xbox\BigodeBot\launcher.bat"
oLink.WorkingDirectory = "D:\dayz xbox\BigodeBot"
oLink.IconLocation = "D:\dayz xbox\BigodeBot\launcher_icon.ico"
oLink.Description = "BigodeTexas Bot - Menu Premium"
oLink.Save
WScript.Echo "Atalho criado com sucesso!"
