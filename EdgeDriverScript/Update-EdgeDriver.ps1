param(
    [string]$EdgeDriverPath = ""
)

If ($EdgeDriverPath -eq $null -or $EdgeDriverPath -eq "") {
    # End the script if the EdgeDriverPath parameter is not specified
    Write-Host "Please specify the path to the EdgeDriver directory." -ForegroundColor Red 
    Write-Host "Example: Update-EdgeDriver.ps1 -EdgeDriverPath 'C:\EdgeDriver'" -ForegroundColor Red
    Exit
}

Write-Output "Getting latest Edge version..."

# Get the current running version of Edge
$EdgeDriverVersion = (Get-Item (Get-ChildItem "$Env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe" -Recurse).VersionInfo.FileName).VersionInfo.ProductVersion
$EdgeDriverVersion = $EdgeDriverVersion[0]

Write-Output "Current Edge version: $EdgeDriverVersion"
Write-Output ""

# Check if the EdgeDriver directory exists, and create it if it does not
if (!(Test-Path $EdgeDriverPath)) {
    Write-Output "Creating EdgeWebDriver directory..."
    
    New-Item -ItemType Directory -Path $EdgeDriverPath

    Write-Output "Directory created."
    Write-Output ""
}

Write-Output "Downloading EdgeWebDriver..."

# Download the latest version of the Edge WebDriver
$DownloadUrl = "https://msedgedriver.azureedge.net/$EdgeDriverVersion/edgedriver_win64.zip"
$DownloadPath = "$EdgeDriverPath\edgedriver.zip"
Invoke-WebRequest -Uri $DownloadUrl -OutFile $DownloadPath

Write-Output "Download complete."
Write-Output ""
Write-Output "Extracting EdgeWebDriver..."

# Extract the Edge WebDriver from the downloaded ZIP file
Expand-Archive -Path "$EdgeDriverPath\edgedriver.zip" -DestinationPath $EdgeDriverPath -Force

Write-Output "Exctraction complete."
Write-Output ""
Write-Output "Removing ZIP file..."

# Remove the downloaded ZIP file
Remove-Item "$EdgeDriverPath\edgedriver.zip"

Write-Output "Removal complete."
Write-Output ""
Write-Output "Done!"
