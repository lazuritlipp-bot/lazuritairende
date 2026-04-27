import base64
import requests
import streamlit as st

try:
    from st_clickable_images import clickable_images
except Exception:
    clickable_images = None


# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"

LOGO_PATH = "logo2.png"

# ваши PNG-иконки (файлы должны лежать рядом с .py)
ICON_FILES = {
    "Вечер": "vecher.png",
    "Аксессуары": "acsesoar.png",
    "Дневной свет": "den.png",
    "Студийный свет": "studio.png",
    "Свой промт": "svoi.png",
}

ICON_ORDER = ["Дневной свет", "Студийный свет", "Вечер", "Аксессуары", "Свой промт"]


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


# --- HELPERS ---
def file_to_b64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def file_to_data_url(path: str) -> str:
    b64 = file_to_b64(path)
    if not b64:
        return ""
    # все ваши кнопки/лого — png
    return f"data:image/png;base64,{b64}"


def image_bytes_to_b64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def process_image(img_b64: str, user_prompt: str, mime: str = "image/jpeg"):
    combined_input = f"{user_prompt}|||data:{mime};base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "x-api-key": APPLICATION_TOKEN,
        "Content-Type": "application/json",
    }
    return requests.post(BASE_URL, json=payload, headers=headers).json()


# --- ИНТЕРФЕЙС И СТИЛИ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

st.markdown(
    """
<style>
/* Основной фон */
.stApp { background-color: #E8E8E1; }

/* Отступ сверху */
.block-container { padding-top: 1rem !important; }

/* Шапка */
.custom-header {
    background-color: white;
    padding: 12px 25px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
    border: 1px solid #D1D1D1;
}

/* Лого */
.header-logo {
    height: 70px !important;
    width: auto !important;
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

/* Черный цвет для заголовков карточек */
.card > b { color: #000000 !important; }

/* Главная кнопка */
div.stButton > button:first-child[kind="primary"] {
    background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
    color: white !important;
    border: none !important;
    height: 55px !important;
    font-size: 18px !important;
    font-weight: bold !important;
}

/* Пустой блок результата */
.empty-result-card {
    height: 600px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #888;
    border: 2px dashed #CCC;
}

/* (на всякий) убираем лишние отступы у clickable_images контейнера */
.iconbar-wrap { margin-top: 8px; margin-bottom: 6px; }
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
    "High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. "
    "Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, "
    "Architectural Digest style. Masterpiece, 8k resolution, photorealistic interior photography. Completely re-texture all surfaces "
    "using high-end materials (marble, brushed metal, grain wood). Replace flat CG lighting with realistic global illumination and dramatic "
    "cinematic shadows. Add subtle natural sunlight from windows. Architectural Digest style, sharp focus, volumetric fog, ray-traced reflections. "
    "NO 3D render look, NO flat textures."
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

# --- STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "Базовый промт"
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = PROMPT_PRESETS["Базовый промт"]
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = ""


def apply_preset(preset_name: str):
    st.session_state.selected_preset = preset_name
    if preset_name == "Свой промт":
        st.session_state.prompt_text = st.session_state.custom_prompt
    else:
        st.session_state.prompt_text = PROMPT_PRESETS.get(preset_name, st.session_state.prompt_text)


def on_prompt_change():
    # сохраняем пользовательский текст, если выбран "Свой промт"
    if st.session_state.selected_preset == "Свой промт":
        st.session_state.custom_prompt = st.session_state.prompt_text


# --- ШАПКА ---
logo_data_url = file_to_data_url(LOGO_PATH)
st.markdown(
    f"""
<div class="custom-header">
    <div style="color:#444; font-size:18px;">
        <b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render
    </div>
    {"<img src='" + logo_data_url + "' class='header-logo'>" if logo_data_url else ""}
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

    # --- ИКОН-КНОПКИ (PNG) ---
    icon_urls = [file_to_data_url(ICON_FILES[name]) for name in ICON_ORDER]

    if clickable_images is None:
        st.warning("Не установлена библиотека st-clickable-images. Добавьте её в requirements.txt")
        # fallback: обычные кнопки
        btn_cols = st.columns(2)
        for i, preset_name in enumerate(ICON_ORDER):
            if btn_cols[i % 2].button(preset_name, use_container_width=True):
                apply_preset(preset_name)
                st.rerun()
    else:
        st.markdown('<div class="iconbar-wrap">', unsafe_allow_html=True)
        clicked = clickable_images(
            icon_urls,
            titles=ICON_ORDER,  # tooltip в браузере
            div_style="""
                display: flex;
                gap: 12px;
                align-items: center;
                justify-content: flex-start;
                flex-wrap: wrap;
            """,
            img_style="""
                width: 54px;
                height: 54px;
                padding: 12px;

                border-radius: 14px;
                background: #EFEFEF;
                border: 1px solid rgba(0,0,0,0.06);

                box-shadow:
                    6px 6px 14px rgba(0,0,0,0.18),
                    -6px -6px 14px rgba(255,255,255,0.85);

                object-fit: contain;
                cursor: pointer;
            """,
            key="preset_icons",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if clicked > -1:
            apply_preset(ICON_ORDER[clicked])
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.text_area(
        "ТЗ промпта:",
        key="prompt_text",
        height=200,
        on_change=on_prompt_change,
    )

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    mime = getattr(f, "type", None) or "image/jpeg"
                    img_b64 = image_bytes_to_b64(f.read())

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
        else:
            st.warning("Загрузите фото!")

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
