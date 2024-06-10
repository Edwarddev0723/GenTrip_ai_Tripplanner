import streamlit as st
import os
from datetime import datetime, timedelta
import json
import openai
import tiktoken
import re

# Inject CSS with HTML for custom styling
m = st.markdown("""
<style>
div.stButton > button {
  all: unset;
  width: 100px;
  height: 30px;
  font-size: 16px;
  background: transparent;
  border: none;
  position: relative;
  color: #f0f0f0;
  cursor: pointer;
  z-index: 1;
  padding: 10px 20px;
  display: block;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  margin: auto;
  top: 15px;
}

div.stButton > button::after, button::before  {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  z-index: -99999;
  transition: all .4s;
}

div.stButton > button::before  {
  transform: translate(0%, 0%);
  width: 100%;
  height: 100%;
  background: #28282d;
  border-radius: 10px;
}
div.stButton > button::after   {
  transform: translate(10px, 10px);
  width: 35px;
  height: 35px;
  background: #ffffff15;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border-radius: 50px;
}
div.stButton > button::hover::before {
  transform: translate(5%, 20%);
  width: 110%;
  height: 110%;
}
div.stButton > button:hover::after {
  border-radius: 10px;
  transform: translate(0, 0);
  width: 100%;
  height: 100%;

}
div.stButton > button:active::after {

  transition: 0s;
  transform: translate(0, 5%);

}
</style>""", unsafe_allow_html=True)

st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .title {
            color: #2C3E50;
            text-align: center;
        }
        .section-title {
            color: #3498DB;
            margin-top: 40px;
            font-size: 1.5em;
        }
        .input-label {
            color: #2980B9;
            font-weight: bold;
            margin-bottom: 15px;
            color: #000;

        }
        .user-input {
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        .result-title {
            color: #1ABC9C;
            margin-top: 40px;
            font-size: 1.5em;
            border-top: 2px solid #1ABC9C;
            padding-top: 10px;
        }
        .activity-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 10px;
            box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
            background-color: #f9f9f9;
            color: #000; /* 使用黑色字體 */
        }
        .activity-card p {
            margin: 5px 0;
            color: #000; /* 使用黑色字體 */
        }
        .activity-card strong {
            color: #000; /* 使用黑色字體 */
        }
        .activity-link {
            color: #1a73e8;
            text-decoration: none;
            font-weight: bold;
        }
        .activity-link:hover {
            text-decoration: underline;
        }
        hr {
            border: 0;
            height: 1px;
            background: #ddd;
            margin: 40px 0;
        }
    </style>
""", unsafe_allow_html=True)


def save_data(data):
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            existing_data = json.load(f)
            print("儲存")
    else:
        existing_data = []

    existing_data.append(data)

    with open("data.json", "w") as f:
        json.dump(existing_data, f, indent=4)


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


def extract_number_from_string(s):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


openai.api_key = "Your_OPENAI_API_KEY"
MODEL = "gpt-4o"

# Streamlit app title
st.markdown("<h1 class='title'>🗺️ GenTrip</h1>", unsafe_allow_html=True)

# Introduction
st.markdown("<h2>快速、方便、多樣計劃您的完美旅行</h2>", unsafe_allow_html=True)

# Layout configuration
col1, col2 = st.columns(2)

# User input for city
with col1:
    # st.markdown("<div class='user-input'><label class='input-label'>1. 旅行目的地</label></div>", unsafe_allow_html=True)
    city = st.text_input("請輸入你想要探索的城市:")

# User input for start date
with col2:
    # st.markdown("<div class='user-input'><label class='input-label'>2. 旅行日期</label></div>", unsafe_allow_html=True)
    start_date = st.date_input("選擇開始日期:", value=datetime.today())

# User input for end date with constraints
with col2:
    # st.markdown("<div class='user-input'><label class='input-label'>3. 結束日期</label></div>", unsafe_allow_html=True)
    max_end_date = start_date + timedelta(days=30)
    end_date = st.date_input(
        "選擇結束日期:",
        value=start_date + timedelta(days=1),
        min_value=start_date,
        max_value=max_end_date
    )

# Calculate the number of days between start_date and end_date
days = (end_date - start_date).days

# User input for hotel type
with col1:
    # st.markdown("<div class='user-input'><label class='input-label'>4. 住宿類型</label></div>", unsafe_allow_html=True)
    hotel_type = st.multiselect(
        "請選擇想要住宿類型:",
        ["🏨 飯店", "🏡 民宿"]
    )

# User input for preferences
# st.markdown("<div class='user-input'><label class='input-label'>5. 興趣偏好</label></div>", unsafe_allow_html=True)
user_pre = st.multiselect(
    "讓我們更了解您~",
    ["🎨 探索藝術", "🏛️ 參觀博物館", "⛰️ 參與戶外活動", "🏠 探索室內活動", "👶 尋找適合兒童的地方", "🧒 適合年輕人的地方",
     "👵 發現適合熟齡長輩的地方"]
)

# User input for special needs
# st.markdown("<div class='user-input'><label class='input-label'>6. 特殊需求</label></div>", unsafe_allow_html=True)
special_need = st.text_input("如果有什麼特殊需求歡迎告訴我們:")

# slider
tem = st.slider("大型語言模型溫度(越高越有創造力)", 0, 100, 1)
tem = tem / 100

# Generate itinerary button
if st.button("🌍 生成行程"):
    st.toast('👌Roger That!我立刻去辦')
    # 根據用戶輸入創建提示
    data = {
        "city": city,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days": days,
        "hotel_type": hotel_type,
        "user_pre": user_pre,
        "special_need": special_need
    }

    save_data(data)
    st.toast('👀讓我來看看!')
    prompt = f"請給我一個{city}的行程安排，為期{days}天，假設每天從上午10點開始到晚上8點結束，每個活動之間有30分鐘的緩衝時間。我喜歡"
    for item in user_pre:
        prompt += item
    prompt += f"飯店我喜歡{str(hotel_type)}。請告訴我明確且具體我要下榻的住宿地點，並且希望一天至兩天至少換一間酒店"
    if special_need != None:
        print('收到需求')
        prompt += f"外我也{special_need}，請買足我的需求"
    # prompt += ". 返回一個可以使用Python中的json.loads函數導入的格式良好的json字符串。"
    prompt += """將輸出json字符串的長度限制在1200個字符內。生成旅行行程的結構化JSON表示。

       {
  "days": [
    {
      "day": 1,
      "activities": [
        {
          "title": "活動1",
          "description": "活動1的描述",
          "link": "https://XXXX",
          "start_time": "10:00 AM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location1",
          "charge" : "$xxx"
        },
        {
          "title": "活動2",
          "description": "活動2的描述",
          "link": "https://XXXX",
          "start_time": "02:00 PM",
          "end_time": "04:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        },
        ....
        {
          "title": "Day 1 飯店",
          "description": "Day 1 飯店的描述",
          "link": "https://XXXX",
          "start_time": "08:00 PM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        }
      ]
    },
    {
      "day": 2,
      "activities": [
        {
          "title": "另一個活動1",
          "description": "另一個活動1的描述",
          "link": "https://XXXX",
          "start_time": "09:30 AM",
          "end_time": "11:30 AM",
          "location": "https://maps.google.com/?q=location1",
          "charge" : "$xxx"
        },
        {
          "title": "另一個活動2",
          "description": "另一個活動2的描述",
          "link": "https://XXXX",
          "start_time": "01:00 PM",
          "end_time": "03:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        },
        ...
        {
          "title": "Day 2 飯店",
          "description": "Day 2 飯店的描述",
          "link": "https://XXXX",
          "start_time": "08:00 PM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        }
      ]
    }
  ]
}

確保每一天都有一個 'day' 字段和一個包含 'title'、'description'、'link', 'start_time'、'end_time', 'location'和'charge' 字段的 'activities' 列表，請全部以小寫表示如果景點不用錢的話已0表示。並且chage費用請以新台幣表示，保持描述簡潔。
"""
    count_fee = "你是一名30年資歷並且擅長規劃行程的台灣導遊. 請幫我根據提供的信息，請給我制定一個詳細的旅遊計劃，包括具體的餐廳名稱和酒店名稱。此外，所有細節都應符合常識。景點參觀和用餐應該多樣化。。將“在家吃飯/在路上吃飯”這類非具體信息替換為更具體的餐廳。" + prompt
    tok = num_tokens_from_string(count_fee, "gpt-4o")
    print(f"運算價格:${(tok / 1000) * 0.06}")

    # Call the OpenAI API
    with st.spinner('🧐我來思考一下...'):
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                 "content": "你是一名擅長規劃行程的導遊. 請幫我根據提供的信息，請給我制定一個詳細的計劃，包括具體的餐廳名稱和酒店名稱。此外，所有細節都應符合常識。景點參觀和用餐應該多樣化。。將“在家吃飯/在路上吃飯”這類非具體信息替換為更具體的餐廳。"},
                {"role": "user", "content": [
                    {"type": "text", "text": f"{prompt}"}
                ]}
            ],
            temperature=tem,
        )
    st.toast('🤸‍♂️我知道了!!這樣的安排如何~~')
    modified_string = modify_string(response.choices[0].message.content)
    print(modified_string)
    itinerary_json = json.loads(modified_string)
    total_charge = 0

    for day in itinerary_json["days"]:
        st.header(f"Day {day['day']}")
        for activity in day["activities"]:
            st.subheader(activity["title"])
            charge = extract_number_from_string(activity["charge"])
            total_charge += int(charge)

            st.markdown(
                f"""
                <div class='activity-card'>
                    <p><strong>介紹:</strong> {activity['description']}</p>
                    <p><strong>地點:</strong> {activity['location']}</p>
                    <p><strong>時間:</strong> {activity['start_time']} - {activity['end_time']}</p>
                    <p><strong>預算:</strong> {activity['charge']}</p>
                </div>
                """, unsafe_allow_html=True
            )

        st.write("<hr>", unsafe_allow_html=True)

    # Set the start date to tomorrow
    start_date = datetime.now() + timedelta(days=1)
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
                <a href="pages/insurance.py" target="_blank">點我線上投保 💼</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )