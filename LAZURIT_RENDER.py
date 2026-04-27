import streamlit as st
import requests
import base64
from streamlit_image_select import image_select

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")

# Проверка параметра выхода в URL
if st.query_params.get("logout") == "true":
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"
BACKGROUND_PATH = "background.png"

@st.cache_data
def _read_b64(path):
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except Exception:
        return ""

def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- ЭКРАН ВХОДА ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        bg_b64 = _read_b64(BACKGROUND_PATH)
        logo_b64 = _read_b64(LOGO_PATH)
        bg_css = (
            f"background: url('data:image/png;base64,{bg_b64}') center/cover no-repeat fixed, #0E1117;"
            if bg_b64
            else "background: #0E1117;"
        )
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }}

            div[data-testid="stForm"] {{
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                width: 420px; max-width: 92vw; height: auto !important; min-height: 0 !important;
                background: rgba(30, 30, 32, 0.82) !important;
                backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
                border-radius: 22px; padding: 28px 32px 24px !important;
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.08) !important; z-index: 9999;
            }}
            div[data-testid="stForm"] label {{ color: #FFFFFF !important; font-weight: 500; font-size: 14px; }}
            div[data-testid="stForm"] input {{
                background: rgba(255, 255, 255, 0.06) !important; color: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important; border-radius: 10px !important;
                height: 46px !important; padding: 0 14px !important; width: 100% !important;
            }}
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
                color: white !important; border: none !important; height: 50px !important;
                font-weight: 600 !important; font-size: 16px !important; border-radius: 10px !important;
                width: 100% !important; margin-top: 6px;
            }}
            .login-logo {{ display: block; margin: 0 auto 14px; width: 78%; max-width: 320px; }}
            .login-subtitle {{ color: rgba(255, 255, 255, 0.85); text-align: center; font-size: 14px; margin: 0 0 22px; }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            if logo_b64:
                st.markdown(f"<img class='login-logo' src='data:image/png;base64,{logo_b64}' alt='LAZURIT' />", unsafe_allow_html=True)
            st.markdown("<p class='login-subtitle'>Введите ваш персональный код доступа.</p>", unsafe_allow_html=True)
            pwd = st.text_input("Код доступа", type="password", placeholder="Введите код")
            submitted = st.form_submit_button("Войти", use_container_width=True)

            if submitted:
                users_data = st.secrets.get("users", {})
                if pwd in users_data:
                    user_info = users_data[pwd]
                    st.session_state.authenticated = True
                    st.session_state.user_role = user_info.get("name", "Сотрудник")
                    st.session_state.user_api_key = user_info.get("key", "")
                    st.rerun()
                else:
                    st.error("❌ Код не опознан")
        st.stop()

check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

# --- СТИЛИ РАБОЧЕЙ ОБЛАСТИ ---
st.markdown("""
    <style>
    .stApp { background-color: #E8E8E1; }
    .block-container { padding-top: 1rem !important; max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    
    .custom-header { 
        background-color: white; 
        padding: 15px 30px; 
        border-radius: 12px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 20px; 
        border: 1px solid #D1D1D1; 
        min-height: 110px;
    }
    
    .header-info-block {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .header-logo { height: 90px !important; width: auto !important; object-fit: contain; }
    
    .btn-logout {
        background-color: #f0f0f0;
        color: #333;
        border: 1px solid #ccc;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 13px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        width: fit-content;
        cursor: pointer;
        font-weight: 500;
        transition: 0.2s;
    }
    .btn-logout:hover { background-color: #e0e0e0; border-color: #bbb; color: #000; }

    .card { background-color: #F8F9FA; border-radius: 15px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .card > b { color: #000000 !important; }
    
    div.stButton > button:first-child[kind="primary"] { 
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; 
        color: white !important; height: 55px !important; font-size: 18px !important; font-weight: bold !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- ШАПКА ---
logo_b64_main = _read_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div class="header-info-block">
            <div style="color: #444; font-size: 18px;">
                <b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render
            </div>
            <a href="?logout=true" target="_self" class="btn-logout">
                🚪 Выйти
            </a>
        </div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

# --- ДАННЫЕ И ПРОЦЕССИНГ ---
BASE_PHOTO_PROMPT = "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style."
PROMPT_PRESETS = {
    "Студия": f"Professional studio lighting. {BASE_PHOTO_PROMPT}",
    "День": f"Natural daylight. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Cozy evening light. {BASE_PHOTO_PROMPT}",
    "Аксессуары": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = next(iter(PROMPT_PRESETS.values()))

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ОСНОВНОЙ КОНТЕНТ ---
col_left, col_main, col_hist = st.columns([2.2, 2.2, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f: st.image(f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)
    PRESET_PATHS = ["icons/studio.png", "icons/den.png", "icons/vecher.png", "icons/acsesoar.png"]
    selected_idx = image_select(label="", images=PRESET_PATHS, key="preset_select")
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=150)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    res = process_image(image_to_base64(f.read()), user_text)
                    if 'outputs' in res:
                        msg = res['outputs'][0]['outputs'][0]['results']['message']['text']
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
        st.image(st.session_state.history[0], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card" style="height:500px; display:flex; align-items:center; justify-content:center; color:#ccc;">Ожидание генерации</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)
