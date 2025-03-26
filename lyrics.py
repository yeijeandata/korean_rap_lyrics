import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import pandas as pd
from PIL import Image
from collections import abc
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw  # Pillow를 사용해서 이미지 크기 조정
from matplotlib import font_manager, rc

font_path = 'font/NanumSquareRoundB.ttf'  # Windows 예시
font_prop = font_manager.FontProperties(fname=font_path)
rc('font', family=font_prop.get_name())

# CSV 파일 로드
artist = pd.read_csv('analysis/artist.csv')
en_data = pd.read_csv('analysis/영어_가사_토큰화.csv')
ko_data = pd.read_csv('analysis/한글_가사_토큰화.csv')

en_means = {
'unique_words_ratio' : en_data['unique_words_ratio'].mean(),
'bad_words_ratio': en_data['bad_words_ratio'].mean(),
'words_cnt': en_data['words_cnt'].mean()/30
}

import functions

en_stop_words = functions.en_common_words + ['hola', 'hoho', 'holla', 'leessang', 'yeh', 'vo', 'wah', 'thats', 'would', 'ru', 'ur']



# 페이지 제목
st.title("국내 래퍼 가사 분석")

# 부제목
st.header("최신 30곡에 기반한 분석을 제공합니다")

#########################################################################################################
def print_data(name):

    # en_data['artist_name']을 대소문자 구분 없이 비교하기 위해 upper() 사용
    index = artist['artist_name'].str.find(name)

    en = en_data [index != -1]



    from collections import Counter
    import plotly.express as px
    # 불용어를 제외한 단어 중 고빈도 단어를 제거하고 
    all_en_words = [ word.strip() for word in en['tokenized_lyrics'].iloc[0].split() ]
    unique_en_words = [word for word in all_en_words if (word not in en_stop_words) & (len(word) >=2 )] # 고빈도, 불용어 제거
    unique_en_counter = Counter (unique_en_words)
    en_top_words = [ item for item, value in unique_en_counter.most_common()]

    en_top_badwords = []
    try:
        en_bad_words = [ word.strip() for word in en['bad_words'].iloc[0].split() ]
        bad_en_counter = Counter(en_bad_words)
        en_top_badwords = [ item for item, value in bad_en_counter.most_common()]
    except:
        if len (en['bad_words'] ) == 0:
            en_bad_words = []
            en_top_badwords = []
    
    ###############################################################################################
    ###############################################################################################

    st.write(f"113명의 래퍼를 분석한 결과 한 곡에 평균 { int(en_means['words_cnt']) }개의 영어 단어를 사용합니다.")
    st.write(f"{name}은(는) 한 곡에 평균 { int(en['words_cnt'].iloc[0]/30) }개의 영어 단어를 사용합니다.")

    fig1 = px.bar ( x = [name, '평균'], y = [  int(en['words_cnt'].iloc[0]/30) , int(en_means['words_cnt'])] , 
                   title = '한 곡의 평균 영어 단어 수', color=['blue','skyblue'])
    # x축, y축 레이블 추가
    fig1.update_layout(
        xaxis_title=f"{name}과 래퍼 113인 평균의 비교",
        yaxis_title="한 곡의 평균 영어 단어 수",
        bargap=0.5
    )
    st.plotly_chart(fig1)

    st.divider()

    #############고 유 단 어 분 석 ################################################################

    st.write(f"113명의 래퍼를 분석한 결과 가장 흔하게 사용한 20개의 영어 단어는 다음과 같습니다.")
    st.write(f"{ ', '.join(functions.en_common_words[:20])}")

    if 'show_1' not in st.session_state:
        st.session_state.show_1 = False  # 텍스트가 처음엔 안 보이게 설정

    # 버튼 클릭 시 상태 토글
    if st.button("흔하게 사용한 단어 200개 더보기", key=f"button1_{name}"):
        st.session_state.show_1 = not st.session_state.show_1  # 상태 반전

    # 상태에 따라 텍스트 표시
    if st.session_state.show_1:
        st.write( f"{', '.join(functions.en_common_words)}")
    else:
        pass

    
    st.write(f"공통적으로 흔하게 사용한 200개의 영어 단어를 제외하고")
    st.write(f"{name}가(이) 고유하게 사용한 단어 중 빈도수 상위 20개 단어는 다음과 같습니다.")
    st.write(f"{', '.join(en_top_words[:20])}")

    if 'show_2' not in st.session_state:
        st.session_state.show_2 = False  # 텍스트가 처음엔 안 보이게 설정

    # 버튼 클릭 시 상태 토글
    if st.button(f"{name}가(이) 사용한 고유 단어 더보기", key=f"button2_{name}"):
        st.session_state.show_2 = not st.session_state.show_2  # 상태 반전

    # 상태에 따라 텍스트 표시
    if st.session_state.show_2:
        st.write( f"{', '.join(en_top_words)}")
    else:
        pass
    st.divider()

    #############고 유 단 어 비 율 분 석 ################################################################
    st.write(f"➡️{name}의 고유한 영어 단어 비율: {en['unique_words_ratio'].iloc[0]*100:.1f}% ({ int(en['unique_words_rank'].iloc[0])}위)")
    st.write( f"113명의 래퍼는 평균적으로 가사에 쓴 단어 중 {en_means['unique_words_ratio']*100:.1f}%가 고유한 단어입니다.")
    st.write("")

    ##############

    fig2 = px.bar ( x = [name, '평균'], y = [  en['unique_words_ratio'].iloc[0]*100 , en_means['unique_words_ratio']*100] , 
                   title = '고유 단어 비율', color=['blue','skyblue'])
    # x축, y축 레이블 추가
    fig2.update_layout(
        xaxis_title=f"{name}과 래퍼 113인 평균의 비교",
        yaxis_title="사용 단어 중 흔한 단어를 제외한 비율(%)",
        bargap=0.5
    )
    st.plotly_chart(fig2)
    st.divider()
    ##############비 속 어 분 석 #################################################################

    st.write(f"➡️{name}의 영어 단어 중 욕설의 비율: {en['bad_words_ratio'].iloc[0]*100:.1f}% ({ int( en['bad_words_rank'].iloc[0]) })")

    #################
    fig3 = px.bar ( x = [name, '평균'], y = [  en['bad_words_ratio'].iloc[0]*100 , en_means['bad_words_ratio']*100] , 
                   title = '비속어 비율', color=['blue','skyblue'])
    # x축, y축 레이블 추가
    fig3.update_layout(
        xaxis_title=f"{name}과 래퍼 113인 평균의 비교",
        yaxis_title="사용 단어 중 비속어의의 비율(%)",
        bargap=0.5
    )
    st.plotly_chart(fig3)

    #####################

    if len ( en_top_badwords ) == 0:
        st.write(f"{name}은(는) 최근 30곡에서 영어 비속어를 사용하지 않았습니다.")
    else:
        st.write(f"{name}가(이) 사용한 영어 비속어는 {', '.join(en_top_badwords)}입니다.")

    functions.generate_en_wordcloud(name, unique_en_counter)


#########################################################################################################


def main():
    # 텍스트
    st.write("안녕하세요, 달땅 컴퍼니에서 만든 국내 래퍼 가사 분석 프로그램입니다.")
    st.write("원하는 기능을 선택하세요.")

    # 세션 상태에서 input_artist와 one_artist를 설정 (없으면 초기값 설정)
    if 'input_artist' not in st.session_state:
        st.session_state.input_artist = ""
    if 'one_artist' not in st.session_state:
        st.session_state.one_artist = False
    if 'all_artist' not in st.session_state:
        st.session_state.all_artist = False

    # '검색하고 싶은 가수가 있습니다.' 버튼 클릭 시
    if st.button("검색하고 싶은 가수가 있습니다.") or st.session_state.one_artist:
        st.session_state.one_artist = True  # 버튼 클릭 상태를 False -> True 로 변경

        # 텍스트 입력창에서 가수 이름 입력
        st.session_state.input_artist = st.text_input(label="검색하고 싶은 가수 이름", value=st.session_state.input_artist).upper().strip()
        
        st.button("검색할 수 있는 가수 보기")

        if 'show_all_artists' not in st.session_state:
            st.session_state.show_all_artists = False  # 텍스트가 처음엔 안 보이게 설정

        # 버튼 클릭 시 상태 토글
        if st.button(f"검색할 수 있는 가수 보기", key=f"show_all_artists"):
            st.session_state.show_all_artists = not st.session_state.show_all_artists  # 상태 반전

        # 상태에 따라 텍스트 표시
        if st.session_state.show_all_artists:
            st.write( f"{', '.join( artist['artist_name'].sort() )}")
        else:
            pass

        # 입력된 값이 있을 경우 처리
        if st.session_state.input_artist:

            # 가수 이름 검색 (대소문자 구분 없이)
            find_artist = artist[artist['artist_name'].str.upper() == st.session_state.input_artist]
            if not find_artist.empty:
                st.title(f"✨{st.session_state.input_artist}의 정보")
                
                name = str ( find_artist['artist_name'].to_list() )
                name = name[2:-2]
                print_data(name)
                
                
            else:
                # 유사한 이름으로 검색
                find_artist_similar = artist[artist['similar_name'].str.upper() == st.session_state.input_artist]
                
                if not find_artist_similar.empty:
                    name = str ( find_artist_similar['artist_name'].to_list() )
                    name = name[2:-2]
                    st.title(f"✨{name}의 정보")
                    print_data(name)
                    
                else:
                    st.title("해당 가수를 찾을 수 없습니다.")
    else:
        # '모든 가수의 분석 결과를 보고 싶습니다.' 버튼 클릭 시
        if st.button("모든 가수의 분석 결과를 보고 싶습니다.") or st.session_state.all_artist:
            st.session_state.all_artist = True  # 버튼 클릭 상태를 True로 변경

            st.write("모든 가수의 데이터의 그래프를 출력합니다.")
            st.write("영어 어휘 다양도와 비속어 비율입니다.")

            # 그래프 생성
            st.title("모든 래퍼 데이터")
            fig_en = functions.generate_en_map()  # 함수 실행 후 figure 리턴 받기
            st.pyplot(fig_en)

main()
