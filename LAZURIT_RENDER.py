import streamlit as st
import requests
import base64

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(
    page_title="LAZURIT AI Render",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Обработка выхода через URL
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
    return base64.b64encode(image_bytes).decode("utf-8")

def image_src(path):
    b64 = _read_b64(path)
    if not b64:
        return ""
    return f"data:image/png;base64,{b64}"

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
            [data-testid="stSidebar"], 
            [data-testid="stSidebarCollapsedControl"], 
            header, 
            [data-testid="stHeader"], 
            [data-testid="stToolbar"],
            #MainMenu {{
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
            }}

            .stApp {{ {bg_css} }}

            .block-container {{
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                max-width: 100% !important;
            }}

            div[data-testid="stForm"] {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 420px;
                max-width: 92vw;
                height: auto !important;
                min-height: 0 !important;
                background: rgba(30, 30, 32, 0.82) !important;
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border-radius: 22px;
                padding: 28px 32px 24px !important;
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                z-index: 9999;
            }}

            div[data-testid="stForm"] label {{
                color: #FFFFFF !important;
                font-weight: 500;
                font-size: 14px;
            }}

            div[data-testid="stForm"] input {{
                background: rgba(255, 255, 255, 0.06) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 10px !important;
                height: 46px !important;
                padding: 0 14px !important;
                width: 100% !important;
            }}

            div[data-testid="stForm"] input::placeholder {{
                color: rgba(255, 255, 255, 0.45) !important;
            }}

            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
                color: white !important;
                border: none !important;
                height: 50px !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                border-radius: 10px !important;
                width: 100% !important;
                margin-top: 6px;
            }}

            .login-logo {{
                display: block;
                margin: 0 auto 14px;
                width: 78%;
                max-width: 320px;
            }}

            .login-subtitle {{
                color: rgba(255, 255, 255, 0.85);
                text-align: center;
                font-size: 14px;
                margin: 0 0 22px;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            if logo_b64:
                st.markdown(
                    f"<img class='login-logo' src='data:image/png;base64,{logo_b64}' alt='LAZURIT' />",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<p class='login-subtitle'>Введите ваш персональный код доступа.</p>",
                unsafe_allow_html=True,
            )

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

# --- ФУНКЦИЯ ВЫХОДА ---
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- СТИЛИ РАБОЧЕЙ ОБЛАСТИ ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #E8E8E1;
    }

    /* Скрываем верхнюю полосу Streamlit */
    header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Шапка */
    .custom-header {
        background-color: white;
        padding: 15px 30px 45px 30px;
        border-radius: 12px;
        position: relative;
        margin-bottom: 0px;
        border: 1px solid #D1D1D1;
        min-height: 100px;
    }

    .header-logo {
        height: 80px !important;
        width: auto !important;
        max-width: 250px;
        object-fit: contain;
        position: absolute;
        right: 30px;
        top: 50%;
        transform: translateY(-50%);
    }

    /* Кнопка выхода внутри шапки */
    div.element-container:has(.logout-marker) {
        display: none;
    }

    div.element-container:has(.logout-marker) + div.element-container {
        margin-top: -58px !important;
        margin-left: 30px !important;
        margin-bottom: 25px !important;
        position: relative;
        z-index: 10;
        width: fit-content;
    }

    div.element-container:has(.logout-marker) + div.element-container button {
        background: transparent !important;
        color: #666 !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
        min-height: 32px !important;
        height: 32px !important;
        padding: 0 14px !important;
        font-size: 13.5px !important;
        transition: all 0.2s;
    }

    div.element-container:has(.logout-marker) + div.element-container button:hover {
        background: #FF4B4B !important;
        color: white !important;
        border-color: #FF4B4B !important;
    }

    /* Карточки */
    .card {
        background-color: #F8F9FA;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #E0E0E0;
        margin-bottom: 15px;
    }

    .card > b {
        color: #000000 !important;
    }

    /* Загрузчик и поле промпта */
    div[data-testid="stFileUploader"] > section {
        border-radius: 16px !important;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 16px !important;
    }

    /* Блок иконок пресетов */
    .preset-grid {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 18px;
        margin: 8px 0 16px 0;
        flex-wrap: nowrap;
    }

    .preset-icon {
        width: 62px;
        height: 62px;
        min-width: 62px;
        min-height: 62px;
        border-radius: 50%;
        background: #FFFFFF;
        border: 1.5px solid #D9D0C5;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        box-shadow: 0 5px 14px rgba(0, 0, 0, 0.04);
        transition: all 0.18s ease;
        overflow: hidden;
    }

    .preset-icon img {
        width: 36px;
        height: 36px;
        object-fit: contain;
        display: block;
    }

    .preset-icon:hover {
        border-color: #B8906D;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
    }

    .preset-icon.active {
        border: 2px solid #B8906D;
        box-shadow: 0 0 0 3px rgba(184, 144, 109, 0.14);
    }

    .preset-fallback {
        color: #B8906D;
        font-size: 13px;
        font-weight: 700;
    }

    /* Кнопка "Свой промт" */
    .custom-prompt-link {
        width: 100%;
        max-width: 360px;
        height: 48px;
        margin: 4px auto 2px auto;
        border-radius: 999px;
        border: 1.5px solid #D9D0C5;
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        text-decoration: none !important;
        color: #4E5966 !important;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.02em;
        transition: all 0.18s ease;
        box-shadow: 0 5px 14px rgba(0, 0, 0, 0.025);
    }

    .custom-prompt-link img {
        max-height: 22px;
        max-width: 74px;
        width: auto;
        object-fit: contain;
        display: block;
    }

    .custom-prompt-link small {
        color: #9A9288;
        font-size: 12px;
        font-weight: 500;
        margin-left: 4px;
        letter-spacing: 0;
    }

    .custom-prompt-link:hover {
        border-color: #B8906D;
        color: #B8906D !important;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.07);
        transform: translateY(-1px);
    }

    .custom-prompt-link.active {
        border: 2px solid #B8906D;
        box-shadow: 0 0 0 3px rgba(184, 144, 109, 0.14);
    }

    /* Главная кнопка генерации */
    div.stButton > button:first-child[kind="primary"] {
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        border: none !important;
        height: 55px !important;
        font-size: 17px !important;
        font-weight: bold !important;
        border-radius: 16px !important;
    }

    .empty-result-card {
        height: 600px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #888;
        border: 2px dashed #CCC;
        border-radius: 24px;
    }

    div[data-testid="column"]:nth-child(1) img {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- ПРОМПТЫ ---
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
PRESET_PATHS = [
    "studio.png",
    "den.png",
    "vecher.png",
    "acsesoar.png",
]

# --- СОСТОЯНИЕ ---
if "history" not in st.session_state:
    st.session_state.history = []

if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = PROMPT_PRESETS["Студия"]

if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = st.session_state.current_prompt

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "_preset_idx" not in st.session_state:
    st.session_state._preset_idx = 0

# --- ОБРАБОТКА КЛИКОВ ПО HTML-ИКОНКАМ ---
preset_param = st.query_params.get("preset")
if preset_param is not None:
    try:
        preset_idx = int(preset_param)
        if 0 <= preset_idx < len(PRESET_NAMES):
            preset_name = PRESET_NAMES[preset_idx]
            st.session_state.current_prompt = PROMPT_PRESETS[preset_name]
            st.session_state.prompt_text = PROMPT_PRESETS[preset_name]
            st.session_state._preset_idx = preset_idx
    except Exception:
        pass

    st.query_params.clear()
    st.rerun()

if st.query_params.get("custom_prompt") == "true":
    st.session_state.current_prompt = PROMPT_PRESETS["Свой промт"]
    st.session_state.prompt_text = PROMPT_PRESETS["Свой промт"]
    st.session_state._preset_idx = None
    st.query_params.clear()
    st.rerun()

# --- ЗАПРОС К API ---
def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"

    payload = {
        "input_value": combined_input,
        "output_type": "chat",
        "input_type": "chat",
    }

    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json",
    }

    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ШАПКА ---
logo_b64_main = _read_b64(LOGO_PATH)

st.markdown(
    f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px; margin-bottom: 5px;">
            <b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render
        </div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """,
    unsafe_allow_html=True,
)

# --- КНОПКА ВЫХОДА ---
st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)

if st.button("🚪 Выйти", key="logout_btn"):
    logout()

# --- РАБОЧАЯ ОБЛАСТЬ ---
# Левая колонка уменьшена примерно до нужного размера.
# Если нужно еще уже — уменьшить первое число.
col_left, col_main, col_hist = st.columns([1.2, 2.75, 0.45], gap="small")

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)

    f = st.file_uploader("upload", label_visibility="collapsed")

    if f:
        st.image(f, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

    # 4 круглые иконки в ряд
    preset_html = '<div class="preset-grid">'

    for idx, name in enumerate(PRESET_NAMES):
        icon_src = image_src(PRESET_PATHS[idx])
        active_class = " active" if st.session_state.get("_preset_idx") == idx else ""

        if icon_src:
            icon_html = f'<img src="{icon_src}" alt="{name}">'
        else:
            icon_html = f'<span class="preset-fallback">{name[0]}</span>'

        preset_html += (
            f'<a class="preset-icon{active_class}" '
            f'href="?preset={idx}" '
            f'target="_self" '
            f'title="{name}">'
            f'{icon_html}'
            f'</a>'
        )

    preset_html += "</div>"

    st.markdown(preset_html, unsafe_allow_html=True)

    # Вытянутая кнопка "Свой промт" с svoi.png
    svoi_src = image_src("svoi.png")
    custom_active_class = " active" if st.session_state.get("_preset_idx") is None else ""

    if svoi_src:
        svoi_icon_html = f'<img src="{svoi_src}" alt="Свой промт">'
    else:
        svoi_icon_html = ""

    st.markdown(
        f"""
        <a class="custom-prompt-link{custom_active_class}" href="?custom_prompt=true" target="_self">
            {svoi_icon_html}
            <span>СВОЙ ПРОМТ <small>(задание)</small></span>
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    user_text = st.text_area(
        "ТЗ промпта:",
        key="prompt_text",
        height=200,
    )

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
        st.markdown(
            """
            <div class="card empty-result-card">
                <h1 style="color: #bbb; font-weight: bold;">Результат генерации</h1>
                <p style="color: #ccc;">Загрузите изображение для начала работы</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)

    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)

if st.session_state.last_response:
    with st.expander("🛠 Лог"):
        st.text(st.session_state.last_response)
