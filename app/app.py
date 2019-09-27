import socket



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),5000))
s.listen(1)

archivo1 = 'tux.jpg'
archivo2 = 'mario.png'
archivo = ''

while True:
    (conn, address) = s.accept()
    solicitud = conn.recv(1024)
    if(solicitud == b"archivo1"):
        archivo = archivo1
    else:
        archivo = archivo2
    
    print('Abriendo archivo',archivo)
    with open(archivo, 'rb') as fa:
        print('se abrió el archivo')
        fa.seek(0,0)
        print("enviando archivo.")
        while True:
            data = fa.read(1024)
            conn.send(data)
            if not data:
                break
        fa.close()
        print("Archivo enviado")
    break
s.close()
