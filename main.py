import time

import requests
import streamlit as st
import os
from datetime import datetime, timedelta
import json
import openai
import tiktoken
import re
import streamlit.components.v1 as components
import random
global itinerary_json_data
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
    logo_path = logo_path,
    urls=urls,
    styles=styles,
    options=options,
)
#function
cities = ["台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市", "基隆市",
          "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義市",
          "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣", "金門縣",
          "連江縣"]

if 'initialized' not in st.session_state:
    # 如果沒有，設置它並執行只需在第一次運行的代碼
    st.session_state['initialized'] = True
    # 這裡是初始化代碼
    st.session_state.current_trip = ''
    st.session_state.mess = ''  # 這裡確保 mess_in 被初始化為空字符串
def generate_city():
    # 從列表中隨機選擇一個縣市
    return random.choice(cities)

def save_log_data(r_data):
    """將行程資料保存到一個 JSON 檔案中"""
    filename = f"user_log.json"  # 構造檔案名，默認為 itinerary.json
    try:
        with open(filename, 'w') as f:
            json.dump(r_data, f, indent=4)  # 寫入 JSON 數據
    except Exception as e:
        st.error(f"保存檔案時發生錯誤: {e}")
def display_itinerary(itinerary_json_data):
    # 初始化總預算和天數列表
    total_charge = 0

    # 遍歷每一天的行程
    for day in itinerary_json_data["days"]:
        st.header(f"Day {day['day']}")
        day_int = day['day']
        day_list.append(f'Day {day_int}')
        for activity in day["activities"]:
            st.subheader(activity["title"])
            charge = extract_number_from_string(activity["charge"])
            total_charge += int(charge) if charge else 0

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

    # 顯示總預算和保險連結
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


def save_data(data, filename="data.json"):
    """將新數據添加到 JSON 文件中。如果文件不存在，則創建一個新文件。"""
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append(data)

        with open(filename, "w") as f:
            json.dump(existing_data, f, indent=4)

        print('資料已加入')
    except Exception as e:
        print(f"保存數據時發生錯誤: {e}")

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
    s = str(s)  # Convert input to string to avoid TypeError
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

#Aggent Setting
openai.api_key = "Your_OPENAI_API_KEY"
MODEL = "gpt-4"

# Main title
st.image("http://127.0.0.1:5000/images/plan_BG.png", use_column_width=True)
st.write(' ')

tab1, tab2 = st.tabs(["AI規劃行程", "盲盒出發"])

with tab1:
    # Layout configuration
    my_bar = st.progress(0, text="快來填入吧👀目前完成進度0%")
    col1, col2 = st.columns(2)
    # User input for city
    with col1:
        #st.markdown("<div class='user-input'><label class='input-label'>1. 旅行目的地</label></div>", unsafe_allow_html=True)
        if 'like_place' not in st.session_state:
            st.session_state.like_place = ''
        if st.session_state.like_place is not None:
            like_p = st.session_state.like_place
        city = st.text_input("請輸入你想要探索的城市:", like_p)
        if city != '':
            my_bar.progress(25, text="HOLA LAMIGO🐣~目前完成進度25%")

    # User input for start date
    with col2:
        #st.markdown("<div class='user-input'><label class='input-label'>2. 旅行日期</label></div>", unsafe_allow_html=True)
        start_date = st.date_input("選擇開始日期:", value=datetime.today())

    # User input for end date with constraints
    with col2:
        #st.markdown("<div class='user-input'><label class='input-label'>3. 結束日期</label></div>", unsafe_allow_html=True)
        max_end_date = start_date + timedelta(days=30)
        end_date = st.date_input(
            "選擇結束日期:",
            value=start_date + timedelta(days=1),
            min_value=start_date,
            max_value=max_end_date
        )

    # Calculate the number of days between start_date and end_date
    days = (end_date - start_date).days
    day_list = [f"Day {i+1}" for i in range(days)]

    # User input for hotel type
    with col1:
        #st.markdown("<div class='user-input'><label class='input-label'>4. 住宿類型</label></div>", unsafe_allow_html=True)
        hotel_type = st.multiselect(
            "請選擇想要住宿類型:",
            ["🏨 飯店", "🏡 民宿"],
            placeholder='選擇喜歡的住宿類型吧~'
        )
        if len(hotel_type) != 0:
            my_bar.progress(50, text="Gen的讚~目前完成進度50%")

    with col1:
        budget_type = st.selectbox(
            "你們的預算類型?",
            ("小資", "一般", "舒適", "高級", "豪華"))

    with col2:
        people_count = st.number_input("輸入人數:", value=1, step=1)
    # User input for preferences
    #st.markdown("<div class='user-input'><label class='input-label'>5. 興趣偏好</label></div>", unsafe_allow_html=True)
    user_pre = st.multiselect(
        "讓我們更了解您~",
        ["🎨 探索藝術", "🏛️ 參觀博物館", "⛰️ 參與戶外活動", "🏠 探索室內活動", "👶 尋找適合兒童的地方", "🧒 適合年輕人的地方", "👵 發現適合熟齡長輩的地方"],
        placeholder="選擇適合您的旅遊偏好吧~"
    )
    if len(user_pre) != 0:
        my_bar.progress(75, text="再一個就完成了🚀目前完成進度75%")
    with st.expander("🧙‍♂️如果有IG貼文也可以告訴我們喔~"):
        mess_in = st.chat_input('輸入IG貼文網址🤩')
        if mess_in is not None:
            with st.spinner('爬取貼文...'):
                time.sleep(3)
            with st.spinner('LLM分析'):
                time.sleep(3)
            if mess_in == 'https://www.instagram.com/p/C736gatvM_-/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==':
                st.session_state.mess += '我想去高雄駁二大義站附近的美麗大港橋拍照。'
                print(st.session_state.mess)
            elif mess_in == 'https://www.instagram.com/reel/C73DUzZvk24/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==':
                st.session_state.mess += '我想去高雄旗津大關路的三郎麵館吃什錦炒油麵和餛飩湯。'


    # User input for special needs
    #st.markdown("<div class='user-input'><label class='input-label'>6. 特殊需求</label></div>", unsafe_allow_html=True)
    special_need = st.text_input("如果有什麼特殊需求歡迎告訴我們:", st.session_state.mess)
    if len(special_need) != 0:
        my_bar.progress(100, text="超讚的😆完成進度100%")
    #slider
    #tem = st.slider("大型語言模型溫度(越高越有創造力)", 0, 100, 1)
    #tem = tem/100

    generate_button = st.button("🌍 生成行程")

    # Generate itinerary button
    if generate_button:
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
        prompt = f"You are a Taiwanese tour guide with 30 years of experience who excels in planning itineraries. Based on the provided information, please help me create a detailed travel plan, including specific restaurant and hotel names. Additionally, all details should be sensible, such as not visiting a night market in the morning. Attractions and dining should be diverse and specific; avoid repetitions or vague suggestions like eat at a stir-fry restaurant without specifying which one. Instead of non-specific information like eat at home/on the road, please provide specific restaurant names. Please give me a travel plan for {city} for {days} days, assuming each day starts at 10 am and ends at 8 pm, with 30-minute buffers between activities. I like"
        for item in user_pre:
            prompt += item
        prompt += f"I prefer the type of accommodation {str(hotel_type)}. Please provide me with specific and detailed lodging options where I will stay, and I would like to switch hotels at least once every one to two days."

        #if budget_type == '小資':
            #prompt += 'I prefer For a budget-friendly experience, I seek youth hostels that are economical yet cozy. I am interested in attractions with free admission, prefer to sample street food, and enjoy viewing natural scenery. I hope to use public transport for mobility, ensuring that the attractions are in close proximity to each other, ideally within a 30-minute travel window. My budget is limited but I am keen on maximizing the experience affordably.'
        #if budget_type == '一般':
            #prompt += 'I prefer comfortable yet standard accommodations such as regular Bed & Breakfasts and mid-range hotels. Dining options include ordinary, well-rated restaurants and chain stores. I am interested in visiting popular tourist attractions and trying famous local snacks, seeking a balance between cost and comfort.'
        #if budget_type == '舒適':
            #prompt += 'I opt for regular hotels that provide a more leisurely travel pace, with transportation options like motorcycles or personal cars. I am interested in specialty cuisines and plan for a moderate budget. My itinerary includes at least one relaxed activity to immerse myself in the local culture, with travel times up to an hour to enrich my understanding of the area.'
        #if budget_type == '高級':
            #prompt += 'I prefer staying in four-star or higher hotels, enjoying self-driven travel. My dining preferences lean towards high-end options, including Michelin-starred restaurants. I seek a quality experience with luxury accommodations and facilities, enjoying high-rise night views and bars, aligning with a higher budget for an upscale experience.'
        #if budget_type == '豪華':
            #prompt += 'I desire ultra-luxurious accommodations in five-star hotels or higher, with chauffeured transfers enhancing my travel experience. I aim to visit the most exclusive and luxurious attractions, enjoy private yacht tours, and dine in private kitchens with custom-made cuisine. My budget is extremely high, focusing on customized experiences and private, exclusive services to ensure a uniquely lavish trip.'
        #prompt += f'Please recommend an itinerary suitable for {people_count} people.'
        if special_need != None:
            prompt += f"Additionally, I also {special_need}, please accommodate my needs fully."
        # prompt += ". 返回一個可以使用Python中的json.loads函數導入的格式良好的json字符串。"
        prompt += """Limit the output JSON string to within 2500 characters. Generate a structured JSON representation of the travel itinerary.
    
           {
      "days": [
        {
          "day": 1,
          "activities": [
            {
              "title": "activate 1",
              "description": "activate 1 introduction",
              "link": "https://XXXX",
              "start_time": "10:00 AM",
              "end_time": "12:00 PM",
              "location": "https://maps.google.com/?q=location1",
              "charge" : "$xxx"
            },
            {
              "title": "activate 2",
              "description": "activate 2 introduction",
              "link": "https://XXXX",
              "start_time": "02:00 PM",
              "end_time": "04:00 PM",
              "location": "https://maps.google.com/?q=location2",
              "charge" : "$xxx"
            },
            ....
            {
              "title": "Day 1 hotel",
              "description": "Day 1 hotel introduction",
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
              "title": "day 2 activate 1",
              "description": "day 2 activate 1 introduction",
              "link": "https://XXXX",
              "start_time": "09:30 AM",
              "end_time": "11:30 AM",
              "location": "https://maps.google.com/?q=location1",
              "charge" : "$xxx"
            },
            {
              "title": "day 2 activate 2",
              "description": "day 2 activate 2 introduction",
              "link": "https://XXXX",
              "start_time": "01:00 PM",
              "end_time": "03:00 PM",
              "location": "https://maps.google.com/?q=location2",
              "charge" : "$xxx"
            },
            ...
            {
              "title": "Day 2 hotel",
              "description": "Day 2 hotel introduction",
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
    """
        prompt += f"Please generate all reference data for hotels and restaurants from the dataset I provided to you.Ensure that each day has a 'day' field and an 'activities' list that contains 'title', 'description', 'link', 'start_time', 'end_time', 'location', and 'charge' fields, all represented in lowercase. If an attraction is free, represent it with 0. Charges should be in New Taiwan Dollars, and descriptions should be concise. Lastly, please provide me with a travel itinerary for {city} lasting {days} days. Each day should include an activity after breakfast, another attraction after lunch, and then proceed to the accommodation after dinner, all in line with common sense and matching the number of days requested. Finally, please answer all questions in Traditional Chinese (zh_tw)."
        #tok = num_tokens_from_string(count_fee, "gpt-4o")
        #print(f"運算價格:${(tok / 1000) * 0.06}")

        data = {
            "query": prompt
        }
        print(prompt)
        # Call the OpenAI API
        with st.spinner('🧐我來思考一下...'):
            res = requests.post("http://localhost:5000/query", json=data)
            if res.status_code == 200:
                # 解析响应内容
                answer = res.json()["answer"]["result"]
                print("回答成功")
            else:
                print("請求失敗:", res.status_code)

        #print(res)
        st.toast('🤸‍♂️我知道了!!這樣的安排如何~~')
        #print(type(answer))
        modified_string = modify_string(str(answer))
        modified_string = modified_string.replace("'", '"')
        print(str(answer))
        itinerary_json_data = json.loads(modified_string)
        display_itinerary(itinerary_json_data)
        now = datetime.now()
        itinerary_json_data['id'] = f'{city}{days}天_{now.month}{now.day}'
        save_log_data(itinerary_json_data)
        st.success(f'儲存成功!檔名:{city}{days}天_{now.month}{now.day}', icon="✅")



##################################################################################################

with tab2:
    city = st.session_state.get('city', '')
    st.text_input("旅遊縣市", f"{city}")

    col1, col2 = st.columns(2)
    with col1:
        start_date_tab2 = st.date_input("選擇開始日期:", value=datetime.today(), key='start_date_tab2')
    with col2:
        # st.markdown("<div class='user-input'><label class='input-label'>3. 結束日期</label></div>", unsafe_allow_html=True)
        max_end_date = start_date_tab2 + timedelta(days=30)
        end_date = st.date_input(
            "選擇結束日期:",
            value=start_date_tab2 + timedelta(days=1),
            min_value=start_date_tab2,
            max_value=max_end_date,
            key='end_date_tab2'
        )
    col3, col4 = st.columns(2)
    with col3:
        if st.button('🎲隨機縣市'):
            st.session_state['city'] = generate_city()
    with col4:
        tab_2_bu = st.button("🌍 生成行程", key='col_gen_button')

    if tab_2_bu:
        days = (end_date - start_date).days
        st.toast('👌Roger That!我立刻去辦')
        # 根據用戶輸入創建提示
        data = {
            "city": '高雄',
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
        }
        city = '高雄'

        save_data(data)
        st.toast('👀讓我來看看!')
        prompt = f"You are a Taiwanese tour guide with 30 years of experience who excels in planning itineraries. Based on the provided information, please help me create a detailed travel plan, including specific restaurant and hotel names. Additionally, all details should be sensible, such as not visiting a night market in the morning. Attractions and dining should be diverse and specific; avoid repetitions or vague suggestions like eat at a stir-fry restaurant without specifying which one. Instead of non-specific information like eat at home/on the road, please provide specific restaurant names. Please give me a travel plan for {city} for {days} days, assuming each day starts at 10 am and ends at 8 pm, with 30-minute buffers between activities. I like"
        prompt += """Limit the output JSON string to within 2500 characters. Generate a structured JSON representation of the travel itinerary.

                   {
              "days": [
                {
                  "day": 1,
                  "activities": [
                    {
                      "title": "activate 1",
                      "description": "activate 1 introduction",
                      "link": "https://XXXX",
                      "start_time": "10:00 AM",
                      "end_time": "12:00 PM",
                      "location": "https://maps.google.com/?q=location1",
                      "charge" : "$xxx"
                    },
                    {
                      "title": "activate 2",
                      "description": "activate 2 introduction",
                      "link": "https://XXXX",
                      "start_time": "02:00 PM",
                      "end_time": "04:00 PM",
                      "location": "https://maps.google.com/?q=location2",
                      "charge" : "$xxx"
                    },
                    ....
                    {
                      "title": "Day 1 hotel",
                      "description": "Day 1 hotel introduction",
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
                      "title": "day 2 activate 1",
                      "description": "day 2 activate 1 introduction",
                      "link": "https://XXXX",
                      "start_time": "09:30 AM",
                      "end_time": "11:30 AM",
                      "location": "https://maps.google.com/?q=location1",
                      "charge" : "$xxx"
                    },
                    {
                      "title": "day 2 activate 2",
                      "description": "day 2 activate 2 introduction",
                      "link": "https://XXXX",
                      "start_time": "01:00 PM",
                      "end_time": "03:00 PM",
                      "location": "https://maps.google.com/?q=location2",
                      "charge" : "$xxx"
                    },
                    ...
                    {
                      "title": "Day 2 hotel",
                      "description": "Day 2 hotel introduction",
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
            """
        prompt += f"Please generate all reference data for hotels and restaurants from the dataset I provided to you.Ensure that each day has a 'day' field and an 'activities' list that contains 'title', 'description', 'link', 'start_time', 'end_time', 'location', and 'charge' fields, all represented in lowercase. If an attraction is free, represent it with 0. Charges should be in New Taiwan Dollars, and descriptions should be concise. Lastly, please provide me with a travel itinerary for {city} lasting {days} days. Each day should include an activity after breakfast, another attraction after lunch, and then proceed to the accommodation after dinner, all in line with common sense and matching the number of days requested. Finally, please answer all questions in Traditional Chinese (zh_tw).Hope to stay in a different hotel every day.i don't wanna to stay in 承攜行旅-高雄新崛江"
        data = {
            "query": prompt
        }

        # Call the OpenAI API
        with st.spinner('🧐我來思考一下...'):
            res = requests.post("http://localhost:5000/query", json=data)
            if res.status_code == 200:
                # 解析响应内容
                answer = res.json()["answer"]["result"]
                print("回答成功")
            else:
                print("請求失敗:", res.status_code)

        # print(res)
        st.toast('🤸‍♂️我知道了!!這樣的安排如何~~')
        # print(type(answer))
        modified_string = modify_string(str(answer))
        modified_string = modified_string.replace("'", '"')
        print(str(answer))
        itinerary_json_data = json.loads(modified_string)
        st.session_state.current_trip = itinerary_json_data
        display_itinerary(st.session_state.current_trip)
        now = datetime.now()
        itinerary_json_data['id'] = f'{city}{days}天_{now.month}{now.day}'
        save_log_data(itinerary_json_data)
        st.success(f'儲存成功!檔名:{city}{days}天_{now.month}{now.day}', icon="✅")
