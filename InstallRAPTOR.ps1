# Download .whl/.xlam
Write-Output "Lade RAPTOR Dateien herunter..."
$release = Invoke-RestMethod -Uri "https://api.github.com/repos/Gustav267/Raptor/releases/latest"
$downloadDir = "$env:USERPROFILE\Downloads\Raptor"
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

$whlFiles = @()
$xlamFile = $null
foreach ($asset in $release.assets) {
    if ($asset.name -like "*.whl" -or $asset.name -like "*.xlam") {
        $outPath = Join-Path $downloadDir $asset.name
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $outPath
        if ($asset.name -like "*.whl") { $whlFiles += $outPath }
        if ($asset.name -like "*.xlam") { $xlamFile = $outPath }
    }
}

# Install downloaded .whl files
Write-Output "Installiere Python Pakete..."
& python -m pip install $whlFiles

# Install .xlam add-in using xlwings
Write-Output "Installiere Excel Add-In..."
$pythonInstallDir = & python -c "import sys; print(sys.prefix)"
$xlwings = "$pythonInstallDir\Scripts\xlwings.exe"
& $xlwings addin install --path $xlamFile
