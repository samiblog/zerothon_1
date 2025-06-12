# %%
import requests
import pymysql
import pandas as pd

# %%
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ecos_api_key")

# %%
# api_key ="R5F7XNV1FNRFT738YRKU"

# %%
# 원/달러 환율 조회
STAT_CODE = "731Y003"
ITEM_NAME1 = "0000003"

# %%
# URL 생성성
url = f"http://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/1000/{STAT_CODE}/D/20250601/20250612/{ITEM_NAME1}/"

# %%
# 요청 보내기
response = requests.get(url)

# 응답 확인
if response.status_code == 200:
    data = response.json()  # JSON -> Python dict
    rows = data['StatisticSearch']['row']  # 실제 데이터 위치

    # 4. DataFrame으로 변환
    df = pd.DataFrame(rows)
    df = df[["TIME", "DATA_VALUE"]]  # 필요한 열만 선택

    # # 5. 결과 출력
    # print(df.head())
else:
    print("데이터 요청 실패:", response.status_code)

# %%
# 날짜 포맷 변경 (YYYY-MM-DD)
df['date'] = pd.to_datetime(df['TIME'], format='%Y%m%d').dt.date
df['value'] = df['DATA_VALUE']
df['item'] = 'KRW'

# %%
df = df[['date', 'value', 'item']]
df

# %%
host = os.getenv("db_host")
user = os.getenv("db_user")
password = os.getenv("db_password")
database = os.getenv("db_database")

# %%
# DB 연결 설정
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    charset='utf8mb4',
    autocommit=True
)


# %%
# 데이터베이스에 저장
try:
    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            # 먼저 존재 여부 확인
            check_sql = """
                SELECT COUNT(*) FROM ECOS
                WHERE date = %s AND item = %s
            """
            cursor.execute(check_sql, (row['date'], row['item']))
            count = cursor.fetchone()[0]

            if count > 0:
                # 존재하면 UPDATE
                update_sql = """
                    UPDATE ECOS
                    SET value = %s
                    WHERE date = %s AND item = %s
                """
                cursor.execute(update_sql, (row['value'], row['date'], row['item']))
            else:
                # 존재하지 않으면 INSERT
                insert_sql = """
                    INSERT INTO ECOS (date, value, item)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_sql, (row['date'], row['value'], row['item']))

finally:
    conn.close()


