import socket
import hashlib
import _thread
import sys
import time

def nuevoCliente(socketCliente,addr, archivo, cliente):
    while True:
        socketCliente.settimeout(1)
        try:
            ##En este se recibe el primer saludo de un cliente
            ##Si el cliente no cumple el protocolo se termina la conexion.
            print("Se recibe al cliente: ", cliente)
            saludo = socketCliente.recv(1024)
            if(saludo == b"syn"):
                print("El cliente se ha conectado correctamente")
                socketCliente.send(b"ack")
            else:
                print("El cliente no cumple el protocolo")
                socketCliente.shutdown(socket.SHUT_WR)
        except Exception as e1:
            print ('El cliente no envio saludo y se cumplio el tiempo de conexion.')
            break
        socketCliente.settimeout(1)
        try:
            ##En este se recibe el mensaje de preparacion del cliente.
            solicitud = socketCliente.recv(1024)
            if(solicitud == b"Preparado"):
                print("El cliente esta preparado para recibir el archivo.")
                print("Enviando archivo")
                with open(archivo, 'rb') as fa:
                    print('Archivo preparado')
                    fa.seek(0,0)
                    t1 = time.time()*1000
                    while True:
                        data = fa.read(1024) 
                        socketCliente.send(data)
                        if not data:
                            t2 = time.time()*1000
                            break
                    fa.close()
        except Exception as e2:
            print ('El cliente no envio mensaje de preparacion para recibir archivo y se cumplio el tiempo de conexion.')
            break
        socketCliente.settimeout(20)
        try: 
            print("Se recibe mensaje de confirmacion:")
            confirmacion = socketCliente.recv(1024)
            if(confirmacion == b"Recibido"):
                print("Archivo enviado correctamente")
            break
        except Exception as e3:
            print ('El cliente no envio confirmacion y se cumplio el tiempo de conexion.')
            break
    tiempoTransferencia = t2-t1
    socketCliente.shutdown(socket.SHUT_WR)
    socketCliente.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),5000))
s.listen(25)

archivo1 = 'archivo1.png'
archivo2 = 'archivo2.png'
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
numClientes = 0
while numClientes < 26:
    (conn, address) = s.accept()
    numClientes += 1
    _thread.start_new_thread(nuevoCliente,(conn,address,archivo,numClientes))
s.shutdown(socket.SHUT_WR)
s.close()
sys.exit(0)
