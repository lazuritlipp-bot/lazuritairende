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
            /* Скрываем элементы навигации на экране логина */
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

            /* КАРТОЧКА ЛОГИНА - ТЕМНАЯ */
            div[data-testid="stForm"] {{
                width: 480px !important;
                background: #333333 !important;
                border-radius: 24px !important;
                padding: 45px !important;
                box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8) !important;
                border: none !important;
                margin: auto !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important; /* Центрируем содержимое */
            }}
            
            div[data-testid="stForm"] label {{
                color: #FFFFFF !important;
                font-weight: 500 !important;
                margin-bottom: 8px !important;
                font-size: 15px !important;
                align-self: flex-start !important;
            }}

            /* ИНПУТ - СВЕТЛЫЙ, РАСТЯНУТЫЙ */
            div[data-testid="stForm"] [data-testid="stTextInput"] {{
                width: 100% !important;
                padding: 0 !important;
                margin-bottom: 5px !important;
            }}
            
            div[data-testid="stForm"] [data-testid="stTextInput"] > div {{
                background: #F0F2F6 !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 5px !important;
            }}
            
            div[data-testid="stForm"] input {{
                color: #333333 !important;
                font-size: 16px !important;
            }}

                      /* КНОПКА ВОЙТИ - ПОЛНАЯ ШИРИНА */
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] {
                width: 100% !important;
                margin-top: 15px !important;
            }
            
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
                background: linear-gradient(90deg, #A886F4 0%, #F17581 100%) !important;
                color: #FFFFFF !important;
                border: none !important;
                height: 62px !important;
                width: 100% !important;
                font-weight: 600 !important;
                font-size: 19px !important;
                border-radius: 14px !important;
                transition: all 0.2s ease;
                display: block !important;
            }
            
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button p {
                width: 100% !important;
                text-align: center !important;
                margin: 0 !important;
            }
            
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
                opacity: 0.92;
                transform: scale(1.01);
            }
            }}

            .login-logo {{
                display: block;
                margin: 0 auto 10px;
                max-width: 280px;
            }}
            .login-subtitle {{
                color: #CCCCCC;
                text-align: center;
                font-size: 15px;
                margin-bottom: 35px;
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
                    st.error("❌ Ошибка доступа")
        st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС (запускается после входа) ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

# Стили для рабочей области
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
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .header-logo { height: 60px !important; }
    
    .card { background-color: #F8F9FA; border-radius: 15px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .card > b { color: #000000 !important; font-size: 16px; margin-bottom: 10px; display: block; }
    
    div.stButton > button:first-child[kind="primary"] { 
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; 
        color: white !important; 
        height: 55px !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
        width: 100% !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Промпты
BASE_PHOTO_PROMPT = "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style."
PROMPT_PRESETS = {
    "Студия": f"Professional studio lighting. {BASE_PHOTO_PROMPT}",
    "День": f"Natural daylight. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Cozy warm light. {BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = PROMPT_PRESETS["Студия"]

def image_to_base64(image_bytes): return base64.b64encode(image_bytes).decode('utf-8')

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# Рендер шапки
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
    preset = st.radio("Выбор режима", list(PROMPT_PRESETS.keys()), horizontal=True)
    if preset: st.session_state.current_prompt = PROMPT_PRESETS[preset]
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("Текст промпта:", value=st.session_state.current_prompt, height=150)
    
    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", type="primary"):
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
    st.markdown('<div class="card"><b>Результат AI генерации</b>', unsafe_allow_html=True)
    if st.session_state.history:
        st.image(st.session_state.history[0], use_container_width=True)
    else:
        st.markdown('<div style="height:500px; background:#EEE; display:flex; align-items:center; justify-content:center; border-radius:10px; color:#888;">Фото результата</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)
