import socket
import json
import threading

# Настройки сервера
HOST = '127.0.0.1'
PORT = 5555

# 1 - стена, 0 - путь
MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

player_pos = {"x": 1, "y": 1}

def handle_client(conn):
    global player_pos
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data: break
            
            move = json.loads(data)
            new_x = player_pos['x'] + move['dx']
            new_y = player_pos['y'] + move['dy']

            # Проверка границ и стен
            if 0 <= new_y < len(MAZE) and 0 <= new_x < len(MAZE[0]):
                if MAZE[new_y][new_x] == 0:
                    player_pos['x'], player_pos['y'] = new_x, new_y

            # Отправляем обновленное состояние
            response = json.dumps({"maze": MAZE, "player": player_pos})
            conn.send(response.encode('utf-8'))
        except:
            break
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Сервер запущен на {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()