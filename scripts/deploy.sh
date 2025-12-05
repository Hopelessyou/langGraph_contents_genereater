#!/bin/bash
# 배포 스크립트

set -e

echo "IBS 법률 AI 시스템 배포 시작..."

# 환경 변수 확인
if [ -z "$OPENAI_API_KEY" ]; then
    echo "경고: OPENAI_API_KEY가 설정되지 않았습니다."
fi

# Docker 빌드
echo "Docker 이미지 빌드 중..."
docker-compose build

# 서비스 시작
echo "서비스 시작 중..."
docker-compose up -d

# 헬스체크
echo "헬스체크 중..."
sleep 5
curl -f http://localhost:8000/api/v1/health || exit 1

echo "배포 완료!"

