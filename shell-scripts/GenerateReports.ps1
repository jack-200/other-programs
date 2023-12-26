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

# Get the current date in a locale-independent way
$dateTime = Get-WmiObject Win32_LocalTime | ForEach-Object { "{0:D4}{1:D2}{2:D2}" -f $_.Year, $_.Month, $_.Day }

# Assemble the date in "YYYY-MM-DD" format
$currentDate = $dateTime.Insert(4, "-").Insert(7, "-")

# Generate the battery and system information report with the date in the filename
$batteryReportPath = Join-Path $env:userprofile "Downloads\battery-report-$currentDate.html"
powercfg /batteryreport /output $batteryReportPath
Write-Host "Battery report generated: $batteryReportPath"
PrintBatteryCapacity -FilePath $batteryReportPath

$systemInfoPath = Join-Path $env:userprofile "Downloads\system-info-$currentDate.nfo"
msinfo32 /nfo "$systemInfoPath"
Wait-Process -Name msinfo32
Write-Host "System information saved: $systemInfoPath`n"

Pause