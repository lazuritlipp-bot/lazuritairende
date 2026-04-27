import streamlit as st
import requests
import base64

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"

# --- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        st.markdown("<style>.stApp { background-color: #0E1117; }</style>", unsafe_allow_html=True)
        st.sidebar.title("🔐 LAZURIT AI Render")
        pwd = st.sidebar.text_input("Введите код доступа:", type="password")
        if st.sidebar.button("Войти", use_container_width=True):
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

# --- ИНТЕРФЕЙС И СТИЛИ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

st.markdown("""
    <style>
    /* Основной фон */
    .stApp { background-color: #E8E8E1; }
    
    /* Отступ сверху */
    .block-container { padding-top: 2rem !important; }
    
    /* Шапка */
    .custom-header {
        background-color: white;
        padding: 15px 30px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border: 1px solid #D1D1D1;
    }
    
    /* РАЗМЕР ЛОГОТИПА */
    .header-logo {
        height: 70px; 
        width: auto;
        object-fit: contain;
    }
    
    /* Карточки блоков */
    .card {
        background-color: #F8F9FA;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #E0E0E0;
        margin-bottom: 15px;
    }
    
    /* ЧЕРНЫЙ ЦВЕТ ДЛЯ ЗАГОЛОВКОВ КАРТОЧЕК */
    .card > b {
        color: #000000 !important;
    }
    
    /* Стиль кнопок выбора промпта */
    div[data-testid="stHorizontalBlock"] button {
        background-color: #FFFFFF !important;
        color: #333 !important;
        border: 1px solid #CCC !important;
    }

    /* Главная кнопка */
    div.stButton > button:first-child[kind="primary"] {
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        border: none !important;
        height: 55px !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }

    /* Стиль для пустого центрального блока */
    .empty-result-card {
        height: 600px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #888;
        border: 2px dashed #CCC;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ДАННЫЕ ---
BASE_PHOTO_PROMPT = ("Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, Architectural Digest style. Masterpiece, 8k resolution, photorealistic interior photography. Completely re-texture all surfaces using high-end materials (marble, brushed metal, grain wood). Replace flat CG lighting with realistic global illumination and dramatic cinematic shadows. Add subtle natural sunlight from windows. Architectural Digest style, sharp focus, volumetric fog, ray-traced reflections. NO 3D render look, NO flat textures.")

PROMPT_PRESETS = {
    "Базовый промт": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
    "Дневной свет": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Студийный свет": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Unreal Style": f"Ultra-realistic Unreal Engine 5.4 Lumen render style. {BASE_PHOTO_PROMPT}"
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = PROMPT_PRESETS["Базовый промт"]
if 'last_response' not in st.session_state: st.session_state.last_response = ""

def image_to_base64(image_bytes): return base64.b64encode(image_bytes).decode('utf-8')
def get_base64_logo(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ШАПКА ---
logo_b64 = get_base64_logo(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/jpeg;base64,{logo_b64}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([1.2, 2.5, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f: st.image(f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)
    p_cols = st.columns(2)
    for i, name in enumerate(PROMPT_PRESETS.keys()):
        if p_cols[i % 2].button(name, use_container_width=True):
            st.session_state.current_prompt = PROMPT_PRESETS[name]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=200)
    
    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    res = process_image(image_to_base64(f.read()), user_text)
                    if 'outputs' in res:
                        msg = res['outputs'][0]['outputs'][0]['results']['message']['text']
                        st.session_state.last_response = msg
                        raw_data = msg.split("|||")[1] if "|||" in msg else msg
                        if "base64," in raw_data: raw_data = raw_data.split("base64,")[1]
                        img_bytes = base64.b64decode(raw_data.replace('"', '').strip())
                        st.session_state.history.insert(0, img_bytes)
                        st.rerun()
                except Exception as e: st.error(f"Ошибка: {e}")
        else: st.warning("Загрузите фото!")

with col_main:
    if st.session_state.history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="card empty-result-card">
                <h1 style="color: #bbb; font-weight: bold;">Результат генерации</h1>
                <p style="color: #ccc;">Загрузите изображение для начала работы</p>
            </div>
        """, unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)

if st.session_state.last_response:
    with st.expander("🛠 Лог"):
        st.text(st.session_state.last_response)
