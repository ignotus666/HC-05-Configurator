!include MUI2.nsh

!define APPNAME "HC-05 Configurator"
!define EXENAME "HC-05 Configurator.exe"
!define ICON "hc-05.ico"

!ifndef VERSION
    !define VERSION "dev"
!endif
!ifndef VERSION_NSI
    !define VERSION_NSI "0.0.0.0"
!endif

OutFile "HC05-Configurator-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"

VIProductVersion "${VERSION_NSI}"
VIAddVersionKey "ProductName" "${APPNAME}"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "CompanyName" ""
VIAddVersionKey "LegalCopyright" "MIT License"

; Modern UI 2 Pages
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

Section "Install"
    SetOutPath "$INSTDIR"
    File "HC-05 Configurator.exe"
    File "hc-05.ico"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${ICON}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${ICON}"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    ; Register uninstaller in Windows Control Panel
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\${ICON}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" ""
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\HC-05 Configurator.exe"
    Delete "$INSTDIR\hc-05.ico"
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}.lnk"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    ; Remove uninstaller entry from Control Panel
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
