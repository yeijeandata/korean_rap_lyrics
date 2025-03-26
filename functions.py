import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from PIL import Image
from collections import abc
import numpy as np

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
    font_path = 'font/NanumSquareRoundB.ttf' # 한글 폰트 경로
    mask_path = "photo/mask.png"  # 상대 경로 사용
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

############################################################################

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw  # Pillow를 사용해서 이미지 크기 조정
from matplotlib import font_manager, rc

def generate_en_map():
    font_path = 'font/NanumSquareRoundB.ttf'  # Windows 예시
    font_prop = font_manager.FontProperties(fname=font_path)
    rc('font', family=font_prop.get_name())

    x = en_data['unique_words_ratio']
    y = en_data['bad_words_ratio']

    fig_en = plt.figure(figsize=(20, 20))  # 👈 plt.figure() 명시적으로 생성

    ax = fig_en.add_subplot(111)

    image_size = (50, 50)

    ax.scatter(x, y)

    for i in range(len(x)):
        if en_data['artist_name'][i] == 'NO:EL':
            image_path = "photo/NOEL.jpg"
        else:
            image_path = f"photo/{en_data['artist_name'][i]}.jpg"

        img = Image.open(image_path)
        img = img.resize(image_size, Image.Resampling.LANCZOS)

        mask = Image.new('L', image_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, image_size[0], image_size[1]), fill=255)

        img.putalpha(mask)
        img = img.convert("RGBA")
        img_arr = np.array(img)

        img_arr[:, :, 3] = img_arr[:, :, 3] * (img_arr[:, :, 3] > 0)

        imagebox = OffsetImage(img, zoom=1, resample=True)
        ab = AnnotationBbox(imagebox, (x[i], y[i]), frameon=False)
        ax.add_artist(ab)

        ax.text(x[i], y[i] + 2.6, en_data['artist_name'][i], ha='center', fontsize=10, color='black')

    ax.set_xlabel('고유 단어 비율')
    ax.set_ylabel('욕설 횟수')

    return fig_en  # 👈 fig_en을 명확히 리턴


