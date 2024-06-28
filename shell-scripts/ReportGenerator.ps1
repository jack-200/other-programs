#Requires -RunAsAdministrator

function PrintBatteryCapacity {
    param (
        [string]$FilePath
    )
    $htmlContent = Get-Content -Path $FilePath -Raw

    # Define a function to extract values using regex
    function Get-ValueFromHtml($html, $pattern) {
        $match = [regex]::Match($html, $pattern)
        if ($match.Success) {
            $match.Groups[1].Value.Trim().Split(' ')
        }
        else {
            Write-Host "Value not found." 
            $null
        }
    }

    # Use regex to extract values for FULL CHARGE CAPACITY and DESIGN CAPACITY
    $fullChargeCapacityActual, $units = (Get-ValueFromHtml -html $htmlContent -pattern '(?<=FULL CHARGE CAPACITY<\/span><\/td>\s*<td>)([^<]+)')
    $designCapacityActual = (Get-ValueFromHtml -html $htmlContent -pattern '(?<=DESIGN CAPACITY<\/span><\/td>\s*<td>)([^<]+)')[0]

    # Calculate the percentage
    if ($fullChargeCapacityActual -and $designCapacityActual) { 
        $percentage = [math]::Round(($fullChargeCapacityActual / $designCapacityActual) * 100, 1)
        Write-Host "Battery capacity: $fullChargeCapacityActual of $designCapacityActual $units ($percentage%)`n"
    }
}

# Get today's date in the format YYYY-MM-DD
$currentDate = (Get-Date).ToString("yyyy-MM-dd")

$reportsFolderPath = Join-Path $env:userprofile "Downloads\Reports-$currentDate"

if (-not (Test-Path $reportsFolderPath)) {
    New-Item -ItemType Directory -Path $reportsFolderPath
}

# Generate a battery report
$batteryReportPath = Join-Path $reportsFolderPath "battery-report-$currentDate.html"
powercfg /batteryreport /output $batteryReportPath
Write-Host "Battery report generated to $batteryReportPath"
PrintBatteryCapacity -FilePath $batteryReportPath

# Generate a system information report
$systemInfoPath = Join-Path $reportsFolderPath "system-info-$currentDate.nfo"
msinfo32 /nfo "$systemInfoPath"
Wait-Process -Name msinfo32
Write-Host "System information saved to $systemInfoPath`n"

# Generate a DxDiag report
$dxdiagPath = Join-Path $reportsFolderPath "DxDiag-$currentDate.txt"
Start-Process -FilePath "dxdiag.exe" -ArgumentList "/t $dxdiagPath" -NoNewWindow -Wait
Write-Host "DxDiag report saved to $dxdiagPath`n"

# Generate a detailed driver information report
$driverInfoPath = Join-Path $reportsFolderPath "driver-info-$currentDate.csv"
driverquery /v /fo csv > $driverInfoPath
Write-Host "Detailed driver information saved to $driverInfoPath`n"

Pause