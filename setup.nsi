# Auto-generated by EclipseNSIS Script Wizard
# 05-mar-2010 21:35:44

Name Condensaciones

# Usar lzma para comprimir - Lo seleccionamos en las preferencias
# SetCompressor /SOLID lzma
# Usar UPX para reducir tamaño del instalador
!packhdr "$%TEMP%\exehead.tmp" '"C:\winp\upx\upx.exe" "$%TEMP%\exehead.tmp"'

# General Symbol Definitions
!define REGKEY "SOFTWARE\$(^Name)"
!define VERSION 0.1
!define COMPANY "Rafael Villar Burke <pachi@rvburke.com>"
!define URL http://www.rvburke.com

# MUI Symbol Definitions
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install-full.ico"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT HKLM
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_REGISTRY_KEY ${REGKEY}
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME StartMenuGroup
!define MUI_STARTMENUPAGE_DEFAULTFOLDER Condensaciones
!define MUI_FINISHPAGE_RUN $INSTDIR\condensa.exe
!define MUI_FINISHPAGE_SHOWREADME $INSTDIR\README
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall-full.ico"

# Included files
!include Sections.nsh
!include MUI2.nsh

# Reserved Files
ReserveFile "${NSISDIR}\Plugins\AdvSplash.dll"

# Variables
Var StartMenuGroup

# Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE dist\COPYING
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuGroup
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# Installer languages
!insertmacro MUI_LANGUAGE SpanishInternational

# Installer attributes
OutFile condensaciones-0.1-setup.exe
InstallDir $PROGRAMFILES\Condensaciones
CRCCheck on
XPStyle on
ShowInstDetails show
VIProductVersion 0.1.0.0
VIAddVersionKey ProductName Condensaciones
VIAddVersionKey ProductVersion "${VERSION}"
VIAddVersionKey CompanyName "${COMPANY}"
VIAddVersionKey CompanyWebsite "${URL}"
VIAddVersionKey FileVersion "${VERSION}"
VIAddVersionKey FileDescription ""
VIAddVersionKey LegalCopyright ""
InstallDirRegKey HKLM "${REGKEY}" Path
ShowUninstDetails show

# Installer sections
Section -Main SEC0000
    SetOutPath $INSTDIR
    SetOverwrite on
    File /r dist\*
;    SetOutPath $INSTDIR\bin
    File /r C:\winp\Gtk+\bin\freetype6.dll
    File /r C:\winp\Gtk+\bin\intl.dll
    File /r C:\winp\Gtk+\bin\libatk-1.0-0.dll
    File /r C:\winp\Gtk+\bin\libcairo-2.dll
    File /r C:\winp\Gtk+\bin\libexpat-1.dll
    File /r C:\winp\Gtk+\bin\libfontconfig-1.dll
    File /r C:\winp\Gtk+\bin\libgailutil-18.dll
    File /r C:\winp\Gtk+\bin\libgdk_pixbuf-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libgdk-win32-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libgio-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libglib-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libgmodule-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libgobject-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libgthread-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libgtk-win32-2.0-0.dll
    File /r C:\winp\Gtk+\bin\libpango-1.0-0.dll
    File /r C:\winp\Gtk+\bin\libpangocairo-1.0-0.dll
    File /r C:\winp\Gtk+\bin\libpangoft2-1.0-0.dll
    File /r C:\winp\Gtk+\bin\libpangowin32-1.0-0.dll
    File /r C:\winp\Gtk+\bin\libpng14-14.dll
    File /r C:\winp\Gtk+\bin\zlib1.dll
    SetOutPath $INSTDIR\etc
    File /r C:\winp\Gtk+\etc\*
    SetOutPath $INSTDIR\lib
    File /r C:\winp\Gtk+\lib\*.dll
;    SetOutPath $INSTDIR\lib\glib-2.0
;    File /r C:\winp\Gtk+\lib\glib-2.0\*.dll
;    SetOutPath $INSTDIR\lib\gtk-2.0
;    File /r C:\winp\Gtk+\lib\gtk-2.0\*.dll
    SetOutPath $INSTDIR\share\themes\MS-Windows
    File /r C:\winp\Gtk+\share\themes\MS-Windows\*
    SetOutPath $INSTDIR\share\locale\es
    File /r C:\winp\Gtk+\share\locale\es\*
    WriteRegStr HKLM "${REGKEY}\Components" Main 1
SectionEnd

Section -post SEC0001
    WriteRegStr HKLM "${REGKEY}" Path $INSTDIR
    SetOutPath $INSTDIR
    WriteUninstaller $INSTDIR\uninstall.exe
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    SetOutPath $SMPROGRAMS\$StartMenuGroup
    CreateShortcut "$SMPROGRAMS\$StartMenuGroup\Uninstall $(^Name).lnk" $INSTDIR\uninstall.exe
    CreateShortCut "$SMPROGRAMS\$StartmenuGroup\$(^Name).lnk" "$INSTDIR\condensa.exe"
    !insertmacro MUI_STARTMENU_WRITE_END
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" DisplayName "$(^Name)"
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" DisplayVersion "${VERSION}"
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" Publisher "${COMPANY}"
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" URLInfoAbout "${URL}"
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" DisplayIcon $INSTDIR\uninstall.exe
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" UninstallString $INSTDIR\uninstall.exe
    WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" NoModify 1
    WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)" NoRepair 1
SectionEnd

# Macro for selecting uninstaller sections
!macro SELECT_UNSECTION SECTION_NAME UNSECTION_ID
    Push $R0
    ReadRegStr $R0 HKLM "${REGKEY}\Components" "${SECTION_NAME}"
    StrCmp $R0 1 0 next${UNSECTION_ID}
    !insertmacro SelectSection "${UNSECTION_ID}"
    GoTo done${UNSECTION_ID}
next${UNSECTION_ID}:
    !insertmacro UnselectSection "${UNSECTION_ID}"
done${UNSECTION_ID}:
    Pop $R0
!macroend

# Uninstaller sections
Section /o -un.Main UNSEC0000
    RmDir /r /REBOOTOK $INSTDIR
    RmDir /r /REBOOTOK $INSTDIR
    Delete /REBOOTOK $INSTDIR\*
    RmDir /r /REBOOTOK $INSTDIR\lib
    RmDir /r /REBOOTOK $INSTDIR\etc
    RmDir /r /REBOOTOK $INSTDIR\share
    DeleteRegValue HKLM "${REGKEY}\Components" Main
SectionEnd

Section -un.post UNSEC0001
    DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)"
    Delete /REBOOTOK "$SMPROGRAMS\$StartMenuGroup\Uninstall $(^Name).lnk"
    Delete /REBOOTOK "$SMPROGRAMS\$StartmenuGroup\$(^Name).lnk"
    Delete /REBOOTOK $INSTDIR\uninstall.exe
    DeleteRegValue HKLM "${REGKEY}" StartMenuGroup
    DeleteRegValue HKLM "${REGKEY}" Path
    DeleteRegKey /IfEmpty HKLM "${REGKEY}\Components"
    DeleteRegKey /IfEmpty HKLM "${REGKEY}"
    RmDir /REBOOTOK $SMPROGRAMS\$StartMenuGroup
    RmDir /REBOOTOK $INSTDIR
SectionEnd

# Installer functions
Function .onInit
    InitPluginsDir
    Push $R1
    File /oname=$PLUGINSDIR\spltmp.bmp splash.bmp
    advsplash::show 1000 600 400 -1 $PLUGINSDIR\spltmp
    Pop $R1
    Pop $R1
FunctionEnd

# Uninstaller functions
Function un.onInit
    SetAutoClose true
    ReadRegStr $INSTDIR HKLM "${REGKEY}" Path
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuGroup
    !insertmacro SELECT_UNSECTION Main ${UNSEC0000}
FunctionEnd

