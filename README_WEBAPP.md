# 새움터 일일 동향 브리핑 시스템 - 웹앱 버전 🌐

## 🎉 웹앱으로 업그레이드!

이제 어디서나 브라우저로 접속 가능한 웹앱입니다!

## ✨ 주요 특징

- 🌍 **어디서나 접속**: 인터넷만 있으면 OK
- 📱 **모바일 지원**: 스마트폰, 태블릿에서도 사용 가능
- 🚀 **설치 불필요**: 브라우저만 있으면 됨
- ☁️ **클라우드 배포**: 24시간 온라인 유지 가능
- 🎨 **깔끔한 UI**: 직관적이고 사용하기 쉬운 인터페이스

## 🏃 빠른 시작 (로컬 실행)

### 1단계: 패키지 설치

```powershell
# 가상환경 활성화
.\venv\Scripts\activate

# 패키지 업데이트
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2단계: 환경 설정

`.env` 파일에 API 키 설정:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### 3단계: 웹앱 실행

```powershell
streamlit run app.py
```

브라우저가 자동으로 열리면서 `http://localhost:8501`로 접속됩니다!

## 🌐 온라인 배포 (무료!)

### 방법 1: Streamlit Cloud (⭐ 추천)

**가장 쉽고 무료입니다!**

#### 준비물
- GitHub 계정
- Anthropic API 키

#### 배포 단계

**1. GitHub에 코드 업로드**

```powershell
# Git 초기화 (처음만)
git init
git add .
git commit -m "Initial commit"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/your-username/cnw-briefing.git
git push -u origin main
```

**2. Streamlit Cloud 배포**

1. https://share.streamlit.io/ 접속
2. "New app" 클릭
3. GitHub 저장소 연결
4. 설정:
   - Repository: `your-username/cnw-briefing`
   - Branch: `main`
   - Main file path: `daily_briefing/app.py`
5. "Advanced settings" 클릭
6. "Secrets" 섹션에 추가:
   ```
   ANTHROPIC_API_KEY = "your_actual_api_key"
   ```
7. "Deploy!" 클릭

**3. 배포 완료!**

5분 후 `https://your-app-name.streamlit.app` 주소로 접속 가능!

### 방법 2: Render.com

**Streamlit Cloud 대안**

1. https://render.com 가입
2. "New" > "Web Service" 선택
3. GitHub 저장소 연결
4. 설정:
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `streamlit run app.py`
5. Environment Variables에 `ANTHROPIC_API_KEY` 추가
6. "Create Web Service" 클릭

### 방법 3: Railway.app

**간단한 배포**

1. https://railway.app 가입
2. "New Project" > "Deploy from GitHub repo"
3. 저장소 선택
4. Environment Variables에 `ANTHROPIC_API_KEY` 추가
5. 자동 배포!

## 📖 사용 방법

### 웹앱 화면 구성

```
┌─────────────────────────────────────────────────┐
│           🌟 새움터 일일 동향 브리핑               │
├──────────────┬──────────────────────────────────┤
│ ⚙️ 설정      │  📊 데이터 수집                   │
│              │  📄 브리핑 생성                   │
│ 데이터 소스:  │  ℹ️ 도움말                       │
│ ☑ 고용노동부  │                                  │
│ ☑ 안전포털    │  [탭 내용 표시]                  │
│ ☑ 중대재해    │                                  │
│ ☑ 매일노동    │                                  │
│ ☑ 뉴스검색    │                                  │
│              │                                  │
│ 키워드:       │                                  │
│ [산업안전...] │                                  │
└──────────────┴──────────────────────────────────┘
```

### 1️⃣ 데이터 수집

1. **좌측 사이드바**에서 수집 소스 선택
2. 뉴스 검색 키워드 입력 (선택)
3. **"📊 데이터 수집"** 탭으로 이동
4. **"🚀 수집 시작"** 버튼 클릭
5. 진행 상황 확인 및 결과 확인

### 2️⃣ 브리핑 생성

1. 데이터 수집 완료 후
2. **"📄 브리핑 생성"** 탭으로 이동
3. **"✨ 브리핑 생성"** 버튼 클릭
4. 생성된 브리핑 확인
5. **다운로드 버튼**으로 저장

### 3️⃣ 도움말

- **"ℹ️ 도움말"** 탭에서 상세 사용법 확인

## 🎯 장점 비교

### 로컬 실행 vs 웹 배포

| 특징 | 로컬 실행 | 웹 배포 |
|------|----------|---------|
| 접근성 | 해당 컴퓨터만 | 어디서나 |
| 설치 | Python 필요 | 브라우저만 |
| 공유 | 어려움 | URL 공유로 간단 |
| 유지보수 | 직접 관리 | 자동 업데이트 |
| 비용 | 무료 | 무료 (기본) |

### GUI vs 웹앱

| 특징 | GUI (tkinter) | 웹앱 (Streamlit) |
|------|--------------|-----------------|
| 플랫폼 | Windows만 | 모든 OS |
| 배포 | .exe 필요 | URL만 |
| 업데이트 | 재배포 필요 | 즉시 반영 |
| 접근성 | 설치 필요 | 브라우저만 |
| 모바일 | 불가 | 가능 |

## 🛠️ 고급 설정

### 포트 변경

```powershell
streamlit run app.py --server.port 8080
```

### 개발 모드

```powershell
# 파일 변경 시 자동 재시작
streamlit run app.py --server.runOnSave true
```

### 네트워크 공유

```powershell
# 같은 네트워크의 다른 기기에서 접속 가능
streamlit run app.py --server.address 0.0.0.0
```

## 🔧 문제 해결

### "Module not found" 오류

```powershell
pip install -r requirements.txt --upgrade
```

### Playwright 브라우저 오류

```powershell
playwright install chromium
```

### 포트 충돌

```powershell
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

### 배포 후 앱이 안 열려요

1. Streamlit Cloud의 "Manage app" > "Logs" 확인
2. API 키가 Secrets에 올바르게 설정되었는지 확인
3. requirements.txt의 패키지 버전 확인

## 📱 모바일 사용

웹앱이므로 스마트폰에서도 완벽하게 작동합니다!

1. 배포된 URL을 모바일 브라우저에서 열기
2. 홈 화면에 추가하면 앱처럼 사용 가능
3. 터치 인터페이스 지원

## 🔐 보안 주의사항

### API 키 보호

- ❌ **절대로** API 키를 코드에 직접 넣지 마세요
- ✅ `.env` 파일 또는 Streamlit Secrets 사용
- ✅ `.gitignore`에 `.env` 추가

### 공개 배포 시

- 비밀번호 인증 추가 권장
- 사용량 제한 설정
- API 키 정기 갱신

## 💡 활용 팁

### 일상 업무

```
1. 아침 출근하면 웹앱 접속
2. "수집 시작" 클릭
3. 커피 마시는 동안 수집 완료
4. "브리핑 생성" 클릭
5. 브리핑 다운로드하여 팀 공유
```

### 팀 공유

```
1. Streamlit Cloud에 배포
2. 팀원들에게 URL 공유
3. 각자 필요할 때 브리핑 생성
4. 중복 작업 방지
```

### 모바일 활용

```
1. 출퇴근 중 스마트폰으로 접속
2. 최신 동향 빠르게 확인
3. 중요 이슈 즉시 파악
```

## 📊 비용

### 무료 플랜으로 충분합니다!

**Streamlit Cloud 무료 플랜:**
- ✅ 공개 앱 무제한
- ✅ 1GB 메모리
- ✅ 1 CPU
- ✅ 충분한 성능

**Anthropic API:**
- Claude Sonnet 4: 입력 $3/M tokens, 출력 $15/M tokens
- 일일 브리핑 1회 = 약 $0.05~0.10
- 월 $3~5 정도면 충분

## 🎓 다음 단계

### 추가 기능 아이디어

- 📧 이메일 자동 발송
- 📅 스케줄러 (매일 아침 자동 생성)
- 💾 과거 브리핑 아카이브
- 📈 통계 대시보드
- 👥 팀원 계정 관리
- 🔔 중대재해 알림 기능

### 커스터마이징

- 테마 색상 변경 (`.streamlit/config.toml`)
- 로고 추가
- 추가 데이터 소스 통합

## 📝 파일 구조

```
daily_briefing/
├── app.py                    # ⭐ Streamlit 웹앱 (신규)
├── gui.py                    # tkinter GUI (선택)
├── main.py                   # CLI 실행
├── scraper.py                # 데이터 수집
├── briefing_generator.py     # AI 브리핑 생성
├── requirements.txt          # 패키지 목록
├── packages.txt              # 시스템 패키지 (배포용)
├── .env                      # 환경 변수 (로컬)
├── .streamlit/
│   ├── config.toml          # Streamlit 설정
│   └── secrets.toml.example # Secrets 예시
└── README_WEBAPP.md         # 이 파일
```

## 🚀 시작하기

### 로컬에서 테스트

```powershell
streamlit run app.py
```

### 온라인 배포

1. GitHub에 푸시
2. Streamlit Cloud에서 배포
3. 팀원들과 공유!

---

## 📞 도움이 필요하신가요?

- Streamlit 공식 문서: https://docs.streamlit.io/
- Streamlit 포럼: https://discuss.streamlit.io/
- Anthropic 문서: https://docs.anthropic.com/

## 📜 라이센스

새움터 내부 사용을 위해 개발되었습니다.
