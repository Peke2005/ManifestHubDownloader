@echo off
setlocal enabledelayedexpansion
color 0C
title Steam Manifest Hub - CLI Edition

:: Disclaimer
cls
echo.
echo ================================
echo [DISCLAIMER]
echo ================================
echo.
echo This script is for informational purposes only.
echo We are not responsible for any consequences that may arise from using the provided data.
echo.

choice /c YN /n /m "Press Y to accept and continue, or N to exit: "
if errorlevel 2 exit /b
if errorlevel 1 goto :main

:main
color 0A
cls
echo.
echo ================================
echo Steam Manifest Hub - CLI Edition
echo ================================
echo.

:input
set "appid="
set /p "appid=Enter your desired Steam AppID: "

:: Validate input
if not defined appid goto :input
echo %appid%| findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo.
    echo [ERROR] Please enter numbers only.
    echo.
    timeout /t 3 /nobreak >nul
    goto :main
)

:: Check manifest
echo.
echo ^> Initiating manifest check for Steam AppID: %appid%
echo ^> Searching database...

set "url=https://api.github.com/repos/SteamAutoCracks/ManifestHub/branches/%appid%"
set "archive_url=https://codeload.github.com/SteamAutoCracks/ManifestHub/zip/refs/heads/%appid%"
set "manifest_status="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command ^
"$headers = @{ 'Accept' = 'application/vnd.github+json'; 'User-Agent' = 'ManifestHubDownloader/1.0' }; ^
$retryable = @(403, 429, 500, 502, 503, 504); ^
$apiUrl = '%url%'; ^
$archiveUrl = '%archive_url%'; ^
$status = 'check_failed'; ^
for ($attempt = 0; $attempt -lt 2; $attempt++) { ^
    try { ^
        $response = Invoke-WebRequest -Uri $apiUrl -Headers $headers -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop; ^
        if ($response.StatusCode -eq 200) { $status = 'found'; break } ^
        if ($response.StatusCode -eq 404) { $status = 'not_found'; break } ^
        if (-not ($retryable -contains [int]$response.StatusCode)) { break } ^
    } catch { ^
        $code = $null; ^
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode.value__; } ^
        if ($code -eq 404) { $status = 'not_found'; break } ^
        if ($code -and (-not ($retryable -contains $code))) { break } ^
    } ^
    Start-Sleep -Milliseconds 700 ^
} ^
if ($status -eq 'check_failed') { ^
    for ($attempt = 0; $attempt -lt 2; $attempt++) { ^
        try { ^
            $response = Invoke-WebRequest -Method Head -Uri $archiveUrl -Headers $headers -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 10 -ErrorAction Stop; ^
            if ($response.StatusCode -eq 200) { $status = 'found'; break } ^
            if ($response.StatusCode -eq 404) { $status = 'not_found'; break } ^
            if (-not ($retryable -contains [int]$response.StatusCode)) { break } ^
        } catch { ^
            $code = $null; ^
            if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode.value__; } ^
            if ($code -eq 404) { $status = 'not_found'; break } ^
            if ($code -and (-not ($retryable -contains $code))) { break } ^
        } ^
        Start-Sleep -Milliseconds 700 ^
    } ^
} ^
Write-Output $status"`) do set "manifest_status=%%i"

if not defined manifest_status set "manifest_status=check_failed"

if /i "%manifest_status%"=="not_found" (
    echo ^> Manifest not found.
    echo.
    echo No manifests were found for this Steam application, at least for now...
    echo.
    pause
    goto :main
)

if /i not "%manifest_status%"=="found" (
    echo ^> GitHub could not verify this manifest right now.
    echo ^> You can still try the direct download link below.
    echo.
    echo Download link:
    echo %archive_url%
    echo.
    echo The manifests are downloaded from the ManifestHub Database.
    echo Show them support on GitHub: https://github.com/SteamAutoCracks/ManifestHub/
    echo.
    pause
    goto :main
)

:: Manifest found
echo ^> Manifest found in database!
echo ^> Preparing download link...
echo ^> Ready for download.
echo.
echo Download link:
echo %archive_url%
echo.
echo The manifests are downloaded from the ManifestHub Database.
echo Show them support on GitHub: https://github.com/SteamAutoCracks/ManifestHub/
echo.
pause
goto :main
