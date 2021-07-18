import socket
import tqdm
import os
import json
import time
import hashlib

def hashFile(filename):
   hObj = hashlib.sha256()

   with open(filename, 'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           hObj.update(chunk)

   return hObj.hexdigest()

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

host = "192.168.1.6"  # deixar o usuario escolher AAAAAAAAAAAAAAAAAAAAAAAAA
port = 5001

s = socket.socket()
s.connect((host, port))

while True:
    print("Digite a operacao que deseja realizar: ")
    op = int(input("1 - List\n"
                   "2 - Put\n"
                   "3 - Get\n"))

    if op == 1:
        payload = {
            "command": "list"
        }

        payload = json.dumps(payload)
        s.send(bytes(payload, 'utf-8'))
        time.sleep(1)

        pacote = s.recv(BUFFER_SIZE)
        pacote_dumped = json.loads(pacote)
        print("Arquivos listados no servidor: ")
        for file in pacote_dumped:
            print(file)

    if op == 2:
        dirList = os.listdir("./")
        print("Arquivos listados no cliente: ")
        for file in dirList:
            print(file)
        print("\nEscolha o arquivo para ser enviado ao servidor (com a extensao): ")
        filename = str(input())
        filesize = os.path.getsize(filename)
        file_hash = hashFile(filename)

        payload = {
            "command": "put",
            "filename": filename,
            "filesize": filesize,
            "hash": file_hash
        }

        payload = json.dumps(payload)
        s.send(bytes(payload, 'utf-8'))

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                progress.update(len(bytes_read))
