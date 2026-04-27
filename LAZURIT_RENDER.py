# -*- coding: utf-8 -*-

import base64
from pathlib import Path

import requests
import streamlit as st

BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT / "logo2.png"

ICON_FILES = {
    "Базовый": None,
    "Свой": "svoi.png",
    "Дневной": "den.png",
    "Студия": "studio.png",
    "Вечер": "vecher.png",
    "Аксессуары": "acsesoar.png",
}

ICON_ORDER = ["Дневной", "Студия", "Вечер", "Аксессуары", "Свой"]


def file_to_b64(path: Path) -> str:
    try:
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        return ""


def file_to_data_url(path: Path) -> str:
    b64 = file_to_b64(path)
    if not b64:
        return ""
    suf = path.suffix.lower()
    mime = "image/png" if suf == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def get_query_param(name: str):
    try:
        v = st.query_params.get(name)
        if isinstance(v, list):
            return v[0] if v else None
        return v
    except Exception:
        return st.experimental_get_query_params().get(name, [None])[0]


def clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        st.experimental_set_query_params()


def get_app_root() -> str:
    base_path = ""
    try:
        base_path = st.get_option("server.baseUrlPath") or ""
    except Exception:
        base_path = ""

    if base_path and not base_path.startswith("/"):
        base_path = "/" + base_path
    if not base_path:
        base_path = "/"
    if not base_path.endswith("/"):
        base_path += "/"
    return base_path


def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        st.markdown("<style>.stApp{background-color:#0E1117;}</style>", unsafe_allow_html=True)
        st.sidebar.title("LAZURIT AI Render")
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
                st.sidebar.error("Код не опознан")
        st.stop()


def process_image(img_b64: str, user_prompt: str, mime: str):
    combined_input = f"{user_prompt}|||data:{mime};base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json",
    }
    return requests.post(BASE_URL, json=payload, headers=headers).json()


def set_preset(preset_name: str, PROMPT_PRESETS: dict):
    st.session_state.selected_preset = preset_name
    if preset_name == "Свой":
        st.session_state.prompt_text = st.session_state.custom_prompt
    else:
        st.session_state.prompt_text = PROMPT_PRESETS.get(preset_name, st.session_state.prompt_text)


def on_prompt_change():
    if st.session_state.selected_preset == "Свой":
        st.session_state.custom_prompt = st.session_state.prompt_text


st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key
APP_ROOT = get_app_root()

BASE_PHOTO_PROMPT = (
    "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
    "Maintain the original color palette and materials of the furniture strictly. Enhance existing textures "
    "(wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic "
    "studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. "
    "High-contrast, sharp details, realistic reflections on surfaces. Ensure 100% photorealism, Architectural Digest style."
)

PROMPT_PRESETS = {
    "Базовый": f"{BASE_PHOTO_PROMPT}",
    "Свой": "",
    "Дневной": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Студия": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Аксессуары": (
        "Add tasteful accessories and decor (plants, vases, books, artworks, textiles), make the interior look lived-in and premium. "
        "Do NOT change the furniture design or layout. "
        f"{BASE_PHOTO_PROMPT}"
    ),
}

if "history" not in st.session_state:
    st.session_state.history = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "Базовый"
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = ""
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = PROMPT_PRESETS["Базовый"]

st.markdown(
    """
<style>
.stApp { background-color: #E8E8E1; }
.block-container { padding-top: 1rem !important; }

.custom-header {
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
.header-logo {
    height: 90px !important;
    width: auto !important;
    object-fit: contain;
}

.card {
    background-color: #F8F9FA;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #E0E0E0;
    margin-bottom: 15px;
}
.card > b {
    color:#000 !important;
    display:block;
    margin-bottom: 12px;
}

div.stButton > button:first-child[kind="primary"] {
    background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
    color: white !important;
    border: none !important;
    height: 55px !important;
    font-size: 18px !important;
    font-weight: bold !important;
}

.empty-result-card {
    height: 600px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    color:#888;
    border:2px dashed #CCC;
}

/* Панель икон-кнопок */
.icon-grid {
    display: grid;
    grid-template-columns: repeat(3, 82px);
    gap: 14px;
    margin-top: 6px;
    margin-bottom: 10px;
}

.icon-btn {
    width: 82px;
    height: 82px;
    border-radius: 18px;
    background: #F2F2F2;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow:
        6px 6px 14px rgba(0,0,0,0.18),
        -6px -6px 14px rgba(255,255,255,0.90);
    display:flex;
    align-items:center;
    justify-content:center;
    text-decoration:none;
    user-select:none;
    -webkit-tap-highlight-color: transparent;
}

.icon-btn img {
    width: 56px;
    height: 56px;
    object-fit: contain;
    display:block;
}

/* Не нужно сейчас (заглушено)
.icon-btn:hover { transform: translateY(-1px); }
.icon-btn:active { transform: scale(0.98); }
.icon-btn.active { outline: 3px solid rgba(167,139,250,0.55); }
*/
</style>
""",
    unsafe_allow_html=True,
)

clicked = get_query_param("preset")
if clicked:
    code_to_preset = {
        "den": "Дневной",
        "studio": "Студия",
        "vecher": "Вечер",
        "acsesoar": "Аксессуары",
        "svoi": "Свой",
        "base": "Базовый",
    }
    preset_name = code_to_preset.get(clicked)
    if preset_name:
        set_preset(preset_name, PROMPT_PRESETS)
    clear_query_params()

logo_url = file_to_data_url(LOGO_PATH)
logo_img = f"<img src='{logo_url}' class='header-logo' />" if logo_url else ""
st.markdown(
    "<div class='custom-header'>"
    f"<div style='color:#444; font-size:18px;'><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>"
    f"{logo_img}"
    "</div>",
    unsafe_allow_html=True,
)

col_left, col_main, col_hist = st.columns([1.2, 2.5, 0.6])

with col_left:
    st.markdown("<div class='card'><b>1. Загрузка</b>", unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f:
        st.image(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><b>2. Освещение</b>", unsafe_allow_html=True)

    missing = []
    tiles = []

    preset_to_code = {
        "Дневной": "den",
        "Студия": "studio",
        "Вечер": "vecher",
        "Аксессуары": "acsesoar",
        "Свой": "svoi",
        "Базовый": "base",
    }

    for preset_name in ICON_ORDER:
        icon_file = ICON_FILES.get(preset_name)
        if not icon_file:
            continue

        icon_path = ROOT / icon_file
        if not icon_path.exists():
            missing.append(icon_file)
            continue

        icon_url = file_to_data_url(icon_path)
        code = preset_to_code[preset_name]

        # КЛЮЧЕВОЕ: target="_self" чтобы не открывалась новая вкладка
        tiles.append(
            f'<a class="icon-btn" target="_self" href="{APP_ROOT}?preset={code}" title="{preset_name}">'
            f'<img src="{icon_url}" alt="{preset_name}"></a>'
        )

    if missing:
        st.error("Не найдены файлы: " + ", ".join(missing))
        st.caption(f"Папка приложения: {ROOT}")
    else:
        st.markdown('<div class="icon-grid">' + "".join(tiles) + "</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.text_area("ТЗ промпта:", key="prompt_text", height=200, on_change=on_prompt_change)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if not f:
            st.warning("Загрузите фото!")
        else:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    mime = getattr(f, "type", None) or "image/jpeg"
                    img_b64 = image_to_base64(f.read())

                    res = process_image(img_b64, st.session_state.prompt_text, mime=mime)

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
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='card empty-result-card'>"
            "<h1 style='color:#bbb; font-weight:bold;'>Результат генерации</h1>"
            "<p style='color:#ccc;'>Загрузите изображение для начала работы</p>"
            "</div>",
            unsafe_allow_html=True,
        )

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)

if st.session_state.last_response:
    with st.expander("Лог"):
        st.text(st.session_state.last_response)
