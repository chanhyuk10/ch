import streamlit as st

st.title("카운터 앱")

# 1. session_state 초기화 (최초 1회만 실행)
if 'count' not in st.session_state:
    st.session_state.count = 0

# 2. 버튼 생성 및 클릭 시 로직 (들여쓰기 수정 및 바깥으로 이동)
if st.button("증가"):
    st.session_state.count += 1

# 3. 결과 출력 (마크다운 문법 띄어쓰기 수정)
st.markdown(f"## 현재 숫자: '{st.session_state.count}'")
