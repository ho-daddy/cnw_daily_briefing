# 🚀 빠른 시작 가이드

## 웹앱 버전 - 3분 안에 시작하기!

### ✨ 로컬에서 실행

```powershell
# 1. 가상환경 활성화
.\venv\Scripts\activate

# 2. 패키지 설치 (처음만)
pip install streamlit

# 3. 웹앱 실행
streamlit run app.py
```

브라우저가 자동으로 열립니다! 🎉

### 🌐 온라인 배포 (무료)

**가장 쉬운 방법 - Streamlit Cloud:**

1. https://share.streamlit.io/ 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 연결
5. Secrets에 API 키 추가
6. Deploy!

**5분 후 전 세계 어디서나 접속 가능합니다!**

---

## 🎯 GUI vs 웹앱 - 뭘 선택할까?

### GUI (tkinter) - `gui.py`
- ✅ Windows 전용
- ✅ 설치형 프로그램
- ❌ 다른 사람과 공유 어려움

**이런 분께:**
- 혼자만 사용
- Windows만 사용
- 설치형 앱 선호

### 웹앱 (Streamlit) - `app.py` ⭐ 추천!
- ✅ 모든 OS (Windows, Mac, Linux)
- ✅ 모바일도 가능
- ✅ URL만 공유하면 끝
- ✅ 온라인 배포 가능

**이런 분께:**
- 팀원들과 공유
- 어디서나 접속 필요
- 모바일도 사용
- 최신 기술 선호

---

## 💡 추천 워크플로우

### 개발/테스트 단계
```powershell
# 로컬에서 웹앱 실행
streamlit run app.py
```

### 실제 사용 단계
```
1. Streamlit Cloud에 배포
2. 팀원들에게 URL 공유
3. 각자 브라우저에서 접속
4. 브리핑 생성!
```

---

## 🔑 API 키 설정

### 로컬 실행 시
`.env` 파일:
```
ANTHROPIC_API_KEY=your_key_here
```

### 온라인 배포 시
Streamlit Cloud > Settings > Secrets:
```
ANTHROPIC_API_KEY = "your_key_here"
```

---

## ❓ 자주 묻는 질문

**Q: 웹앱과 GUI 둘 다 사용할 수 있나요?**
A: 네! 둘 다 같은 코드를 공유합니다.

**Q: 배포 비용은?**
A: Streamlit Cloud 무료 플랜으로 충분합니다!

**Q: 모바일에서도 되나요?**
A: 네! 웹앱은 모바일에서도 완벽하게 작동합니다.

**Q: 설치가 복잡하지 않나요?**
A: 웹앱을 배포하면 설치가 필요 없습니다!

---

## 🎬 바로 시작하기

### 선택 1: 로컬 실행 (테스트용)
```powershell
streamlit run app.py
```

### 선택 2: 온라인 배포 (실전용)
1. README_WEBAPP.md 보고 따라하기
2. 5분이면 배포 완료!

---

**어떤 방법을 선택하든, 즐거운 브리핑 생성 되세요! 🌟**
