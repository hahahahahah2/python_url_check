from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles




#맨아래
@app.get("/", response_class=HTMLResponse)
def serve_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()



서버 실행
Bash
코드 복사
uvicorn server:app --host 0.0.0.0 --port 8000
방 생성
코드 복사

http://서버IP:8000/create_room
동료들한테 공유
코드 복사

http://서버IP:8000
끝.
🔥 회사에서 실제로 쓰려면
같은 와이파이/사내망이면
👉 네 PC IP 주소로 접속 가능
예:
코드 복사

192.168.0.15:8000
IP 확인:
Windows → ipconfig
Mac → ifconfig
