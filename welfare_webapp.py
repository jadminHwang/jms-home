import streamlit as st
from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse

# 1. 환경변수 로드
load_dotenv()

# 2. 환경변수에서 API 키와 URL 불러오기
API_KEY_ENCODED = os.getenv('WELFARE_API_KEY')
API_KEY_DECODED = urllib.parse.unquote(API_KEY_ENCODED) if API_KEY_ENCODED else ""
CENTRAL_LIST_URL = os.getenv('CENTRAL_LIST_URL')

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

    try:
        response = requests.get(CENTRAL_LIST_URL, params=params, timeout=30, verify=False)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        wanted_list = root.find(".//wantedList")
        if wanted_list is not None:
            serv_list = wanted_list.findall(".//servList")
            results = []
            for svc in serv_list:
                results.append({
                    "서비스명": svc.findtext('servNm', ''),
                    "서비스ID": svc.findtext('servId', ''),
                    "요약": svc.findtext('servDgst', ''),
                    "소관부처": svc.findtext('jurMnofNm', ''),
                    "문의처": svc.findtext('rprsCtadr', ''),
                    "온라인신청": svc.findtext('onapPsbltYn', ''),
                    "대상": svc.findtext('trgterIndvdlArray', ''),
                    "생애주기": svc.findtext('lifeArray', ''),
                    "관심주제": svc.findtext('intrsThemaArray', ''),
                    "상세링크": svc.findtext('servDtlLink', '')
                })
            return results
        else:
            st.warning("검색 결과가 없습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류가 발생했습니다: Invalid URL \"os.getenv('CENTRAL_LIST_URL')\": No scheme supplied. Perhaps you meant https://os.getenv('CENTRAL_LIST_URL')? {e}")
    except ET.ParseError:
        st.error("API 응답을 XML로 파싱하는 중 오류가 발생했습니다.")

    return []

st.title("복지서비스 카테고리별 검색 웹앱")

# --- 검색 조건 UI ---
col1, col2, col3 = st.columns(3)
with col1:
    life = st.selectbox("생애주기", options=list(LIFE_ARRAY_CODES.keys()), format_func=lambda x: LIFE_ARRAY_CODES[x])
with col2:
    target = st.selectbox("대상", options=list(TRGTER_INDVDL_ARRAY_CODES.keys()), format_func=lambda x: TRGTER_INDVDL_ARRAY_CODES[x])
with col3:
    theme = st.selectbox("관심주제", options=list(INTRS_THEMA_ARRAY_CODES.keys()), format_func=lambda x: INTRS_THEMA_ARRAY_CODES[x])

if st.button("검색"):
    results = search_welfare_services(life, target, theme)
    if results:
        st.success(f"검색 결과: {len(results)}건")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        # --- 다운로드 버튼 ---
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="CSV로 다운로드",
            data=csv,
            file_name="복지서비스_검색결과.csv",
            mime="text/csv"
        )
        excel = df.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="엑셀로 다운로드",
            data=excel,
            file_name="복지서비스_검색결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("검색 결과가 없습니다.")