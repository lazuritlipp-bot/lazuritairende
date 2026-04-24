import streamlit as st
import requests
import base64
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
        
        # Поле ввода
        pwd = st.sidebar.text_input("Введите персональный код доступа:", type="password")
        
        # Кнопка входа
        login_button = st.sidebar.button("Войти", use_container_width=True)
        
        # Подпись под кнопкой со ссылкой
        st.sidebar.markdown("""
            <div style="font-size: 14px; color: gray; margin-top: 10px;">
            По вопросам доступа обращайтесь на 
            <a href="https://hd.lazurit.us" target="_blank" style="color: #007bff; text-decoration: none;">портал поддержки</a>
            </div>
            """, unsafe_allow_html=True)
        
        if login_button:
            users_data = st.secrets.get("users", {})
            if pwd in users_data:
                user_info = users_data[pwd]
                st.session_state.authenticated = True
                st.session_state.user_role = user_info.get("name", "Сотрудник")
                st.session_state.user_api_key = user_info.get("key", "")
                st.rerun()
            else:
                st.sidebar.error("❌ Код не опознан")
        st.stop()

check_password()

APPLICATION_TOKEN = st.session_state.user_api_key

# ТВОИ ОРИГИНАЛЬНЫЕ ПРОМПТЫ (БЕЗ ИЗМЕНЕНИЙ)
BASE_PHOTO_PROMPT = ("Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, Architectural Digest style. Masterpiece, 8k resolution, photorealistic interior photography. Completely re-texture all surfaces using high-end materials (marble, brushed metal, grain wood). Replace flat CG lighting with realistic global illumination and dramatic cinematic shadows.  Add subtle natural sunlight from windows.  Architectural Digest style, sharp focus, volumetric fog, ray-traced reflections. NO 3D render look, NO flat textures.")

PROMPT_PRESETS = {
    "Базовый промт": f"{BASE_PHOTO_PROMPT}",
    "️Свой промт": f"",
    "Базовый + Дневной свет": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Базовый + Студийный свет": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Базовый + Вечернее освещение": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Базовый + Unreal render style": f"Ultra-realistic Unreal Engine 5.4 Lumen render style. {BASE_PHOTO_PROMPT}",
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

# --- ИНИЦИАЛИЗАЦИЯ ---
if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = list(PROMPT_PRESETS.values())[0]
if 'last_full_response' not in st.session_state: st.session_state.last_full_response = ""

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide", page_icon=LOGO_PATH)

logo_b64 = get_base64_logo(LOGO_PATH)
st.markdown(f"""
    <style>
    html, body, [class*="st-"] {{ font-size: 20px !important; }}
    .stButton button {{ font-size: 22px !important; height: 3em !important; font-weight: bold !important; }}
    label {{ font-size: 22px !important; font-weight: bold !important; }}
    .header-container {{ display: flex; align-items: center; gap: 15px; padding: 5px 0; }}
    .header-logo {{ width: 100px; }}
    .header-text {{ font-size: 32px !important; font-weight: 800; margin: 0; }}
    </style>

    <div class="header-container">
        <img src="data:image/jpeg;base64,{logo_b64}" class="header-logo">
        <h1 class="header-text">LAZURIT AI Render: Фотореализм</h1>
    </div>
    <div style="color: gray; padding-bottom: 10px;">Аккаунт: {st.session_state.user_role}</div>
    <hr style="margin-top: 0;">
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Загрузка данных")
    uploaded_file = st.file_uploader("Выберите фото или рендер", type=['jpg', 'jpeg', 'png'])

    if uploaded_file:
        st.image(uploaded_file, caption="Ваш исходник", width=350)

    st.write("**Выбор освещения:**")
    preset_cols = st.columns(3)
    for i, (name, full_text) in enumerate(PROMPT_PRESETS.items()):
        if preset_cols[i % 3].button(name, use_container_width=True):
            st.session_state.current_prompt = full_text
            st.rerun()

    user_prompt = st.text_area("Техническое задание:", value=st.session_state.current_prompt, height=250)

with col2:
    st.subheader("2. Результат обработки")
    
    # Кнопка всегда доступна после входа
    if st.button("🚀 Запустить генерацию", use_container_width=True):
        if not uploaded_file:
            st.error("Загрузите изображение!")
        else:
            with st.spinner("Создаем фотореалистичный рендер..."):
                try:
                    uploaded_file.seek(0)
                    img_bytes = uploaded_file.read()
                    img_b64 = image_to_base64(img_bytes)
                    result = process_image(img_b64, user_prompt)

                    if 'outputs' in result:
                        msg = result['outputs'][0]['outputs'][0]['results']['message']['text']
                        st.session_state.last_full_response = msg
                        
                        img_data = msg.split("|||")[1] if "|||" in msg else msg
                        clean_data = img_data.replace('"', '').replace("'", "").strip()
                        raw_b64 = clean_data.split("base64,")[1] if "base64," in clean_data else clean_data

                        out_bytes = base64.b64decode(raw_b64)
                        st.image(out_bytes, caption="Готовый результат", use_container_width=True)

                        st.session_state.history.insert(0, out_bytes)
                        if len(st.session_state.history) > 12: st.session_state.history.pop()
                    else:
                        st.error("Ошибка API: Проверьте баланс ключа или промпт.")
                except Exception as e:
                    st.error(f"Ошибка при генерации: {e}")

    if st.session_state.last_full_response:
        st.divider()
        with st.expander("🛠 Итоговый промпт", expanded=True):
            full_text = st.session_state.last_full_response
            marker = "![result](data:image/png;base64,"
            if marker in full_text:
                only_prompt = full_text.split(marker)[0].strip()
            else:
                only_prompt = full_text.split("|||")[0].strip()
            st.text_area("Лог промпта:", value=only_prompt, height=400)

if st.session_state.history:
    st.divider()
    st.subheader("🕒 Последние результаты")
    h_cols = st.columns(12)
    for idx, img in enumerate(st.session_state.history):
        with h_cols[idx]:
            st.image(img, use_container_width=True)
