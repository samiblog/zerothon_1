import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# rp 데이터 가져오기
rp = pd.read_csv("1_RP_data.txt", sep='\t')
nickel = rp[rp['지표'] == 'LME 니켈'].copy()
nickel.drop(columns='지표', inplace = True)
nickel.set_index('시나리오', inplace = True)
#st.write(nickel)

#daily 니켈 데이터 가져오기
daily_nickel = pd.read_csv("/Users/hye/Desktop/Zerothon/wx/XBBG_NICKEL.csv")
daily_nickel['date']=pd.to_datetime(daily_nickel['date'])
daily_nickel = daily_nickel[daily_nickel['date']>='2024-01-01']
daily_nickel.drop(columns='name', inplace=True)
#st.write(daily_nickel)

#rp 데이터를 일간으로 늘리기
# 날짜 문자열 → datetime 변환
cols = pd.to_datetime(nickel.columns)

# 결과 저장용 리스트
daily_rows = []

# 각 시나리오별로 처리
for scenario in nickel.index:
    for i in range(len(cols)):
        start_date = cols[i]
        if i + 1 < len(cols):
            end_date = cols[i + 1] - pd.Timedelta(days=1)
        else:
            # 마지막 분기의 경우 → 현재 분기 시작일 기준으로 "해당 분기 말일" 계산
            end_date = (start_date + pd.offsets.QuarterEnd(0))  # ex: 2026-01-01 → 2026-03-31
        price = nickel.loc[scenario, str(start_date.date())]
        
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

st.subheader("🔎 LME 니켈 가격 전망 모니터링")
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
fig.add_trace(go.Scatter(
    x=daily_nickel['date'],
    y=daily_nickel['value'],
    mode='lines',
    name='실적',
    line=dict(color='grey', width=1)
))

fig.update_layout(
    xaxis_title="date",
    yaxis=dict(
        title="가격($/톤)",
        tickformat=',.0f'
    ),
    template="plotly_white", #흰 배경 밝은 테마
    legend_title="구분",  #범례
    hovermode="x unified"  #x축에 올렸을때 x값이 같은 모든 trace의 정보를 표시
)

st.plotly_chart(fig, use_container_width=True)
st.divider()


st.subheader("🔎 최근 원자재 시장을 반영한 LME 니켈 가격 급등락 가능성")


st.divider()
st.subheader("🔎 생성형 AI를 반영한 향후 LME 니켈 가격 시장 반응 ")
ai_nickel=pd.read_csv("니켈_확률_결과.csv")
ai_nickel.columns = ai_nickel.columns.str.strip()
ai_nickel = ai_nickel.rename(columns={ai_nickel.columns[0]:'회차'})

avg_row = ai_nickel[ai_nickel['회차']=='평균']
ai_nickel_plot = ai_nickel[ai_nickel['회차']!='평균'].copy()

avg_rise = avg_row['상승 확률'].values[0]
avg_fall = avg_row['하락 확률'].values[0]

col1, col2 = st.columns(2)
col1.metric("📈 평균 상승 확률", f"{avg_rise:.1f}%")
col2.metric("📉 평균 하락 확률", f"{avg_fall:.1f}%")

fig2 = go.Figure()
fig2.add_trace(go.Bar(x=ai_nickel_plot['회차'], y=ai_nickel_plot['상승 확률'], name='상승 확률', marker_color='royalblue'))
fig2.add_trace(go.Bar(x=ai_nickel_plot['회차'], y=ai_nickel_plot['하락 확률'], name='하락 확률', marker_color='indianred'))

fig2.update_layout(
    barmode='group',
    title='회차별 상승/하락 확률 비교',
    xaxis_title='회차',
    yaxis_title='확률 (%)',
    yaxis=dict(tickformat=',.0f'),
    template='plotly_white',
    legend_title='구분'
    )

st.plotly_chart(fig2, use_container_width=True)
##########################################################
nickel_up = pd.read_csv("니켈_상승_요인.csv")

st.markdown("📈 향후 LME 니켈 가격이 상승할 수 있는 요인은 아래와 같습니다.")
for idx, row in nickel_up.iterrows():
    with st.expander(f"{row['요인']}"):
        st.markdown(row['설명'])
    
nickel_down = pd.read_csv("니켈_약세_요인.csv")

st.markdown("📉 향후 LME 니켈 가격이 하락할 수 있는 요인은 아래와 같습니다.")
for idx, row in nickel_down.iterrows():
    with st.expander(f"{row['요인']}"):
        st.markdown(row['설명'])


#환율 전망 모니터링
#주요 지표 연관관계
#최근 금융시장을 반영한 급등락 가능성
#생성형 AI를 반영한 시장 반응