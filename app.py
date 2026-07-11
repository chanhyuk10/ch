import streamlit as st

# 1. 초기 상태 설정 및 리셋 함수 정의
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "weather" not in st.session_state:
    st.session_state.weather = "맑음"
if "top_type" not in st.session_state:
    st.session_state.top_type = "후드티"
if "top_color" not in st.session_state:
    st.session_state.top_color = "무난함"
if "bottom_type" not in st.session_state:
    st.session_state.bottom_type = "청바지"
if "bottom_color" not in st.session_state:
    st.session_state.bottom_color = "레귤러"
if "shoes" not in st.session_state:
    st.session_state.shoes = "스니커즈"
if "acc" not in st.session_state:
    st.session_state.acc = []

def reset_all():
    st.session_state.user_name = ""
    st.session_state.weather = "맑음"
    st.session_state.top_type = "후드티"
    st.session_state.top_color = "무난함"
    st.session_state.bottom_type = "청바지"
    st.session_state.bottom_color = "레귤러"
    st.session_state.shoes = "스니커즈"
    st.session_state.acc = [] # 빈 리스트로 올바르게 수정

# 2. 사이드바 구성
with st.sidebar:
    st.header("프로필")
    # key를 연결하여 session_state와 동기화합니다.
    user_name = st.text_input("닉네임", key="user_name")
    weather = st.selectbox("오늘 날씨", ["맑음", "흐림", "비/눈", "매우 추움"], key="weather")
    st.markdown("---")
    st.info(f"반가워요, {user_name}님! 오늘 날씨는 '{weather}'이네요.")

# 3. 메인 화면 구성
st.title("👗 AI 코디 메이커")
st.write("사이드바에서 날씨를 먼저 선택하고 코디를 시작하세요!")

st.header("👕 아이템 조합하기")
col1, col2 = st.columns(2)
with col1:
    st.subheader("상의")
    top_type = st.radio("종류", ["후드티", "셔츠", "맨투맨", "반팔 티셔츠"], key="top_type")
    top_color = st.select_slider("색상 톤", options=["밝음", "무난함", "어두움"], key="top_color")
with col2:
    st.subheader("하의")
    bottom_type = st.radio("종류", ["청바지", "슬랙스", "트레이닝 팬츠", "반바지"], key="bottom_type")
    bottom_color = st.select_slider("핏(Fit)", options=["슬림", "레귤러", "오버핏"], key="bottom_color")

st.header("디테일 추가")
tab1, tab2 = st.tabs(["신발", "액세서리"])
with tab1:
    st.write("오늘의 발걸음을 책임질 신발:")
    shoes = st.selectbox("신발 선택", ["스니커즈", "운동화", "구두", "슬리퍼"], key="shoes")
    with st.expander("신발 선택 팁 보기"):
        st.info("너무 튀는 신발은 지양하도록 해요!")
with tab2:
    st.write("포인트 아이템:")
    acc = st.multiselect("액세서리 추가", ["모자", "안경", "목걸이", "가방"], key="acc")
    with st.expander("액세서리 스타일링 팁 보기"):
        st.warning("너무 많은 액세서리는 투머치가 될 수 있어요.")

st.markdown("---")
if st.button("코디 완성하기"):
    with st.container(border=True):
        st.subheader(f"{user_name}님의 오늘의 룩북")
        st.write(f"오늘 같은 **{weather}** 날씨에는 이렇게 입어보세요!")
        st.markdown(f"""
        * **상의:** {top_color} {top_type}
        * **하의:** {bottom_color} {bottom_type}
        * **매칭:** {shoes}와 {', '.join(acc) if acc else '악세서리 없이 깔끔하게!'}
        """)
        st.success("오늘의 스타일링이 완성되었습니다! 자신 있게 외출하세요!")
        
        with st.expander("코디 연출 팁 영상 보기"):
            st.video("https://www.youtube.com/watch?v=lkMZ8ytly1k")
            st.write("전문가가 제안하는 코디 연출법을 참고해 보세요.")

# on_click 으로 오타 수정
st.button("전체 초기화", on_click=reset_all)
