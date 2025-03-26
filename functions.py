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
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import font_manager as fm
import os
from PIL import Image, ImageDraw  # Pillow를 사용해서 이미지 크기 조정
import matplotlib.image as mpimg
import numpy as np

Image.MAX_IMAGE_PIXELS = None

fpath = os.path.join(os.getcwd(), "font/NanumSquareRoundB.ttf")
prop = fm.FontProperties(fname=fpath)


def generate_en_map():

    x = en_data['unique_words_ratio']
    y = en_data['bad_words_ratio']

    fig_en = plt.figure(figsize=(30, 30))  # 👈 plt.figure() 명시적으로 생성

    ax = fig_en.add_subplot(111)

    

    ax.scatter(x, y)

    for i in range(len(x)):
        if en_data['artist_name'][i] == 'NO:EL':
            image_path = "photo/NOEL.jpg"
        else:
            image_path = f"photo/{en_data['artist_name'][i]}.jpg"

        # 이미지 크기 줄이기
        img = Image.open(image_path)
        image_size = (50, 50)

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

        ax.text(x[i], y[i], en_data['artist_name'][i], ha='center', fontsize=10, color='black', fontproperties=prop)

    ax.set_xlabel('고유 단어 비율', fontproperties=prop, fontsize = 20)
    ax.set_ylabel('비속어 비율', fontproperties=prop, fontsize = 20)
    ax.tick_params(axis='both', labelsize=12)  # x축, y축 눈금 크기 설정
    ax.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)

    return fig_en  # 👈 fig_en을 명확히 리턴


######################
from PIL import Image
import base64
from io import BytesIO

def resize_image(image_path, max_size=(500, 500)):
    """ 이미지 크기를 최대한 제한된 크기로 리사이즈 """
    with Image.open(image_path) as img:
        img.thumbnail(max_size)  # 이미지를 max_size 크기로 축소
        return img

def generate_en_map_plotly():
    # 데이터 불러오기 (en_data가 이미 정의되었다고 가정)
    x = en_data['unique_words_ratio']
    y = en_data['bad_words_ratio']
    
    fig = go.Figure()

    image_size = (50, 50)  # 원형 이미지 크기 설정
    max_image_size = (500, 500)  # 이미지 리사이징 최대 크기 설정

    # 이미지 삽입
    for i in range(len(x)):
        if en_data['artist_name'][i] == 'NO:EL':
            image_path = "photo/NOEL.jpg"
        else:
            image_path = f"photo/{en_data['artist_name'][i]}.jpg"

        # 이미지 리사이징
        img = resize_image(image_path, max_size=max_image_size)
        img = img.resize(image_size, Image.Resampling.LANCZOS)  # 이미지 크기 변경

        # 이미지를 원형으로 자르기
        mask = Image.new('L', image_size, 0)  # 'L' 모드는 흑백 이미지
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, image_size[0], image_size[1]), fill=255)  # 원형 그리기

        # 원형 마스크를 이미지에 적용
        img.putalpha(mask)  # alpha 채널을 적용하여 원형 이미지 생성

        # 이미지를 base64로 변환
        buffered = BytesIO()
        img.save(buffered, format="PNG")  # 이미지를 PNG 형식으로 저장
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')  # base64로 변환

        # 해당 위치에 이미지 추가
        fig.add_trace(go.Scatter(
            x=[x[i]],
            y=[y[i]],
            mode='markers+text',
            marker=dict(
                size=20,  # 점 크기
                color="blue",  # 점 색상
                opacity=0.7
            ),
            hovertemplate=f"{en_data['artist_name'][i]}<br>고유 단어 비율: {x[i]:.2f}<br>비속어 비율: {y[i]:.2f}<extra></extra>",
        ))

        # 이미지 삽입 위치 (x, y)
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{img_str}",  # base64로 인코딩된 이미지 문자열
                x=x[i],  # 이미지 위치 (x좌표)
                y=y[i],  # 이미지 위치 (y좌표)
                xref="x",  # x축을 기준으로 위치 지정
                yref="y",  # y축을 기준으로 위치 지정
                sizex=0.02,  # 이미지 크기 (x축에 대한 비율)
                sizey=0.02,  # 이미지 크기 (y축에 대한 비율)
                opacity=1,
                layer="above",  # 그래프 위에 이미지 표시
                xanchor="center",  # 이미지의 중심을 x좌표에 맞춤
                yanchor="middle"  # 이미지의 중심을 y좌표에 맞춤
            )
        )

    # 레이아웃 설정
    fig.update_layout(
        title="고유 단어 비율 vs 비속어 비율",
        xaxis_title="고유 단어 비율",
        yaxis_title="비속어 비율",
        font=dict(family="NanumSquareRoundB", size=14),
        showlegend=False,
        plot_bgcolor="white",
        height=1200,  # 그래프의 높이 설정
        width=1200,   # 그래프의 너비 설정
    )

    # 격자 추가
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='gray')

    # 그래프 출력
    return fig
