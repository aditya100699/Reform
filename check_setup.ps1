# Reform Project - Setup Verification Script
# Run this script to check what's installed and what you need to install

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Reform Project - Setup Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = py --version 2>&1
    Write-Host "   [OK] Python found: $pythonVersion" -ForegroundColor Green
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $majorVersion = [int]$matches[1]
        $minorVersion = [int]$matches[2]
        if ($majorVersion -ge 3 -and $minorVersion -ge 9) {
            Write-Host "   [OK] Python version is 3.9+ (required)" -ForegroundColor Green
        } else {
            Write-Host "   [FAIL] Python 3.9+ required, you have $majorVersion.$minorVersion" -ForegroundColor Red
            $allGood = $false
        }
    }
} else {
    Write-Host "   [FAIL] Python not found. Install from: https://www.python.org/" -ForegroundColor Red
    $allGood = $false
}

# Check Node.js
Write-Host ""
Write-Host "2. Checking Node.js..." -ForegroundColor Yellow
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVersion = node --version 2>&1
    Write-Host "   [OK] Node.js found: $nodeVersion" -ForegroundColor Green
    if ($nodeVersion -match "v(\d+)") {
        $nodeVersionNumber = [int]$matches[1]
        if ($nodeVersionNumber -ge 18) {
            Write-Host "   [OK] Node.js version is 18+ (required)" -ForegroundColor Green
        } else {
            Write-Host "   [WARN] Node.js 18+ recommended, you have $nodeVersion" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   [FAIL] Node.js not found. Install from: https://nodejs.org/" -ForegroundColor Red
    $allGood = $false
}

# Check npm
Write-Host ""
Write-Host "3. Checking npm..." -ForegroundColor Yellow
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if ($npmCmd) {
    $npmVersion = npm --version 2>&1
    Write-Host "   [OK] npm found: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] npm not found" -ForegroundColor Red
    $allGood = $false
}

# Check PostgreSQL
Write-Host ""
Write-Host "4. Checking PostgreSQL..." -ForegroundColor Yellow
$psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlCmd) {
    $psqlVersion = psql --version 2>&1
    Write-Host "   [OK] PostgreSQL found: $psqlVersion" -ForegroundColor Green
} else {
    Write-Host "   [WARN] PostgreSQL command not in PATH" -ForegroundColor Yellow
    Write-Host "     Checking if service is running..." -ForegroundColor Yellow
    $pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
    if ($pgService) {
        Write-Host "     [OK] PostgreSQL service found: $($pgService.Name)" -ForegroundColor Green
        if ($pgService.Status -eq "Running") {
            Write-Host "     [OK] PostgreSQL service is running" -ForegroundColor Green
        } else {
            Write-Host "     [WARN] PostgreSQL service is not running" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   [FAIL] PostgreSQL not found. Install from: https://www.postgresql.org/download/windows/" -ForegroundColor Red
        $allGood = $false
    }
}

# Check Redis
Write-Host ""
Write-Host "5. Checking Redis..." -ForegroundColor Yellow
$redisCmd = Get-Command redis-cli -ErrorAction SilentlyContinue
if ($redisCmd) {
    $redisVersion = redis-cli --version 2>&1
    Write-Host "   [OK] Redis found: $redisVersion" -ForegroundColor Green
} else {
    Write-Host "   [WARN] Redis not found (optional for development)" -ForegroundColor Yellow
    Write-Host "     Install from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    Write-Host "     Or use Docker: docker run -d -p 6379:6379 redis" -ForegroundColor Yellow
}

# Check Git
Write-Host ""
Write-Host "6. Checking Git..." -ForegroundColor Yellow
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) {
    $gitVersion = git --version 2>&1
    Write-Host "   [OK] Git found: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "   [WARN] Git not found. Install from: https://git-scm.com/download/win" -ForegroundColor Yellow
}

# Check Backend Setup
Write-Host ""
Write-Host "7. Checking Backend Setup..." -ForegroundColor Yellow
if (Test-Path "backend") {
    Write-Host "   [OK] Backend directory exists" -ForegroundColor Green
    
    if (Test-Path "backend\venv") {
        Write-Host "   [OK] Virtual environment exists" -ForegroundColor Green
        
        $pythonExe = "backend\venv\Scripts\python.exe"
        if (Test-Path $pythonExe) {
            $djangoCheck = & $pythonExe -c "import django; print(django.get_version())" 2>&1
            if ($djangoCheck -match "\d+\.\d+") {
                Write-Host "   [OK] Django installed: v$djangoCheck" -ForegroundColor Green
            } else {
                Write-Host "   [FAIL] Django not installed in virtual environment" -ForegroundColor Red
                Write-Host "     Run: cd backend; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Yellow
                $allGood = $false
            }
        }
    } else {
        Write-Host "   [FAIL] Virtual environment not created" -ForegroundColor Red
        Write-Host "     Run: cd backend; py -m venv venv" -ForegroundColor Yellow
        $allGood = $false
    }
    
    if (Test-Path "backend\.env") {
        Write-Host "   [OK] .env file exists" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] .env file not found" -ForegroundColor Yellow
        Write-Host "     Run: cd backend; copy .env.example .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [FAIL] Backend directory not found" -ForegroundColor Red
    $allGood = $false
}

# Check Mobile Setup
Write-Host ""
Write-Host "8. Checking Mobile App Setup..." -ForegroundColor Yellow
if (Test-Path "mobile") {
    Write-Host "   [OK] Mobile directory exists" -ForegroundColor Green
    
    if (Test-Path "mobile\node_modules") {
        Write-Host "   [OK] Node modules installed" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Node modules not installed" -ForegroundColor Yellow
        Write-Host "     Run: cd mobile; npm install" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [FAIL] Mobile directory not found" -ForegroundColor Red
    $allGood = $false
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  Status: [OK] Ready to code!" -ForegroundColor Green
} else {
    Write-Host "  Status: [WARN] Some setup required" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $allGood) {
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Install missing prerequisites (see above)" -ForegroundColor White
    Write-Host "2. Run the setup script: cd backend; .\setup_windows.ps1" -ForegroundColor White
    Write-Host "3. Or follow the manual setup in QUICKSTART_WINDOWS.md" -ForegroundColor White
    Write-Host ""
}
