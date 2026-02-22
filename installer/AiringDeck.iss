#define MyAppName "AiringDeck"
#define MyAppPublisher "AiringDeck"
#define MyAppURL "https://github.com/Pankyop/AiringDeck"

#ifndef AppVersion
  #define AppVersion "0.0.0-dev"
#endif

#ifndef SourceExe
  #define SourceExe "..\\dist\\AiringDeck.exe"
#endif

[Setup]
AppId={{D4B57C65-6EA2-4894-94E9-3EFBC42A0E8A}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\AiringDeck
DefaultGroupName=AiringDeck
DisableProgramGroupPage=yes
WizardStyle=modern
OutputDir=..\dist
OutputBaseFilename=AiringDeck-Setup-{#AppVersion}
SetupIconFile=..\resources\icons\app.ico
UninstallDisplayIcon={app}\AiringDeck.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ShowLanguageDialog=yes
LanguageDetectionMethod=none
UsePreviousLanguage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[CustomMessages]
english.AppLanguageTitle=Application language
english.AppLanguageDescription=Choose the default language for AiringDeck.
english.AppLanguageSub=You can change this later in Settings.
english.AppLanguageEnglish=English (Default)
english.AppLanguageItalian=Italian

italian.AppLanguageTitle=Application language
italian.AppLanguageDescription=Choose the default language for AiringDeck.
italian.AppLanguageSub=You can change this later in Settings.
italian.AppLanguageEnglish=English (Default)
italian.AppLanguageItalian=Italian

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "AiringDeck.exe"; Flags: ignoreversion
Source: "..\resources\icons\app.ico"; DestDir: "{app}"; DestName: "app.ico"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\AiringDeck"; Filename: "{app}\AiringDeck.exe"; IconFilename: "{app}\app.ico"
Name: "{autodesktop}\AiringDeck"; Filename: "{app}\AiringDeck.exe"; IconFilename: "{app}\app.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\AiringDeck\AiringDeck"; ValueType: string; ValueName: "app_language"; ValueData: "{code:GetAppLanguage}"; Flags: preservestringtype

[Run]
Filename: "{app}\AiringDeck.exe"; Description: "{cm:LaunchProgram,AiringDeck}"; Flags: nowait postinstall skipifsilent

[Code]
var
  AppLanguagePage: TInputOptionWizardPage;

function GetCurrentAppLanguageIndex: Integer;
var
  ExistingLang: string;
begin
  Result := 0;
  if RegQueryStringValue(HKCU, 'Software\AiringDeck\AiringDeck', 'app_language', ExistingLang) then
  begin
    if CompareText(ExistingLang, 'it') = 0 then
      Result := 1
    else
      Result := 0;
  end;
end;

procedure InitializeWizard;
begin
  AppLanguagePage := CreateInputOptionPage(
    wpSelectDir,
    ExpandConstant('{cm:AppLanguageTitle}'),
    ExpandConstant('{cm:AppLanguageDescription}'),
    ExpandConstant('{cm:AppLanguageSub}'),
    True,
    False
  );

  AppLanguagePage.Add(ExpandConstant('{cm:AppLanguageEnglish}'));
  AppLanguagePage.Add(ExpandConstant('{cm:AppLanguageItalian}'));
  AppLanguagePage.SelectedValueIndex := GetCurrentAppLanguageIndex();
end;

function GetAppLanguage(Param: string): string;
begin
  if (AppLanguagePage <> nil) and (AppLanguagePage.SelectedValueIndex = 1) then
    Result := 'it'
  else
    Result := 'en';
end;
