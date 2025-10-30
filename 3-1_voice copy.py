########### 설치 ###########
# pip install openai streamlit python-dotenv
###########################

import os
import time
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# ====== 환경 설정 ======
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
client = OpenAI(api_key=api_key)

# ====== UI ======
st.title("🌏 다국어 TTS + 자동 성우 추천 (독립 실행)")

st.image("https://wikidocs.net/images/page/215361/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5%EC%84%B1%EC%9A%B0.jpg", width=200)

# 언어 선택
languages = {
    "한국어": "Korean",
    "영어": "English",
    "일본어": "Japanese",
    "중국어(간체)": "Chinese (Simplified)",
    "스페인어": "Spanish",
    "프랑스어": "French",
}
selected_lang = st.selectbox("🎧 생성할 음성 언어를 선택하세요:", list(languages.keys()))

# 텍스트 입력
default_text = "포기하지 않는 간절한 꿈은 꼭 이루어집니다."
user_prompt = st.text_area("🎤 읽을 문장을 입력하세요:", value=default_text, height=160)

# ====== 성우 추천 ======
def recommend_voice(prompt):
    """간단 규칙 기반 추천"""
    if any(word in prompt for word in ["꿈", "희망", "용기", "행복", "응원", "화이팅"]):
        return "nova"
    if any(word in prompt for word in ["어둠", "위기", "전쟁", "공포", "슬픔"]):
        return "onyx"
    if any(word in prompt for word in ["사랑", "추억", "감성", "그리움"]):
        return "fable"
    if any(word in prompt for word in ["기술", "로봇", "미래", "데이터"]):
        return "echo"
    return "alloy"

recommended_voice = recommend_voice(user_prompt)
st.info(f"🎙️ 추천 성우: **{recommended_voice}**")

# 성우 선택 박스 (추천 성우 기본값)
voices_list = ['alloy', 'ash', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer']
default_index = voices_list.index(recommended_voice) if recommended_voice in voices_list else 0
voice = st.selectbox("🎤 성우를 선택하세요:", voices_list, index=default_index)

# ====== OpenAI로 번역 ======
def translate_text(text, target_language_name):
    """OpenAI chat completion을 이용해 자연스러운 번역"""
    messages = [
        {"role": "system", "content": f"You are a translator. Translate the user's sentence into {target_language_name}."},
        {"role": "user", "content": text}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=1000
    )
    return resp.choices[0].message.content.strip()

# ====== 버튼 ======
if st.button("🔊 Generate Audio"):

    with st.spinner("번역 중..."):
        try:
            translated_text = translate_text(user_prompt, languages[selected_lang])
        except Exception as e:
            st.error(f"번역 실패: {e}")
            translated_text = None

    if translated_text:
        st.write("💬 번역된 텍스트:")
        st.success(translated_text)

        with st.spinner("음성 생성 중..."):
            try:
                audio_response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=translated_text
                )
            except Exception as e:
                st.error(f"음성 생성 실패: {e}")
                audio_response = None

        if audio_response:
            os.makedirs("output_audio", exist_ok=True)
            path = f"output_audio/audio_{int(time.time())}.mp3"
            with open(path, "wb") as f:
                f.write(audio_response.content)

            st.audio(path, format="audio/mp3")
            st.download_button("⬇️ 다운로드", data=open(path, "rb"), file_name="translated_audio.mp3")
            st.success("✅ 오디오 생성 완료!")
