# Sync repo assets/ to frontend/public/assets/
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root "assets"
$dst = Join-Path $root "frontend\public\assets"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
Write-Host "Synced assets to frontend/public/assets"
