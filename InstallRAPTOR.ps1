Write-Host "Willkommen im Raptor installer!`n`nWir werden die folgenden Dinge installieren:`n`n - Python`n - Python Pakete fuer RAPTOR (matplotlib, numpy, lmfit, xlwings)`n - das Excel Add-In"

$confirmation = Read-Host "Weiter machen? [y/n]"
while($confirmation -ne "y")
{
    if ($confirmation -eq 'n') {exit}
    $confirmation = Read-Host "Weiter machen? [y/n]"
}

Write-Output "Checke, ob winget installiert ist..."
if (Get-Command "winget.exe" -ErrorAction SilentlyContinue) 
{
    Write-Output "winget.exe ist installiert"
}
else
{
    Write-Output "Installiere winget..."
    $appInstallerUrl = "https://aka.ms/getwinget"  
    $downloadPath = "$env:TEMP\AppInstaller.msixbundle"  
    New-Item -ItemType Directory -Path "$env:TEMP" -Force | Out-Null
    Invoke-WebRequest -Uri $appInstallerUrl -OutFile $downloadPath -UseBasicParsing
    Add-AppxPackage -Path $downloadPath
}

Write-Output "Installiere Python mit winget..."
& winget install -s winget "Python.Python.3.14"
$pythonpath = "$env:USERPROFILE\AppData\Local\Programs\Python\Python314"
$python = "$pythonpath\python.exe"
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pythonpath;$pythonpath\Scripts", [System.EnvironmentVariableTarget]::User)
& $python --version
Write-Output "Python erfolgreich installier!"

Write-Output "Hole den aktuellen Quellcode von RAPTOR..."
$raptorZip = "https://github.com/Gustav267/Automated-analysis-of-potentiometric-titrations/archive/refs/heads/gui.zip"
$downloadPath = "$env:TEMP\RAPTOR-Code.zip"  
Invoke-WebRequest -Uri $raptorZip -OutFile $downloadPath

$raptorPath = "$env:USERPROFILE\RAPTOR"
Expand-Archive -Path $downloadPath -DestinationPath "$env:USERPROFILE"
Remove-Item -Recurse -Path $raptorPath
Move-Item "$env:USERPROFILE\Automated-analysis-of-potentiometric-titrations-gui\" "$raptorPath" -Force

$location = Get-Location
Set-Location "$raptorPath"

Write-Output "Installiere Raptor Dependencies..."
& $python -m pip install -r requirements.txt 

Write-Output "Installiere Raptor..."
& $python -m pip install --editable .
'"INTERPRETER_WIN","{0}"
"UDF MODULES","chemistry_raptor_excel"' -f $python | Out-File -FilePath "$env:USERHOME\.xlwings\xlwings.conf"

Write-Output "Installiere xlwings Add-in"
& "$pythonpath\Scripts\xlwings.exe" addin install

Set-Location $location

