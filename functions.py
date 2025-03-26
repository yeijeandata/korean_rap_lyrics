import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from PIL import Image
from collections import abc
import numpy as np
import os

##################################################################################
with open('analysis/고빈도_영어단어_200.txt', 'r', encoding='utf-8') as file:
    content = file.read()

en_common_words = [ word.strip() for word in content.split() ]

##################################################################################
artist = pd.read_csv('analysis/artist.csv')
en_data = pd.read_csv('analysis/영어_가사_토큰화.csv')
ko_data = pd.read_csv('analysis/한글_가사_토큰화.csv')

def make_list (df, column): 
    tokenized_lyrics = []
    for text in df[column]:
        word_list = [  word.strip() for word in text.split() if len(word.strip())>=2]
        tokenized_lyrics.append(word_list)

def generate_en_wordcloud(name, word_counter): # 단어빈도수, 제목, 색상맵
    import numpy as np
    font_path = 'c:/windows/fonts/malgun.ttf' # 한글 폰트 경로
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트 위치
    mask_path = os.path.join(base_dir, "photo", "mask.png")  # 상대 경로 사용
    mask_image = np.array(Image.open(mask_path))

    # Counter 객체를 딕셔너리로 변환
    word_freq = dict(word_counter)

    wc = WordCloud(  # 워드클라우드 객체 생성
        font_path=font_path, # 폰트 경로
        background_color='white', # 배경색
        max_words=100, # 최대 단어 수
        colormap='Greens', # 색상맵
        width=800, # 너비
        height=500, # 높이
        mask = mask_image # 불용어 
    ).generate_from_frequencies(word_freq)
    
    # 단어 빈도수를 이용하여 워드클라우드를 만듭니다.

    st.title("영어 단어 워드 클라우드")
    st.write(f"{name}의 영어 어휘를 빈도수를 반영하여 그린 워드 클라우드 입니다.")

    # Matplotlib로 워드 클라우드 시각화
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")  # 축 제거
    st.pyplot(plt)



