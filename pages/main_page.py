import os

import streamlit as st
import streamlit.components.v1 as components
from streamlit_carousel import carousel
from PIL import Image
import time
from streamlit_navigation_bar import st_navbar
st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "images/GENTRIPLOGO_svg.svg")
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

page = st_navbar(
    pages,
    logo_path=logo_path,
    urls=urls,
    styles=styles,
    options=options,
)
def load_custom_styles():
    st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .button-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin-top: 10px;
        }
        .button {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 200px;
            height: 130px;
            margin: 5px;
            padding: 10px;
            text-decoration: none;
            background-color: #f1f1f1;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: background-color 0.3s, box-shadow 0.3s;
        }
        .button:hover {
            background-color: #e1e1e1;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .button img {
            width: 50px;
            height: 50px;
            margin-bottom: 10px;
        }
        .button span {
            font-size: 16px;
            color: #333;
        }
    </style>
    """, unsafe_allow_html=True)

# Main title
st.image("http://127.0.0.1:5000/images/main_pageBG.png", use_column_width=True)
st.write(' ')

# Chat messages
messages = st.container(height=195, border=False)
time.sleep(1)
messages.chat_message("user").write('我想要前往台中一日遊，但我真的沒有時間也不擅長，你可以幫我規劃嗎?😟😟')
time.sleep(1)
messages.chat_message("assistant").write(f"好的!這是我的專業!立刻為您規劃😎😎")
time.sleep(0.5)
like_place = messages.chat_input("輸入下個旅遊地點吧🏂")
if like_place is not None:
    st.session_state.like_place = like_place
    st.switch_page("main.py")

st.write(' ')
# Display custom styles
load_custom_styles()

# Add button links
st.subheader("更多功能")
st.markdown("""
<div class="button-container">
    <a href="http://localhost:8501/" class="button">
        <img src="https://img.icons8.com/material-outlined/50/FD7E14/bot.png" alt="找住宿">
        <span>AI行程規劃</span>
    </a>
    <a href="http://localhost:8501/budget_manager" class="button">
        <img src="https://img.icons8.com/material-sharp/50/40C057/accounting.png" alt="找住宿">
        <span>旅行記帳</span>
    </a>
    <a href="http://localhost:8501/insurance" class="button">
        <img src="https://img.icons8.com/material/50/22C3E6/security-checked--v1.png" alt="限時買一送一">
        <span>旅平險計算</span>
    </a>
</div>
""", unsafe_allow_html=True)

st.write(' ')
st.subheader("GenTrip AI 行程規劃小助手 Beta計畫介紹")
messages_button = st.container(height=350, border=False)
messages_button.chat_message("assistant").write("想出外遊玩，但沒時間規劃行程嗎？  \n 想走就走隨性出遊，懶得找景點美食資訊嗎？  \n 玩到不知道去哪玩，想找尋旅遊靈感嗎？  \n 快來嘗試「AI行程規劃小助手」的服務吧！")
messages_button.chat_message("user").write("你們具體是怎麼製作的呢?")
messages_button.chat_message("assistant").write("AI行程規劃小助手是Gentrip利用AI演算技術來優化旅遊行程的免費服務，透過Reg以及Prompt Engineer的方式，讓大型語言模型(Gpt4-o)可以根據使用者的個人偏好、預算和預計的旅遊時間，一鍵自動生成最符合使用者偏好的旅遊行程。")
st.subheader('推薦旅遊回憶')

# Components HTML for slideshow
components.html(
    """
    <!DOCTYPE html>
    <html>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    * {box-sizing: border-box;}
    body {font-family: Verdana, sans-serif;}
    .mySlides {display: none;}
    img {vertical-align: middle;}

    /* Slideshow container */
    .slideshow-container {
      max-width: 850px;
      position: relative;
      margin: auto;
    }

    /* The dots/bullets/indicators */
    .dot {
      height: 15px;
      width: 15px;
      margin: 0 2px;
      background-color: #bbb;
      border-radius: 10%;
      display: inline-block;
      transition: background-color 0.6s ease;
    }

    .active {
      background-color: #717171;
    }

    /* Fading animation */
    .fade {
      animation-name: fade;
      animation-duration: 2s;
    }

    @keyframes fade {
      from {opacity: .4} 
      to {opacity: 1}
    }
    </style>
    <body>
    <div class="slideshow-container">
    <div class="mySlides fade">
      <img src="http://127.0.0.1:5000/images/Group%208.png" style="width:100%">
    </div>
    <div class="mySlides fade">
      <img src="http://127.0.0.1:5000/images/Group%209.png" style="width:100%">
    </div>
    <div class="mySlides fade">
      <img src="http://127.0.0.1:5000/images/Group%2010.png" style="width:100%">
    </div>
    </div>
    <br>
    <div style="text-align:center">
      <span class="dot"></span> 
      <span class="dot"></span> 
      <span class="dot"></span> 
    </div>
    <script>
    let slideIndex = 0;
    showSlides();
    function showSlides() {
      let i;
      let slides = document.getElementsByClassName("mySlides");
      let dots = document.getElementsByClassName("dot");
      for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";  
      }
      slideIndex++;
      if (slideIndex > slides.length) {slideIndex = 1}    
      for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
      }
      slides[slideIndex-1].style.display = "block";  
      dots[slideIndex-1].className += " active";
      setTimeout(showSlides, 2000); // Change image every 2 seconds
    }
    </script>
    </body>
    </html> 
    """,
    height=600,
)
