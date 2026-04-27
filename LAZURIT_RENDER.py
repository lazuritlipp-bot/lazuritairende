import streamlit as st
import requests
import base64
from streamlit_image_select import image_select

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"
BACKGROUND_PATH = "background.png"
MAX_HISTORY = 10

# --- КЭШИРОВАНИЕ РЕСУРСОВ ---
@st.cache_data
def read_file_b64(path):
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except Exception:
        return ""


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
    "Свой промпт": "",
}
PRESET_NAMES = list(PROMPT_PRESETS.keys())[:-1]  # без «Свой промпт»
PRESET_ICONS = [
    "icons/studio.png",
    "icons/den.png",
    "icons/vecher.png",
    "icons/acsesoar.png",
]


# --- СИСТЕМА АВТОРИЗАЦИИ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if st.session_state.authenticated:
        return

    bg_b64 = read_file_b64(BACKGROUND_PATH)
    logo_b64 = read_file_b64(LOGO_PATH)
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
        header {{ display: none !important; }}

        .stApp {{ {bg_css} }}

        .block-container {{
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
        }}

        /* ---------- КАРТОЧКА ЛОГИНА ---------- */
        div[data-testid="stForm"] {{
            position: fixed;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 420px; max-width: 92vw;
            height: auto !important; min-height: 0 !important;
            background: rgba(30, 30, 32, 0.82) !important;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-radius: 22px;
            padding: 28px 32px 24px !important;
            box-shadow: 0 24px 70px rgba(0,0,0,0.55);
            border: 1px solid rgba(255,255,255,0.08) !important;
            z-index: 9999;
        }}
        div[data-testid="stForm"] > div,
        div[data-testid="stForm"] [data-testid="stVerticalBlock"] {{
            height: auto !important; min-height: 0 !important;
            gap: 0.6rem !important;
        }}
        div[data-testid="stForm"] label {{
            color: #FFF !important; font-weight: 500; font-size: 14px;
        }}
        div[data-testid="stForm"] [data-testid="stTextInput"] > div {{
            background: transparent !important; border: none !important;
        }}
        div[data-testid="stForm"] input {{
            background: rgba(255,255,255,0.06) !important;
            color: #FFF !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 10px !important;
            height: 46px !important; padding: 0 14px !important;
        }}
        div[data-testid="stForm"] input::placeholder {{
            color: rgba(255,255,255,0.45) !important;
        }}
        /* Иконка «глаз» внутри инпута */
        div[data-testid="stForm"] [data-testid="stTextInput"] button {{
            background: transparent !important;
            color: rgba(255,255,255,0.7) !important;
            border: none !important; box-shadow: none !important;
            width: auto !important; height: auto !important;
            padding: 0 8px !important;
        }}
        div[data-testid="stForm"] [data-testid="stTextInput"] button:hover {{
            background: rgba(255,255,255,0.06) !important; color: #FFF !important;
        }}
        /* Кнопка «Войти» */
        div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
            color: #FFF !important; border: none !important;
            height: 50px !important; font-weight: 600 !important;
            font-size: 16px !important; border-radius: 10px !important;
            width: 100%; margin-top: 6px;
        }}

        .login-logo {{
            display: block; margin: 0 auto 14px;
            width: 78%; max-width: 320px;
        }}
        .login-subtitle {{
            color: rgba(255,255,255,0.85);
            text-align: center; font-size: 14px; margin: 0 0 22px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        if logo_b64:
            st.markdown(
                f"<img class='login-logo' src='data:image/png;base64,{logo_b64}' alt='LAZURIT'/>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<h2 style='color:#FFF;text-align:center;margin:0 0 12px;'>LAZURIT</h2>",
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
                info = users_data[pwd]
                st.session_state.authenticated = True
                st.session_state.user_role = info.get("name", "Сотрудник")
                st.session_state.user_api_key = info.get("key", "")
                st.rerun()
            else:
                st.error("❌ Код не опознан")
    st.stop()


# --- HELPERS ---
def image_to_base64(raw_bytes: bytes) -> str:
    return base64.b64encode(raw_bytes).decode()


def extract_image_bytes(response: dict) -> bytes:
    """Безопасно извлекает картинку из ответа API."""
    try:
        msg = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Неожиданный формат ответа: {exc}\n{response}")

    raw = msg.split("|||", 1)[1] if "|||" in msg else msg
    raw = raw.split("base64,", 1)[1] if "base64," in raw else raw
    raw = raw.replace('"', "").strip()

    try:
        return base64.b64decode(raw)
    except Exception as exc:
        raise ValueError(f"Не удалось декодировать base64: {exc}")


def process_image(img_b64: str, user_prompt: str, mime: str = "image/jpeg") -> dict:
    combined = f"{user_prompt}|||data:{mime};base64,{img_b64}"
    payload = {
        "input_value": combined,
        "output_type": "chat",
        "input_type": "chat",
    }
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json",
    }
    resp = requests.post(BASE_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()


# ================================================================
#  ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ================================================================
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()

APPLICATION_TOKEN = st.session_state.user_api_key
if not APPLICATION_TOKEN:
    st.error("Для вашей учётной записи не задан API-ключ. Обратитесь к администратору.")
    st.stop()

# --- INIT STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = PROMPT_PRESETS["Студия"]
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "_preset_idx" not in st.session_state:
    st.session_state._preset_idx = 0

# --- СТИЛИ РАБОЧЕЙ ОБЛАСТИ ---
st.markdown("""
    <style>
    .stApp { background-color: #E8E8E1; }
    .block-container {
        padding-top: 1rem !important;
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
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
    .header-logo {
        height: 120px !important;
        width: auto !important;
        max-width: 300px;
        object-fit: contain;
    }
    .card {
        background-color: #F8F9FA;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #E0E0E0;
        margin-bottom: 15px;
    }
    .card > b { color: #000 !important; }
    div.stButton > button:first-child[kind="primary"] {
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important; border: none !important;
        height: 55px !important; font-size: 18px !important;
        font-weight: bold !important;
    }
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

# --- ШАПКА ---
logo_b64 = read_file_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color:#444;font-size:18px;">
            <b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render
        </div>
        {'<img src="data:image/png;base64,' + logo_b64 + '" class="header-logo">' if logo_b64 else ''}
    </div>
    """, unsafe_allow_html=True)

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([2.2, 2.2, 0.6])

# -------- ЛЕВАЯ КОЛОНКА --------
with col_left:
    # 1. Загрузка
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    uploaded = st.file_uploader("upload", label_visibility="collapsed")
    if uploaded:
        st.image(uploaded, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Освещение / пресеты
    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

    selected_idx = image_select(
        label="",
        images=PRESET_ICONS,
        captions=PRESET_NAMES,
        use_container_width=False,
        return_value="index",
        key="preset_image_select",
    )

    if selected_idx is not None and st.session_state._preset_idx != selected_idx:
        st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[selected_idx]]
        st.session_state._preset_idx = selected_idx
        st.rerun()

    if st.button("Свой промпт", key="custom_prompt_btn", use_container_width=True):
        st.session_state.prompt_text = ""
        st.session_state._preset_idx = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Текст промпта
    user_text = st.text_area("ТЗ промпта:", key="prompt_text", height=200)

    # 4. Генерация
    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if not uploaded:
            st.warning("Загрузите фото!")
        else:
            with st.spinner("Генерация..."):
                try:
                    uploaded.seek(0)
                    file_bytes = uploaded.read()
                    mime = uploaded.type or "image/jpeg"

                    res = process_image(image_to_base64(file_bytes), user_text, mime=mime)
                    st.session_state.last_response = str(res)

                    img_bytes = extract_image_bytes(res)
                    st.session_state.history.insert(0, img_bytes)
                    st.session_state.history = st.session_state.history[:MAX_HISTORY]
                    st.rerun()
                except requests.exceptions.RequestException as exc:
                    st.error(f"Ошибка сети: {exc}")
                except ValueError as exc:
                    st.error(f"Ошибка обработки ответа: {exc}")
                except Exception as exc:
                    st.error(f"Непредвиденная ошибка: {exc}")

# -------- ЦЕНТРАЛЬНАЯ КОЛОНКА --------
with col_main:
    if st.session_state.history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="card empty-result-card">
                <h1 style="color:#bbb;font-weight:bold;">Результат генерации</h1>
                <p style="color:#ccc;">Загрузите изображение для начала работы</p>
            </div>
        """, unsafe_allow_html=True)

# -------- ПРАВАЯ КОЛОНКА (ИСТОРИЯ) --------
with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)

# --- ЛОГ ---
if st.session_state.last_response:
    with st.expander("🛠 Лог ответа API"):
        st.text(st.session_state.last_response)

# --- КНОПКА ВЫХОДА ---
with st.sidebar:
    if st.button("🚪 Выйти"):
        for key in ["authenticated", "user_role", "user_api_key", "history",
                     "prompt_text", "last_response", "_preset_idx"]:
            st.session_state.pop(key, None)
        st.rerun()
