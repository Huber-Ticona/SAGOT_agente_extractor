import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap , QIcon
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import os
import rpyc
import socket
import ctypes
import subprocess
import json


logging.basicConfig(level=logging.DEBUG , format='%(threadName)s: %(message)s')

class menu(QMainWindow):
    def __init__(self):
        super(menu, self).__init__()
        uic.loadUi('agente.ui', self)

        self.conexion = ''
        self.host = None
        self.port = None
        self.conn_estado = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.aux_facturas = []
        self.aux_boletas = []
        self.estado = True    #PARA BUSCAR FACTURAS Y BOLETAS
        self.estado2 = True   #PARA BUSCAR GUIAS DE DESPACHO
        self.estado3 = True   #PARA BUSCAR NOTAS DE CREDITO
        self.boleta = 0
        self.factura = 0
        self.guia = 0
        self.credito = 0  #
        self.filename = None            #directorio de las boletas y facturas.
        self.filename_guia = None       #directorio de las GUIAS.
        self.filename_credito = None    #directorio de las NOTAS DE CREDITO
        self.f_top = False #top de la lista de facturas
        self.b_top = False #top de la lsita de boletas
        self.g_top = False #TOP DE LA LISTA DE GUIAS
        self.c_top = False #TOP DE LA LISTA DE notas de credito.
         

        self.rango = 1      #velocidad de buscaqueda fact y bol
        self.rango2 = 5  # velocidad de buscqueda guias
        self.rango3 = 5  # velocidad de buscqueda notas de credito
        self.inicializar()
        self.obtener_ultimos()
        
        self.btn_conectar.clicked.connect(self.conectar)

        self.btn_comenzar.clicked.connect(self.comenzar)
        self.btn_detener.clicked.connect(self.detener)

        self.btn_comenzar2.clicked.connect(self.comenzar2)
        self.btn_detener2.clicked.connect(self.detener2)

        self.btn_comenzar3.clicked.connect(self.comenzar3)
        self.btn_detener3.clicked.connect(self.detener3)
        #self.btn_comenzar.setEnabled(False)
        self.label_conexion.setText('DESCONECTADO')


    def inicializar(self):
        self.btn_detener.setEnabled(False)
        self.btn_detener2.setEnabled(False)
        self.txt_rango.setText('3') #velocidad de busqueda
        self.txt_rango2.setText('5') #velocidad de busqueda
        self.txt_rango3.setText('5') #velocidad de busqueda
        actual = os.path.abspath(os.getcwd())
        actual = actual.replace('\\' , '/')
        print(actual)
        ruta = actual + '/icono_imagen/madenco logo.png'
        foto = QPixmap(ruta)
        self.lb_logo.setPixmap(foto)
        self.btn_comenzar.setIcon(QIcon('icono_imagen/start.ico'))
        self.btn_detener.setIcon(QIcon('icono_imagen/stop.ico'))

        if os.path.isfile(actual + '/manifest.txt'):
            print('encontrado manifest')
            with open(actual + '/manifest.txt' , 'r', encoding='utf-8') as file:
                lines = file.readlines()
                try:
                    n_host = lines[0].split(':')
                    n_host = n_host[1]
                    host = n_host[:len(n_host)-1]

                    n_port = lines[1].split(':')
                    n_port = n_port[1]
                    port = n_port[:len(n_port)-1]

                    n_filename = lines[2].split(':')
                    n_filename = n_filename[1]
                    
                    filename = n_filename[:len(n_filename)-1]  #?? porque usaba esto? para quitar el salto de LINEA
                    print(filename)

                    if lines[3]:
                        dir_guia = lines[3].split(':')
                        dir_guia = dir_guia[1]
                        dir_guia = dir_guia[:len(dir_guia)-1]
                        print(dir_guia)
                        self.filename_guia = dir_guia

                    if lines[4]:
                        dir_credito = lines[4].split(':')
                        dir_credito = dir_credito[1]
                        dir_credito = dir_credito[:len(dir_credito)-1]
                        print(dir_credito)
                        self.filename_credito = dir_credito

                    self.host = host
                    self.port = port
                    self.filename = filename
                    



                except IndexError:
                    pass #si no encuentra alguna linea

        else:
            print('no encontrado manifest')
        

    def conectar(self):
        print('conectando...')
        try:
            self.label_conexion.setText('CONECTANDO ...')
            self.conexion = rpyc.connect(self.host , self.port)
            self.conn_estado = True
            self.label_conexion.setText('CONECTADO')
            #self.btn_comenzar.setEnabled(True)

        except ConnectionRefusedError:
            self.label_conexion.setText('EL SERVIDOR NO RESPONDE')
            #QMessageBox.about(self,'ERROR' ,'El servidor no responde')
        except socket.error:
            self.label_conexion.setText('NO SE PUEDE ESTABLECER CONEXION CON EL HOST')
            #QMessageBox.about(self,'ERROR' ,'No se puede establecer la conexion con el servidor')

    def comenzar(self):
        self.estado = True

        boleta = self.lineboleta.text()
        factura = self.linefactura.text()
        rango = self.txt_rango.text() 
        if(boleta != '' and factura != '' and rango != ''):
            try:
                self.boleta = int(boleta)
                self.factura = int(factura)
                self.rango = float(rango)
                if self.rango >= 0 and self.rango <= 10:
                    #print('buscando factura:  33_' + str(factura) + ' y boleta:  39_' + str(boleta))
                    #self.executor.submit(self.buscar_boleta)
                    print('paso0')
                    self.executor.submit(self.busqueda)
                    #self.executor.submit(self.reconectar)
                    self.btn_comenzar.setEnabled(False)
                    self.btn_detener.setEnabled(True)

                else:
                    QMessageBox.about(self,'ERROR','El valor del rango debe estar entre 1 y 10')
            except ValueError:
                QMessageBox.about(self,'ERROR DE TIPO' ,'Solo ingrese numeros')
                
            
        else:
            QMessageBox.about(self,'ERROR' ,'Rellene todos los campos antes de realizar la busqueda.')

    def comenzar2(self): #Comenzar a buscar las guias 
        guia = self.lineguia.text()
        rango = self.txt_rango2.text() 

        if(guia != ''  and rango != ''):
            try:
                self.guia = int(guia)
                self.rango2 = float(rango)
                if self.rango2 >= 0 and self.rango2 <= 10:
                    #print('buscando factura:  33_' + str(factura) + ' y boleta:  39_' + str(boleta))
                  
                    print('paso guia')
                    self.estado2 = True #guias
                    self.executor.submit(self.busqueda_guia)
                    print("ya entro al ciclo")
               
                    self.btn_comenzar2.setEnabled(False)
                    self.btn_detener2.setEnabled(True)

                else:
                    QMessageBox.about(self,'ERROR','El valor del rango debe estar entre 1 y 10')
            except ValueError:
                QMessageBox.about(self,'ERROR DE TIPO' ,'Solo ingrese numeros')
                
            
        else:
            QMessageBox.about(self,'ERROR' ,'Rellene todos los campos antes de realizar la busqueda.')

    def comenzar3(self): #Comenzar a buscar las notas de credito.
        credito = self.linecredito.text()
        rango = self.txt_rango3.text() 

        if(credito != ''  and rango != ''):
            try:
                self.credito = int(credito)
                self.rango3 = float(rango)
                if self.rango3 >= 0 and self.rango3 <= 10:
                    #print('buscando factura:  33_' + str(factura) + ' y boleta:  39_' + str(boleta))
                    print('paso credito')
                    self.estado3 = True 
                    self.executor.submit(self.busqueda_credito)
                    print("ya entro al ciclo creditos")
               
                    self.btn_comenzar3.setEnabled(False)
                    self.btn_detener3.setEnabled(True)

                else:
                    QMessageBox.about(self,'ERROR','El valor del rango debe estar entre 1 y 10')
            except ValueError:
                QMessageBox.about(self,'ERROR DE TIPO' ,'Solo ingrese numeros')
                
            
        else:
            QMessageBox.about(self,'ERROR' ,'Rellene todos los campos antes de realizar la busqueda.')


    def detener(self):
        self.estado = False
        self.btn_comenzar.setEnabled(True)
        self.btn_detener.setEnabled(False)

    def detener2(self):
        self.estado2 = False
        self.btn_comenzar2.setEnabled(True)
        self.btn_detener2.setEnabled(False)
        print('detener 2 xd')

    def detener3(self):
        self.estado3 = False
        self.btn_comenzar3.setEnabled(True)
        self.btn_detener3.setEnabled(False)
        print('detener 3 xd')

    def envio_boleta(self, intern):
      
        nombre_archivo = self.filename + '39_' + str(intern) + '.txt'
        #print(nombre_archivo)
        with open(nombre_archivo, 'r', encoding='utf-8') as file:
            
            lines = file.readlines()
            vendedor = self.Obt_nombre(lines[12]) #Se asume que el FORMATO ES INMODIFICABLE...
            print(vendedor) 

            l_datos = []
            items = []

            for line in lines:
                if line != '\n' :
                    if line[0] == 'H' :
                        dato1 = line.split('  ')
                        hora = dato1[1] #Se obtiene la hora con formato string
                        print(hora)
                        
                    elif line[0] == 'F' :
                        dato2 = line.split(' ')  
                        fecha = dato2[1] #Se obtiene la fecha con formato string
                        print(fecha)
                        bol = line[55:82].split(' ')
                        bol = int(bol[2])
                        print(bol)
                        
                    elif line[0] == 'T' :
                        dato3 = line.split(' ')
                        total = float(dato3[1])  #Se obtiene el monto total de la venta de tipo string.
                        print(total)
                        
                    elif line[0] == ' ': #Ubicandose en los productos
                        
                        cantidad = float(line[0:8].replace(',','.',2) )   #Se obtiene la cantidad de tipo float
                        cod = line[10:27].split(' ')                      #Se obtiene el codigo el formato string
                        codigo = cod[0]
                        descripcion = line[27:121]

                        data = line.split('  ')
                        #print(data) 
                        t_producto = data[len(data) - 2] #len() retorna la cantidad de elementos en la lista, por ende se obtiene el total del producto
                        t_producto = float( t_producto.replace(',','.',2) )  #de tipo float
                        p_unitario = t_producto/ cantidad #Se calcula el p_unitario mediante el p_total y la cantidad de tipo float

                        print(str(cantidad) + ' ' + codigo + ' ' + descripcion + ' ' + str(p_unitario) + ' ' + str(t_producto) )
                        item = ( intern ,cantidad , codigo , descripcion , p_unitario ,t_producto)
                        items.append(item)

            l_datos.append(intern)
            l_datos.append(bol)
            aux = fecha.split('-')
            final = aux[2] + '-' + aux[1] + '-' + aux[0] + ' ' + hora #Formateamos la fecha al formato datetime
            l_datos.append(final)
            l_datos.append(vendedor)
            l_datos.append(total)
            try:
                self.conexion.root.registrar_boleta(l_datos, items)
            except EOFError:
                print('se perdio la conexion -- durante el envio de la boleta: ' + str(intern))
                self.conn_estado = False

    def envio_factura(self,folio):
        nombre_archivo = self.filename + '33_' + str(folio) + '.txt'
        with open(nombre_archivo, 'r') as file:
            lines = file.readlines()
            
            l_datos = []
            items = []
            nro_interno = 0

            iterator = 1
            i = 0
            while i < len(lines) :

                if lines[i] != '\n': #Chequear que la linea no sea vacia
                    linea = lines[i]
                    try:
                        if(linea[0:4]  == 'Nume' ):
                            nro_interno = linea.split('   ')
                            nro_interno = int(nro_interno[1]) #Se obtiene el nro interno bruto. Tipo entero
                            print(nro_interno)
                                            
                        elif(linea[0:5] == 'Fecha' ):
                            fecha = linea.split('  ')       #Se obtiene la fecha de tipo String
                            print(fecha[1])

                        elif  linea[0:5] == 'Razon' :
                            nombre =linea.split(': ')
                            nombre = nombre[1]
                            cliente = nombre[:len(nombre)-1]

                        elif(linea[0:4] == 'Hora' ):
                            hora = linea.split(' ')         #Se obtiene la hora de tipo String
                            print(hora[1])
                                                
                        elif(linea[0:8] == 'Vendedor' ):
                            vendedor = linea.split(': ')
                            vendedor = vendedor[1]
                            vendedor = vendedor[:len(vendedor)-1] #Se obtiene el nombre del vendedor de tipo string
                            print(vendedor)                      
                        elif(linea[0:5] == 'Total'):
                            total = linea.split('     ')
                            total = float(total[1])                   #Se obtiene el total de la venta de tipo float
                            print(total)
                            

                        
                        elif( int(linea[0:4]) == iterator): #verifica si la linea es una descripcion
                            separador = linea[4:22].replace(',' , '.' , 1)
                            cantidad = float(separador)                 #Se obtiene la cantidad bruta de tipo float
                            codigo = linea[22:57].split(' ')            #Se obtiene el codigo del producto como codigo[0] de tipo string
                            descripcion = linea[58:137]                 #Se obtiene la descripcion bruta como descripcion[0] de tipo string
                            p_total = linea[234:]
                            p_total = p_total.replace(',' , '.' , 1 )
                            p_total = float(p_total)                        #Se obtiene el precio total de tipo float
                            try:               
                                p_unitario = linea[188:230]
                                p_unitario = p_unitario.replace(',' , '.' , 1 )       
                                p_unitario = float(p_unitario)              #Se obtiene el precio unitario de tipo float
                                
                            except ValueError:                              #Si la factura tiene descuento, se produce un error en el precio unitario.
                                p_unitario = linea[188:205]                 #Se adapta el limite de extraccción para facturas con descuento
                                p_unitario = p_unitario.replace(',' , '.' , 1 )       
                                p_unitario = float(p_unitario)              #Se obtiene el precio unitario de tipo float
                            finally:
                                print(str(cantidad) + ' | ' + codigo[0]  + ' | ' + descripcion + ' | ' + str(p_unitario) + ' | ' + str(p_total))
                            item = (nro_interno ,cantidad , codigo[0] , descripcion , p_unitario ,p_total)
                            items.append(item)
                            iterator +=1

                    except ValueError:
                        #print('El dato leido no es descripcion')     
                        pass      
                
                i += 1
            l_datos.append(nro_interno)
            l_datos.append(folio)
            aux = fecha[1].split('-')
            final = aux[2] + '-' + aux[1] + '-' + aux[0] + ' ' + hora[1] #Formateamos la fecha al formato datetime
            l_datos.append(final)
            l_datos.append(vendedor)
            l_datos.append(total)
            l_datos.append(cliente) #v4
            try:
                self.conexion.root.registrar_factura(l_datos , items )
                #factura +1
            except EOFError:
                print('se perdio la conexion -- durante el envio de la factura: ' + str(folio))
                self.conn_estado = False

    def envio_guia(self, nro_interno):
        nombre_archivo = self.filename_guia  + '52_' + str(nro_interno) + '.txt'
        #print(nombre_archivo)
        with open(nombre_archivo, 'r', encoding='utf-8') as file:
            
            lines = file.readlines()
            #print('total de lineas: ' + str(len(lines)))

            linea_uno = lines[0]
            interno = linea_uno[0:38] #CAPTURA EL TEXTO COMPLETO DE NRO INTERNO
            #print(interno)
            interno = interno.split(':')
            #print(interno)
            interno = int(interno[1]) #NRO INTERNO TIPO INT
            print(interno)

            folio = linea_uno[38:59]  #CAPTURA EL TEXTO COMPLETO DEL FOLIO
            folio = folio.split(':')
            #print(folio)
            folio = int(folio[1])     #FOLIO TIPO INT
            print(folio)

            linea_dos = lines[1]
            fecha = linea_dos[0:37]
            #print(fecha)
            fecha = fecha.split(': ')
            #print(fecha)
            fecha = fecha[1].split(' ')
            #print(fecha)
            fecha = fecha[0] #FECHA DE TIPO STRING
            print(fecha)

            rut = linea_dos[37:56]  #CAPTURA TODO EL TEXTO DEL RUT
            #print(rut)
            rut = rut.split(': ')
            #print(rut)
            rut = rut[1].split(' ')
            rut = rut[0]  #RUT DE TIPO STRING
            print(rut)

            linea_tres = lines[2]
            razon_social = linea_tres[0:56]
            #print(razon_social)
            razon_social = razon_social.split(': ')
            #print(razon_social)
            razon_social = razon_social[1]
            print(razon_social)

            doc_ref = linea_tres[56:80].split(': ') #doc ref el max se estimo.
            print(doc_ref)
            doc_ref = doc_ref[1].split('  ')
            print(doc_ref)
            doc_ref = doc_ref[0]  #DOC REF DE TIPO STRING
            print(doc_ref)

            doc_ref = doc_ref.split(' ')
            print(doc_ref)

            tipo_doc = 'NINGUNO'
            if doc_ref[0] == '':
                print('no tiene asociacion')
                doc_ref = 0
            elif doc_ref[0] == '(FA)':
                print('asociado a factura')
                tipo_doc = 'FACTURA'
                doc_ref = int(doc_ref[1])

            elif doc_ref[0] == '(BO)':
                print('asociado a BOLETA') 
                tipo_doc = 'BOLETA'
                doc_ref = int(doc_ref[1])
                
            print(tipo_doc)
            print(doc_ref)

            linea_cuatro = lines[3]
            giro = linea_cuatro[0:77].split(': ')
            giro = giro[1]
            print(giro)

            direccion = lines[4]
            direccion = direccion[0:42]  
            print(direccion)

            linea_seis = lines[5]
            telefono = linea_seis[0:32].split(': ')
            telefono = telefono[1]
            print(telefono)

            linea_nueve = lines[8]
            vendedor = linea_nueve.split(': ')
            vendedor = vendedor[1].split('  ')
            vendedor = vendedor[0]
            print(vendedor)

            observacion = lines[9]
            #print(observacion)
            observacion = observacion.split(': ')
            #print(observacion)
            observacion = observacion[1].split('   ')
            observacion = observacion[0]
            print(observacion)

            campo_regla = lines[10].split(': ') # Mas bien "observacion de despacho" mostrado en la guia de despacho
            #print(campo_regla)
            campo_regla = campo_regla[1]
            #print(len(campo_regla))
            campo_regla = campo_regla[0:102]  #se elimina el caracter de salto de linea
            print(campo_regla)

            linea_doce = lines[11]
            hora = linea_doce[0:21].split(': ')
            #print(hora)
            hora = hora[1].split(' ')
            hora = hora[0]
            print(hora)

            linea_trece = lines[12]
            chofer = linea_trece[26:50].split(': ')
            chofer = chofer[1]
            print(chofer)
            rut_chofer = linea_trece[0:26].split(': ')
            rut_chofer = rut_chofer[1].split(' ')
            rut_chofer = rut_chofer[0]
            print(rut_chofer)
            print('-------------------- ITEMS -----------------------')
            #-------------------- ITEMS -----------------------#
            inicio = 14
            i = 1
            cantidades = []
            descripciones = []
            unitarios = []
            totales = []
            while lines[inicio] != '\n' :

                #print(f'Item: {str(i)} - ' + lines[inicio])
                item = lines[inicio]

                cantidad = item[0:8].replace(',','.',1)
                cantidad = float(cantidad)
                print(cantidad)

                descripcion =  item[20:115] #CAPTURA SOLO EL TEXTO DE LA DESCRIPCION DEL PRODUCTO
                print(descripcion)

                unitario = item[120:134] #ESTIMA EL VALOR UNITARIO ENTRE [limite exacto --> 120 : 134 <-- limite exacto] 
                #print(unitario)
                try:
                    unitario = unitario.replace(',' , '.' , 1 )  
                    unitario = float(unitario)
                    print(unitario)

                except ValueError:
                    print('Error de valores al capturar guias')
                    unitario = 0
                    print(unitario)


                total = cantidad * unitario 
                print(total)

                cantidades.append(cantidad)
                descripciones.append(descripcion)
                unitarios.append(unitario)
                totales.append(total)

                i += 1
                inicio += 1
            print('-------------------- FIN ITEMS -----------------------')
            print(f'termino el ciclo en: {str(inicio)} ')


            neto = lines[49].split(': ')  #neto
            neto = neto[1].split(' ')
            neto = float( neto[0].replace(',','.',1) ) #neto de tipo float
            print(neto)

            monto_final = lines[51].split(': ') #monto total de la guia
            monto_final = monto_final[1].split(' ')
            monto_final = float( monto_final[0].replace(',','.',1) )   #monto final de tipo float
            print(monto_final)

            tipo = lines[52].split(': ') #tipo de guia *falta por DESCUBRIR
            tipo = tipo[1].split('  ')
            tipo = tipo[0]
            print(tipo)
            aux = fecha.split('-')
            fecha_final = aux[2] +'-' + aux[1] + '-' + aux[0] + ' ' + hora + ':00'
            print(fecha_final)

            formato = {
                "cantidades" : cantidades, #
                "descripciones" : descripciones,#
                "unitarios" : unitarios,#
                "totales" : totales,
                "observacion" : observacion,#
                "rut" : rut,#
                "tipo_doc": tipo_doc,#
                "doc_ref": doc_ref,#
                "giro" : giro,#
                "direccion" : direccion,#
                "telefono" : telefono,#
                "vendedor": vendedor,#
                "campo_regla" : campo_regla,#
                "neto" : neto,#
                "monto_final" : monto_final,#
                "tipo": tipo      
            }
            detalle = json.dumps(formato)

            try:
                if self.conexion.root.registrar_guia( folio,interno, fecha_final, razon_social, detalle ) :
                    print('REGISTRADA CORRECTAMENTE')
                    if self.conexion.root.añadir_vinculo_guia_a_venta(tipo_doc,doc_ref,folio):
                        print('vinculo añadido con exito')
                    else:
                        print('vinculo añadido sin exito')
                else:
                    print("ERROR AL REGISTRAR")

            except EOFError:
                print('se perdio la conexion con el servidor')
                self.conn_estado = False

    def envio_credito(self, folio):
        nombre_archivo = self.filename_credito  + '61_' + str( folio ) + '.txt'
        print(nombre_archivo)
        with open(nombre_archivo, 'r', encoding='utf-8') as file:

            lineas = file.readlines()
        
            #NRO INTERNO Y FOLIO
            interno = lineas[0].split('Folio:') #separa interno y folio
            folio = interno[1]
            interno = interno[0].split(':')
            try:
                folio  = int(folio)  
                print(folio)
                interno = int( interno[1] )
                print(interno)
            except:
                print('aki ta el error')
                folio = 0
                interno = 0

            #FECHA DE EMISION Y RUT
            linea1 = lineas[1]
            
            fecha = linea1[16:26]  #LIMITE EXACTO PARA LA FECHA
            rut = linea1.split('Rut:')
            rut = rut[1]
            rut = rut[ : len(rut) - 1]  #RUT TIPO STRING
            #print(fecha)
            #print(rut)

            #RAZON SOCIAL
            razon_social = lineas[2].split(': ')
            razon_social = razon_social[1]
            razon_social = razon_social[ : len(razon_social) - 1 ]
            print(razon_social)

            #GIRO
            giro = lineas[3].split(': ')
            giro = giro[1]
            giro = giro[ : len(giro) - 1 ]
            #print(giro)

            #DIRECCION
            direccion = lineas[4]
            direccion  = direccion[ : len(direccion) - 1]
            #print(direccion)
            #TELEFONO -> no ahi en la mayoria de las notas de credito


            #VENDEDOR -> no ahi en la mayoria de las notas de credito

            #MOTIVO_NOTA_CREDITO
            motivo = lineas[8].split(': ')
            motivo = motivo[1]
            motivo = motivo[ : len(motivo) - 1 ]
            #print(motivo)

            #SOLICITANTE no se tiene importancia

            #OBSERVACION
            observacion = lineas[10].split(': ')
            observacion = observacion[1]
            observacion = observacion[ : len(observacion) - 1]
            #print( observacion)
            #CAMPO_REGLA no capturado . no se sabe su uso en nota de credito.

            #------ITEMS-------
            inicio = 15
            cantidades = []
            descripciones = []
            unitarios = []
            totales = []
            while lineas[inicio] != '\n':
                #LINEA A LEER
                linea = lineas[inicio]
                print('---------------------')
                #CANTIDAD
                try:
                    cantidad = float( linea[4:15].replace(',','.',1) )  #float
                except ValueError:
                    cantidad = 0
                
                #DESCRIPCION
                descripcion = linea[85:149] #LIMITE EXACTO
                print(descripcion)
                try:
                    #UNITARIO
                    unitario = float( linea[149:165].replace(',','.',1) )  #Limite de 15 digitos para el unitario
                    #print(unitario)
                    #TOTAL
                    total = float( linea[ 165: ].replace(',','.',1) )  #limite muy grande pero consciso para el total.
                    #print(total)
                except ValueError:
                    unitario = 0
                    total = 0
                    print('Error de valores al capturar unitario y total')
                
                cantidades.append(cantidad)
                descripciones.append(descripcion)
                unitarios.append(unitario)
                totales.append(total)
                inicio += 1

            #DOCUMENTO-ASOCIADO o DOC_REF
            linea14 = lineas[40]
            nro_tipo = linea14[0:5]  #limite exacto
            nro_tipo = int(nro_tipo)

            if(nro_tipo == 33):      #TIPO STRING
                tipo_doc = 'FACTURA'
            elif nro_tipo == 39:
                tipo_doc = 'BOLETA'
            else: 
                tipo_doc = 'DOCUMENTO ' + str(nro_tipo)

            doc_ref = linea14[33: 42] #limite exacto

            try:
                doc_ref = int(doc_ref)  #TIPO ENTERO
            except ValueError:
                doc_ref = 0

            print(tipo_doc + ' ' + str(doc_ref))

            #NETO
            neto = lineas[49].split(':')  #neto
            neto = neto[1]
            neto = float( neto.replace(',','.',1) )
            #print(neto)

            #MONTO FINAL
            monto_final = lineas[51].split(':')
            monto_final = monto_final[1] 
            monto_final = float( monto_final.replace(',','.',1) )
            #print(monto_final)

            aux = fecha.split('-')
            fecha_final = aux[2] +'-' + aux[1] + '-' + aux[0]
            print(fecha_final)

            formato = {
                "cantidades" : cantidades, #
                "descripciones" : descripciones,#
                "unitarios" : unitarios,#
                "totales" : totales,
                "observacion" : observacion,#
                "rut" : rut,#
                "doc_ref": doc_ref,#
                "tipo_doc": tipo_doc,
                "giro" : giro,#
                "direccion" : direccion,#
                "motivo": motivo,
                "neto" : neto,#
                "monto_final" : monto_final,#
            }
            detalle = json.dumps(formato)

            try:
                if self.conexion.root.registrar_nota_credito( folio,interno, fecha_final, razon_social, detalle ) :
                    print('REGISTRADA CORRECTAMENTE')
                    print('añadiendo VINCULACION...')

                    if self.conexion.root.añadir_vinculo_credito_a_venta(tipo_doc,doc_ref,folio):
                        print('Vinculo añadido con exito')
                    else:
                        print('Nota venta  no encontrada en la BD')
                else:
                    print("ERROR AL REGISTRAR")

            except EOFError:
                print('se perdio la conexion con el servidor en nota de credito')
                self.conn_estado = False

    def busqueda(self):
        while(self.estado):
            if(self.conn_estado):
                self.lb_detalle.setText('Buscando Factura: ' + str(self.factura) + ' -- ' + 'Boleta: ' + str(self.boleta))
                self.linefactura.setText( str(self.factura))
                self.lineboleta.setText(str(self.boleta))
                lista_boletas , lista_facturas = self.obtener_fact_bol_ordenadas()
                
                try:
                    if self.factura != 0:
                        self.busqueda_rango_fact(lista_facturas)
                    else:
                        logging.debug("factura omitida")
                        time.sleep(1)
                    #######################################################
                    
                    if self.boleta != 0:
                        self.busqueda_rango_bol(lista_boletas)
                    else:
                        logging.debug("boleta omitida")
                        time.sleep(1)
                    ##############################################
                except EOFError:
                    self.conn_estado = False
                    print('se perdio la conexion consultando al servidor')

            else:
                self.conectar()
            self.lb_factura.setText('')
            self.lb_boleta.setText('')
            
            

        self.lb_detalle.setText('BUSQUEDA FINALIZADA')
        print('BUSKEDA FINALIZADA')

    def busqueda_guia(self):

        while(self.estado2):
            if self.conn_estado: #ESTADO DE LA CONEXION CON EL SERVIDOR

                self.lb_detalle2.setText('Buscando Guia: ' + str(self.guia) )
                print('----------------------------------- GUIA -----------------------------------')
                self.lineguia.setText(str(self.guia))
                lista_guias = self.obtener_guias_ordenadas()

                try:
                    index1 = lista_guias.index(str(self.guia))
                    
                    if lista_guias[0] != str(self.guia): #que no consulte siempre a la BD

                        if( self.conexion.root.buscar_guia( int(self.guia)) == False ):       #
                                self.lb_guia.setText('ENCONTRADA: '+ str(self.guia))                          #                  
                                self.envio_guia(str(self.guia))
                                time.sleep(0.2)
                                self.lb_guia.setText('ALMACENADA: '+ str(self.guia))    
                                nuevo_index = index1 - 1
                                if nuevo_index > 0:
                                    self.guia = lista_guias[nuevo_index]
                                    self.g_top = False
                                    print('GUIA ALMACENADA: ' + lista_guias[index1] + ' -  Buscando: ' + str(self.guia) )
                                elif nuevo_index == 0 :
                                    self.guia = lista_guias[nuevo_index]
                                    self.g_top = True
                                    print('GUIA ALMACENADA: ' + lista_guias[index1]  + ' -  Buscando el top: ' + str(self.guia) )
                                
                                                            
                        else:           #si esta en la BD  
                            self.lb_guia.setText('EN LA BD: '+ str(self.guia))                                                     #
                            nuevo_index = index1 - 1  
                            if nuevo_index > 0 : #se captura el indice que continua si es que existe
                                self.guia = lista_guias[nuevo_index]
                                self.g_top = False
                                print('GUIA en la BD: ' + lista_guias[index1]  + ' -  Buscando a: ' + lista_guias[nuevo_index] )
                            elif nuevo_index == 0 :
                                self.guia = lista_guias[nuevo_index]
                                self.g_top = True
                                print('GUIA en la BD: ' + lista_guias[index1]  + ' -  Buscando el top : ' + lista_guias[nuevo_index] )

                    else:
                        if self.g_top: #si esta al inicio de la lista, se analisa su almacenamiento

                            if( self.conexion.root.buscar_guia( int(self.guia)) == False ):       #
                                self.lb_guia.setText('ENCONTRADA: '+ str(self.guia))                          #                  
                                self.envio_guia(str(self.guia))
                                time.sleep(0.2)
                                self.lb_guia.setText('ALMACENADA: '+ str(self.guia))    
                                self.g_top = False #se cambia para que no siga consultando a la BD inecesariamente.
                                print('GUIA TOP ALMACENADA: ' + lista_guias[index1]  + ' -  Buscando mayor a: ' + str(self.guia) )
                            else:
                                self.g_top = False
                                self.lb_guia.setText('EN LA BD: '+ str(self.guia)) 
                                print('TOP GUIA en la BD - buscando MAYOR A: ' + str(self.guia))

                        else:
                            self.lb_guia.setText('EN LA BD: '+ str(self.guia))    
                            print('Top GUIA almacenado anteriormetne - Buscando GUIA mayor a: '+ str(self.guia))
                    
                    time.sleep(self.rango2)

                except ValueError:
                    print('GUIA no encontrada en la lista')
                    self.lb_guia.setText('NO ENCONTRADA: '+ str(self.guia))    
                    time.sleep(2)

                print('------------------------------------------------------------------')
            else:
                self.conectar()
                self.lb_guia.setText('reconectando...')

        self.lb_detalle2.setText('BUSQUEDA FINALIZADA')
        self.lb_guia.setText(':3')

    def busqueda_credito(self):
    
        while(self.estado3):
            if self.conn_estado: #ESTADO DE LA CONEXION CON EL SERVIDOR

                #self.lb_detalle2.setText('Buscando Guia: ' + str(self.guia) )
                print('----------------------------------- CREDITO -----------------------------------')
                self.linecredito.setText(str(self.credito))
                lista_creditos = self.obtener_creditos_ordenadas()
                print('a')
                try:
                    index1 = lista_creditos.index(str(self.credito))
                    print('b')
                    if lista_creditos[0] != str(self.credito): #que no consulte siempre a la BD
                        print('c')
                        if( self.conexion.root.buscar_credito( int(self.credito)) == False ):       #
                                #self.lb_guia.setText('ENCONTRADA: '+ str(self.credito))                          #                  
                                print('d')
                                self.envio_credito(str(self.credito))
                                print('e')
                                time.sleep(0.2)
                                #self.lb_guia.setText('ALMACENADA: '+ str(self.credito))    
                                nuevo_index = index1 - 1
                                if nuevo_index > 0:
                                    self.credito = lista_creditos[nuevo_index]
                                    self.c_top = False
                                    print('NOTA CREDITO ALMACENADA: ' + lista_creditos[index1] + ' -  Buscando: ' + str(self.credito) )
                                elif nuevo_index == 0 :
                                    self.credito = lista_creditos[nuevo_index]
                                    self.c_top = True
                                    print('NOTA CREDITO ALMACENADA: ' + lista_creditos[index1]  + ' -  Buscando el top: ' + str(self.credito) )
                                
                                                            
                        else:           #si esta en la BD  
                            #self.lb_guia.setText('EN LA BD: '+ str(self.credito))                                                     #
                            nuevo_index = index1 - 1  
                            if nuevo_index > 0 : #se captura el indice que continua si es que existe
                                self.credito = lista_creditos[nuevo_index]
                                self.c_top = False
                                print('NOTA CREDITO en la BD: ' + lista_creditos[index1]  + ' -  Buscando a: ' + lista_creditos[nuevo_index] )
                            elif nuevo_index == 0 :
                                self.credito = lista_creditos[nuevo_index]
                                self.c_top = True
                                print('NOTA CREDITO en la BD: ' + lista_creditos[index1]  + ' -  Buscando el top : ' + lista_creditos[nuevo_index] )

                    else:
                        print('F')
                        if self.c_top: #si esta al inicio de la lista, se analisa su almacenamiento

                            if( self.conexion.root.buscar_credito( int(self.credito)) == False ):       #
                                #self.lb_guia.setText('ENCONTRADA: '+ str(self.credito))                          #                  
                                #self.envio_guia(str(self.guia))
                                time.sleep(0.2)
                                #self.lb_guia.setText('ALMACENADA: '+ str(self.credito))    
                                self.c_top = False #se cambia para que no siga consultando a la BD inecesariamente.
                                print('NOTA CREDITO TOP ALMACENADA: ' + lista_creditos[index1]  + ' -  Buscando mayor a: ' + str(self.credito) )
                            else:
                                self.c_top = False
                                #self.lb_guia.setText('EN LA BD: '+ str(self.credito)) 
                                print('TOP NOTA CREDITO en la BD - buscando MAYOR A: ' + str(self.credito))

                        else:
                            #self.lb_guia.setText('EN LA BD: '+ str(self.credito))    
                            print('Top NOTA CREDITO almacenado anteriormetne - Buscando NOTA CREDITO mayor a: '+ str(self.credito))
                    
                    time.sleep(self.rango3)

                except ValueError:
                    print('nota de credito no encontrada en la lista')
                    #self.lb_guia.setText('NO ENCONTRADA: '+ str(self.guia))    
                    time.sleep(2)

                print('------------------------------------------------------------------')
            else:
                self.conectar()
                print('desde credito ... reconectando ...')
                #self.lb_guia.setText('reconectando...')

        print('busqueda de notas de credito finalizada')
        #self.lb_detalle2.setText('BUSQUEDA FINALIZADA')
        #self.lb_guia.setText(':3')

    def busqueda_rango_fact(self, lista_facturas):
        print('-------------------------FACTURA-------------------------------')
        try:
            
            index1 = lista_facturas.index(str(self.factura))
            
            if lista_facturas[0] != str(self.factura): #que no consulte siemrpre a la BD

                if( self.conexion.root.buscar_fact( int(self.factura)) == False ):       #
                        self.lb_factura.setText('ENCONTRADA: '+ str(self.factura))                                            
                        self.envio_factura(str(self.factura))
                        time.sleep(0.2) 
                        self.lb_factura.setText('ALMACENADA: '+ str(self.factura))
                        nuevo_index = index1 - 1
                        if nuevo_index > 0:
                            self.factura = lista_facturas[nuevo_index]
                            self.f_top = False
                            print('FACT ALMACENADA: ' + lista_facturas[index1] + ' -  Buscando: ' + str(self.factura) )
                        elif nuevo_index == 0 :
                            self.factura = lista_facturas[nuevo_index]
                            self.f_top = True
                            print('FACT ALMACENADA: ' + lista_facturas[index1]  + ' -  Buscando el top: ' + str(self.factura) )
                        
                        
                                                    
                else:           #si esta en la BD
                    self.lb_factura.setText('EN LA BD: '+ str(self.factura))                                                   #
                    nuevo_index = index1 - 1  
                    if nuevo_index > 0 : #se captura el indice que continua si es que existe
                        self.factura = lista_facturas[nuevo_index]
                        self.f_top = False
                        print('FACT en la BD: ' + lista_facturas[index1]  + ' -  Buscando a: ' + lista_facturas[nuevo_index] )
                    elif nuevo_index == 0 :
                        self.factura = lista_facturas[nuevo_index]
                        self.f_top = True
                        print('FACT en la BD: ' + lista_facturas[index1]  + ' -  Buscando el top : ' + lista_facturas[nuevo_index] )

            else:
                if self.f_top: #si esta al inicio de la lista, se analisa su almacenamiento

                    if( self.conexion.root.buscar_fact( int(self.factura)) == False ):       #
                        self.lb_factura.setText('ENCONTRADA: '+ str(self.factura))
                        time.sleep(0.2)                          #                  
                        self.envio_factura(str(self.factura))
                        self.lb_factura.setText('ALMACENADA: '+ str(self.factura))
                        self.f_top = False #se cambia para que no siga consultando a la BD inecesariamente.
                        print('FACT TOP ALMACENADA: ' + lista_facturas[index1]  + ' -  Buscando mayor a: ' + str(self.factura) )
                    else:
                        self.f_top = False
                        self.lb_factura.setText('EN LA BD: '+ str(self.factura))
                        print('TOP FACT en la BD - buscando MAYOR A: ' + str(self.factura) )

                else:
                    self.lb_factura.setText('EN LA BD: '+ str(self.factura))
                    print('Top FACT almacenado anteriormetne - Buscando factura mayor a: '+ str(self.factura) ) 
             

            time.sleep(self.rango)

        except ValueError:
            print('factura no encontrada en la lista')
            self.lb_factura.setText('NO ENCONTRADA: '+ str(self.factura))
            self.fact_encont = False
            time.sleep(2)
        print('------------------------------------------------------------------')     

    def busqueda_rango_bol(self, lista_boletas): #continuar
        print('--------------------------BOLETA--------------------------------') 
        try:
             
            index1 = lista_boletas.index(str(self.boleta))
            
            if lista_boletas[0] != str(self.boleta): #que no consulte siemrpre a la BD

                if( self.conexion.root.buscar_bol( int(self.boleta)) == False ):       #
                        self.lb_boleta.setText('ENCONTRADA: '+ str(self.boleta))                          #                  
                        self.envio_boleta(str(self.boleta))
                        time.sleep(0.2)
                        self.lb_boleta.setText('ALMACENADA: '+ str(self.boleta))    
                        nuevo_index = index1 - 1
                        if nuevo_index > 0:
                            self.boleta = lista_boletas[nuevo_index]
                            self.b_top = False
                            print('BOL ALMACENADA: ' + lista_boletas[index1] + ' -  Buscando: ' + str(self.boleta) )
                        elif nuevo_index == 0 :
                            self.boleta = lista_boletas[nuevo_index]
                            self.b_top = True
                            print('BOL ALMACENADA: ' + lista_boletas[index1]  + ' -  Buscando el top: ' + str(self.boleta) )
                        
                                                    
                else:           #si esta en la BD  
                    self.lb_boleta.setText('EN LA BD: '+ str(self.boleta))                                                     #
                    nuevo_index = index1 - 1  
                    if nuevo_index > 0 : #se captura el indice que continua si es que existe
                        self.boleta = lista_boletas[nuevo_index]
                        self.b_top = False
                        print('BOL en la BD: ' + lista_boletas[index1]  + ' -  Buscando a: ' + lista_boletas[nuevo_index] )
                    elif nuevo_index == 0 :
                        self.boleta = lista_boletas[nuevo_index]
                        self.b_top = True
                        print('BOL en la BD: ' + lista_boletas[index1]  + ' -  Buscando el top : ' + lista_boletas[nuevo_index] )

            else:
                if self.b_top: #si esta al inicio de la lista, se analisa su almacenamiento

                    if( self.conexion.root.buscar_bol( int(self.boleta)) == False ):       #
                        self.lb_boleta.setText('ENCONTRADA: '+ str(self.boleta))                          #                  
                        self.envio_boleta(str(self.boleta))
                        time.sleep(0.2)
                        self.lb_boleta.setText('ALMACENADA: '+ str(self.boleta))    
                        self.b_top = False #se cambia para que no siga consultando a la BD inecesariamente.
                        print('BOL TOP ALMACENADA: ' + lista_boletas[index1]  + ' -  Buscando mayor a: ' + str(self.boleta) )
                    else:
                        self.b_top = False
                        self.lb_boleta.setText('EN LA BD: '+ str(self.boleta))    
                        print('TOP BOL en la BD - buscando MAYOR A: ' + str(self.boleta) )

                else:
                    self.lb_boleta.setText('EN LA BD: '+ str(self.boleta))    
                    print('Top BOL almacenado anteriormetne - Buscando boleta mayor a: '+ str(self.boleta) ) 
            
            time.sleep(self.rango)

        except ValueError:
            print('boleta no encontrada en la lista')
            self.lb_boleta.setText('NO ENCONTRADA: '+ str(self.boleta))    
            time.sleep(2)
        print('------------------------------------------------------------------')  
                            
    def obtener_fact_bol_ordenadas(self):
        if(os.path.isdir(self.filename)):
            contenido = os.listdir(self.filename)
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
    def obtener_guias_ordenadas(self):
        if(os.path.isdir(self.filename_guia)):
            contenido = os.listdir(self.filename_guia)
            guias = []
            for nombre in contenido:
                aux = nombre.split('.')
                aux2 = aux[0].split('_')
                guias.append( aux2[1] )
            guias.reverse()
            return guias
        else: 
            print('no es un directorio el de guias')
    def obtener_creditos_ordenadas(self):
        if(os.path.isdir(self.filename_credito)):
            contenido = os.listdir(self.filename_credito)
            creditos = []
            for nombre in contenido:
                aux = nombre.split('.')
                aux2 = aux[0].split('_')
                if aux2[0] == '61':
                    creditos.append( aux2[1] )
                
            creditos.reverse()
            #print(creditos)
            return creditos
        else: 
            print('no es un directorio el de creditos')
    
    
    def Obt_nombre(self , linea):
        linea = linea[118:].split(':') 
        linea = linea[1].split(' ')
        #print(linea)
        nombre = ''
        first = True
        i = 0
        while(i < len(linea) - 2): #Se puede optimizar para que no recorra toda la lista
            if(linea[i] != '' and first == True):
                nombre = linea[i]
                first = False
            elif(linea[i] != '' and first == False):
                nombre = nombre + ' ' + linea[i]  #Se da formato al nombre del vendedor
            
            i += 1
        return nombre

    def obtener_ultimos(self):
        boletas , facturas = self.obtener_fact_bol_ordenadas()
        guias = self.obtener_guias_ordenadas()
        creditos = self.obtener_creditos_ordenadas()
        print('Ultima guia: ' + guias[0])
        print('Ultima boleta: '+ boletas[0])
        print('Ultima factura: '+ facturas[0])
        print('Ultima nota credito: '+ creditos[0] )
        self.lineboleta.setText(boletas[0])
        self.linefactura.setText(facturas[0])
        self.lineguia.setText(guias[0])
        self.linecredito.setText(creditos[0])

    def closeEvent(self, event):
        self.detener()
        self.detener2()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myappid = 'madenco.extractor' # arbitrary string
    app.setWindowIcon(QIcon('icono_imagen/search.ico'))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid) 
    inicio = menu()
    inicio.show()
    sys.exit(app.exec_())
  





