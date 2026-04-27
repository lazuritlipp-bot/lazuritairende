import streamlit as st
import requests
import base64
import os

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"

# Список кнопок в строгом порядке (для CSS)
BUTTONS = [
    {"label": "Дневной", "img": "den.png", "prompt": "Natural bright daylight from windows, soft sun rays."},
    {"label": "Студийный", "img": "studio.png", "prompt": "Professional architectural studio lighting, balanced fills."},
    {"label": "Вечерний", "img": "vecher.png", "prompt": "Warm cozy evening light, mix of interior lamps and dusk."},
    {"label": "Аксессуары", "img": "acsesoar.png", "prompt": "Focus on luxury accessories, detailed textures, cinematic close-up."},
    {"label": "Свой", "img": "svoi.png", "prompt": ""},
]

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

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

# Генерируем CSS для каждой кнопки по её порядковому номеру
button_css = ""
for i, btn in enumerate(BUTTONS):
    b64 = get_base64_image(btn["img"])
    if b64:
        # nth-of-type(i+1) точно находит кнопку по порядку в контейнере
        button_css += f"""
        div[data-testid="stHorizontalBlock"]:nth-of-type({(i//3)+1}) button:nth-of-type({(i%3)+1}) {{
            background-image: url("data:image/png;base64,{b64}") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: 60% !important;
            color: transparent !important;
            border: 1px solid #E0E0E0 !important;
        }}
        """
# Более надежный селектор для сетки кнопок
button_css_fixed = ""
for i, btn in enumerate(BUTTONS):
    b64 = get_base64_image(btn["img"])
    if b64:
        # Таргетируем все кнопки в блоке Освещение по их индексу
        button_css_fixed += f"""
        div.lighting-grid button:nth-of-type({i+1}) {{
            background-image: url("data:image/png;base64,{b64}") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: 60% !important;
            color: transparent !important;
        }}
        """

st.markdown(f"""
    <style>
    .stApp {{ background-color: #E8E8E1; }}
    .block-container {{ padding-top: 1rem !important; }}
    
    .custom-header {{
        background-color: white;
        padding: 10px 30px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border: 1px solid #D1D1D1;
        min-height: 100px;
    }}
    
    .header-logo {{
        height: 120px !important;
        width: auto !important;
        max-width: 300px;
        object-fit: contain;
    }}
    
    .card {{
        background-color: #F8F9FA;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #E0E0E0;
        margin-bottom: 15px;
    }}
    
    .card > b {{
        color: #000000 !important;
        display: block;
        margin-bottom: 15px;
    }}
    
    /* СТИЛЬ КНОПОК-ПЛИТОК */
    div.stButton > button {{
        border-radius: 22px !important;
        background-color: white !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        height: 80px !important;
        width: 80px !important;
        transition: all 0.2s ease !important;
        margin: 0 auto !important;
        border: 1px solid #E0E0E0 !important;
    }}

    div.stButton > button:hover {{
        box-shadow: 0 6px 15px rgba(0,0,0,0.1) !important;
        transform: translateY(-3px) !important;
        border-color: #B0B0B0 !important;
    }}

    div.stButton > button:active {{
        transform: scale(0.95) !important;
    }}

    /* Главная кнопка ГЕНЕРИРОВАТЬ */
    div.stButton > button:first-child[kind="primary"] {{
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        height: 55px !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100% !important;
    }}

    .empty-result-card {{
        height: 600px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #888;
        border: 2px dashed #CCC;
    }}
    
    {button_css_fixed}
    </style>
    """, unsafe_allow_html=True)

# --- ДАННЫЕ ---
BASE_PHOTO_PROMPT = ("Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, Architectural Digest style.")

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = BASE_PHOTO_PROMPT
if 'last_response' not in st.session_state: st.session_state.last_response = ""

def image_to_base64(image_bytes): return base64.b64encode(image_bytes).decode('utf-8')

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ШАПКА ---
logo_b64 = get_base64_image(LOGO_PATH)
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

    # Обертка для кнопок, чтобы CSS мог их найти
    st.markdown('<div class="card lighting-grid"><b>2. Освещение</b>', unsafe_allow_html=True)
    
    p_cols = st.columns(3)
    for i, btn in enumerate(BUTTONS):
        col = p_cols[i % 3]
        if col.button(btn["label"], key=f"btn_{i}"):
            full_prompt = f"{btn['prompt']} {BASE_PHOTO_PROMPT}" if btn['prompt'] else ""
            st.session_state.current_prompt = full_prompt
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
