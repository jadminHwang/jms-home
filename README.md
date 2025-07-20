# 복지서비스 검색 웹앱 🏥

공공데이터 포털의 복지서비스 API를 활용한 카테고리별 검색 웹앱입니다.

## 🌟 주요 기능

- **카테고리별 검색**: 연령별, 대상, 관심주제별 필터링
- **검색 수량 조절**: 10~100개까지 선택 가능
- **페이지네이션**: 여러 페이지 결과 탐색
- **데이터 다운로드**: CSV, 엑셀 형식으로 다운로드
- **HTTP 우선 연결**: SSL 문제 해결

## 🚀 사용 방법

### 로컬 실행
```bash
# 1. 저장소 클론
git clone [repository-url]
cd bokjro

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정 (.env 파일)
WELFARE_API_KEY=your_api_key_here
CENTRAL_LIST_URL=https://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001

# 4. 웹앱 실행
streamlit run welfare_webapp.py
```

### 웹에서 접속
- **로컬**: http://localhost:8501
- **네트워크**: http://[your-ip]:8501

## 📋 검색 조건

### 연령별
- 영유아, 아동, 청소년, 청년, 중장년, 노년, 임신·출산

### 대상
- 다문화·탈북민, 다자녀, 보훈대상자, 장애인, 저소득, 한부모·조손

### 관심주제
- 신체건강, 정신건강, 생활지원, 주거, 일자리, 문화·여가, 안전·위기, 임신·출산, 보육, 교육, 입양·위탁, 보호·돌봄, 서민금융, 법률

## 🔧 기술 스택

- **Backend**: Python 3.11+
- **Web Framework**: Streamlit
- **HTTP Client**: Requests
- **Data Processing**: Pandas
- **Excel Support**: OpenPyXL
- **Environment**: python-dotenv

## 📁 파일 구조

```
bokjro/
├── welfare_webapp.py      # 메인 웹앱 파일
├── requirements.txt       # Python 패키지 목록
├── .env                   # 환경변수 (API 키)
├── .gitignore            # Git 제외 파일
└── README.md             # 프로젝트 설명
```

## 🔑 API 설정

### 1. 공공데이터 포털 가입
- https://www.data.go.kr 접속
- 회원가입 및 로그인

### 2. API 키 발급
- "복지서비스" 검색
- "중앙부처복지서비스" API 신청
- 인증키 발급

### 3. 환경변수 설정
`.env` 파일에 다음 내용 추가:
```
WELFARE_API_KEY=your_api_key_here
CENTRAL_LIST_URL=https://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001
```

## 🚀 배포

### Streamlit Cloud 배포
1. GitHub에 코드 업로드
2. https://share.streamlit.io 접속
3. GitHub 저장소 연결
4. 환경변수 설정 (Secrets)
5. 배포 완료

## 🐛 문제 해결

### SSL 오류
- HTTP 방식으로 자동 전환
- 네트워크 환경 확인

### API 연결 실패
- API 키 확인
- 네트워크 방화벽 확인
- VPN 사용 고려

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.

## 📄 라이선스

MIT License

---

**복지서비스 검색으로 더 나은 삶을 찾아보세요!** 💙 