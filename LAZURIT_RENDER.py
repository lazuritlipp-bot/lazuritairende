import streamlit as st
import requests
import base64
from pathlib import Path

--- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"

ROOT = Path(file).resolve().parent
LOGO_PATH = ROOT / "logo2.png"

preset_code -> (label, icon_file, prompt_addition)
BUTTONS = {
"den": ("Дневной", "den.png", "Natural bright daylight from windows, soft sun rays."),
"studio": ("Студийный", "studio.png", "Professional architectural studio lighting, balanced fills."),
"vecher": ("Вечерний", "vecher.png", "Warm cozy evening light, mix of interior lamps and dusk."),
"acsesoar": ("Аксессуары", "acsesoar.png", "Add premium accessories and decor, lived-in details, stylish props."),
"svoi": ("Свой", "svoi.png", ""),
}
BUTTON_ORDER = ["den", "studio", "vecher", "acsesoar", "svoi"]

--- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
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

def get_query_param(name: str):
# Streamlit new API
try:
v = st.query_params.get(name)
if isinstance(v, list):
return v[0] if v else None
return v
except Exception:
# Streamlit old API
return st.experimental_get_query_params().get(name, [None])[0]

def clear_query_params():
try:
st.query_params.clear()
except Exception:
st.experimental_set_query_params()

def image_to_base64(image_bytes: bytes) -> str:
return base64.b64encode(image_bytes).decode("utf-8")

--- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
if "authenticated" not in st.session_state:
st.session_state.authenticated = False
st.session_state.user_role = ""
st.session_state.user_api_key = ""

text

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
def process_image(img_b64: str, user_prompt: str, mime: str):
combined_input = f"{user_prompt}|||data:{mime};base64,{img_b64}"
payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
headers = {
"Authorization": f"Bearer {APPLICATION_TOKEN}",
"x-api-key": APPLICATION_TOKEN,
"Content-Type": "application/json",
}
return requests.post(BASE_URL, json=payload, headers=headers).json()

--- ИНТЕРФЕЙС И СТИЛИ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

st.markdown(
"""

<style> .stApp { background-color: #E8E8E1; } .block-container { padding-top: 1rem !important; } .custom-header{ background-color: white; padding: 10px 30px; border-radius: 12px; display:flex; justify-content: space-between; align-items:center; margin-bottom: 20px; border: 1px solid #D1D1D1; min-height: 90px; } .header-logo{ height: 90px !important; width: auto !important; object-fit: contain; } .card{ background-color: #F8F9FA; border-radius: 15px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; } .card > b{ color:#000 !important; display:block; margin-bottom: 12px; } /* Главная кнопка */ div.stButton > button:first-child[kind="primary"]{ background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; color: white !important; border: none !important; height: 55px !important; font-size: 18px !important; font-weight: bold !important; } /* Пустой блок результата */ .empty-result-card{ height: 600px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#888; border:2px dashed #CCC; } /* --- ИКОНКИ-ПЛИТКИ --- */ .icon-grid{ display: grid; grid-template-columns: repeat(3, 82px); gap: 14px; margin-top: 6px; margin-bottom: 10px; } .icon-btn{ width: 82px; height: 82px; border-radius: 18px; background: #F2F2F2; border: 1px solid rgba(0,0,0,0.06); box-shadow: 6px 6px 14px rgba(0,0,0,0.18), -6px -6px 14px rgba(255,255,255,0.90); display:flex; align-items:center; justify-content:center; text-decoration:none; user-select:none; -webkit-tap-highlight-color: transparent; } .icon-btn:hover{ transform: translateY(-1px); box-shadow: 8px 8px 18px rgba(0,0,0,0.20), -8px -8px 18px rgba(255,255,255,0.92); } .icon-btn:active{ transform: scale(0.98); } .icon-btn.active{ outline: 3px solid rgba(167,139,250,0.55); } .icon-btn img{ width: 56px; height: 56px; object-fit: contain; display:block; } </style>
""",
unsafe_allow_html=True,
)

--- ДАННЫЕ ---
BASE_PHOTO_PROMPT = (
"Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
"Maintain the original color palette and materials of the furniture strictly. Enhance existing textures "
"(wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic "
"studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. "
"High-contrast, sharp details, realistic reflections on surfaces. Ensure 100% photorealism, Architectural Digest style."
)

--- STATE ---
if "history" not in st.session_state:
st.session_state.history = []
if "current_prompt" not in st.session_state:
st.session_state.current_prompt = BASE_PHOTO_PROMPT
if "selected_mode" not in st.session_state:
st.session_state.selected_mode = "den"
if "custom_prompt" not in st.session_state:
st.session_state.custom_prompt = ""
if "last_response" not in st.session_state:
st.session_state.last_response = ""

def apply_mode(mode_code: str):
if mode_code not in BUTTONS:
return
st.session_state.selected_mode = mode_code
_label, _icon, add_text = BUTTONS[mode_code]
if mode_code == "svoi":
st.session_state.current_prompt = st.session_state.custom_prompt
else:
st.session_state.current_prompt = f"{add_text} {BASE_PHOTO_PROMPT}".strip()

--- обработка клика по HTML-плитке через query params ---
clicked_mode = get_query_param("preset")
if clicked_mode:
apply_mode(clicked_mode)
clear_query_params()

--- ШАПКА ---
logo_url = file_to_data_url(LOGO_PATH)
header_html = f"""

<div class="custom-header"> <div style="color:#444; font-size:18px;"> <b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render </div> {"<img src='" + logo_url + "' class='header-logo' />" if logo_url else ""} </div> """ st.markdown(header_html, unsafe_allow_html=True)
--- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([1.2, 2.5, 0.6])

with col_left:
st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
f = st.file_uploader("upload", label_visibility="collapsed")
if f:
st.image(f, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

text

st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

missing = []
tiles = []

for code in BUTTON_ORDER:
    label, icon_file, _add = BUTTONS[code]
    icon_path = ROOT / icon_file

    if not icon_path.exists():
        missing.append(icon_file)
        continue

    icon_url = file_to_data_url(icon_path)
    active_cls = "active" if st.session_state.selected_mode == code else ""

    # без переносов/отступов внутри HTML, чтобы Markdown не превращал в code-block
    tiles.append(
        f'<a class="icon-btn {active_cls}" href="?preset={code}" title="{label}">'
        f'<img src="{icon_url}" alt="{label}"></a>'
    )

if missing:
    st.error("Не найдены файлы: " + ", ".join(missing))
    st.caption(f"Папка приложения: {ROOT}")
else:
    st.markdown('<div class="icon-grid">' + "".join(tiles) + "</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=200)

# сохраняем "Свой"
if st.session_state.selected_mode == "svoi":
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

<div class="card empty-result-card"> <h1 style="color:#bbb; font-weight:bold;">Результат генерации</h1> <p style="color:#ccc;">Загрузите изображение для начала работы</p> </div> """, unsafe_allow_html=True, )
with col_hist:
st.markdown("<b>История</b>", unsafe_allow_html=True)
for img in st.session_state.history[1:6]:
st.image(img, use_container_width=True)

if st.session_state.last_response:
with st.expander("🛠 Лог"):
st.text(st.session_state.last_response)
