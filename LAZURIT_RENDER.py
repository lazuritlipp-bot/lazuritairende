import streamlit as st
import requests
import base64
import subprocess
import platform
import io

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo.jpg"

# --- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        st.sidebar.title("🔐 LAZURIT AI Render")
        pwd = st.sidebar.text_input("Введите персональный код доступа:", type="password")
        
        # Получаем данные из Secrets (формат [users.Пароль])
        users_data = st.secrets.get("users", {})
        
        if pwd in users_data:
            user_info = users_data[pwd]
            st.session_state.authenticated = True
            st.session_state.user_role = user_info.get("name", "Сотрудник")
            st.session_state.user_api_key = user_info.get("key", "")
            st.sidebar.success(f"Доступ: {st.session_state.user_role}")
            st.rerun()
        elif pwd:
            st.sidebar.error("❌ Код не опознан")
        
        st.info("Для получения доступа обратитесь в IT-отдел.")
        st.stop()

check_password()

# Присваиваем токен из сессии конкретного пользователя
APPLICATION_TOKEN = st.session_state.user_api_key

# --- ПРОМПТЫ ---
BASE_PHOTO_PROMPT = (
    "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
    "Strictly maintain the original furniture geometry and color palette. "
    "Enhance textures (wood grain, marble, fabric) with professional cinematic studio lighting. "
    "Natural soft sunlight from windows, deep realistic shadows, ray-traced reflections. "
    "NO 3D render look, NO flat textures."
)

PROMPT_PRESETS = {
    "Базовый промт": f"{BASE_PHOTO_PROMPT}",
    "️Дневной свет": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Студийный свет": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Вечернее освещение": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
}

# --- ФУНКЦИИ ---
def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def get_base64_logo(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json"
    }
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ИНТЕРФЕЙС ---
if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = list(PROMPT_PRESETS.values())[0]

st.set_page_config(page_title="LAZURIT AI Render", layout="wide", page_icon=LOGO_PATH)

logo_b64 = get_base64_logo(LOGO_PATH)
st.markdown(f"""
    <style>
    .stButton button {{ font-size: 20px !important; height: 3em !important; }}
    .header-container {{ display: flex; align-items: center; gap: 15px; }}
    .header-logo {{ width: 80px; }}
    </style>
    <div class="header-container">
        <img src="data:image/jpeg;base64,{logo_b64}" class="header-logo">
        <h2 style="margin:0;">LAZURIT AI Render</h2>
    </div>
    <div style="color: gray;">Аккаунт: {st.session_state.user_role}</div>
    <hr>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Исходник")
    uploaded_file = st.file_uploader("Загрузите фото", type=['jpg', 'png', 'jpeg'])
    if uploaded_file: st.image(uploaded_file, width=300)
    
    st.write("Стиль света:")
    p_cols = st.columns(2)
    for i, (name, text) in enumerate(PROMPT_PRESETS.items()):
        if p_cols[i % 2].button(name, use_container_width=True):
            st.session_state.current_prompt = text
            st.rerun()
    
    user_prompt = st.text_area("Задание:", value=st.session_state.current_prompt, height=200)

with col2:
    st.subheader("2. Результат")
    if st.button("🚀 Сгенерировать рендер", use_container_width=True):
        if not uploaded_file:
            st.error("Ошибка: Загрузите изображение!")
        elif not APPLICATION_TOKEN:
            st.error("Ошибка: В вашем профиле не настроен API-ключ.")
        else:
            with st.spinner("Магия нейросети в процессе..."):
                try:
                    uploaded_file.seek(0)
                    img_b64 = image_to_base64(uploaded_file.read())
                    result = process_image(img_b64, user_prompt)
                    
                    msg = result['outputs'][0]['outputs'][0]['results']['message']['text']
                    img_data = msg.split("|||")[1] if "|||" in msg else msg
                    clean_data = img_data.replace('"', '').replace("'", "").strip()
                    raw_b64 = clean_data.split("base64,")[1] if "base64," in clean_data else clean_data
                    
                    out_bytes = base64.b64decode(raw_b64)
                    st.image(out_bytes, caption=f"Готово для: {st.session_state.user_role}", use_container_width=True)
                    st.session_state.history.insert(0, out_bytes)
                except Exception as e:
                    st.error(f"Ошибка API: Проверьте ваш ключ или баланс.")

if st.session_state.history:
    st.divider()
    st.subheader("Последние работы")
    h_cols = st.columns(10)
    for idx, img in enumerate(st.session_state.history[:6]):
        with h_cols[idx]: st.image(img, use_container_width=True)