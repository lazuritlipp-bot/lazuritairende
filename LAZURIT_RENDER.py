import streamlit as st
import requests
import base64

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide", initial_sidebar_state="collapsed")

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
    return base64.b64encode(image_bytes).decode("utf-8")

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
            if bg_b64 else "background: #0E1117;"
        )
        st.markdown(f"""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header, [data-testid="stHeader"] {{
                display: none !important;
            }}
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
            """, unsafe_allow_html=True)
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

# --- ВЫХОД ---
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- ДАННЫЕ ---
BASE_PHOTO_PROMPT = (
    "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
    "Maintain the original color palette and materials of the furniture strictly. "
    "Enhance existing textures (wood grain, stone, fabric) without changing their color. "
    "Replace flat lighting with professional cinematic studio lighting and realistic global illumination. "
    "Add natural soft sunlight and deep realistic shadows to create depth. "
    "High-contrast, sharp details, realistic reflections."
)

PROMPT_PRESETS = {
    "Студия": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "День": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Аксессуары": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

PRESET_NAMES = ["Студия", "День", "Вечер", "Аксессуары"]
PRESET_ICONS = ["studio.png", "den.png", "vecher.png", "acsesoar.png"]

# --- STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
if "sel_idx" not in st.session_state:
    st.session_state.sel_idx = 0
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[0]]
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# --- API ---
def process_image(img_b64_val, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64_val}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json",
    }
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ДИНАМИЧЕСКИЙ CSS ДЛЯ ИКОНОК (встраиваем base64 прямо в background-image кнопки) ---
def build_preset_css():
    css = ""
    for i in range(4):
        b64 = _read_b64(PRESET_ICONS[i])
        if not b64:
            continue
        is_active = (st.session_state.sel_idx == i)
        border = "#B8906D" if is_active else "#D4C4B0"
        shadow = "0 0 0 3px rgba(184,144,109,0.14)" if is_active else "0 5px 14px rgba(0,0,0,0.04)"
        css += f"""
        [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child({i+1}) [data-testid="stButton"] button {{
            width: 70px !important;
            height: 70px !important;
            border-radius: 50% !important;
            background-image: url('data:image/png;base64,{b64}') !important;
            background-size: 36px !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-color: white !important;
            border: 2px solid {border} !important;
            box-shadow: {shadow} !important;
            color: transparent !important;
            font-size: 0 !important;
            padding: 0 !important;
            transition: all 0.2s !important;
        }}
        [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child({i+1}) [data-testid="stButton"] button:hover {{
            border-color: #B8906D !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 18px rgba(0,0,0,0.08) !important;
        }}
        """
    return css

preset_css = build_preset_css()

# --- CSS ИКОНКИ ДЛЯ "СВОЙ ПРОМТ" ---
svoi_b64 = _read_b64("svoi.png")
svoi_css = ""
if svoi_b64:
    svoi_css = f"""
    .custom-prompt-wrapper button::before {{
        content: '';
        display: inline-block;
        width: 18px; height: 18px;
        background-image: url('data:image/png;base64,{svoi_b64}');
        background-size: contain; background-repeat: no-repeat;
        margin-right: 8px; vertical-align: middle;
    }}
    """

# --- ВСЕ СТИЛИ ОДНИМ БЛОКОМ ---
logo_b64_main = _read_b64(LOGO_PATH)

st.markdown(f"""
    <style>
    .stApp {{ background-color: #E8E8E1; }}
    header, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important; visibility: hidden !important; height: 0 !important;
    }}
    .block-container {{
        padding-top: 1.2rem !important; max-width: 100% !important;
        padding-left: 2rem !important; padding-right: 2rem !important;
    }}

    /* Шапка */
    .custom-header {{
        background: white; padding: 15px 30px 45px 30px; border-radius: 12px;
        position: relative; border: 1px solid #D1D1D1; min-height: 100px;
    }}
    .header-logo {{
        height: 80px !important; position: absolute; right: 30px;
        top: 50%; transform: translateY(-50%);
    }}

    /* Кнопка выхода */
    div.element-container:has(.logout-marker) {{ display: none; }}
    div.element-container:has(.logout-marker) + div.element-container {{
        margin-top: -58px !important; margin-left: 30px !important;
        margin-bottom: 25px !important; position: relative; z-index: 10; width: fit-content;
    }}
    div.element-container:has(.logout-marker) + div.element-container button {{
        background: transparent !important; color: #666 !important;
        border: 1px solid #ccc !important; border-radius: 8px !important;
        height: 32px !important; font-size: 13.5px !important;
    }}
    div.element-container:has(.logout-marker) + div.element-container button:hover {{
        background: #FF4B4B !important; color: white !important;
    }}

    /* Карточки */
    .card {{
        background: #F8F9FA; border-radius: 20px; padding: 20px;
        border: 1px solid #E0E0E0; margin-bottom: 15px;
    }}
    .card > b {{ color: #000 !important; }}
    div[data-testid="stTextArea"] textarea {{ border-radius: 16px !important; }}

    /* Кнопка "Свой промт" */
    .custom-prompt-wrapper button {{
        width: 100% !important; height: 48px !important; border-radius: 999px !important;
        background: white !important; border: 2px solid #D4C4B0 !important;
        color: #4E5966 !important; font-weight: 700 !important; font-size: 13px !important;
        transition: all 0.2s !important;
    }}
    .custom-prompt-wrapper button:hover {{
        border-color: #B8906D !important; color: #B8906D !important;
    }}
    {svoi_css}

    /* Кнопка генерации */
    button[kind="primary"] {{
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important; height: 55px !important; font-weight: bold !important;
        border-radius: 16px !important; font-size: 17px !important;
    }}

    .empty-result-card {{
        height: 600px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; color: #888;
        border: 2px dashed #CCC; border-radius: 24px;
    }}

    /* ДИНАМИЧЕСКИЙ CSS КРУГЛЫХ ИКОНОК — иконка ВСТРАИВАЕТСЯ в кнопку */
    {preset_css}
    </style>
    """, unsafe_allow_html=True)

# --- ШАПКА ---
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)
if st.button("🚪 Выйти", key="logout_btn"):
    logout()

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([1.2, 2.75, 0.45], gap="small")

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f:
        st.image(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

    # 4 КРУГЛЫЕ КНОПКИ-ИКОНКИ — настоящие st.button, иконка встроена через CSS background-image
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(PRESET_NAMES[0], key="preset_btn_0"):
            st.session_state.sel_idx = 0
            st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[0]]
            st.rerun()
    with c2:
        if st.button(PRESET_NAMES[1], key="preset_btn_1"):
            st.session_state.sel_idx = 1
            st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[1]]
            st.rerun()
    with c3:
        if st.button(PRESET_NAMES[2], key="preset_btn_2"):
            st.session_state.sel_idx = 2
            st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[2]]
            st.rerun()
    with c4:
        if st.button(PRESET_NAMES[3], key="preset_btn_3"):
            st.session_state.sel_idx = 3
            st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[3]]
            st.rerun()

    # Кнопка "Свой промт" — настоящая st.button, стилизована как овал
    st.markdown('<div class="custom-prompt-wrapper">', unsafe_allow_html=True)
    if st.button("СВОЙ ПРОМТ (задание)", key="custom_prompt_btn"):
        st.session_state.sel_idx = -1
        st.session_state.prompt_text = PROMPT_PRESETS["Свой промт"]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", key="prompt_text", height=200)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    res = process_image(image_to_base64(f.read()), user_text)
                    if "outputs" in res:
                        msg = res["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                        st.session_state.last_response = msg
                        raw_data = msg.split("|||")[1] if "|||" in msg else msg
                        if "base64," in raw_data:
                            raw_data = raw_data.split("base64,")[1]
                        img_bytes = base64.b64decode(raw_data.replace('"', "").strip())
                        st.session_state.history.insert(0, img_bytes)
                        st.session_state.history = st.session_state.history[:10]
                        st.rerun()
                    else:
                        st.error("API не вернул изображение.")
                        st.session_state.last_response = str(res)
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.warning("Загрузите фото!")

with col_main:
    if st.session_state.history:
        st.markdown('<div class="card" style="padding: 10px;">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown("</div>", unsafe_allow_html=True)
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
