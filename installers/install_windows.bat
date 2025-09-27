@echo off
REM ScalPDF Windows Installer
REM Installs ScalPDF with full functionality and Start Menu integration

setlocal EnableDelayedExpansion

REM Colors (using PowerShell for colored output)
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM Configuration
set "APP_NAME=ScalPDF"
set "INSTALL_DIR=%LOCALAPPDATA%\ScalPDF"
set "VENV_DIR=%INSTALL_DIR%\venv"
set "START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"

echo %BLUE%🚀 ScalPDF Windows Installer%NC%
echo ==================================

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python is not installed or not in PATH%NC%
    echo Please install Python 3.11+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%✅ Python %PYTHON_VERSION% detected%NC%

REM Verify Python version is 3.11+
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python 3.11+ required, found %PYTHON_VERSION%%NC%
    pause
    exit /b 1
)

REM Check if pip is available
echo 📦 Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ pip is not available%NC%
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)
echo %GREEN%✅ pip is available%NC%

REM Create installation directory
echo 📁 Creating installation directory...
if exist "%INSTALL_DIR%" (
    echo Removing existing installation...
    rmdir /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"
echo %GREEN%✅ Installation directory created%NC%

REM Copy application files
echo 📋 Copying application files...
xcopy /E /I /H /Y . "%INSTALL_DIR%" >nul
echo %GREEN%✅ Application files copied%NC%

REM Create virtual environment
echo 🐍 Creating Python virtual environment...
cd /d "%INSTALL_DIR%"
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo %RED%❌ Failed to create virtual environment%NC%
    pause
    exit /b 1
)
echo %GREEN%✅ Virtual environment created%NC%

REM Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%❌ Failed to install dependencies%NC%
    pause
    exit /b 1
)
echo %GREEN%✅ Python dependencies installed%NC%

REM Create launcher scripts
echo 🔧 Creating launcher scripts...

REM GUI launcher
(
echo @echo off
echo REM ScalPDF GUI Launcher
echo cd /d "%INSTALL_DIR%"
echo call "%VENV_DIR%\Scripts\activate.bat"
echo python main.py %%*
) > "%INSTALL_DIR%\ScalPDF.bat"

REM CLI launcher
(
echo @echo off
echo REM ScalPDF CLI Launcher
echo cd /d "%INSTALL_DIR%"
echo call "%VENV_DIR%\Scripts\activate.bat"
echo python -m cli.cli %%*
) > "%INSTALL_DIR%\ScalPDF-CLI.bat"

echo %GREEN%✅ Launcher scripts created%NC%

REM Create PowerShell launchers (for better integration)
(
echo # ScalPDF GUI PowerShell Launcher
echo Set-Location "%INSTALL_DIR%"
echo ^& "%VENV_DIR%\Scripts\Activate.ps1"
echo python main.py $args
) > "%INSTALL_DIR%\ScalPDF.ps1"

(
echo # ScalPDF CLI PowerShell Launcher
echo Set-Location "%INSTALL_DIR%"
echo ^& "%VENV_DIR%\Scripts\Activate.ps1"
echo python -m cli.cli $args
) > "%INSTALL_DIR%\ScalPDF-CLI.ps1"

REM Create application icon (simple text-based icon)
echo 🎨 Creating application icon...
if not exist "%INSTALL_DIR%\assets" mkdir "%INSTALL_DIR%\assets"

REM Create a simple ICO file using PowerShell (if available)
powershell -Command "
Add-Type -AssemblyName System.Drawing
$bitmap = New-Object System.Drawing.Bitmap(256, 256)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::FromArgb(37, 99, 235))
$font = New-Object System.Drawing.Font('Arial', 24, [System.Drawing.FontStyle]::Bold)
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$graphics.DrawString('PDF', $font, $brush, 90, 110)
$bitmap.Save('%INSTALL_DIR%\assets\icon.png', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
" >nul 2>&1

echo %GREEN%✅ Application icon created%NC%

REM Create Start Menu shortcuts
echo 🖥️ Creating Start Menu shortcuts...

REM Create VBS script for shortcuts (to avoid showing command prompt)
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%START_MENU_DIR%\ScalPDF.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\ScalPDF.bat"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "ScalPDF - Secure PDF Management Tool"
echo oLink.IconLocation = "%INSTALL_DIR%\assets\icon.png"
echo oLink.WindowStyle = 7
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

REM Create CLI shortcut
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%START_MENU_DIR%\ScalPDF CLI.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "cmd.exe"
echo oLink.Arguments = "/k ""%INSTALL_DIR%\ScalPDF-CLI.bat"""
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "ScalPDF Command Line Interface"
echo oLink.IconLocation = "%INSTALL_DIR%\assets\icon.png"
echo oLink.Save
) > "%TEMP%\create_cli_shortcut.vbs"

cscript //nologo "%TEMP%\create_cli_shortcut.vbs"
del "%TEMP%\create_cli_shortcut.vbs"

echo %GREEN%✅ Start Menu shortcuts created%NC%

REM Create Desktop shortcut (optional)
echo 🖥️ Creating Desktop shortcut...
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP_DIR%\ScalPDF.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\ScalPDF.bat"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "ScalPDF - Secure PDF Management Tool"
echo oLink.IconLocation = "%INSTALL_DIR%\assets\icon.png"
echo oLink.WindowStyle = 7
echo oLink.Save
) > "%TEMP%\create_desktop_shortcut.vbs"

cscript //nologo "%TEMP%\create_desktop_shortcut.vbs"
del "%TEMP%\create_desktop_shortcut.vbs"

echo %GREEN%✅ Desktop shortcut created%NC%

REM Add to Windows PATH (optional)
echo 🛤️ Adding to system PATH...
setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
echo %GREEN%✅ Added to PATH%NC%

REM Create uninstaller
echo 🗑️ Creating uninstaller...
(
echo @echo off
echo echo 🗑️ Uninstalling ScalPDF...
echo.
echo REM Remove installation directory
echo if exist "%INSTALL_DIR%" ^(
echo     rmdir /s /q "%INSTALL_DIR%"
echo     echo ✅ Application files removed
echo ^)
echo.
echo REM Remove Start Menu shortcuts
echo if exist "%START_MENU_DIR%\ScalPDF.lnk" del "%START_MENU_DIR%\ScalPDF.lnk"
echo if exist "%START_MENU_DIR%\ScalPDF CLI.lnk" del "%START_MENU_DIR%\ScalPDF CLI.lnk"
echo echo ✅ Start Menu shortcuts removed
echo.
echo REM Remove Desktop shortcut
echo if exist "%DESKTOP_DIR%\ScalPDF.lnk" del "%DESKTOP_DIR%\ScalPDF.lnk"
echo echo ✅ Desktop shortcut removed
echo.
echo echo ✅ ScalPDF uninstalled successfully
echo echo Note: You may need to restart your command prompt for PATH changes to take effect
echo pause
) > "%INSTALL_DIR%\Uninstall.bat"

REM Create uninstaller shortcut in Start Menu
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%START_MENU_DIR%\Uninstall ScalPDF.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\Uninstall.bat"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "Uninstall ScalPDF"
echo oLink.Save
) > "%TEMP%\create_uninstall_shortcut.vbs"

cscript //nologo "%TEMP%\create_uninstall_shortcut.vbs"
del "%TEMP%\create_uninstall_shortcut.vbs"

echo %GREEN%✅ Uninstaller created%NC%

REM Run installation tests
echo 🧪 Running installation tests...
call "%VENV_DIR%\Scripts\activate.bat"

python -c "
try:
    import PySide6; print('✅ PySide6 OK')
    import fitz; print('✅ PyMuPDF OK')
    import pikepdf; print('✅ pikepdf OK')
    import PIL; print('✅ Pillow OK')
    import cryptography; print('✅ cryptography OK')
    import argon2; print('✅ argon2 OK')
    print('✅ All dependencies working!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if errorlevel 1 (
    echo %RED%❌ Installation tests failed%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ Installation tests passed%NC%

REM Final success message
echo.
echo %GREEN%🎉 ScalPDF installed successfully!%NC%
echo.
echo 📖 Usage:
echo   • GUI: Find 'ScalPDF' in Start Menu or Desktop
echo   • CLI: Open Command Prompt and run 'ScalPDF-CLI --help'
echo   • Uninstall: Find 'Uninstall ScalPDF' in Start Menu
echo.
echo 🔧 Installation Details:
echo   • Application: %INSTALL_DIR%
echo   • Start Menu: %START_MENU_DIR%\ScalPDF.lnk
echo   • Desktop: %DESKTOP_DIR%\ScalPDF.lnk
echo.
echo %BLUE%ScalPDF is now ready to use! 🚀%NC%
echo.
pause
