import streamlit as st
from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse
import urllib3
import ssl
import certifi

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL 컨텍스트 설정
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 1. 환경변수 로드
load_dotenv()

# 2. 환경변수에서 API 키와 URL 불러오기
API_KEY_ENCODED = os.getenv('WELFARE_API_KEY')
API_KEY_DECODED = urllib.parse.unquote(API_KEY_ENCODED) if API_KEY_ENCODED else ""
CENTRAL_LIST_URL = os.getenv('CENTRAL_LIST_URL')

# 디버그 정보 표시
st.sidebar.markdown("### 🔧 디버그 정보")
st.sidebar.write(f"API_KEY_ENCODED: {API_KEY_ENCODED[:20] if API_KEY_ENCODED else 'None'}...")
st.sidebar.write(f"API_KEY_DECODED: {API_KEY_DECODED[:20] if API_KEY_DECODED else 'None'}...")
st.sidebar.write(f"CENTRAL_LIST_URL: {CENTRAL_LIST_URL}")

# 3. 코드표
LIFE_ARRAY_CODES = {
    '': '전체',
    '001': '영유아', '002': '아동', '003': '청소년', '004': '청년', '005': '중장년', '006': '노년', '007': '임신·출산'
}
TRGTER_INDVDL_ARRAY_CODES = {
    '': '전체',
    '010': '다문화·탈북민', '020': '다자녀', '030': '보훈대상자', '040': '장애인', '050': '저소득', '060': '한부모·조손'
}
INTRS_THEMA_ARRAY_CODES = {
    '': '전체',
    '010': '신체건강', '020': '정신건강', '030': '생활지원', '040': '주거', '050': '일자리', '060': '문화·여가',
    '070': '안전·위기', '080': '임신·출산', '090': '보육', '100': '교육', '110': '입양·위탁', '120': '보호·돌봄',
    '130': '서민금융', '140': '법률'
}

def search_welfare_services(life_array, trgter_indvdl_array, intrs_thema_array, page_no=1, num_of_rows=30):
    # 1. 환경변수 체크
    if not CENTRAL_LIST_URL:
        st.error("❌ 중앙복지서비스 API URL이 설정되지 않았습니다. .env 파일이나 환경변수를 확인해주세요.")
        st.stop()
    if not API_KEY_DECODED:
        st.error("❌ API 인증키가 설정되지 않았습니다. .env 파일이나 환경변수를 확인해주세요.")
        st.stop()

    params = {
        "serviceKey": API_KEY_DECODED,
        "callTp": "L",
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "srchKeyCode": "001",  # 서비스명 기준(필요시 변경)
    }
    if life_array:
        params["lifeArray"] = life_array
    if trgter_indvdl_array:
        params["trgterIndvdlArray"] = trgter_indvdl_array
    if intrs_thema_array:
        params["intrsThemaArray"] = intrs_thema_array

    # HTTP 우선 시도 (SSL 문제 해결)
    methods = [
        "method1_http_rest",           # HTTP + REST 방식
        "method2_http_soap",           # HTTP + SOAP 방식  
        "method3_https_rest_ssl_off",  # HTTPS + REST + SSL 해제
        "method4_https_soap_ssl_off"   # HTTPS + SOAP + SSL 해제
    ]
    
    for method in methods:
        try:
            if method == "method1_http_rest":
                # 방법 1: HTTP + REST 방식 (가장 안전)
                http_url = CENTRAL_LIST_URL.replace('https://', 'http://')
                session = requests.Session()
                session.verify = False
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/xml, text/xml, */*',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                st.info(f"🔄 {method} 시도 중... (HTTP + REST)")
                response = session.get(http_url, params=params, timeout=30, headers=headers)
                
            elif method == "method2_http_soap":
                # 방법 2: HTTP + SOAP 방식
                http_url = CENTRAL_LIST_URL.replace('https://', 'http://')
                session = requests.Session()
                session.verify = False
                
                # SOAP 요청 헤더
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': ''
                }
                
                st.info(f"🔄 {method} 시도 중... (HTTP + SOAP)")
                response = session.get(http_url, params=params, timeout=30, headers=headers)
                
            elif method == "method3_https_rest_ssl_off":
                # 방법 3: HTTPS + REST + SSL 완전 해제
                session = requests.Session()
                session.verify = False
                session.trust_env = False
                
                # SSL 컨텍스트 완전 비활성화
                from requests.adapters import HTTPAdapter
                from urllib3.util.ssl_ import create_urllib3_context
                
                class CustomHTTPAdapter(HTTPAdapter):
                    def init_poolmanager(self, *args, **kwargs):
                        context = create_urllib3_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        kwargs['ssl_context'] = context
                        return super().init_poolmanager(*args, **kwargs)
                
                session.mount('https://', CustomHTTPAdapter())
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/xml, text/xml, */*'
                }
                
                st.info(f"🔄 {method} 시도 중... (HTTPS + REST + SSL 해제)")
                response = session.get(CENTRAL_LIST_URL, params=params, timeout=30, headers=headers)
                
            elif method == "method4_https_soap_ssl_off":
                # 방법 4: HTTPS + SOAP + SSL 완전 해제
                session = requests.Session()
                session.verify = False
                session.trust_env = False
                
                # SSL 컨텍스트 완전 비활성화
                from requests.adapters import HTTPAdapter
                from urllib3.util.ssl_ import create_urllib3_context
                
                class CustomHTTPAdapter(HTTPAdapter):
                    def init_poolmanager(self, *args, **kwargs):
                        context = create_urllib3_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        kwargs['ssl_context'] = context
                        return super().init_poolmanager(*args, **kwargs)
                
                session.mount('https://', CustomHTTPAdapter())
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': ''
                }
                
                st.info(f"🔄 {method} 시도 중... (HTTPS + SOAP + SSL 해제)")
                response = session.get(CENTRAL_LIST_URL, params=params, timeout=30, headers=headers)
            
            response.raise_for_status()
            
            # API 응답 디버깅
            st.sidebar.markdown("### 📡 API 응답 디버깅")
            st.sidebar.write(f"**Status Code:** {response.status_code}")
            st.sidebar.write(f"**Response Length:** {len(response.text)} characters")
            st.sidebar.write(f"**First 200 chars:** {response.text[:200]}...")
            
            # XML 파싱 시도
            try:
                root = ET.fromstring(response.text)
                
                # XML 구조 디버깅
                st.sidebar.write(f"**Root Tag:** {root.tag}")
                st.sidebar.write(f"**Child Elements:** {[child.tag for child in root]}")
                
                # 다양한 XML 경로 시도
                possible_paths = [
                    ".//wantedList",
                    ".//servList", 
                    ".//item",
                    ".//row",
                    ".//result",
                    ".//body",
                    ".//items"
                ]
                
                found_data = None
                for path in possible_paths:
                    found = root.findall(path)
                    if found:
                        st.sidebar.write(f"**Found at {path}:** {len(found)} items")
                        found_data = found
                        break
                
                if found_data:
                    # 첫 번째 방법으로 데이터 추출 시도
                    if path == ".//wantedList":
                        serv_list = root.findall(".//servList")
                    elif path == ".//servList":
                        serv_list = found_data
                    elif path == ".//item":
                        serv_list = found_data
                    elif path == ".//row":
                        serv_list = found_data
                    else:
                        serv_list = found_data
                    
                    results = []
                    for svc in serv_list:
                        # 다양한 필드명 시도
                        result = {}
                        possible_fields = {
                            'servNm': ['servNm', 'servName', 'serviceName', 'name'],
                            'servId': ['servId', 'id', 'serviceId'],
                            'servDgst': ['servDgst', 'summary', 'description', 'content'],
                            'jurMnofNm': ['jurMnofNm', 'department', 'ministry'],
                            'rprsCtadr': ['rprsCtadr', 'contact', 'phone', 'address'],
                            'onapPsbltYn': ['onapPsbltYn', 'online', 'apply'],
                            'trgterIndvdlArray': ['trgterIndvdlArray', 'target', 'beneficiary'],
                            'lifeArray': ['lifeArray', 'lifecycle', 'age'],
                            'intrsThemaArray': ['intrsThemaArray', 'theme', 'category'],
                            'servDtlLink': ['servDtlLink', 'link', 'url', 'detail']
                        }
                        
                        for key, field_names in possible_fields.items():
                            for field_name in field_names:
                                value = svc.findtext(field_name, '')
                                if value:
                                    result[key] = value
                                    break
                            if key not in result:
                                result[key] = ''
                        
                        results.append(result)
                    
                    if results:
                        st.success(f"✅ {method}로 성공! (HTTP 방식이 효과적이었습니다)")
                        return results
                    else:
                        st.warning(f"⚠️ {method}: 데이터 구조를 찾을 수 없습니다.")
                        continue
                else:
                    st.warning(f"⚠️ {method}: XML에서 데이터를 찾을 수 없습니다.")
                    st.sidebar.write("**Full Response:**", response.text[:500] + "..." if len(response.text) > 500 else response.text)
                    continue
                    
            except ET.ParseError as e:
                st.warning(f"⚠️ {method} XML 파싱 실패: {str(e)[:100]}...")
                st.sidebar.write("**Raw Response:**", response.text[:500] + "..." if len(response.text) > 500 else response.text)
                continue
                
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ {method} 실패: {str(e)[:100]}...")
            continue
    
    # 모든 방법이 실패한 경우
    st.error("❌ 모든 연결 방법이 실패했습니다.")
    st.info("💡 해결 방안:")
    st.info("1. HTTP 방식이 우선 시도되었습니다")
    st.info("2. 네트워크 환경 확인 (회사/학교 방화벽)")
    st.info("3. 다른 네트워크에서 시도")
    st.info("4. VPN 사용")
    
    return []

st.title("복지서비스 카테고리별 검색 웹앱")

# --- 검색 조건 UI ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    life = st.selectbox("연령별", options=list(LIFE_ARRAY_CODES.keys()), format_func=lambda x: LIFE_ARRAY_CODES[x])
with col2:
    target = st.selectbox("대상", options=list(TRGTER_INDVDL_ARRAY_CODES.keys()), format_func=lambda x: TRGTER_INDVDL_ARRAY_CODES[x])
with col3:
    theme = st.selectbox("관심주제", options=list(INTRS_THEMA_ARRAY_CODES.keys()), format_func=lambda x: INTRS_THEMA_ARRAY_CODES[x])
with col4:
    num_of_rows = st.selectbox("검색 수량", options=[10, 20, 30, 50, 100], index=2, help="한 번에 검색할 서비스 개수")

# 페이지네이션 상태 관리
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

if st.button("검색"):
    st.session_state.current_page = 1  # 검색 시 첫 페이지로 리셋
    results = search_welfare_services(life, target, theme, page_no=st.session_state.current_page, num_of_rows=num_of_rows)
    if results:
        st.success(f"검색 결과: {len(results)}건 (페이지 {st.session_state.current_page})")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        # --- 페이지네이션 ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("◀ 이전 페이지", disabled=st.session_state.current_page <= 1):
                st.session_state.current_page -= 1
                st.rerun()
        with col2:
            st.write(f"페이지 {st.session_state.current_page}")
        with col3:
            if st.button("다음 페이지 ▶", disabled=len(results) < num_of_rows):
                st.session_state.current_page += 1
                st.rerun()
        with col4:
            if st.button("처음으로"):
                st.session_state.current_page = 1
                st.rerun()

        # --- 다운로드 버튼 ---
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="CSV로 다운로드",
            data=csv,
            file_name=f"복지서비스_검색결과_페이지{st.session_state.current_page}.csv",
            mime="text/csv"
        )
        
        # 엑셀 다운로드 수정
        from io import BytesIO
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_data = excel_buffer.getvalue()
        st.download_button(
            label="엑셀로 다운로드",
            data=excel_data,
            file_name=f"복지서비스_검색결과_페이지{st.session_state.current_page}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("검색 결과가 없습니다.")
else:
    # 검색 버튼을 누르지 않았을 때도 페이지네이션 작동
    if st.session_state.current_page > 1:
        results = search_welfare_services(life, target, theme, page_no=st.session_state.current_page, num_of_rows=num_of_rows)
        if results:
            st.success(f"검색 결과: {len(results)}건 (페이지 {st.session_state.current_page})")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # --- 페이지네이션 ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("◀ 이전 페이지", disabled=st.session_state.current_page <= 1):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col2:
                st.write(f"페이지 {st.session_state.current_page}")
            with col3:
                if st.button("다음 페이지 ▶", disabled=len(results) < num_of_rows):
                    st.session_state.current_page += 1
                    st.rerun()
            with col4:
                if st.button("처음으로"):
                    st.session_state.current_page = 1
                    st.rerun()

            # --- 다운로드 버튼 ---
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="CSV로 다운로드",
                data=csv,
                file_name=f"복지서비스_검색결과_페이지{st.session_state.current_page}.csv",
                mime="text/csv"
            )
            
            # 엑셀 다운로드 수정
            from io import BytesIO
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="엑셀로 다운로드",
                data=excel_data,
                file_name=f"복지서비스_검색결과_페이지{st.session_state.current_page}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )