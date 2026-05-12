# Copies branding images from repo Data_Dummy into the Flutter app bundle.
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path (Split-Path $PSScriptRoot)
$dataDummy = Join-Path $repoRoot "Data_Dummy"
$destDir = Join-Path (Split-Path $PSScriptRoot) "assets\branding"
New-Item -ItemType Directory -Force -Path $destDir | Out-Null
$logoSrc = Join-Path $dataDummy "logo1.png"
$openSrc = Join-Path $dataDummy "opening_screen.png"
if (Test-Path $logoSrc) {
  Copy-Item -Force $logoSrc (Join-Path $destDir "logo1.png")
  Write-Host "Copied logo1.png"
} else { Write-Warning "Missing: $logoSrc" }
if (Test-Path $openSrc) {
  Copy-Item -Force $openSrc (Join-Path $destDir "opening_screen.png")
  Write-Host "Copied opening_screen.png"
} else { Write-Warning "Missing: $openSrc" }
