import streamlit as st

usdkrw = st.Page("usdkrw.py", title="원/달러 환율", icon = "💲")
nickel = st.Page("nickel.py", title="LME 니켈", icon ="🪨")

pg = st.navigation([usdkrw, nickel])
pg.run()