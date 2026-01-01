import socket
import sys

def main():
    HOST = '127.0.0.1'
    PORT = 9999

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
            print("[1.py] 已连接到 2.py")
        except ConnectionRefusedError:
            print("[1.py] 无法连接到 2.py，请先运行 2.py")
            sys.exit(1)

        while True:
            user_input = input("[1.py] 请输入要发送给 2.py 的文本（输入 'quit' 退出）: ")
            client_socket.send(user_input.encode('utf-8'))

            if user_input == 'quit':
                break

            # 等待回复
            response = client_socket.recv(1024).decode('utf-8')
            print(f"[1.py] 收到来自 2.py 的回复: {response}")

    print("[1.py] 连接已关闭")

if __name__ == '__main__':
    main()