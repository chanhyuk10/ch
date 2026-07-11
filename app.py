import streamlit as st

st.markdown("# 앱 UI 만들기")
st.markdown("---")

user_id = st.text_input("이름을 입력 해주세요", placeholder="example_user")
ai_model = st.radio("학년을 알려주세요", ["1학년", "2학년", "3학년"], horizontal=True)
age = st.number_input("반을 입력 해주세요", min_value=1, max_value=100, value=1)
ai_speed = st.select_slider("난이도", options=["매우 쉬움", "쉬움", "보통", "어려움", "매우 어려움"], value="보통")
creativity = st.slider("점수", 0, 100, 50)

question = st.text_area("소감", placeholder="여기에 소감을 작성해주세요.")

if st.button("확인"):
    st.success(f"이름: {user_id} | 학년: {ai_model} | 반: {age}반 | 난이도: {ai_speed}")
 if question:
        st.info(f" 작성해주신 소감:\n\n{question}")
