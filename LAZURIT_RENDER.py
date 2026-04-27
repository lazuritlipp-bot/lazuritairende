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
            f"background: url('data:image/png;base64,{bg_b64}') center/cover no-repeat fixed, #0E1117;"
            if bg_b64
            else "background: #0E1117;"
        )
        st.markdown(
            f"""
            <style>
            /* Скрываем лишнее на логине */
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            
            .block-container {{
                padding-top: 0 !important;
                max-width: 100% !important;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh !important;
            }}

            /* Карточка логина */
            div[data-testid="stForm"] {{
                width: 400px !important;
                height: auto !important;
                background: rgba(255, 255, 255, 0.95) !important;
                backdrop-filter: blur(15px);
                border-radius: 20px !important;
                padding: 40px !important;
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3) !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                flex-grow: 0 !important;
            }}
            
            /* Убираем растягивание вертикального блока внутри формы */
            div[data-testid="stForm"] [data-testid="stVerticalBlock"] {{
                gap: 15px !important;
            }}

            div[data-testid="stForm"] label {{
                color: #000000 !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                margin-bottom: 5px !important;
            }}

            /* Контейнер ввода: черная рамка, скругление, белый фон */
            div[data-testid="stForm"] [data-testid="stTextInput"] > div {{
                background: white !important;
                border: 1px solid #000000 !important;
                border-radius: 12px !important;
                padding: 2px !important;
                overflow: hidden !important;
            }}

            /* Текст ввода - ЧЕРНЫЙ */
            div[data-testid="stForm"] input {{
                color: #000000 !important; 
                background: white !important;
                border: none !important;
                font-size: 16px !important;
            }}

            /* Глаз - ЧЕРНЫЙ и скругленный */
            div[data-testid="stForm"] [data-testid="stTextInput"] button {{
                color: #000000 !important; 
                background: transparent !important;
                border: none !important;
                border-radius: 0 12px 12px 0 !important;
                margin-right: 5px !important;
            }}
            
            div[data-testid="stForm"] [data-testid="stTextInput"] button svg {{
                fill: #000000 !important; 
            }}

            /* Кнопка Войти */
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
                color: white !important;
                border: none !important;
                height: 48px !important;
                font-weight: 700 !important;
                border-radius: 12px !important;
                width: 100% !important;
                margin-top: 10px !important;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .login-logo {{
                display: block;
                margin: 0 auto 20px;
                max-width: 220px;
            }}
            .login-subtitle {{
                color: #444;
                text-align: center;
                font-size: 14px;
                margin-bottom: 25px;
                font-weight: 400;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            if logo_b64:
                st.markdown(f"<img class='login-logo' src='data:image/png;base64,{logo_b64}'>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='text-align:center; color:black;'>LAZURIT</h2>", unsafe_allow_html=True)
            
            st.markdown("<p class='login-subtitle'>Введите ваш персональный код доступа.</p>", unsafe_allow_html=True)
            pwd = st.text_input("Код доступа", type="password", placeholder="Ваш код")
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

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

st.markdown("""
    <style>
    .stApp { background-color: #E8E8E1; }
    
    /* Стили основного интерфейса после логина */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header { display: flex !important; }
    
    .block-container { 
        padding-top: 1.5rem !important; 
        max-width: 100% !important; 
        padding-left: 2rem !important; 
        padding-right: 2rem !important;
        height: auto !important;
        display: block !important;
    }
    
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
    
    .header-logo { height: 70px !important; width: auto !important; object-fit: contain; }
    
    .card { 
        background-color: #F8F9FA; 
        border-radius: 15px; 
        padding: 20px; 
        border: 1px solid #E0E0E0; 
        margin-bottom: 15px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    
    .card > b { color: #000000 !important; font-size: 16px; margin-bottom: 10px; display: block; }
    
    /* Кнопки и инпуты в рабочем интерфейсе */
    div.stButton > button:first-child[kind="primary"] { 
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; 
        color: white !important; 
        border: none !important; 
        height: 55px !important; 
        font-size: 18px !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
    }
    
    .empty-result-card { 
        height: 600px; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        color: #888; 
        border: 2px dashed #CCC; 
        background: #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ПРЕЗЕТЫ И ПРОМПТЫ ---
BASE_PHOTO_PROMPT = "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain materials strictly."

PROMPT_PRESETS = {
    "Студия": f"Professional architectural studio lighting. {BASE_PHOTO_PROMPT}",
    "День": f"Natural bright daylight from windows. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light. {BASE_PHOTO_PROMPT}",
    "Аксуары": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = next(iter(PROMPT_PRESETS.values()))

def image_to_base64(image_bytes): return base64.b64encode(image_bytes).decode('utf-8')

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# Шапка
logo_b64_main = _read_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #333; font-size: 20px;"><b>{st.session_state.user_role},</b> добро пожаловать!</div>
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
    PRESET_NAMES = ["Студия", "День", "Вечер", "Аксуары"]
    PRESET_PATHS = ["icons/studio.png", "icons/den.png", "icons/vecher.png", "icons/acsesoar.png"]

    selected_idx = image_select(
        label="",
        images=PRESET_PATHS,
        return_value="index",
        key="preset_image_select",
    )
    if selected_idx is not None and st.session_state.get("_preset_idx") != selected_idx:
        st.session_state.current_prompt = PROMPT_PRESETS[PRESET_NAMES[selected_idx]]
        st.session_state._preset_idx = selected_idx
        st.rerun()

    if st.button("Свой промт", use_container_width=True):
        st.session_state.current_prompt = ""
        st.session_state._preset_idx = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("Текст промпта:", value=st.session_state.current_prompt, height=180)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерируем..."):
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
        else: st.warning("Сначала загрузите фото!")

with col_main:
    st.markdown('<div class="card"><b>Результат AI генерации</b>', unsafe_allow_html=True)
    if st.session_state.history:
        st.image(st.session_state.history[0], use_container_width=True)
    else:
        st.markdown('<div class="empty-result-card"><h1>Фото результата</h1></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)
