# 배포 스크립트 (PowerShell)

Write-Host "IBS 법률 AI 시스템 배포 시작..." -ForegroundColor Green

# 환경 변수 확인
if (-not $env:OPENAI_API_KEY) {
    Write-Host "경고: OPENAI_API_KEY가 설정되지 않았습니다." -ForegroundColor Yellow
}

# Docker 빌드
Write-Host "Docker 이미지 빌드 중..." -ForegroundColor Cyan
docker-compose build

# 서비스 시작
Write-Host "서비스 시작 중..." -ForegroundColor Cyan
docker-compose up -d

# 헬스체크
Write-Host "헬스체크 중..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing
    Write-Host "배포 완료!" -ForegroundColor Green
} catch {
    Write-Host "헬스체크 실패: $_" -ForegroundColor Red
    exit 1
}

