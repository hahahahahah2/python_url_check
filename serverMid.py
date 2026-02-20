return await error(ws, "당신의 턴이 아닙니다.")
    if now() > room.deadline:
        return await eliminate_current_player(room, "시간초과")

    w = normalize(word)
    if len(w) < 2:
        return await error(ws, "단어가 너무 짧습니다.")
    if w in room.used_words:
        return await eliminate_current_player(room, "중복 단어")

    # 첫 단어는 아무 글자나 OK
    if room.current_word is not None:
        prev_last = last_char(room.current_word)
        nxt_first = first_char(w)
        if not chain_ok(prev_last, nxt_first):
            return await eliminate_current_player(room, "끝말잇기(두음) 규칙 위반")

    room.current_word = w
    room.used_words.add(w)
    await system(room, f"{find_player(room, pid).name}: {w}")

    room.turn_idx = next_alive_idx(room, room.turn_idx)
    room.deadline = now() + TURN_SECONDS
    await broadcast(room, state_payload(room))


# =========================
#  HTTP / WebSocket
# =========================
@app.get("/create_room")
def create_room():
    rid = secrets.token_urlsafe(4)  # 짧은 방 코드
    rooms[rid] = Room(rid=rid)
    return {"rid": rid}

@app.websocket("/ws/{rid}")
async def ws_room(ws: WebSocket, rid: str):
    await ws.accept()
    room = get_room(rid)

    pid = secrets.token_urlsafe(8)

    try:
        # 첫 메시지 join
        raw = await ws.receive_text()
        data = json.loads(raw)
        if data.get("type") != "join":
            await error(ws, "첫 메시지는 join이어야 합니다.")
            await ws.close()
            return

        name = (data.get("name") or "").strip()[:20]
        if not name:
            await error(ws, "이름이 필요합니다.")
            await ws.close()
            return

        room.players.append(Player(pid=pid, name=name))
        room.sockets[pid] = ws

        await system(room, f"{name} 입장")
        await ws.send_text(json.dumps({"type": "joined", "pid": pid, "rid": rid}, ensure_ascii=False))
        await broadcast(room, state_payload(room))

        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            t = data.get("type")

            if t == "start":
                # ✅ 누구나 start 가능
                await start_game(room)

            elif t == "submit":
                await handle_submit(room, pid, data.get("word", ""), ws)

            elif t == "ping":
                await ws.send_text(json.dumps({"type": "pong"}, ensure_ascii=False))

            else:
                await error(ws, "알 수 없는 메시지 타입입니다.")

    except WebSocketDisconnect:
        room.sockets.pop(pid, None)
        try:
            p = find_player(room, pid)
            await system(room, f"{p.name} 연결 끊김")
        except Exception:
            pass
