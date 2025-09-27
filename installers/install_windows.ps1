# ScalPDF Windows PowerShell Installer
# Advanced installer with better error handling and Windows integration

param(
    [switch]$NoDesktopShortcut,
    [switch]$NoStartMenu,
    [string]$InstallPath = "$env:LOCALAPPDATA\ScalPDF"
)

# Requires PowerShell 5.0+
#Requires -Version 5.0

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Green = "Green"
    Blue = "Blue" 
    Yellow = "Yellow"
    Red = "Red"
    Cyan = "Cyan"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Status {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Main installation function
function Install-ScalPDF {
    Write-ColorOutput "🚀 ScalPDF Windows PowerShell Installer" "Blue"
    Write-Host "=" * 50

    # Configuration
    $AppName = "ScalPDF"
    $VenvDir = Join-Path $InstallPath "venv"
    $StartMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
    $DesktopDir = [Environment]::GetFolderPath("Desktop")
    
    try {
        # Check if running as administrator (not required, but warn)
        if (Test-Administrator) {
            Write-Warning "Running as Administrator. This will install for all users."
        }

        # Check Python installation
        Write-Host "🔍 Checking Python installation..."
        try {
            $pythonVersion = python --version 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "Python not found"
            }
            Write-Status "Python detected: $pythonVersion"
        }
        catch {
            Write-Error "Python is not installed or not in PATH"
            Write-Host "Please install Python 3.11+ from https://python.org"
            Write-Host "Make sure to check 'Add Python to PATH' during installation"
            exit 1
        }

        # Verify Python version
        $versionCheck = python -c "import sys; print(sys.version_info >= (3, 11))" 2>&1
        if ($versionCheck -ne "True") {
            Write-Error "Python 3.11+ required"
            exit 1
        }

        # Check pip
        Write-Host "📦 Checking pip..."
        try {
            python -m pip --version | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "pip not available"
            }
            Write-Status "pip is available"
        }
        catch {
            Write-Error "pip is not available"
            exit 1
        }

        # Create installation directory
        Write-Host "📁 Creating installation directory..."
        if (Test-Path $InstallPath) {
            Write-Host "Removing existing installation..."
            Remove-Item -Path $InstallPath -Recurse -Force
        }
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Status "Installation directory created: $InstallPath"

        # Copy application files
        Write-Host "📋 Copying application files..."
        $sourceFiles = Get-ChildItem -Path "." -Exclude "installers", ".git", "__pycache__", "*.pyc", "build", "dist"
        foreach ($file in $sourceFiles) {
            Copy-Item -Path $file.FullName -Destination $InstallPath -Recurse -Force
        }
        Write-Status "Application files copied"

        # Create virtual environment
        Write-Host "🐍 Creating Python virtual environment..."
        Set-Location $InstallPath
        python -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Status "Virtual environment created"

        # Activate virtual environment and install dependencies
        Write-Host "📦 Installing Python dependencies..."
        & "$VenvDir\Scripts\Activate.ps1"
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        Write-Status "Python dependencies installed"

        # Create launcher scripts
        Write-Host "🔧 Creating launcher scripts..."
        
        # PowerShell GUI launcher
        $guiLauncher = @"
# ScalPDF GUI Launcher
Set-Location "$InstallPath"
& "$VenvDir\Scripts\Activate.ps1"
python main.py `$args
"@
        $guiLauncher | Out-File -FilePath "$InstallPath\ScalPDF.ps1" -Encoding UTF8

        # PowerShell CLI launcher
        $cliLauncher = @"
# ScalPDF CLI Launcher
Set-Location "$InstallPath"
& "$VenvDir\Scripts\Activate.ps1"
python -m cli.cli `$args
"@
        $cliLauncher | Out-File -FilePath "$InstallPath\ScalPDF-CLI.ps1" -Encoding UTF8

        # Batch file launchers (for compatibility)
        $guiBatch = @"
@echo off
cd /d "$InstallPath"
call "$VenvDir\Scripts\activate.bat"
python main.py %*
"@
        $guiBatch | Out-File -FilePath "$InstallPath\ScalPDF.bat" -Encoding ASCII

        $cliBatch = @"
@echo off
cd /d "$InstallPath"
call "$VenvDir\Scripts\activate.bat"
python -m cli.cli %*
"@
        $cliBatch | Out-File -FilePath "$InstallPath\ScalPDF-CLI.bat" -Encoding ASCII

        Write-Status "Launcher scripts created"

        # Create application icon
        Write-Host "🎨 Creating application icon..."
        $assetsDir = Join-Path $InstallPath "assets"
        if (-not (Test-Path $assetsDir)) {
            New-Item -ItemType Directory -Path $assetsDir | Out-Null
        }

        # Create a simple icon using .NET
        try {
            Add-Type -AssemblyName System.Drawing
            $bitmap = New-Object System.Drawing.Bitmap(256, 256)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.Clear([System.Drawing.Color]::FromArgb(37, 99, 235))
            
            # Draw PDF text
            $font = New-Object System.Drawing.Font("Arial", 32, [System.Drawing.FontStyle]::Bold)
            $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
            $graphics.DrawString("PDF", $font, $brush, 80, 100)
            
            # Draw lock symbol
            $lockPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Gold, 4)
            $graphics.DrawRectangle($lockPen, 180, 180, 30, 40)
            $graphics.DrawArc($lockPen, 175, 165, 40, 30, 0, 180)
            
            $iconPath = Join-Path $assetsDir "icon.png"
            $bitmap.Save($iconPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $graphics.Dispose()
            $bitmap.Dispose()
            Write-Status "Application icon created"
        }
        catch {
            Write-Warning "Could not create icon: $($_.Exception.Message)"
        }

        # Create Start Menu shortcuts
        if (-not $NoStartMenu) {
            Write-Host "🖥️  Creating Start Menu shortcuts..."
            
            $shell = New-Object -ComObject WScript.Shell
            
            # GUI shortcut
            $shortcut = $shell.CreateShortcut("$StartMenuDir\ScalPDF.lnk")
            $shortcut.TargetPath = "powershell.exe"
            $shortcut.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$InstallPath\ScalPDF.ps1`""
            $shortcut.WorkingDirectory = $InstallPath
            $shortcut.Description = "ScalPDF - Secure PDF Management Tool"
            $shortcut.IconLocation = "$InstallPath\assets\icon.png"
            $shortcut.Save()
            
            # CLI shortcut
            $cliShortcut = $shell.CreateShortcut("$StartMenuDir\ScalPDF CLI.lnk")
            $cliShortcut.TargetPath = "powershell.exe"
            $cliShortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$InstallPath\ScalPDF-CLI.ps1`""
            $cliShortcut.WorkingDirectory = $InstallPath
            $cliShortcut.Description = "ScalPDF Command Line Interface"
            $cliShortcut.IconLocation = "$InstallPath\assets\icon.png"
            $cliShortcut.Save()
            
            Write-Status "Start Menu shortcuts created"
        }

        # Create Desktop shortcut
        if (-not $NoDesktopShortcut) {
            Write-Host "🖥️  Creating Desktop shortcut..."
            
            $shell = New-Object -ComObject WScript.Shell
            $desktopShortcut = $shell.CreateShortcut("$DesktopDir\ScalPDF.lnk")
            $desktopShortcut.TargetPath = "powershell.exe"
            $desktopShortcut.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$InstallPath\ScalPDF.ps1`""
            $desktopShortcut.WorkingDirectory = $InstallPath
            $desktopShortcut.Description = "ScalPDF - Secure PDF Management Tool"
            $desktopShortcut.IconLocation = "$InstallPath\assets\icon.png"
            $desktopShortcut.Save()
            
            Write-Status "Desktop shortcut created"
        }

        # Create uninstaller
        Write-Host "🗑️  Creating uninstaller..."
        $uninstaller = @"
# ScalPDF Uninstaller
Write-Host "🗑️ Uninstalling ScalPDF..." -ForegroundColor Yellow

# Remove installation directory
if (Test-Path "$InstallPath") {
    Remove-Item -Path "$InstallPath" -Recurse -Force
    Write-Host "✅ Application files removed" -ForegroundColor Green
}

# Remove Start Menu shortcuts
Remove-Item -Path "$StartMenuDir\ScalPDF.lnk" -ErrorAction SilentlyContinue
Remove-Item -Path "$StartMenuDir\ScalPDF CLI.lnk" -ErrorAction SilentlyContinue
Remove-Item -Path "$StartMenuDir\Uninstall ScalPDF.lnk" -ErrorAction SilentlyContinue
Write-Host "✅ Start Menu shortcuts removed" -ForegroundColor Green

# Remove Desktop shortcut
Remove-Item -Path "$DesktopDir\ScalPDF.lnk" -ErrorAction SilentlyContinue
Write-Host "✅ Desktop shortcut removed" -ForegroundColor Green

Write-Host "✅ ScalPDF uninstalled successfully" -ForegroundColor Green
Read-Host "Press Enter to continue"
"@
        $uninstaller | Out-File -FilePath "$InstallPath\Uninstall.ps1" -Encoding UTF8

        # Create uninstaller shortcut
        if (-not $NoStartMenu) {
            $shell = New-Object -ComObject WScript.Shell
            $uninstallShortcut = $shell.CreateShortcut("$StartMenuDir\Uninstall ScalPDF.lnk")
            $uninstallShortcut.TargetPath = "powershell.exe"
            $uninstallShortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallPath\Uninstall.ps1`""
            $uninstallShortcut.WorkingDirectory = $InstallPath
            $uninstallShortcut.Description = "Uninstall ScalPDF"
            $uninstallShortcut.Save()
        }

        Write-Status "Uninstaller created"

        # Run installation tests
        Write-Host "🧪 Running installation tests..."
        & "$VenvDir\Scripts\Activate.ps1"
        
        $testScript = @"
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
"@
        
        python -c $testScript
        if ($LASTEXITCODE -ne 0) {
            throw "Installation tests failed"
        }
        Write-Status "Installation tests passed"

        # Success message
        Write-Host ""
        Write-ColorOutput "🎉 ScalPDF installed successfully!" "Green"
        Write-Host ""
        Write-Host "📖 Usage:"
        Write-Host "  • GUI: Find 'ScalPDF' in Start Menu or Desktop"
        Write-Host "  • CLI: Open PowerShell and run the ScalPDF CLI shortcut"
        Write-Host "  • Uninstall: Find 'Uninstall ScalPDF' in Start Menu"
        Write-Host ""
        Write-Host "🔧 Installation Details:"
        Write-Host "  • Application: $InstallPath"
        Write-Host "  • Start Menu: $StartMenuDir\ScalPDF.lnk"
        Write-Host "  • Desktop: $DesktopDir\ScalPDF.lnk"
        Write-Host ""
        Write-ColorOutput "ScalPDF is now ready to use! 🚀" "Blue"
        
    }
    catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        Write-Host "Please check the error message above and try again."
        exit 1
    }
}

# Run the installer
Install-ScalPDF
