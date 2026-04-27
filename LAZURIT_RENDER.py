import streamlit as st
import requests
import base64
from pathlib import Path

from st_clickable_images import clickable_images


# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"

ROOT = Path.cwd()  # на Streamlit Cloud это обычно корень репозитория
LOGO_PATH = ROOT / "logo2.png"

# Название -> (файл, добавка к промпту)
BUTTON_CONFIG = {
    "Дневной": ("den.png", "Natural bright daylight from windows, soft sun rays."),
    "Студийный": ("studio.png", "Professional architectural studio lighting, balanced fills."),
    "Вечерний": ("vecher.png", "Warm cozy evening light, mix of interior lamps and dusk."),
    "Аксессуары": ("acsesoar.png", "Add premium accessories and decor, lived-in details, stylish props."),
    "Свой": ("svoi.png", ""),
}
BUTTON_ORDER = ["Дневной", "Студийный", "Вечерний", "Аксессуары", "Свой"]


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_base64_image(path: Path) -> str:
    try:
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        return ""


def img_to_data_url(path: Path) -> str:
    b64 = get_base64_image(path)
    if not b64:
        return ""
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def process_image(img_b64: str, user_prompt: str, mime: str):
    combined_input = f"{user_prompt}|||data:{mime};base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json",
    }
    return requests.post(BASE_URL, json=payload, headers=headers).json()


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

st.markdown(
    """
<style>
.stApp { background-color: #E8E8E1; }
.block-container { padding-top: 1rem !important; }

.custom-header{
    background-color: white;
    padding: 10px 30px;
    border-radius: 12px;
    display:flex;
    justify-content: space-between;
    align-items:center;
    margin-bottom: 20px;
    border: 1px solid #D1D1D1;
    min-height: 90px;
}
.header-logo{
    height: 90px !important;
    width: auto !important;
    object-fit: contain;
}

.card{
    background-color: #F8F9FA;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #E0E0E0;
    margin-bottom: 15px;
}
.card > b{
    color:#000 !important;
    display:block;
    margin-bottom: 12px;
}

div.stButton > button:first-child[kind="primary"]{
    background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
    color: white !important;
    border: none !important;
    height: 55px !important;
    font-size: 18px !important;
    font-weight: bold !important;
}

.empty-result-card{
    height: 600px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    color:#888;
    border:2px dashed #CCC;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- ДАННЫЕ ---
BASE_PHOTO_PROMPT = (
    "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
    "Maintain the original color palette and materials of the furniture strictly. Enhance existing textures "
    "(wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic "
    "studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. "
    "High-contrast, sharp details, realistic reflections on surfaces. Ensure 100% photorealism, Architectural Digest style."
)

# --- STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = BASE_PHOTO_PROMPT
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "Дневной"
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = ""


# --- ШАПКА ---
logo_url = img_to_data_url(LOGO_PATH)
st.markdown(
    f"""
<div class="custom-header">
  <div style="color:#444; font-size:18px;">
    <b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render
  </div>
  {"<img src='" + logo_url + "' class='header-logo'>" if logo_url else ""}
</div>
""",
    unsafe_allow_html=True,
)

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([1.2, 2.5, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f:
        st.image(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

    # --- ИКОНКИ-ПЛИТКИ ---
    missing = []
    icon_urls = []
    for name in BUTTON_ORDER:
        filename, _ = BUTTON_CONFIG[name]
        p = ROOT / filename
        if not p.exists():
            missing.append(filename)
            icon_urls.append("")
        else:
            icon_urls.append(img_to_data_url(p))

    if missing:
        st.error("Не найдены файлы: " + ", ".join(missing))
        st.caption(f"Проверка пути: ROOT = {ROOT}")
    else:
        clicked = clickable_images(
            icon_urls,
            titles=BUTTON_ORDER,
            div_style="""
                display:flex;
                gap:14px;
                align-items:center;
                justify-content:flex-start;
                flex-wrap:wrap;
                margin-top:6px;
                margin-bottom:8px;
            """,
            img_style="""
                width:72px;
                height:72px;
                box-sizing:border-box;
                padding:14px;

                background:#F2F2F2;
                border-radius:16px;
                border:1px solid rgba(0,0,0,0.06);

                box-shadow:
                    6px 6px 14px rgba(0,0,0,0.18),
                    -6px -6px 14px rgba(255,255,255,0.90);

                object-fit:contain;
                cursor:pointer;
            """,
            key="light_icons",
        )

        if clicked > -1:
            mode = BUTTON_ORDER[clicked]
            st.session_state.selected_mode = mode

            _, add_text = BUTTON_CONFIG[mode]
            if mode == "Свой":
                st.session_state.current_prompt = st.session_state.custom_prompt
            else:
                st.session_state.current_prompt = f"{add_text} {BASE_PHOTO_PROMPT}".strip()

            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=200)

    # сохраняем "Свой"
    if st.session_state.selected_mode == "Свой":
        st.session_state.custom_prompt = user_text

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if not f:
            st.warning("Загрузите фото!")
        else:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    mime = getattr(f, "type", None) or "image/jpeg"
                    img_b64 = image_to_base64(f.read())

                    res = process_image(img_b64, user_text, mime=mime)

                    if "outputs" in res:
                        msg = res["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                        st.session_state.last_response = msg

                        raw_data = msg.split("|||")[1] if "|||" in msg else msg
                        if "base64," in raw_data:
                            raw_data = raw_data.split("base64,")[1]

                        img_bytes = base64.b64decode(raw_data.replace('"', "").strip())
                        st.session_state.history.insert(0, img_bytes)
                        st.rerun()
                    else:
                        st.error(f"Неожиданный ответ API: {res}")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with col_main:
    if st.session_state.history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
<div class="card empty-result-card">
  <h1 style="color:#bbb; font-weight:bold;">Результат генерации</h1>
  <p style="color:#ccc;">Загрузите изображение для начала работы</p>
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
