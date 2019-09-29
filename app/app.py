import socket
import hashlib
import _thread
import threading
import sys
import time

def nuevoCliente(socketCliente,addr, archivo, cliente):

    BUFFER_SIZE = 2048
    h = hashlib.sha256()
    with open(archivo, 'rb') as fa:
                    print('Archivo preparado')
                    fa.seek(0,0)
                    t1 = time.time()*1000
                    while True:
                        data = fa.read(BUFFER_SIZE) 
                        h.update(data)
                        if not data:
                            break
                    fa.close()
    print("Hash generado por el servidor: ", h.digest())
    while True:
        socketCliente.settimeout(1)
        try:
            ##En este se recibe el primer saludo de un cliente
            ##Si el cliente no cumple el protocolo se termina la conexion.
            print("Se recibe al cliente: ", cliente)
            saludo = socketCliente.recv(BUFFER_SIZE)
            if(saludo == b"syn"):
                print("El cliente se ha conectado correctamente")
                socketCliente.send(b"ack")
            else:
                print("El cliente no cumple el protocolo")
                socketCliente.shutdown(socket.SHUT_WR)
        except Exception as e1:
            print ('El cliente no envio saludo y se cumplio el tiempo de conexion.')
            break
        socketCliente.settimeout(None)
        try:
            ##En este se recibe el mensaje de preparacion del cliente.
            solicitud = socketCliente.recv(BUFFER_SIZE)
            if(solicitud == b"Preparado"):
                print("El cliente esta preparado para recibir el archivo.")
                print("Enviando archivo")
                with open(archivo, 'rb') as fa:
                    print('Archivo preparado')
                    fa.seek(0,0)
                    t1 = time.time()*1000
                    while True:
                        data = fa.read(BUFFER_SIZE) 
                        socketCliente.send(data)
                        if not data:
                            t2 = time.time()*1000
                            break
                    fa.close()
        except Exception as e2:
            print ('El cliente no envio mensaje de preparacion para recibir archivo y se cumplio el tiempo de conexion.')
            break
        socketCliente.settimeout(None)
        try:
            solicitudHash = socketCliente.recv(BUFFER_SIZE)
            if(solicitudHash== b"hash"):
                socketCliente.send(h.digest())
        except Exception as e4:
            break
        socketCliente.settimeout(1)
        try: 
            print("Se recibe mensaje de confirmacion:")
            confirmacion = socketCliente.recv(BUFFER_SIZE)
            if(confirmacion == b"Recibido"):
                print("Archivo enviado correctamente")
            elif(confirmacion == b"noIntegridad"):
                print('El Archivo recibido por el cliente ha sido corrompido.')
            break
        except Exception as e3:
            print ('El cliente no envio confirmacion y se cumplio el tiempo de conexion.')
            break
    tiempoTransferencia = t2-t1
    socketCliente.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),5000))
s.listen(25)

archivo1 = 'archivo1.mkv'
archivo2 = 'archivo2.mkv'
archivo = ""


print('Servidor Iniciado')
escoger = True
while(escoger):
    escoger=False
    print('Escoger archivo a enviar: 1: archivo de 100 Mb y 2: archivo de 250Mb')
    escogido = input()
    if(escogido == "1"):
        archivo = archivo1
    elif(escogido == "2"):
        archivo = archivo2
    else:
        escoger=True
        print('No digito un numero valido, vuelva a intentarlo')

print('Escuchando a clientes')
clientesThreads=[]
numClientes = 0
while numClientes < 26:
    if(numClientes == 25):
        break
    (conn, address) = s.accept()
    numClientes += 1
    _thread.start_new_thread(nuevoCliente,(conn,address,archivo,numClientes))
    ##clientesThreads.append(threading.Thread(target=nuevoCliente, args=(conn,address,archivo,numClientes),)) 
##for x in clientesThreads:
##    x.start()

##for y in clientesThreads:
##    y.join()
s.shutdown(socket.SHUT_WR)
s.close()
try:
    sys.exit(0)
except:
    print("Se apaga el servidor")
