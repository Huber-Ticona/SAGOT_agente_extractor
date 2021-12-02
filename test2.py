import os
from concurrent.futures import ThreadPoolExecutor
import time

estado = True

def buscar_cambios():
    actual = os.path.abspath(os.getcwd())
    actual = actual.replace('\\' , '/')
    filename = actual + '/dato1'
    if(os.path.isdir(filename)):
        contenido = os.listdir(filename)
    else: 
        print('no es un directorio')

    while estado:
        print('buscando cambios')
        aux = os.listdir(filename)
        if aux != contenido:
            print('CAMBIO DETECTADO')
            contenido = aux
        else:
            print('SIN CAMBIOS')
        time.sleep(3)


def obtener_fact_bol_ordenadas():
    actual = os.path.abspath(os.getcwd())
    actual = actual.replace('\\' , '/')
    filename = actual + '/dato1'
    if(os.path.isdir(filename)):
        contenido = os.listdir(filename)
        boletas = []
        facturas = []
        for nombre in contenido:
            aux = nombre.split('.')
            aux2 = aux[0].split('_')
            #print(aux2)
            if aux2[0] == '33' :
                facturas.append(aux2[1])
            elif aux2[0] == '39' :
                boletas.append(aux2[1])
        boletas.reverse()
        facturas.reverse()
        return boletas , facturas
    else: 
        print('no es un directorio')

if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=3)
    #executor.submit(buscar_cambios)
    '''bol, fac = obtener_fact_bol_ordenadas()
    print(bol)
    print(fac)
    
    index = fac.index('190866')
    print(index)
    print(fac[index])
    z = index - 1
    print(z)
    
    aux = bol[z] '''

    lista = []
    lista.append('hola')
    if  'hola' not in lista:
        print('dentro')
    else:
        print('no encontrado')
    print('EJECUCIO TERMIMADA')
'''
    opc = 0
    print('1-DETENER\n-0 SALIR')
    opc= int(input())
    
    while opc != 0:
        if opc ==1:
            estado = False
            break
        elif opc == 0:
            estado = False
            break
        print('1- DETENER\n-0 SALIR')
        opc= int(input()) '''

    