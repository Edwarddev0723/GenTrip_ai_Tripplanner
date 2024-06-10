import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
import re
import matplotlib.pyplot as plt
import openai
import json
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
openai.api_key = "Your_OPENAI_API_KEY"
MODEL="gpt-4o"

def plot_expenses(expenses_df):
    fig, ax = plt.subplots()
    expenses_df.plot(kind='bar', x='Date', y='Amount', ax=ax, legend=None)
    ax.set_title('Expenses over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def modify_string(s):
    if not isinstance(s, str):
        try:
            s = s.text
        except AttributeError:
            raise ValueError("Input is not a string and does not have a 'text' attribute")
    if not s.startswith('{') or not s.endswith('}'):
        start_index = s.find('{')
        end_index = s.rfind('}')
        if start_index != -1 and end_index != -1 and start_index < end_index:
            s = s[start_index:end_index + 1]
        else:
            s = ''
    return s

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

st.markdown("""
<style>
div[data-testid="stForm"] {
    width: 100%;  /* 調整表單的寬度 */
}
div[data-testid="stBlock"] {
    width: 100%;  /* 調整表格的寬度 */
}
</style>
""", unsafe_allow_html=True)

st.image("http://127.0.0.1:5000/images/Rectangle 22.jpg", use_column_width=True)

# 初始化一個空的DataFrame用來儲存收據資料
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'place', 'Item', 'Amount'])

with st.form("AI 智慧辨識", clear_on_submit=True):
    image = st.file_uploader("上傳收據照片給AI辨識", type=['jpg', 'jpeg', 'png'])
    submit_button = st.form_submit_button("🧙‍♂️AI辨識")

    if submit_button and image is not None:
        # 讀取並保存圖片
        img_path = f'images/{image.name}'
        base64_image = encode_image(img_path)
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "This is a receipt, and you are a secretary.  Please organize the details from the receipt into JSON format for me. I only need the JSON representation of the receipt data. "},
                {"role": "user", "content": [
                    {"type": "text", "text": "Eventually, I will need to input it into a database with the following structure:Receipt(ReceiptID, PurchaseStore, PurchaseDate, PurchaseAddress, TotalAmount) and Items(ItemID, ReceiptID, ItemName, ItemPrice).Data format as follow:- ReceiptID, using PurchaseDate, but Represent the year, month, day, hour, and minute without any separators.- ItemID, using ReceiptID and sequel number in that receipt. Otherwise, if any information is unclear, fill in with N/A.This is a JSON representation of a receipt.Please translate the Japanese characters into Chinese for me.Using format as follow:japanese(Chinese)All the Chinese will use in zh_tw.Please response with the translated JSON."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]}
            ],
            temperature=.0,
        )
        data_res = response.choices[0].message.content
        modify_str = modify_string(data_res)
        data = json.loads(modify_str)
        receipt_date = data['Receipt']['PurchaseDate']
        receipt_place = data['Receipt']['PurchaseStore']
        items = data['Items']

        # 假设已经有一个DataFrame名为expenses，包含列Date, Item, Amount, Image
        # 如果还没有DataFrame, 请首先创建一个空的DataFrame
        # expenses = pd.DataFrame(columns=['Date', 'Item', 'Amount', 'Image'])

        # 转换JSON数据为DataFrame中的行
        new_rows = [{'Date': receipt_date, 'place' : receipt_place, 'Item': item['ItemName'], 'Amount': item['ItemPrice']} for item in items]

        # 将新数据加入到现有DataFrame中
        expenses = pd.DataFrame(new_rows)
        if 'expenses' in st.session_state:
            st.session_state.expenses = pd.concat([st.session_state.expenses, expenses], ignore_index=True)
        else:
            st.session_state.expenses = expenses


with st.form("expense_form", clear_on_submit=True):

    st.write("手動輸入:")
    receipt_date = st.date_input("日期")
    receipt_place = st.text_input("地點")
    item = st.text_input("項目")
    amount = st.number_input("價格", format='%f')
    submit_button = st.form_submit_button("加入帳目")

    if submit_button:
        # 將新的收據資訊加入到DataFrame
        new_data = {'Date': receipt_date, 'place': receipt_place, 'Item': item, 'Amount': amount}
        st.session_state.expenses = st.session_state.expenses.append(new_data, ignore_index=True)

st.write("所有花費")

expenses = pd.DataFrame(st.session_state.expenses)
show_chart_df = expenses[['Date', 'Amount']]
show_chart_df['Amount'] = show_chart_df['Amount'].apply(lambda x: int(re.sub(r'[^\d]', '', x)))

st.bar_chart(show_chart_df, x="Date", y="Amount", color="#DDA069")
st.dataframe(st.session_state.expenses, use_container_width=True)

# 如果需要，也可以提供保存DataFrame到CSV檔的功能
if st.button("Save to CSV"):
    st.session_state.expenses.to_csv("expenses.csv", index=False)
    st.success("Data saved to expenses.csv")
