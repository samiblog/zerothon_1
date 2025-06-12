import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# rp 데이터 가져오기
rp = pd.read_csv("1_RP_data.txt", sep='\t')
usdkrw = rp[rp['지표'] == '원/달러'].copy()
usdkrw.drop(columns='지표', inplace = True)
usdkrw.set_index('시나리오', inplace = True)
#st.write(usdkrw)

#daily 환율 데이터 가져오기
def load_file():
    d_usdkrw = pd.read_csv("/Users/hye/Desktop/Zerothon/wx/ECOS_KRW.csv")
    d_usdjpy = pd.read_csv("/Users/hye/Desktop/Zerothon/wx/FRED_DEXJPUS.csv")
    d_usdcny = pd.read_csv("/Users/hye/Desktop/Zerothon/wx/XBBG_CNY.csv")
    d_eurusd = pd.read_csv("/Users/hye/Desktop/Zerothon/wx/FRED_DEXUSEU.csv")
    d_usd = pd.read_csv("/Users/hye/Desktop/Zerothon/wx/XBBG_DXY.csv")
    
    for df in [d_usdkrw, d_usdjpy, d_usdcny, d_eurusd, d_usd]:
        if 'name' in df.columns:
            df.drop(columns='name', inplace=True)

    for df in [d_usdkrw, d_usdjpy, d_usdcny, d_eurusd, d_usd]:
            df['date'] = pd.to_datetime(df['date'])
    
    d_usdkrw.rename(columns={'value':'USD/KRW'}, inplace=True)
    d_usdjpy.rename(columns={'value':'USD/JPY'}, inplace=True)
    d_usdcny.rename(columns={'value':'USD/CNY'}, inplace=True)
    d_eurusd.rename(columns={'value':'EUR/USD'}, inplace=True)
    d_usd.rename(columns={'value':'Dollar Index'}, inplace=True)
    
    for df in [d_usdkrw, d_usdjpy, d_usdcny, d_eurusd, d_usd]:
        df.set_index('date', inplace=True)
    
    merged = pd.concat([d_usdkrw, d_usdjpy, d_usdcny, d_eurusd, d_usd], axis=1)
    merged.reset_index(inplace=True)
    
    return merged

exchange = load_file()
exchange = exchange[exchange['date']>='1999-01-04']
exchange = exchange.ffill()
#st.write(exchange)



#rp 데이터를 일간으로 늘리기
# 날짜 문자열 → datetime 변환
cols = pd.to_datetime(usdkrw.columns)

# 결과 저장용 리스트
daily_rows = []

# 각 시나리오별로 처리
for scenario in usdkrw.index:
    for i in range(len(cols)):
        start_date = cols[i]
        if i + 1 < len(cols):
            end_date = cols[i + 1] - pd.Timedelta(days=1)
        else:
            # 마지막 분기의 경우 → 현재 분기 시작일 기준으로 "해당 분기 말일" 계산
            end_date = (start_date + pd.offsets.QuarterEnd(0))  # ex: 2026-01-01 → 2026-03-31
        price = usdkrw.loc[scenario, str(start_date.date())]
        
        # 날짜 범위 생성 (일간)
        for dt in pd.date_range(start_date, end_date, freq='D'):
            daily_rows.append({
                "date": dt,
                "price": price,
                "scenario": scenario
            })

# 최종 일간 DataFrame 생성
daily_rp = pd.DataFrame(daily_rows)
#st.write(daily_rp)

st.subheader("🔎 원/달러 환율 전망 모니터링")
fig = go.Figure()

for scenario in daily_rp['scenario'].unique():
    df_scn = daily_rp[daily_rp['scenario'] == scenario]
    fig.add_trace(go.Scatter(
        x=df_scn['date'],
        y=df_scn['price'],
        mode='lines',
        name=f"시나리오: {scenario}"
    ))

# 실적 라인 추가
exchange_rp = exchange[exchange['date']>='2024-01-01']
fig.add_trace(go.Scatter(
    x=exchange_rp['date'],
    y=exchange_rp['USD/KRW'],
    mode='lines',
    name='실적',
    line=dict(color='grey', width=1)
))

fig.update_layout(
    xaxis_title="date",
    yaxis=dict(
        title="USD/KRW",
        tickformat=',.0f'
    ),
    template="plotly_white", #흰 배경 밝은 테마
    legend_title="구분",  #범례
    hovermode="x unified"  #x축에 올렸을때 x값이 같은 모든 trace의 정보를 표시
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("💰 원/달러 환율과 기타 주요 통화의 연관성")
option = [col for col in exchange.columns if col not in ['date','USD/KRW']]
selected = st.selectbox("📌 궁금한 통화를 선택하세요",option)

fig2 = go.Figure()

# 왼쪽 y축: USD/KRW
fig2.add_trace(go.Scatter(
    x=exchange['date'],
    y=exchange['USD/KRW'],
    name='USD/KRW',
    yaxis='y1',
    line=dict(color='royalblue')
))

# 오른쪽 y축: 선택한 통화
fig2.add_trace(go.Scatter(
    x=exchange['date'],
    y=exchange[selected],
    name=selected,
    yaxis='y2',
    line=dict(color='green')
))

# 4. 레이아웃 설정 (이중 y축)
fig2.update_layout(
    title=f"USD/KRW vs {selected}",
    xaxis=dict(title='date'),
    yaxis=dict(
        title=dict(text='USD/KRW', font=dict(color='royalblue')),
        tickfont=dict(color='black'),
        tickformat=',.0f',
        showgrid =False
    ),
    yaxis2=dict(
        title=dict(text=selected, font=dict(color='green')),
        tickfont=dict(color='black'),
        overlaying='y',
        side='right',
        tickformat=',.2f',
        showgrid = False
    ),
    legend=dict(x=0.75, y=0.99, bgcolor='rgba(255,255,255,0)', borderwidth =0),
    template='plotly_white',
    hovermode='x unified'
)

st.plotly_chart(fig2, use_container_width=True)



st.divider()
st.subheader("🔎 최근 금융 시장을 반영한 원/달러 환율 급등락 가능성")


st.divider()


st.subheader("🔎 생성형 AI를 반영한 향후 원화 가치 변동 시장 반응 ")
ai_usdkrw=pd.read_csv("환율_확률_결과.csv")
ai_usdkrw.columns = ai_usdkrw.columns.str.strip()
ai_usdkrw = ai_usdkrw.rename(columns={ai_usdkrw.columns[0]:'회차'})

avg_row = ai_usdkrw[ai_usdkrw['회차']=='평균']
ai_usdkrw_plot = ai_usdkrw[ai_usdkrw['회차']!='평균'].copy()

avg_rise = avg_row['상승 확률'].values[0]
avg_fall = avg_row['하락 확률'].values[0]

col1, col2 = st.columns(2)
col1.metric("📈 평균 상승 확률", f"{avg_rise:.1f}%")
col2.metric("📉 평균 하락 확률", f"{avg_fall:.1f}%")

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=ai_usdkrw_plot['회차'], y=ai_usdkrw_plot['상승 확률'], name='상승 확률', marker_color='royalblue'))
fig4.add_trace(go.Bar(x=ai_usdkrw_plot['회차'], y=ai_usdkrw_plot['하락 확률'], name='하락 확률', marker_color='indianred'))

fig4.update_layout(
    barmode='group',
    title='회차별 상승/하락 확률 비교',
    xaxis_title='회차',
    yaxis_title='확률 (%)',
    yaxis=dict(tickformat=',.0f'),
    template='plotly_white',
    legend_title='구분'
    )

st.plotly_chart(fig4, use_container_width=True)
##########################################################
nickel_up = pd.read_csv("원화_강세_요인.csv")

st.markdown("📈 향후 원화 가치 강세 요인은 아래와 같습니다.")
for idx, row in nickel_up.iterrows():
    with st.expander(f"{row['요인']}"):
        st.markdown(row['설명'])
    
nickel_down = pd.read_csv("원화_약세_요인.csv")

st.markdown("📉 향후 원화 가치 약세 요인은 아래와 같습니다.")
for idx, row in nickel_down.iterrows():
    with st.expander(f"{row['요인']}"):
        st.markdown(row['설명'])




