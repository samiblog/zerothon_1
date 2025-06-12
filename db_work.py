# %%
import pandas as pd

# %%
import glob

csv_files = glob.glob("DATA/*.csv")

# %%
data_list = []
for csv in csv_files:
    csv = csv.replace('.csv', '')
    tname = csv.split('\\')[-1]
    dbname = tname.split('_')[0]
    itemname = tname.split('_')[1]
    data_list.append({
        'dbname': dbname,
        'itemname': itemname,
    })


# %%
data_list

# %%
df = pd.read_csv(csv_files[0], parse_dates=["date"])
df.dtypes

# %%
df

# %%
import pymysql

# %%
import os
from dotenv import load_dotenv

load_dotenv()

# %%
host = os.getenv("db_host")
user = os.getenv("db_user")
password = os.getenv("db_password")
database = os.getenv("db_database")

# %%
# 2. DB 접속 정보
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()


# %%


# %%
def insert_dataframe_to_mysql(table_name: str, df: pd.DataFrame, conn):
    """
    DataFrame을 MySQL에 삽입하는 함수.
    테이블이 없으면 생성하고, 있으면 그대로 INSERT 수행.
    
    :param table_name: 생성 또는 삽입할 테이블 이름
    :param df: pandas DataFrame (columns: date, value, item)
    :param conn: pymysql 커넥션 객체
    """
    cursor = conn.cursor()

    # 1. 테이블 존재 여부 확인
    check_sql = """
        SELECT COUNT(*) AS count 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() AND table_name = %s
    """
    cursor.execute(check_sql, (table_name,))
    result = cursor.fetchone()

    # 2. 테이블이 없다면 생성
    if result["count"] == 0:
        create_sql = f"""
        CREATE TABLE {table_name} (
            date DATE,
            value DOUBLE,
            item VARCHAR(255)
        )
        """
        cursor.execute(create_sql)

    # 3. 데이터 INSERT
    insert_sql = f"INSERT INTO {table_name} (date, value, item) VALUES (%s, %s, %s)"
    records = list(df.itertuples(index=False, name=None))  # 튜플 리스트
    cursor.executemany(insert_sql, records)

    conn.commit()
    cursor.close()

# %%
csv_files, data_list

# %%
for csv_path, data_info in zip(csv_files, data_list):
    df = pd.read_csv(csv_path, parse_dates=["date"])
    insert_dataframe_to_mysql(data_info["dbname"], df, conn)


# %%

conn.close()

# %%
pd.read_csv("http://10.1.13.178:5000/fred/DTWEXBGS/")

# %%



