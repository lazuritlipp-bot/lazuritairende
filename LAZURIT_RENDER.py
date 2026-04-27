import streamlit as st
import requests
import base64
from streamlit_image_select import image_select

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"
BACKGROUND_PATH = "background.png"

# --- КЭШИРОВАНИЕ РЕСУРСОВ ---
@st.cache_data
def _read_b64(path):
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except Exception:
        return ""

# --- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        bg_b64 = _read_b64(BACKGROUND_PATH)
        logo_b64 = _read_b64(LOGO_PATH)
        bg_css = (
            f"background: url('data:image/png;base64,{bg_b64}') center/cover no-repeat fixed, #111111;"
            if bg_b64
            else "background: #111111;"
        )
        st.markdown(
            f"""
            <style>
            /* Скрываем лишнее */
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            
            .block-container {{
                padding-top: 0 !important;
                max-width: 100% !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                height: 100vh !important;
                position: fixed !important;
                top: 0; left: 0; right: 0; bottom: 0;
            }}

            /* КАРТОЧКА ЛОГИНА - ТЕМНАЯ (согласно image_94e9b8.png) */
            div[data-testid="stForm"] {{
                width: 400px !important;
                background: #333333 !important; /* Темный цвет карточки */
                border-radius: 20px !important;
                padding: 30px !important;
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5) !important;
                border: none !important;
                margin: auto !important;
            }}
            
            div[data-testid="stForm"] label {{
                color: #FFFFFF !important;
                font-weight: 400 !important;
                margin-bottom: 8px !important;
                font-size: 14px !important;
            }}

            /* ИНПУТ - СВЕТЛЫЙ (согласно image_955b31.png) */
            div[data-testid="stForm"] [data-testid="stTextInput"] > div {{
                background: #F0F2F6 !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 5px !important;
            }}
            
            div[data-testid="stForm"] input {{
                color: #333333 !important;
            }}

            /* КНОПКА ВОЙТИ - МАЛЕНЬКАЯ И ВЛЕВО (согласно image_94f936.jpg) */
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] {{
                text-align: left !important;
                margin-top: 20px !important;
            }}
            
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(135deg, #A886F4 0%, #F17581 100%) !important;
                color: white !important;
                border: none !important;
                height: 42px !important;
                padding: 0 35px !important;
                font-weight: 500 !important;
                font-size: 15px !important;
                border-radius: 10px !important;
                width: auto !important;
                transition: transform 0.2s;
            }}

            .login-logo {{
                display: block;
                margin: 0 auto 10px;
                max-width: 200px;
                filter: brightness(1.5); /* Чтобы лого на темном было видно */
            }}
            .login-subtitle {{
                color: #CCCCCC;
                text-align: center;
                font-size: 13px;
                margin-bottom: 20px;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            if logo_b64:
                st.markdown(f"<img class='login-logo' src='data:image/png;base64,{logo_b64}'>", unsafe_allow_html=True)
            st.markdown("<p class='login-subtitle'>Введите ваш персональный код доступа.</p>", unsafe_allow_html=True)
            pwd = st.text_input("Код доступа", type="password", placeholder="Введите код")
            submitted = st.form_submit_button("Войти")
            
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

# --- ОСНОВНОЙ ИНТЕРФЕЙС (после входа) ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

st.markdown("""
    <style>
    .stApp { background-color: #E8E8E1; }
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header { display: flex !important; }
    .block-container { padding-top: 1.5rem !important; max-width: 100% !important; display: block !important; position: relative !important; height: auto !important; }
    
    .custom-header { 
        background-color: white; 
        padding: 15px 30px; 
        border-radius: 15px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 25px; 
        border: 1px solid #D1D1D1; 
    }
    .header-logo { height: 60px !important; }
    
    .card { background-color: #F8F9FA; border-radius: 15px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .card > b { color: #000000; font-size: 16px; margin-bottom: 10px; display: block; }
    
    div.stButton > button:first-child[kind="primary"] { 
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; 
        color: white !important; 
        height: 55px !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Шапка
logo_b64_main = _read_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #333; font-size: 20px;"><b>{st.session_state.user_role},</b> добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

col_left, col_main, col_hist = st.columns([2.2, 2.2, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка данных</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f: st.image(f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)
    # Упрощенный выбор для примера
    preset = st.radio("Пресеты", ["Студия", "День", "Вечер", "Свой промт"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("Текст промпта:", height=150)
    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", type="primary"):
        if f: st.info("Идет обработка...")
        else: st.warning("Загрузите фото!")

with col_main:
    st.markdown('<div class="card"><b>Результат AI генерации</b>', unsafe_allow_html=True)
    st.markdown('<div style="height:500px; background:#EEE; display:flex; align-items:center; justify-content:center; border-radius:10px; color:#888;">Фото результата</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
