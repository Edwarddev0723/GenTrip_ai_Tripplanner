import streamlit as st
import os
import json
import datetime
from streamlit_navigation_bar import st_navbar
import webbrowser
st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
styles = {
    "nav": {
        "background-color": "rgb(221, 160, 105)",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(49, 51, 63)",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}
pages = ["首頁", "AI旅遊規劃", "旅平險計算", "AI旅遊記帳", "我的行程"]

urls = {"AI旅遊規劃": "http://localhost:8501/",
        "首頁":"http://localhost:8501/main_page",
        "AI旅遊記帳":"http://localhost:8501/budget_manager",
        "旅平險計算":"http://localhost:8501/insurance",
        "我的行程":"http://localhost:8501/Edit_Trip"}
options = {
    #"show_menu": False,
    "show_sidebar": False,
}
parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "images/GENTRIPLOGO_svg.svg")
page = st_navbar(
    pages,
    logo_path=logo_path,
    urls=urls,
    styles=styles,
    options=options,
)
def load_data():
    # 檢查是否存在 data.json 檔案
    if os.path.exists("data.json"):
        # 如果存在,就讀取資料
        with open("data.json", "r") as f:
            data = json.load(f)
            # 如果資料是列表且不為空,我們取列表中的最後一個元素作為字典
            if isinstance(data, list) and len(data) > 0:
                data = data[-1]
            else:
                data = {}
        return data
    else:
        # 如果不存在,就返回空字典
        return {}

def open_page(url):
    open_script= """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    st.html(open_script)

data = load_data()
st.image('http://127.0.0.1:5000/images/insurance_BG.png', use_column_width=True)
# 標題
st.title("旅平險計算")
st.subheader("隨時報價,即時投保,簡單方步驟立即完成!")

# 表單欄位
with st.form("booking_form"):
    # 讀取已儲存的資料
    data = load_data()

    # 旅遊地區
    col9, col10 = st.columns(2)
    with col9:
        destination = st.selectbox("旅遊地區/地區(最多可選擇五個)", ["海外地區", "國內(限台澎金馬地區)"], index=0 if data.get("destination") == "國內(限台澎金馬地區)" else 1)
        de_name = st.text_input("旅遊城市", value=data['city'])
    with col10:
        departure_date = st.date_input("出發日期", value=datetime.date.fromisoformat(data['start_date']), min_value=None, max_value=None)
        end_date = st.date_input("結束日期", value=datetime.date.fromisoformat(data['end_date']), min_value=None, max_value=None)
    # 出發時間
    departure_time = st.time_input("出發時間")

    # 預訂按鈕
    submit_button = st.form_submit_button("🧮保費計算", use_container_width=True)

    # 處理表單提交
    if submit_button:
        days = (end_date - departure_date).days
        # 定義保費計算規則
        base_fee = 300  # 基本保費
        domestic_rate = 0.1  # 國內旅遊每天保費比率
        overseas_rate = 0.2  # 海外旅遊每天保費比率

        # 計算保費
        if destination == "國內(限台澎金馬地區)":
            fee = base_fee + days * domestic_rate * base_fee
        else:
            fee = base_fee + days * overseas_rate * base_fee
if submit_button:
    card_html = """
    <style>
    .card {
        border: 2px solid #eee;
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .value {
        font-size: 16px;
        color: #333;
    }
    </style>
    """


    # Function to create a card
    def create_card(title, value):
        return f"""
        <div class="card">
            <div class="title">{title}</div>
            <div class="value">{value}萬元</div>
        </div>
        """


    # Start a form with a unique key
    with st.form(key='my_form'):
        st.markdown(card_html, unsafe_allow_html=True)  # Apply CSS globally
        st.subheader('新光產物 - 國內基本型')

        # Row 1
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(create_card("身份安全保險金額", "500"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_card("網絡技術責任保險金額", "10"), unsafe_allow_html=True)

        # Row 2
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(create_card("專家費用賠償保險金額", "1"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_card("儲備媒體責任保險金額", "50"), unsafe_allow_html=True)

        # Row 3
        col5, col6 = st.columns(2)
        with col5:
            st.markdown(create_card("個人責任保險", "25"), unsafe_allow_html=True)
        with col6:
            st.markdown(create_card("專家諮詢費責任保險金額", "1"), unsafe_allow_html=True)

        # Submit button at the bottom

        st.markdown("""
        <style>
        .custom-header {
            font-size: 24px;
            color: #4a4a4a;
            font-weight: bold;
            padding: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        col7, col8 = st.columns([2, 1])
        with col7:
            st.markdown(f"<div class='custom-header'>共投保{days}天保費 NT${fee:.2f}</div>", unsafe_allow_html=True)
        with col8:
            st.form_submit_button("立即購買", use_container_width=True, on_click=open_page('https://www.sk858.com.tw/Products/ta/ski-travel-insurance'))



