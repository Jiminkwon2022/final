import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib
from io import BytesIO
import matplotlib.font_manager as fm

def get_stock_info(market_type = None):
    base_url= "http://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"
    if market_type == 'kospi':
        marketType = "stockMkt"
    elif market_type == 'kosdaq':
        marketType = "kosdaqMkt"
    elif market_type == None:
        marketType = ""
    url= "{0}?method={1}&marketType={2}".format(base_url, method, marketType)

    df = pd.read_html(url, header=0)[0]

    df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06d}")

    df = df[['회사명', '종목코드']]

    return df

def get_ticker_symbol(company_name, market_type):
    df = get_stock_info(market_type)
    code = df[df['회사명']==company_name]['종목코드'].values
    code = code[0]

    if market_type == 'kospi':
        ticker_symbol = code + ".KS"
    elif market_type == 'kosdaq':
        ticker_symbol = code + ".KQ"
    
    return ticker_symbol

st.title("주식 정보를 가져오는 웹 앱")

radio_options = ['코스피', '코스닥']
radio_selected = st.sidebar.radio('증권시장', radio_options)
st.sidebar.header("회사 이름과 기간 입력")

stock_name = st.sidebar.text_input('회사 이름', value="NAVER")
date_range = st.sidebar.date_input("시작일과 종료일", 
                [datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)])

clicked = st.sidebar.button("주가 데이터 가져오기")
if clicked:
    market_type = 'kospi'
    if radio_selected == '코스닥':
        market_type = 'kosdaq'
        
if(clicked == True):
    ticker_symbol = get_ticker_symbol(stock_name, "kospi")
    ticker_data = yf.Ticker(ticker_symbol)
    
    start_p = date_range[0]
    end_p = date_range[1] + datetime.timedelta(days=1)
    
    df = ticker_data.history(start=start_p, end=end_p)
    
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.head())

    fontprop = fm.FontProperties(fname='NanumGothic.ttf', size=18)
    matplotlib.rcParams['axes.unicode_minus'] = False

    ax = df['Close'].plot(grid=True, figsize=(15,5))
    ax.set_title("주가(종가) 그래프", fontsize=30)
    ax.set_xlabel("기간", fontsize=20)
    ax.set_ylabel("주가(원)", fontsize = 20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    fig = ax.get_figure()
    st.pyplot(fig)

    st.markdown("**주가 데이터 파일 다운로드**")
    csv_data = df.to_csv()

    excel_data = BytesIO()
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df.set_index('Date', inplace = True)
    df.to_excel(excel_data)

    columns = st.columns(2)
    with columns[0]:
        st.download_button("CSV 파일 다운로드", csv_data, file_name='stock_data.csv')
    with columns[1]:
        st.download_button("엑셀 파일 다운로드", excel_data, file_name='stock_data.xlsx')
