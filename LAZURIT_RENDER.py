import streamlit as st
import requests
import base64

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"
BACKGROUND_PATH = "background.png"


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
            /* Скрываем сайдбар и хедер на экране логина */
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            .block-container {{
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                max-width: 100% !important;
            }}

            /* Тёмная карточка авторизации по центру */
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
            /* Внутренние контейнеры формы тоже не должны растягиваться */
            div[data-testid="stForm"] > div,
            div[data-testid="stForm"] [data-testid="stVerticalBlock"] {{
                height: auto !important;
                min-height: 0 !important;
                gap: 0.6rem !important;
            }}
            div[data-testid="stForm"] label {{
                color: #FFFFFF !important;
                font-weight: 500;
                font-size: 14px;
            }}
            /* Контейнер инпута — без лишних рамок */
            div[data-testid="stForm"] [data-testid="stTextInput"] > div {{
                background: transparent !important;
                border: none !important;
            }}
            /* Поле ввода — тёмное */
            div[data-testid="stForm"] input {{
                background: rgba(255, 255, 255, 0.06) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 10px !important;
                height: 46px !important;
                padding: 0 14px !important;
            }}
            div[data-testid="stForm"] input::placeholder {{ color: rgba(255, 255, 255, 0.45) !important; }}
            /* Кнопка показа пароля внутри инпута — прозрачная, не градиентная */
            div[data-testid="stForm"] [data-testid="stTextInput"] button {{
                background: transparent !important;
                color: rgba(255, 255, 255, 0.7) !important;
                border: none !important;
                box-shadow: none !important;
                width: auto !important;
                height: auto !important;
                padding: 0 8px !important;
            }}
            div[data-testid="stForm"] [data-testid="stTextInput"] button:hover {{
                background: rgba(255, 255, 255, 0.06) !important;
                color: #FFFFFF !important;
            }}
            div[data-testid="stForm"] [data-testid="stTextInput"] button svg {{
                fill: currentColor !important;
            }}

            /* Главная градиентная кнопка — только submit формы */
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
                color: white !important;
                border: none !important;
                height: 50px !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                border-radius: 10px !important;
                width: 100%;
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
            else:
                st.markdown(
                    "<h2 style='color:#FFFFFF;text-align:center;margin:0 0 12px;letter-spacing:1px;'>LAZURIT</h2>",
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

# --- ИНТЕРФЕЙС И СТИЛИ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

st.markdown("""
    <style>
    /* Основной фон */
    .stApp { background-color: #E8E8E1; }

    /* Компактная рабочая область, не на всю ширину */
    .block-container {
        padding-top: 1rem !important;
        max-width: 1280px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Шапка */
    .custom-header {
        background-color: white;
        padding: 10px 30px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border: 1px solid #D1D1D1;
        min-height: 100px;
    }

    /* РАЗМЕР ЛОГОТИПА */
    .header-logo {
        height: 120px !important;
        width: auto !important;
        max-width: 300px;
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
        font-size: 12px !important;
        padding: 4px 6px !important;
    }

    /* Карточки-иконки пресетов */
    .preset-card {
        background: #FFFFFF;
        border-radius: 22px;
        height: 100px;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        border: 1px solid #EAEAEA;
        transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
    }
    .preset-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12);
        border-color: #C8AE85;
    }
    .preset-card img {
        max-width: 80%;
        max-height: 80%;
        object-fit: contain;
        pointer-events: none;
    }
    /* Якорь — невидимый маркер для CSS */
    .preset-overlay-anchor { display: none; }

    /* Поднимаем ряд кнопок-пресетов поверх ряда иконок */
    [data-testid="stElementContainer"]:has(.preset-overlay-anchor) ~ [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"],
    [data-testid="element-container"]:has(.preset-overlay-anchor) ~ [data-testid="element-container"] [data-testid="stHorizontalBlock"] {
        margin-top: -116px !important;
        position: relative;
        z-index: 5;
    }
    /* Делаем сами кнопки-наложения прозрачными */
    [data-testid="stElementContainer"]:has(.preset-overlay-anchor) ~ [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] .stButton button,
    [data-testid="element-container"]:has(.preset-overlay-anchor) ~ [data-testid="element-container"] [data-testid="stHorizontalBlock"] .stButton button {
        background: transparent !important;
        border: 1px solid transparent !important;
        box-shadow: none !important;
        color: transparent !important;
        height: 100px !important;
        border-radius: 22px !important;
        cursor: pointer;
        transition: border-color 0.12s ease, transform 0.12s ease !important;
    }
    [data-testid="stElementContainer"]:has(.preset-overlay-anchor) ~ [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] .stButton button:hover,
    [data-testid="element-container"]:has(.preset-overlay-anchor) ~ [data-testid="element-container"] [data-testid="stHorizontalBlock"] .stButton button:hover {
        background: rgba(200, 174, 133, 0.08) !important;
        border-color: #C8AE85 !important;
    }
    /* Скрываем подпись внутри прозрачной кнопки */
    [data-testid="stElementContainer"]:has(.preset-overlay-anchor) ~ [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] .stButton button p,
    [data-testid="stElementContainer"]:has(.preset-overlay-anchor) ~ [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] .stButton button div,
    [data-testid="element-container"]:has(.preset-overlay-anchor) ~ [data-testid="element-container"] [data-testid="stHorizontalBlock"] .stButton button p,
    [data-testid="element-container"]:has(.preset-overlay-anchor) ~ [data-testid="element-container"] [data-testid="stHorizontalBlock"] .stButton button div {
        color: transparent !important;
        visibility: hidden !important;
        font-size: 0 !important;
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
    "Аксуары": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = next(iter(PROMPT_PRESETS.values()))
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
    PRESET_ICONS = {
        "Студия": "icons/studio.png",
        "День": "icons/den.png",
        "Вечер": "icons/vecher.png",
        "Аксуары": "icons/acsesoar.png",
    }

    # Ряд видимых иконок-карточек (через колонки, чтобы ширина совпадала с кнопками)
    visual_cols = st.columns(len(PRESET_ICONS), gap="small")
    for i, (name, icon_path) in enumerate(PRESET_ICONS.items()):
        with visual_cols[i]:
            b64 = _read_b64(icon_path)
            if b64:
                st.markdown(
                    f'<div class="preset-card" title="{name}">'
                    f'<img src="data:image/png;base64,{b64}" alt="{name}"/>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Якорь — по нему CSS найдёт следующий ряд кнопок и наложит его поверх иконок
    st.markdown('<div class="preset-overlay-anchor"></div>', unsafe_allow_html=True)

    overlay_cols = st.columns(len(PRESET_ICONS), gap="small")
    for i, name in enumerate(PRESET_ICONS.keys()):
        with overlay_cols[i]:
            if st.button(name, key=f"preset_btn_{i}", help=name, use_container_width=True):
                st.session_state.current_prompt = PROMPT_PRESETS[name]
                st.rerun()

    if st.button("Свой промт", key="custom_prompt_btn", use_container_width=True):
        st.session_state.current_prompt = PROMPT_PRESETS.get("Свой промт", "")
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
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.warning("Загрузите фото!")

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
