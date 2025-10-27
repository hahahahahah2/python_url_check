import pandas as pd
import requests
from selectolax.parser import HTMLParser
from urllib3.util.retry import Retry
from tqdm.auto import tqdm
import tkinter as tk
from tkinter import filedialog

# 파일 가져오기
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfile().name

# 컬럼명
SHEET = input('시트명 입력: ')
CID = input('컨텐츠 ID 컬럼명 입력 (없으면 Enter): ')
CURL = input('컨텐츠 URL 컬럼명 입력 (없으면 Enter): ')

df = pd.read_excel(file_path, sheet_name=SHEET, dtype={CID:str, CURL:str})

print(f'{"OPEN FILE":=^50}')
print(df.head(), df.shape)

# 타이틀 가져오는 함수
def get_contents_title(contents_id:str, contents_url:str=""):
    try:
        url = contents_url if contents_url else f"https://www.lge.co.kr/support/solutions-{contents_id}"
        response = session.get(url)
        title = HTMLParser(response.text).head.css_first('title').text()
        title = title.replace("&amp;", "&")
        title = title.replace('&#039;', "'")
        title = title.replace('&#034;', "'")
    except Exception as err:
        title = err
    return title

# maxretry 에러 방지를 위한 세션 설정
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = requests.adapters.HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 컨텐츠 TITLE 수집
print(f'{"checking URLs":=^50}')
urls = list(set(df[CURL])) if CURL else [f'https://www.lge.co.kr/support/solutions-{cid}' for cid in set(df[CID])]
titles = []
for contents_url in tqdm(urls):
    titles.append(get_contents_title("", contents_url))

# 최종파일 생성
print(f'{"Framing":.^50}')
df_ctt = pd.DataFrame({"contents_URL":urls, "contents_title_check":titles})
df_ctt['contents_ID'] = df_ctt['contents_URL'].str[40:]
df_ctt['contents_title_check'] = df_ctt.contents_title_check.str.replace(r" \| (스스로 해결|고객지원|LG전자)", "", regex=True)
df_ctt = df_ctt[['contents_ID', 'contents_URL', 'contents_title_check']]

# 저장
res_path = f"{file_path.strip('.xlsx')}_{CURL}컨텐츠유효성체크.xlsx"
df_ctt.to_excel(res_path, index=False)
print(res_path)

input("종료하시려면 Enter 키를 눌러주세요: ")