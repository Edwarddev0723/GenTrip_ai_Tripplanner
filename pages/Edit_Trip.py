import json
import os
import re
import pandas as pd
import streamlit
import streamlit as st
import streamlit.components.v1 as components
from streamlit_carousel import carousel
from PIL import Image
import time
from streamlit_navigation_bar import st_navbar
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

def extract_number_from_string(s):
    s = str(s)  # Convert input to string to avoid TypeError
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")
with open('user_log.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
st.image('http://127.0.0.1:5000/images/edit_bg.png', use_column_width=True)
# 获取 ID 并显示
id_list = [data['id']]
with st.form(key='my_form'):
    select = st.selectbox(label='選擇你想編輯的行程', options=id_list)
    send_button = st.form_submit_button('送出')

if send_button:
    if data['id'] == f'{select}':
        days_data = data['days']
        activities = []
        total_charge = 0
        for day in data['days']:
            for activity in day['activities']:
                day_n = day['day']
                if activity['start_time'][:2] == '10':
                    activity['order'] = f'第{day_n}天早上'
                elif activity['start_time'][:2] == '12':
                    activity['order'] = f'第{day_n}天中午午餐'
                elif activity['start_time'][:2] == '2:' or activity['start_time'][:2] == '02':
                    activity['order'] = f'第{day_n}天下午'
                elif activity['start_time'][:2] == '6:' or activity['start_time'][:2] == '06':
                    activity['order'] = f'第{day_n}天晚上晚餐'
                elif activity['start_time'][:2] == '8:' or activity['start_time'][:2] == '08':
                    activity['order'] = f'第{day_n}天住宿'
                else:
                    activity['order'] = f'第{day_n}特殊行程'
                charge = extract_number_from_string(activity["charge"])
                total_charge += int(charge) if charge else 0

                activities.append(activity)
        df = pd.DataFrame(activities)
        df = df[['order', 'start_time', 'title', 'description', 'link', 'charge']]
        df.assign(Name='order')
        edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
        csv = convert_df(edited_df)
        st.download_button(
            label="下載行程",
            data=csv,
            file_name=f"GenTrip{select}.csv",
            mime="text/csv",
        )

        st.markdown(
            f"""
                    <style>
                        .container {{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-top: 10px;
                        }}
                        .total-charge {{
                            font-size: 24px;
                            color: #4CAF50;
                            font-weight: bold;
                        }}
                        .page-link a {{
                            font-size: 18px;
                            color: #1E90FF;
                            font-weight: bold;
                            text-decoration: none;
                        }}
                    </style>
                    <div class="container">
                        <div class="total-charge">
                            總預算: {total_charge}元
                        </div>
                        <div class="page-link">
                            <a href="insurance" target="_blank">點我線上投保 💼</a>
                        </div>
                    </div>
                    """,
            unsafe_allow_html=True
        )

