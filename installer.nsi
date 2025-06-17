!define APPNAME "HC-05 Configurator"
!define EXENAME "HC-05 Configurator.exe"
!define ICON "hc-05.ico"

OutFile "HC05-Configurator-Setup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Install"
    SetOutPath "$INSTDIR"
    File "HC-05 Configurator.exe"
    File "hc-05.ico"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${ICON}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${ICON}"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\HC-05 Configurator.exe"
    Delete "$INSTDIR\hc-05.ico"
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}.lnk"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
SectionEnd
