# %%
from fredapi import Fred
import pandas as pd
# import glob
import pymysql

# %%
import os
from dotenv import load_dotenv

load_dotenv()

# %%
api_key = os.getenv("fred_api_key")

# %%
# api_key = "ae5480bbc5e84829fa0b4bf032c59e32"

# %%
# csv_files = glob.glob("DATA/*.csv")

# %%
# csv_files

# %%
# fred_tickers = [csv.replace("DATA\\", "").replace(".csv", "").replace("FRED_", "") for csv in csv_files if "FRED" in csv ]

# %%
fred_tickers = ['DCOILWTICO', 'DEXCHUS', 'DEXJPUS', 'DEXUSEU', 'DGS10', 'DTWEXBGS', 'SP500']

# %%
fred = Fred(api_key=api_key)

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
def update_or_insert_db(df, conn):
    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            # 먼저 존재 여부 확인
            check_sql = """
                SELECT COUNT(*) FROM FRED
                WHERE date = %s AND item = %s
            """
            cursor.execute(check_sql, (row['date'], row['item']))
            count = cursor.fetchone()[0]

            if count > 0:
                # 존재하면 UPDATE
                update_sql = """
                    UPDATE FRED
                    SET value = %s
                    WHERE date = %s AND item = %s
                """
                cursor.execute(update_sql, (row['value'], row['date'], row['item']))
                print("update", row['value'], row['date'], row['item'])
            else:
                # 존재하지 않으면 INSERT
                insert_sql = """
                    INSERT INTO FRED (date, value, item)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_sql, (row['date'], row['value'], row['item']))
                print("insert", row['value'], row['date'], row['item'])


# %%
for fred_ticker in fred_tickers:
    # FRED API를 통해 데이터 가져오기
    fdata = fred.get_series(observation_start="2025-06-01", series_id=fred_ticker)
    df = pd.DataFrame({"date": fdata.index, "value": fdata.values, "item": fred_ticker})
    update_or_insert_db(df, conn)
    # print(df.tail())

# %%
conn.close()


