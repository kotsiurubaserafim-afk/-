import socket
import json
import threading
import random

HOST = '127.0.0.1'
PORT = 5555
ROWS, COLS = 11, 15

players = {}
winners = []
lock = threading.Lock()

def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    def walk(x, y):
        maze[y][x] = 0
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx*2, y + dy*2
            if 0 < nx < cols-1 and 0 < ny < rows-1 and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                walk(nx, ny)
    walk(1, 1)
    maze[rows-2][cols-2] = 2
    lx, ly = 1, 1
    while (lx, ly) == (1, 1) or (lx, ly) == (cols-2, rows-2) or maze[ly][lx] != 0:
        lx, ly = random.randint(1, cols-2), random.randint(1, rows-2)
    maze[ly][lx] = 4
    def is_reachable(tx, ty):
        q, v = [(1, 1)], set([(1, 1)])
        while q:
            cx, cy = q.pop(0)
            if (cx, cy) == (tx, ty): return True
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= ny < rows and 0 <= nx < cols and maze[ny][nx] != 1 and maze[ny][nx] != 3 and (nx, ny) not in v:
                    v.add((nx, ny)); q.append((nx, ny))
        return False
    t_add = 6
    while t_add > 0:
        tx, ty = random.randint(1, cols-2), random.randint(1, rows-2)
        if maze[ty][tx] == 0 and (tx, ty) != (1, 1):
            maze[ty][tx] = 3
            if is_reachable(lx, ly) and is_reachable(cols-2, rows-2): t_add -= 1
            else: maze[ty][tx] = 0
    return maze

MAZE = generate_maze(ROWS, COLS)

def handle_client(conn, addr):
    global MAZE, winners
    addr_str = str(addr)
    try:
        data = conn.recv(1024).decode('utf-8')
        p_name = json.loads(data).get("name", "Гість")
    except: p_name = "Гість"

    with lock:
        players[addr_str] = {"x": 1, "y": 1, "finished": False, "name": p_name}

    try:
        while True:
            data = conn.recv(2048).decode('utf-8')
            if not data: break
            req = json.loads(data)
            
            with lock:
                # Команда на перезапуск
                if req.get("type") == "reset":
                    MAZE = generate_maze(ROWS, COLS)
                    winners = []
                    for p in players.values():
                        p["x"], p["y"], p["finished"] = 1, 1, False
                
                # Обробка руху
                elif not players[addr_str]["finished"]:
                    dx, dy = req.get("dx", 0), req.get("dy", 0)
                    curr = players[addr_str]
                    nx, ny = curr['x'] + dx, curr['y'] + dy
                    if 0 <= ny < len(MAZE) and 0 <= nx < len(MAZE[0]) and MAZE[ny][nx] != 1:
                        cell = MAZE[ny][nx]
                        players[addr_str]['x'], players[addr_str]['y'] = nx, ny
                        if cell == 3: players[addr_str]['x'], players[addr_str]['y'] = 1, 1
                        if cell == 4:
                            for r in range(len(MAZE)):
                                for c in range(len(MAZE[0])):
                                    if MAZE[r][c] in [3, 4]: MAZE[r][c] = 0
                        if cell == 2:
                            players[addr_str]['finished'] = True
                            if p_name not in winners: winners.append(p_name)

                conn.send(json.dumps({"maze": MAZE, "players": players, "winners": winners, "id": addr_str}).encode('utf-8'))
    except: pass
    finally:
        with lock:
            if addr_str in players: del players[addr_str]
        conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5555)); server.listen()
print("Сервер з перезапуском готовий...")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()