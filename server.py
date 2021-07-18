import json
import socket
import tqdm
import os
import hashlib

def hashFile(filename):
   hObj = hashlib.sha256()

   with open(filename, 'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           hObj.update(chunk)

   return hObj.hexdigest()

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

s = socket.socket()
serverAddr = (SERVER_HOST, SERVER_PORT)
s.bind(serverAddr)

s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

client_socket, address = s.accept()

print(f"[+] {address} is connected.")

while True:
    pacote = client_socket.recv(BUFFER_SIZE)
    pacote_dumped = json.loads(pacote)

    if pacote_dumped["command"] == "list":
        dirList = os.listdir("./")
        payload = dirList
        payload = json.dumps(payload)
        client_socket.send(bytes(payload, 'utf-8'))

    if pacote_dumped["command"] == "put":
        filename = pacote_dumped["filename"]
        filesize = pacote_dumped["filesize"]
        clientHash = pacote_dumped["hash"]

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))

        serverHash = hashFile(filename)

        if serverHash == clientHash:
            payload = {
                "file": filename,
                "operation": "put",
                "status": "success"
            }
            payload = json.dumps(payload)
            client_socket.send(bytes(payload, 'utf-8'))
        else:
            payload = {
                "file": filename,
                "operation": "put",
                "status": "fail"
            }
            payload = json.dumps(payload)
            client_socket.send(bytes(payload, 'utf-8'))
