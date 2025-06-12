# %%
import requests
import re
import pandas as pd

# %%
import os
from dotenv import load_dotenv

load_dotenv()

# %%
api_key = os.getenv("lechat_api_key")

# %%
# api_key = "TqwpZsnTmT1WQG5A6T3fzDomj4PwZ0hn" # Replace with your actual API key

# %%
def ask_le_chat(api_key, question, temperature=0.7):
    api_endpoint = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-tiny", # or another engine if available
        "messages": [{"role": "user", "content": question}],
        "temperature": temperature
    }

    try:
        response = requests.post(api_endpoint, headers=headers, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Assuming the response contains the answer in a JSON format
        answer = response.json()
        return answer.get('choices', [{}])[0].get('message', {}).get('content', 'No answer found')

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# %%
# 1. 확률 답변 요청

question = """
2025년 5월 1일부터 오늘까지의 한글/영문/중문문 기사 중 원/달러 환율과 달러화지수를 조사한 후,
답변은 한국 원화의 통화가치가 상승할 확률과 한국 원화의 통화 가치가 하락할 확률 숫자만 보여주세요.
예시) 한국 원화의 통화가치가 상승할 확률: 70%, 하락 확률: 30%
"""

# %%
answers = []
for i in range(10):
    answer = ask_le_chat(api_key, question, temperature=0.9)
    answers.append(answer)
    print(answer)


# %%
def extract_first_two_percent_values(text):
    """
    주어진 텍스트에서 앞에 등장하는 두 개의 '숫자%' 값을 찾아 숫자(int)로 반환합니다.
    
    Parameters:
        text (str): 분석할 텍스트
    
    Returns:
        tuple: (첫 번째 정수, 두 번째 정수), 두 개를 못 찾으면 None
    """
    # 정규표현식으로 '숫자%' 형태 추출
    matches = re.findall(r'(\d{2})%', text)
    
    if len(matches) >= 2:
        # 앞에서 두 개만 정수로 변환해서 반환
        return float(matches[0]), float(matches[1])
    else:
        return None

# %%
answers_float = []
for text in answers:
    if text is not None:
        temp = extract_first_two_percent_values(text)
        if temp is not None and temp[0] + temp[1] == 100:
            answers_float.append(temp)

# %%
answers_float

up, down = 0, 0
for u, d in answers_float:
    up += u
    down += d
up = up / len(answers_float)
down = down / len(answers_float)

answers_float.append((round(up, 1), round(down, 1)))
answers_float

# %%
pd.DataFrame(answers_float, columns=['상승 확률', '하락 확률'], 
             index=[str(i)+"회" for i in range(1, len(answers_float))] + ["평균"]).to_csv("환율_확률_결과.csv", encoding='utf-8')

# %%


# %%

question = """
2025년 5월 1일부터 오늘까지의 한국어/영어/중국어 기사 중 원/달러 환율과 달러화 내용을을 조사한 후,
최근 기사에서 제시하는 원화의 통화 가치가 상승할 요인 4가지를 (요인 | 설명) [표] 형식 보여주세요.
"""

for i in range(5):
    answer = ask_le_chat(api_key, question, temperature=0.2)
    if "| --- | --- |" in answer:
        break

print(answer)

# %%
contents = []
for i, text in enumerate(answer.split("\n")):
    if i == 0:
        continue
    if "| --- | --- |" in text:
        continue
    if "|" in text:
        temp = text.split("|")[1:3]
        contents.append(temp)

# %%
pd.DataFrame(contents, columns=['요인', '설명']).to_csv("원화_강세_요인.csv", encoding='utf-8', index=False)

# %%
question = """
2025년 5월 1일부터 오늘까지의의 한국어/영어/중국어 기사 중 원/달러 환율과 달러화 내용을을 조사한 후,
최근 기사에서 제시하는 원화의 통화 가치가 하락할 요인 4가지를 (요인 | 설명) [표] 형식 보여주세요.
"""

for i in range(5):
    answer = ask_le_chat(api_key, question, temperature=0.2)
    if "| --- | --- |" in answer:
        break

print(answer)

# %%
contents = []
for i, text in enumerate(answer.split("\n")):
    if i == 0:
        continue
    if "| --- | --- |" in text:
        continue
    if "|" in text:
        temp = text.split("|")[1:3]
        contents.append(temp)

# %%
pd.DataFrame(contents, columns=['요인', '설명']).to_csv("원화_약세_요인.csv", encoding='utf-8', index=False)


