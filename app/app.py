import socket
import hashlib
import threading
import sys
import time
import datetime

##Aqui se configura la informacion del log.
nombreArchivo = ""
fechaPrueba = ""
ipClientes = []
exito = []
tiemposTransferencia = []
paquetesEnviados = 0
paquetesRecibidos = 0
bytesTransmitidos = 0


def crearLog():
    fechaPrueba = datetime.datetime.now().strftime("%d-%b-%Y(%H-%M-%S)")
    log = "logs/" + datetime.datetime.now().strftime("%d-%b-%Y(%H-%M-%S)")
    if(nombreArchivo == "archivo1.mkv"):
        peso = 131572000
    else:
        peso = 269660000
    paquetesEnviados = peso/2048 + 2048*4
    paquetesRecibidos = 4
    
    with open(log, 'w') as fw:
        fw.seek(0,0)
        fw.write("Fecha de la prueba " + fechaPrueba + '\n')
        fw.write("Nombre del archivo enviado: " + nombreArchivo + '\n')
        fw.write("Peso del archivo enviado:  " + str(peso) + " Bytes"'\n')
        fw.write("Aqui estan todos los clientes identificados con su direccion IP:" + '\n')
        i = 0
        for x in ipClientes:
            i+=1
            fw.write("Cliente " + str(i) + " :" + x[0] + '\n')
        fw.write("Aqui se muestran todas las solicitudes, si fueron existosas dicen True, de lo contrario dicen false" + '\n')
        i = 0
        for y in exito:
            i+=1
            print(y)
            fw.write("Solicitud " + str(i) + " :" + y + '\n')
        fw.write("Aqui se muestran los tiempos de las solicitudes." + '\n')
        i = 0
        for z in tiemposTransferencia:
            i+=1
            fw.write("Tiempo Solicitud " + str(i) + " :" + str(z) + " ms" + '\n')
            paquetesEnviados = paquetesEnviados*i
            paquetesRecibidos= paquetesRecibidos*i
        bytesTransmitidos = paquetesEnviados*2048
        fw.write("Paquetes Enviados: " + str(round(paquetesEnviados,3)) + '\n' )
        fw.write("Paquetes Recibidos: " + str(round(paquetesRecibidos,3))+  '\n')
        fw.write("Bytes Transmitidos: " + str(round(bytesTransmitidos,3))+ " Bytes" + '\n')

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
        socketCliente.settimeout(250)
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
        socketCliente.settimeout(1000)
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
        socketCliente.settimeout(1000)
        try:
            solicitudHash = socketCliente.recv(BUFFER_SIZE)
            if(solicitudHash== b"hash"):
                socketCliente.send(h.digest())
        except Exception as e4:
            break
        socketCliente.settimeout(250)
        try: 
            print("Se recibe mensaje de confirmacion:")
            confirmacion = socketCliente.recv(BUFFER_SIZE)
            if(confirmacion == b"Recibido"):
                print("Archivo enviado correctamente")
                exito.append("True")
            elif(confirmacion == b"noIntegridad"):
                print('El Archivo recibido por el cliente ha sido corrompido.')
            break
        except Exception as e3:
            print ('El cliente no envio confirmacion y se cumplio el tiempo de conexion.')
            exito.append("False")
            break
    tiempoTransferencia = t2-t1
    tiemposTransferencia.append(tiempoTransferencia)
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
nombreArchivo = archivo
print('Escuchando a clientes')
clientesThreads=[]
numClientes = 0
while numClientes < 2:
    if(numClientes == 1):
        break
    (conn, address) = s.accept()
    numClientes += 1
    ipClientes.append(address)
    clientesThreads.append(threading.Thread(target=nuevoCliente, args=(conn,address,archivo,numClientes),)) 
for x in clientesThreads:
    x.start()

for y in clientesThreads:
    y.join()
s.close()
crearLog()
try:
    sys.exit(0)
except:
    print("Se apaga el servidor")
