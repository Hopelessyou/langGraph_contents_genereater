# Docker 실행 vs 로컬 실행 차이점

## 📋 개요

이 문서는 IBS 법률 AI 시스템을 Docker에서 실행할 때와 로컬에서 실행할 때의 주요 차이점을 설명합니다.

## 🔄 주요 차이점

### 1. **환경 격리**

#### 로컬 실행
- 호스트 시스템의 Python 환경 사용
- 시스템 전역 패키지와 충돌 가능
- 가상환경(venv)으로 격리 가능하지만 완전한 격리는 아님

#### Docker 실행
- 완전히 격리된 컨테이너 환경
- 호스트 시스템과 독립적인 파일 시스템
- Python 버전과 패키지가 컨테이너 내부에만 존재
- 다른 프로젝트와 완전히 분리

```bash
# 로컬: 가상환경 사용
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Docker: 자동으로 격리된 환경
docker-compose up -d
```

---

### 2. **파일 시스템 경로**

#### 로컬 실행
```python
# 상대 경로 사용
data_dir = "./data"
chroma_persist_directory = "./data/vector_db"
log_file = "./logs/app.log"
```

**실제 경로 예시:**
- Windows: `C:\Users\1gmla\OneDrive\Documents\coding\gpt_langraph\ibs_legal_ai_system\data`
- Linux/Mac: `/home/user/projects/ibs_legal_ai_system/data`

#### Docker 실행
```python
# 컨테이너 내부 경로
data_dir = "/app/data"
chroma_persist_directory = "/app/data/vector_db"
log_file = "/app/logs/app.log"
```

**Volume 마운트:**
```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data      # 호스트의 ./data → 컨테이너의 /app/data
  - ./logs:/app/logs      # 호스트의 ./logs → 컨테이너의 /app/logs
```

**차이점:**
- 로컬: 직접 파일 시스템 접근
- Docker: Volume을 통해 호스트와 공유 (데이터 영속성 보장)

---

### 3. **환경 변수 설정**

#### 로컬 실행
```bash
# .env 파일 사용 (프로젝트 루트)
OPENAI_API_KEY=your_key
API_KEY=your_api_key
LOG_LEVEL=INFO
```

**설정 방법:**
```bash
# .env 파일 생성
cp .env.example .env
# .env 파일 편집
```

#### Docker 실행
```yaml
# docker-compose.yml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}  # 호스트의 .env에서 읽음
  - API_KEY=${API_KEY}
  - LLM_MODEL=${LLM_MODEL:-gpt-4-turbo-preview}
  - CHROMA_PERSIST_DIRECTORY=/app/data/vector_db
```

**차이점:**
- 로컬: `.env` 파일 직접 읽기
- Docker: 호스트의 `.env` 파일을 읽어서 컨테이너 환경 변수로 전달

---

### 4. **네트워크 설정**

#### 로컬 실행
```bash
# localhost로 접근
http://localhost:8000
http://127.0.0.1:8000
```

**특징:**
- 같은 머신에서만 접근 가능 (기본 설정)
- `0.0.0.0`으로 바인딩하면 네트워크의 다른 기기에서도 접근 가능

#### Docker 실행
```yaml
# docker-compose.yml
ports:
  - "8000:8000"  # 호스트:컨테이너 포트 매핑
```

**특징:**
- 컨테이너 내부: `0.0.0.0:8000`으로 바인딩
- 호스트에서: `localhost:8000`으로 접근
- 네트워크의 다른 기기에서도 접근 가능 (호스트 IP 사용)

**차이점:**
- 로컬: 직접 포트 바인딩
- Docker: 포트 매핑을 통해 접근

---

### 5. **의존성 관리**

#### 로컬 실행
```bash
# 가상환경 생성 후 설치
pip install -r requirements.txt

# 패키지 업데이트 시
pip install --upgrade package_name
```

**특징:**
- 시스템 의존성(gcc 등)이 호스트에 설치되어 있어야 함
- Python 버전이 호스트 시스템에 맞아야 함

#### Docker 실행
```dockerfile
# Dockerfile
FROM python:3.11-slim

# 시스템 의존성 자동 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt
```

**특징:**
- 컨테이너 빌드 시 모든 의존성 자동 설치
- 호스트 시스템에 Python이나 패키지 설치 불필요
- 재현 가능한 환경 보장

---

### 6. **실행 방식**

#### 로컬 실행
```bash
# 방법 1: Python 모듈로 실행
python -m src.api.main

# 방법 2: uvicorn 직접 실행
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 방법 3: 스크립트 실행
python scripts/parse_statute_pdf.py "path/to/file.pdf"
```

**특징:**
- 코드 변경 시 즉시 반영 (reload 옵션)
- 디버깅이 쉬움
- 개발 중에 유리

#### Docker 실행
```bash
# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 내부에서 명령 실행
docker-compose exec api python scripts/parse_statute_pdf.py "path/to/file.pdf"
```

**특징:**
- 프로덕션 환경에 적합
- 자동 재시작 설정 가능 (`restart: unless-stopped`)
- Health check 자동 수행

---

### 7. **데이터 영속성**

#### 로컬 실행
```python
# 데이터가 직접 프로젝트 디렉토리에 저장
data/
├── vector_db/
│   └── chroma.sqlite3
├── collected/
└── processed/
```

**특징:**
- 파일이 직접 저장됨
- 백업이 쉬움
- 삭제 시 데이터 손실

#### Docker 실행
```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data  # 호스트와 공유
```

**특징:**
- Volume을 통해 호스트와 공유
- 컨테이너 삭제해도 데이터 유지
- 여러 컨테이너가 같은 데이터 공유 가능

**주의사항:**
- Volume 마운트 없이 실행하면 컨테이너 삭제 시 데이터 손실
- Volume 경로는 절대 경로 또는 상대 경로 사용 가능

---

### 8. **로그 관리**

#### 로컬 실행
```python
# 로그 파일이 직접 프로젝트 디렉토리에 저장
logs/
└── app.log
```

**확인 방법:**
```bash
# 직접 파일 확인
cat logs/app.log
tail -f logs/app.log
```

#### Docker 실행
```yaml
# docker-compose.yml
volumes:
  - ./logs:/app/logs  # 호스트와 공유
```

**확인 방법:**
```bash
# Docker 로그 확인
docker-compose logs -f api

# 또는 호스트의 로그 파일 확인
cat logs/app.log
```

**차이점:**
- 로컬: 직접 파일 접근
- Docker: `docker-compose logs` 명령 또는 Volume을 통한 파일 접근

---

### 9. **개발 편의성**

#### 로컬 실행
✅ **장점:**
- 코드 수정 시 즉시 반영 (reload)
- 디버깅이 쉬움
- IDE 통합이 용이
- 빠른 반복 개발

❌ **단점:**
- 환경 설정이 복잡할 수 있음
- 시스템 의존성 관리 필요
- 다른 프로젝트와 충돌 가능

#### Docker 실행
✅ **장점:**
- 환경 설정이 간단 (Docker만 설치)
- 재현 가능한 환경
- 프로덕션과 동일한 환경
- 여러 프로젝트 격리

❌ **단점:**
- 코드 수정 시 컨테이너 재빌드 필요 (개발 모드 제외)
- 디버깅이 상대적으로 어려움
- 초기 빌드 시간 소요

---

### 10. **성능**

#### 로컬 실행
- 네이티브 성능
- 오버헤드 없음
- 빠른 시작 시간

#### Docker 실행
- 약간의 오버헤드 (거의 무시 가능)
- 컨테이너 시작 시간 소요
- 메모리 사용량 약간 증가

**실제 차이:**
- 성능 차이는 거의 없음 (1-2% 이하)
- 대부분의 경우 무시 가능한 수준

---

## 🎯 언제 무엇을 사용할까?

### 로컬 실행을 권장하는 경우
- ✅ 개발 중일 때
- ✅ 빠른 프로토타이핑
- ✅ 디버깅이 중요한 경우
- ✅ 코드를 자주 수정하는 경우
- ✅ 시스템 의존성을 쉽게 관리할 수 있는 경우

### Docker 실행을 권장하는 경우
- ✅ 프로덕션 배포
- ✅ 환경 일관성이 중요한 경우
- ✅ 여러 개발자가 같은 환경을 사용해야 하는 경우
- ✅ CI/CD 파이프라인
- ✅ 시스템 의존성 관리가 어려운 경우
- ✅ 서버에 직접 설치하기 어려운 경우

---

## 🔧 Docker 개발 모드 설정

개발 중에도 Docker를 사용하고 싶다면:

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  api:
    build: .
    volumes:
      - .:/app  # 코드를 마운트하여 변경사항 즉시 반영
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - API_RELOAD=true
```

```bash
# 개발 모드로 실행
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## 📝 요약

| 항목 | 로컬 실행 | Docker 실행 |
|------|----------|------------|
| **환경 격리** | 가상환경 (부분적) | 완전 격리 |
| **경로** | `./data` | `/app/data` (Volume 마운트) |
| **환경 변수** | `.env` 파일 | `.env` → 컨테이너 환경 변수 |
| **네트워크** | `localhost:8000` | 포트 매핑 필요 |
| **의존성** | 수동 설치 | 자동 설치 |
| **실행** | 직접 실행 | `docker-compose up` |
| **데이터** | 직접 저장 | Volume 공유 |
| **로그** | 파일 직접 접근 | `docker-compose logs` |
| **개발** | 즉시 반영 | 재빌드 필요 (개발 모드 제외) |
| **성능** | 네이티브 | 약간의 오버헤드 |

---

## 🚀 빠른 시작

### 로컬 실행
```bash
# 1. 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 4. 서버 실행
python -m src.api.main
```

### Docker 실행
```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 2. Docker Compose로 실행
docker-compose up -d

# 3. 로그 확인
docker-compose logs -f
```

---

## ❓ 자주 묻는 질문

### Q: Docker를 사용하면 여러 컴퓨터에서 접속이 가능한가요?
**A:** 
**중요:** Docker 자체가 여러 컴퓨터 접속을 가능하게 하는 것은 **아닙니다**. 

**실제 상황:**

1. **로컬 실행도 여러 컴퓨터 접속 가능:**
   ```bash
   # .env 파일에서
   API_HOST=0.0.0.0  # 모든 네트워크 인터페이스에서 접근 가능
   
   # 서버 실행
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```
   - 같은 네트워크의 다른 컴퓨터에서 `http://서버IP:8000`으로 접속 가능
   - 예: `http://192.168.1.100:8000`

2. **Docker의 실제 장점:**
   - ✅ **서버 배포가 쉬움**: 원격 서버에 Docker만 설치하면 바로 실행 가능
   - ✅ **환경 일관성**: 어떤 서버에서든 동일한 환경 보장
   - ✅ **포트 매핑 자동화**: `docker-compose.yml`에서 간단히 설정
   - ✅ **여러 인스턴스 실행**: 로드 밸런싱, 스케일링이 쉬움

3. **여러 컴퓨터 접속을 위한 실제 요구사항:**
   - ✅ `API_HOST=0.0.0.0` 설정 (로컬/Docker 공통)
   - ✅ 방화벽에서 포트 8000 허용
   - ✅ 서버의 IP 주소 확인
   - ✅ 같은 네트워크에 있거나, 공인 IP/도메인 필요

**결론:** 
- 로컬 실행: `0.0.0.0` 설정 + 방화벽 설정 → 여러 컴퓨터 접속 가능 ✅
- Docker 실행: `0.0.0.0` 설정 + 방화벽 설정 → 여러 컴퓨터 접속 가능 ✅
- **Docker의 장점은 "접속 가능"이 아니라 "배포와 관리가 쉬움"입니다.**

### Q: Docker에서 데이터를 수정하면 로컬에도 반영되나요?
**A:** 네, Volume 마운트를 사용하면 호스트와 컨테이너가 같은 디렉토리를 공유하므로 양방향으로 반영됩니다.

### Q: 로컬에서 개발하다가 Docker로 배포할 수 있나요?
**A:** 네, 가능합니다. 코드는 동일하며 환경 변수만 조정하면 됩니다.

### Q: Docker 컨테이너를 삭제하면 데이터가 사라지나요?
**A:** Volume 마운트를 사용했다면 데이터는 호스트에 남아있습니다. Volume 마운트 없이 실행했다면 데이터가 손실됩니다.

### Q: 로컬과 Docker에서 성능 차이가 있나요?
**A:** 거의 없습니다. 대부분의 경우 1-2% 이하의 차이로 무시 가능한 수준입니다.

### Q: 여러 컴퓨터에서 접속하려면 어떻게 해야 하나요?

**로컬 실행 시:**
```bash
# 1. .env 파일 설정
API_HOST=0.0.0.0
API_PORT=8000

# 2. 서버 실행
python -m src.api.main

# 3. 서버 IP 확인 (Windows)
ipconfig
# IPv4 주소 확인 (예: 192.168.1.100)

# 4. 다른 컴퓨터에서 접속
http://192.168.1.100:8000
```

**Docker 실행 시:**
```bash
# 1. docker-compose.yml 확인 (포트 매핑 확인)
ports:
  - "8000:8000"

# 2. Docker 실행
docker-compose up -d

# 3. 서버 IP 확인
ipconfig  # Windows
ifconfig  # Linux/Mac

# 4. 다른 컴퓨터에서 접속
http://서버IP:8000
```

**공통 주의사항:**
- 🔥 **방화벽 설정**: Windows 방화벽 또는 Linux iptables에서 포트 8000 허용
- 🌐 **네트워크**: 같은 네트워크(같은 공유기)에 있어야 함
- 🔒 **보안**: 프로덕션 환경에서는 HTTPS와 인증 설정 필수

### Q: 다른 네트워크(인터넷)에서 접속하려면 어떻게 해야 하나요?

**A:** 다른 네트워크에서 접속하려면 여러 방법이 있습니다:

#### 방법 1: 공인 IP + 포트 포워딩 (가정/사무실 서버)

**설정 단계:**

1. **공인 IP 확인**
   ```bash
   # 서버에서 실행
   curl ifconfig.me  # Linux/Mac
   # 또는 브라우저에서 https://whatismyipaddress.com 접속
   ```

2. **공유기에서 포트 포워딩 설정**
   - 공유기 관리 페이지 접속 (보통 `192.168.1.1` 또는 `192.168.0.1`)
   - 포트 포워딩/가상서버 설정 메뉴로 이동
   - 설정 예시:
     ```
     외부 포트: 8000
     내부 IP: 192.168.1.100 (서버의 로컬 IP)
     내부 포트: 8000
     프로토콜: TCP
     ```

3. **방화벽 설정**
   ```bash
   # Windows: 방화벽에서 포트 8000 인바운드 규칙 추가
   # Linux: iptables 또는 ufw 사용
   sudo ufw allow 8000/tcp
   ```

4. **접속**
   ```
   http://공인IP:8000
   예: http://123.45.67.89:8000
   ```

**주의사항:**
- ⚠️ **보안**: 공인 IP 노출은 보안 위험 (HTTPS + 인증 필수)
- ⚠️ **ISP 제한**: 일부 ISP는 포트 포워딩을 차단할 수 있음
- ⚠️ **동적 IP**: 대부분 가정용 인터넷은 동적 IP (재접속 시 IP 변경)

---

#### 방법 2: DDNS (Dynamic DNS) 사용

**동적 IP 문제 해결:**

1. **DDNS 서비스 가입** (무료 서비스)
   - No-IP (https://www.noip.com)
   - DuckDNS (https://www.duckdns.org)
   - Dynu (https://www.dynu.com)

2. **DDNS 설정**
   ```bash
   # 예: DuckDNS 사용
   # 1. DuckDNS에서 도메인 생성 (예: myapi.duckdns.org)
   # 2. 공유기 또는 서버에서 DDNS 클라이언트 설정
   ```

3. **접속**
   ```
   http://myapi.duckdns.org:8000
   ```

**장점:**
- ✅ 동적 IP 문제 해결
- ✅ 기억하기 쉬운 도메인 사용
- ✅ 무료 서비스 많음

---

#### 방법 3: 터널링 서비스 (가장 쉬운 방법)

**ngrok 사용 (개발/테스트용):**

1. **ngrok 설치 및 실행**
   ```bash
   # ngrok 다운로드: https://ngrok.com/
   # ngrok 실행
   ngrok http 8000
   ```

2. **접속**
   ```
   ngrok이 제공하는 URL 사용
   예: https://abc123.ngrok.io
   ```

**Cloudflare Tunnel (프로덕션 권장):**

1. **Cloudflare Tunnel 설치**
   ```bash
   # cloudflared 설치
   # https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
   
   # 터널 생성
   cloudflared tunnel create my-tunnel
   
   # 터널 실행
   cloudflared tunnel run my-tunnel
   ```

2. **접속**
   ```
   Cloudflare가 제공하는 도메인 사용
   ```

**장점:**
- ✅ 포트 포워딩 불필요
- ✅ 방화벽 설정 불필요
- ✅ HTTPS 자동 제공 (ngrok, Cloudflare)
- ✅ 빠른 설정

**단점:**
- ⚠️ ngrok 무료 버전: 세션당 2시간 제한, URL 변경
- ⚠️ Cloudflare: 초기 설정 복잡

---

#### 방법 4: 클라우드 서버 배포 (프로덕션 권장)

**AWS, Azure, GCP 등:**

1. **클라우드 서버 생성**
   ```bash
   # 예: AWS EC2 인스턴스 생성
   # Ubuntu 22.04 LTS 선택
   ```

2. **Docker 설치 및 배포**
   ```bash
   # 서버에 접속
   ssh user@서버IP
   
   # 프로젝트 클론
   git clone <repository-url>
   cd ibs_legal_ai_system
   
   # Docker Compose로 실행
   docker-compose up -d
   ```

3. **보안 그룹 설정**
   - AWS: Security Group에서 포트 8000 인바운드 허용
   - Azure: Network Security Group 설정
   - GCP: Firewall Rules 설정

4. **접속**
   ```
   http://서버공인IP:8000
   또는
   http://도메인:8000 (도메인 연결 시)
   ```

**장점:**
- ✅ 안정적인 서비스
- ✅ 정적 IP 제공
- ✅ 확장성
- ✅ 백업 및 모니터링 도구

---

#### 방법 5: VPN 사용 (내부 네트워크처럼 접속)

**VPN 서버 구축:**

1. **VPN 서버 설정** (예: WireGuard, OpenVPN)
   ```bash
   # WireGuard 설치 예시
   sudo apt install wireguard
   ```

2. **클라이언트 연결**
   - VPN 클라이언트에서 서버에 연결
   - 연결 후 내부 네트워크처럼 접속
   ```
   http://192.168.1.100:8000
   ```

**장점:**
- ✅ 보안성 높음 (암호화된 연결)
- ✅ 내부 네트워크처럼 사용 가능
- ✅ 여러 서비스 접근 가능

**단점:**
- ⚠️ VPN 서버 구축 필요
- ⚠️ 클라이언트 설정 필요

---

## 📊 방법 비교

| 방법 | 난이도 | 비용 | 보안 | 안정성 | 추천 용도 |
|------|--------|------|------|--------|-----------|
| **포트 포워딩** | 중 | 무료 | 낮음 | 중 | 가정/사무실 서버 |
| **DDNS** | 중 | 무료 | 낮음 | 중 | 동적 IP 환경 |
| **터널링 (ngrok)** | 쉬움 | 무료/유료 | 중 | 중 | 개발/테스트 |
| **터널링 (Cloudflare)** | 중 | 무료 | 높음 | 높음 | 프로덕션 |
| **클라우드 서버** | 중 | 유료 | 높음 | 높음 | 프로덕션 |
| **VPN** | 어려움 | 무료/유료 | 높음 | 높음 | 내부 네트워크 |

---

## 🔒 보안 권장사항

**다른 네트워크에서 접속할 때 필수:**

1. **HTTPS 사용**
   ```bash
   # Nginx 리버스 프록시 설정 (예시)
   # Let's Encrypt로 SSL 인증서 발급
   ```

2. **API 키 인증**
   ```env
   # .env 파일
   API_KEY=강력한_비밀번호_설정
   ```

3. **방화벽 설정**
   ```bash
   # 특정 IP만 허용 (선택사항)
   sudo ufw allow from 특정IP to any port 8000
   ```

4. **Rate Limiting**
   - 이미 구현되어 있음 (`src/api/middleware.py`)

5. **로그 모니터링**
   - 접속 로그 확인
   - 의심스러운 활동 감지

---

## 🚀 빠른 시작 가이드

### 개발/테스트용 (가장 빠름)
```bash
# ngrok 사용
ngrok http 8000
# 제공된 URL 사용
```

### 프로덕션용 (권장)
```bash
# 1. 클라우드 서버에 배포
# 2. 도메인 연결 (선택사항)
# 3. HTTPS 설정
# 4. API 키 설정
```

---

## 📚 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [프로젝트 README.md](./README.md)
- [환경 변수 설정 가이드](./env.example)

