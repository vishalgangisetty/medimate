# ============================================
# MediMate Premium UI - Activation Script
# ============================================

Write-Host "`n🎨 MediMate Premium UI Activation`n" -ForegroundColor Cyan

# Check if we're in the right directory
if (-Not (Test-Path "app.py")) {
    Write-Host "❌ Error: app.py not found. Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Backup original files
Write-Host "📦 Step 1: Creating backups..." -ForegroundColor Yellow
if (-Not (Test-Path "app_original.py")) {
    Copy-Item "app.py" "app_original.py"
    Write-Host "   ✅ Backed up app.py → app_original.py" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Backup already exists: app_original.py" -ForegroundColor Gray
}

if (-Not (Test-Path "src\ui_pages_original.py")) {
    Copy-Item "src\ui_pages.py" "src\ui_pages_original.py"
    Write-Host "   ✅ Backed up ui_pages.py → ui_pages_original.py" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Backup already exists: ui_pages_original.py" -ForegroundColor Gray
}

# Activate premium UI
Write-Host "`n🚀 Step 2: Activating Premium UI..." -ForegroundColor Yellow
Copy-Item "app_premium.py" "app.py" -Force
Write-Host "   ✅ Activated app_premium.py → app.py" -ForegroundColor Green

Copy-Item "src\ui_pages_premium.py" "src\ui_pages.py" -Force
Write-Host "   ✅ Activated ui_pages_premium.py → ui_pages.py" -ForegroundColor Green

# Verify CSS file exists
Write-Host "`n🎨 Step 3: Verifying design assets..." -ForegroundColor Yellow
if (Test-Path "style.css") {
    Write-Host "   ✅ style.css found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  WARNING: style.css not found! Premium styling will not work." -ForegroundColor Red
    Write-Host "   Please ensure style.css is in the project root." -ForegroundColor Red
}

# Success message
Write-Host "`n✨ Premium UI Activated Successfully!`n" -ForegroundColor Green
Write-Host "To run the premium app:" -ForegroundColor Cyan
Write-Host "   streamlit run app.py`n" -ForegroundColor White

Write-Host "To restore original UI:" -ForegroundColor Cyan
Write-Host "   Copy-Item app_original.py app.py -Force" -ForegroundColor White
Write-Host "   Copy-Item src\ui_pages_original.py src\ui_pages.py -Force`n" -ForegroundColor White

Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - DESIGN_SYSTEM.md   (Complete visual specs)" -ForegroundColor White
Write-Host "   - PREMIUM_UI_GUIDE.md (Implementation guide)" -ForegroundColor White
Write-Host "   - QUICK_START.md     (Quick reference)`n" -ForegroundColor White
