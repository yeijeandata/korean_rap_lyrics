import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from collections import abc
import numpy as np

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import font_manager as fm
import os
from PIL import Image, ImageDraw  # Pillow를 사용해서 이미지 크기 조정
import matplotlib.image as mpimg

import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

##################################################################################
with open('analysis/고빈도_영어단어_200.txt', 'r', encoding='utf-8') as file:
    content1 = file.read()

en_common_words = [ word.strip() for word in content1.split() ]

with open('analysis/고빈도_한글단어_200.txt', 'r', encoding='utf-8') as file:
    content2 = file.read()

ko_common_words = [ word.strip() for word in content2.split() ]

##################################################################################
# 필요한 데이터 불러오기
artist = pd.read_csv('analysis/artist.csv')
en_data = pd.read_csv('analysis/영어_가사_토큰화.csv')
ko_data = pd.read_csv('analysis/한글_가사_토큰화.csv')

# 평균값 계산
en_means = {
'unique_words_ratio' : en_data['unique_words_ratio'].mean(),
'bad_words_ratio': en_data['bad_words_ratio'].mean(),
'words_cnt': en_data['words_cnt'].mean()/30
}

ko_means = {
'unique_words_ratio' : ko_data['unique_words_ratio'].mean(),
'bad_words_ratio': ko_data['bad_words_ratio'].mean(),
'words_cnt': ko_data['words_cnt'].mean()/30
}

###########################################################
def make_list (df, column, n=2): 
    # df 데이터 프레임의 column 의 정보를 공백 단위로 잘라서 리스트로 만들어 반환하는데, 단어는 n글자 이상만 포함
    tokenized_lyrics = []
    for text in df[column]:
        word_list = [  word.strip() for word in text.split() if len(word.strip())>=n]
        tokenized_lyrics.append(word_list)
    return(tokenized_lyrics)

###########################################################
# 워드 클라우드
###########################################################

def generate_en_wordcloud(word_counter, color): # 단어빈도수, 제목, 색상맵
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
        colormap=color, # 색상맵
        width=300, # 너비
        height=300, # 높이
        mask = mask_image # 불용어 
    ).generate_from_frequencies(word_freq)
    

    # Matplotlib로 워드 클라우드 시각화
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")  # 축 제거
    col = st.columns([1])
    with col[0]:
        st.pyplot(plt, use_container_width=False)

############################################################################
# 얼굴 넣은 맵 그리기
###########################################################################
Image.MAX_IMAGE_PIXELS = None

fpath = os.path.join(os.getcwd(), "font/NanumSquareRoundB.ttf")
prop = fm.FontProperties(fname=fpath)

##########################################################################
# artist_names에는 리스트 형태로 가수 이름을 넣습니다. (ex: ['Crush', 리쌍])

def generate_map_byartist(language, artist_names):
    
    if language == 'k':
        data = ko_data
        means = ko_means
        size = 1
        artist_names = list (set (artist_names + ['Don Mills', '허클베리피', 'Yuzion', '원슈타인'] ))

    elif language == 'e':
        data = en_data
        means = en_means
        size = 2
        artist_names = list (set (artist_names + ['빈첸', '원써겐', '식케이'] ))

    # 데이터 불러오기
    wanted_data = data.loc[ data['artist_name'].isin(artist_names), : ].reset_index(drop=True)
    
    fig = go.Figure()

    # 이미지 삽입
    for i, row in wanted_data.iterrows():

        artist_name = row['artist_name']
        if artist_name == 'NO:EL':
            image_path = "photo/NOEL.jpg"
        else:
            image_path = f"photo/{artist_name}.jpg"

        # 이미지 리사이징
        try: 
            img = Image.open(image_path)
        except:
            print("이미지를 찾을 수 없습니다.")
        image_size = (50, 50)
        img = img.resize(image_size, resample=Image.Resampling.LANCZOS)
        
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
        print(img_str)
        # 해당 위치에 이미지 추가
        fig.add_trace(go.Scatter(
            x=[row['unique_words_ratio'] * 100],
            y=[row['bad_words_ratio'] * 100],
            mode='markers+text',
            marker=dict(
                size=20,  # 점 크기
                color="blue",  # 점 색상
                opacity=0.7
            ),
            hovertemplate=f"{artist_name}<br>고유 단어 비율: {row['unique_words_ratio'] * 100:.2f}<br>비속어 비율: {row['bad_words_ratio'] * 100:.2f}<extra></extra>",
        ))


        # 이미지 삽입 위치 (x, y)
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{img_str}",  # base64로 인코딩된 이미지 문자열
                x=row['unique_words_ratio'] * 100,  # 이미지 위치 (x좌표)
                y=row['bad_words_ratio'] * 100,  # 이미지 위치 (y좌표)
                xref="x",  # x축을 기준으로 위치 지정
                yref="y",  # y축을 기준으로 위치 지정
                sizex=size,  # 이미지 크기 (x축에 대한 비율)
                sizey=size,  # 이미지 크기 (y축에 대한 비율)
                opacity=1,
                layer="above",  # 그래프 위에 이미지 표시
                xanchor="center",  # 이미지의 중심을 x좌표에 맞춤
                yanchor="middle"  # 이미지의 중심을 y좌표에 맞춤
            )
        )


        # 평균 값을 표시하는 점 추가
        fig.add_trace(go.Scatter(
            x=[means['unique_words_ratio']*100],
            y=[means['bad_words_ratio']*100],
            mode='markers+text',
            marker=dict(
                size=30,  # 평균 값 점 크기
                color="skyblue",  # 평균 값을 하늘색으로 표시
                opacity=0.5
            ),
            text="Average",
            textposition="bottom center",
            hovertemplate=f"평균 고유 단어 비율: {means['unique_words_ratio']*100:.2f}<br>평균 비속어 비율: {means['bad_words_ratio']*100:.2f}<extra></extra>",
        ))


        
    # 레이아웃 설정
    fig.update_layout(
        title="고유 단어 비율 vs 비속어 비율",
        xaxis_title="고유 단어 비율(%)",
        yaxis_title="비속어 비율(%)",
        font=dict(family="NanumSquareRoundB", size=14),
        showlegend=False,
        plot_bgcolor="white",
        height=1000,  # 그래프의 높이 설정
        width=1000,   # 그래프의 너비 설정
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='gray',
            zeroline=True,
            zerolinewidth=2,  # x축 0선 굵기 설정
            showline=True,
            linewidth=2,  # x축 선 굵기 설정
            linecolor='black'  # x축 선 색상 설정
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='gray',
            zeroline=True,
            zerolinewidth=2,  # y축 0선 굵기 설정
            showline=True,
            linewidth=2,  # y축 선 굵기 설정
            linecolor='black'  # y축 선 색상 설정
        )
    )


    # 격자 추가
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='gray')

    # 그래프 출력
    return fig
##################
# 

def get_three_graph(en, name):

    # 단어 수 그래프
    fig1 = px.bar ( x = [name, '평균'], y = [  int(en['words_cnt'].iloc[0]/30) , int(en_means['words_cnt'])] , 
                   title = '한 곡의 평균 단어 수', color=['blue','skyblue'])
    # x축, y축 레이블 추가
    fig1.update_layout(
        xaxis_title=f"{name}과 래퍼 113인 평균의 비교",
        yaxis_title="한 곡의 평균 단어 수",
        bargap=0.5
    )

    # 고유 단어 비율 그래프
    fig2 = px.bar ( x = [name, '평균'], y = [  en['unique_words_ratio'].iloc[0]*100 , en_means['unique_words_ratio']*100] , 
                   title = '고유 단어 비율', color=['blue','skyblue'])
    # x축, y축 레이블 추가
    fig2.update_layout(
        xaxis_title=f"{name}과 래퍼 113인 평균의 비교",
        yaxis_title="사용 단어 중 흔한 단어를 제외한 비율(%)",
        bargap=0.5
    )


    #비속어 비율 그래프
    fig3 = px.bar ( x = [name, '평균'], y = [  en['bad_words_ratio'].iloc[0]*100 , en_means['bad_words_ratio']*100] , 
                   title = '비속어 비율', color=['blue','skyblue'])
    # x축, y축 레이블 추가
    fig3.update_layout(
        xaxis_title=f"{name}과 래퍼 113인 평균의 비교",
        yaxis_title="사용 단어 중 비속어의의 비율(%)",
        bargap=0.5
    )

    return (fig1, fig2, fig3)

###############
