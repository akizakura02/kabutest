import yfinance as yf
import pandas as pd
import altair as alt
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数', 1, 50, 20)

st.write(f"""
## 過去 **{days}日間** のGAFA株価
""")

@st.cache   #キャッシュにためておく
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')	#フォーマットの日付が変更できる
        hist = hist[['Close']]			#終値のみ参照する
        hist.columns = [company]		#会社名をcolumnsに登録
        hist = hist.T				#行と列を入れ替える
        hist.index.name = 'Name'		#index名にNameを追加する
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。', 
        0.0, 3500.0, (0.0, 3500.0)
    )

    tickers = {
      'apple': 'AAPL',
      'facebook': 'FB',
      'google': 'GOOGL',
      'microsoft': 'MSFT',
      'netflix': 'NFLX',
      'amazon': 'AMZN'
    }
    df = get_data(days, tickers)

    companies = st.multiselect(
        '会社名を選択してください',
       list(df.index),
        ['google', 'amazon', 'facebook', 'apple']   #デフォルトの表示
    )

    if not companies:
        st.error('少なくとも1社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )