import socket
import os
import threading
import mimetypes
import psycopg2
import json

def handle_request(client_socket):
    # Lê os dados da requisição HTTP
    try:
        request_data = client_socket.recv(1024).decode()

    # Separa a primeira linha da requisição para obter o método e o caminho do recurso
        method, path, _ = request_data.split(None, 2)
        headers, body = request_data.split('\r\n\r\n', 1)

        if method == 'GET':
            if path == '/':
              path = '/index.html'

        # Construir o caminho absoluto do arquivo
            full_path = os.getcwd() + path

        # Verifica se o arquivo existe e é um arquivo regular
            if os.path.isfile(full_path):
            # Determina o tipo de conteúdo (MIME type) do arquivo
                mime_type, _ = mimetypes.guess_type(full_path)
                response = 'HTTP/1.1 200 OK\n'
                if mime_type:
                    response += f'Content-Type: {mime_type}\n'
                response += '\n'
                with open(full_path, 'rb') as file:
                    response = response.encode() + file.read()
            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\n404 Not Found'.encode()

        # Envia a resposta de volta para o cliente
            client_socket.sendall(response)
        elif method == 'POST':
            if path == '/submit':
                print("ENTREI NO POST")
                try:
                    body_data = json.loads(body)
                except json.JSONDecodeError:
                    response = 'HTTP/1.1 400 Bad Request\r\n\r\nInvalid JSON'
                    client_socket.sendall(response.encode())
                    return
            #Inserir dados no BD
                try:
                    # Tenta se conectar ao banco de dados
                    conn_string = "host='192.168.0.5' dbname='postest' user='postgres'  password='6792010'"
                    conn = psycopg2.connect(conn_string)
        
                    # Se a conexão for bem-sucedida, imprime uma mensagem de sucesso
                    print("Conexão com o banco de dados estabelecida com sucesso!")
        
                    # Não se esqueça de fechar a conexão após o uso
                except Exception as e:
                    # Se ocorrer um erro ao conectar, imprime a mensagem de erro
                    print("Erro ao conectar ao banco de dados:", e)
                    response = 'HTTP/1.1 500 Internal Server Error\r\n\r\nDatabase connection failed'
                    client_socket.sendall(response.encode())
                    return
                cursor = conn.cursor()
                cursor.execute("INSERT INTO post (nome, email, msg) VALUES (%s, %s, %s)", (body_data['nome'], body_data['email'], body_data['msg']))
                conn.commit()
                cursor.close()
                conn.close()
            # Responde com uma mensagem de sucesso
                response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nDados enviados com sucesso!'
                client_socket.sendall(response.encode())
            else:
                response = 'HTTP/1.1 400 Bad Request\r\n\r\nInvalid JSON'
        else:
        # Se o método ou o caminho não forem compatíveis, retorna um erro 404
            response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\n404 Not Found'
            client_socket.sendall(response.encode())

    except Exception as e:
        # Se ocorrer uma exceção, imprime o erro e fecha o socket
        print("Error:", e)
    finally:
        # Fecha o socket do cliente
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen()
    print('Server listening on port 8080...')

    try:
        while True:
            # Aceita conexões de clientes
            client_socket, client_address = server_socket.accept()
            print(f'Client connected: {client_address}')         
            # Lida com a requisição do cliente
            client_handler = threading.Thread(target=handle_request, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print('Server shutting down...')
    finally:
        # Fecha o socket do servidor
        server_socket.close()

if __name__ == '__main__':
    start_server()