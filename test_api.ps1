# 测试后端接口的脚本
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$base = 'http://localhost:5000'

Write-Host "== LOGIN ==" -ForegroundColor Green
$loginData = @{
    username = 'admin';
    password = 'admin123';
}
$loginBody = $loginData | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Method Post -Uri "$base/api/v1/auth/login" -ContentType "application/json" -Body $loginBody
Write-Host "Login Response:" -ForegroundColor Yellow
$loginResponse | ConvertTo-Json -Depth 6

$token = $loginResponse.data.token
if (-not $token) {
    Write-Error "未获取到token"
    exit 1
}

Write-Host "== GET USER INFO ==" -ForegroundColor Green
$headers = @{ Authorization = "Bearer $token" }
$userInfo = Invoke-RestMethod -Method Get -Uri "$base/api/v1/auth/userinfo" -Headers $headers
Write-Host "User Info:" -ForegroundColor Yellow
$userInfo | ConvertTo-Json -Depth 6

Write-Host "== LIST TASKS ==" -ForegroundColor Green
try {
    $tasks = Invoke-RestMethod -Method Get -Uri "$base/api/v1/dispatch/tasks" -Headers $headers
    Write-Host "Task list OK:" -ForegroundColor Green
    $tasks | ConvertTo-Json -Depth 6
} catch {
    Write-Host "Task list FAILED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host ("Error Content: " + $errorContent) -ForegroundColor Red
    }
}

# == CREATE TASK ==
Write-Host "== CREATE TASK ==" -ForegroundColor Green
$createBodyObj = [ordered]@{
    title           = "airport-transfer-auto-" + (Get-Date).ToString('yyyyMMddHHmmss');
    description     = "auto created";
    start_time      = (Get-Date).AddMinutes(5).ToString('yyyy-MM-ddTHH:mm:ss');
    end_time        = (Get-Date).AddHours(2).ToString('yyyy-MM-ddTHH:mm:ss');
    vehicle_type    = "minibus";
    passenger_count = 5;
    location        = "T3 Terminal";
    contact_person  = "LiSi";
    contact_phone   = "13800138000";
}
$createResp = $null
try {
    $createResp = Invoke-RestMethod -Method Post -Uri "$base/api/v1/dispatch/tasks" -Headers $headers -ContentType "application/json" -Body ($createBodyObj | ConvertTo-Json -Depth 6)
    Write-Host "Create OK:" -ForegroundColor Green
    $createResp | ConvertTo-Json -Depth 6
} catch {
    Write-Host "Create FAILED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host ("Error Content: " + $errorContent) -ForegroundColor Red
    }
    exit 1
}

$taskId = $createResp.data.task_id
if (-not $taskId) {
    Write-Error "未获取到task_id"
    exit 1
}

# == UPDATE TASK ==
Write-Host "== UPDATE TASK ==" -ForegroundColor Green
$updateObj = @{
    description = 'desc updated';
    location    = 'T3 Waiting Hall';
}
try {
    $updateResp = Invoke-RestMethod -Method Put -Uri "$base/api/v1/dispatch/tasks/$taskId" -Headers $headers -ContentType "application/json" -Body ($updateObj | ConvertTo-Json -Depth 6)
    Write-Host "Update OK:" -ForegroundColor Green
    $updateResp | ConvertTo-Json -Depth 6
} catch {
    Write-Host "Update FAILED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host ("Error Content: " + $errorContent) -ForegroundColor Red
    }
    exit 1
}

# == APPROVE TASK ==
Write-Host "== APPROVE TASK ==" -ForegroundColor Green
$approveObj = @{ approved = $true; comment = "approved" }
try {
    $approveResp = Invoke-RestMethod -Method Post -Uri "$base/api/v1/dispatch/tasks/$taskId/approve" -Headers $headers -ContentType "application/json" -Body ($approveObj | ConvertTo-Json -Depth 6)
    Write-Host "Approve OK:" -ForegroundColor Green
    $approveResp | ConvertTo-Json -Depth 6
} catch {
    Write-Host "Approve FAILED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host ("Error Content: " + $errorContent) -ForegroundColor Red
    }
    exit 1
}

# == ASSIGN VEHICLE ==
Write-Host "== ASSIGN VEHICLE ==" -ForegroundColor Green
$assignObj = [ordered]@{
    vehicle_id    = $null;
    license_plate = "BJ-A" + (Get-Random -Minimum 10000 -Maximum 99999);
    driver_name   = "Zhang San";
    driver_phone  = "13800000000";
}
try {
    $assignResp = Invoke-RestMethod -Method Post -Uri "$base/api/v1/dispatch/tasks/$taskId/assign" -Headers $headers -ContentType "application/json" -Body ($assignObj | ConvertTo-Json -Depth 6)
    Write-Host "Assign OK:" -ForegroundColor Green
    $assignResp | ConvertTo-Json -Depth 6
} catch {
    Write-Host "Assign FAILED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host ("Error Content: " + $errorContent) -ForegroundColor Red
    }
    exit 1
}

# == COMPLETE TASK ==
Write-Host "== COMPLETE TASK ==" -ForegroundColor Green
$completeObj = @{ completion_notes = "Driver completed drop-off" }
try {
    $completeResp = Invoke-RestMethod -Method Post -Uri "$base/api/v1/dispatch/tasks/$taskId/complete" -Headers $headers -ContentType "application/json" -Body ($completeObj | ConvertTo-Json -Depth 6)
    Write-Host "Complete OK:" -ForegroundColor Green
    $completeResp | ConvertTo-Json -Depth 6
} catch {
    Write-Host "Complete FAILED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host ("Error Content: " + $errorContent) -ForegroundColor Red
    }
    exit 1
}

Write-Host "== TEST DONE ==" -ForegroundColor Green