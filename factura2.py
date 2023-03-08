def calcular_verificador(rut):
        
        rut.reverse()
        recorrido = 2
        multiplicar = 0
        for x in rut:
            multiplicar +=int(x)*recorrido

            if recorrido==7: 
                recorrido = 1

            recorrido+=1
        modulo = multiplicar % 11
        resultado = 11-modulo

        if resultado == 11: 
            digito=0
        elif resultado == 10: 
            digito="K"
        else: 
            digito=resultado

        return digito

filename = '/Users/super/Desktop/INGENIERIA INFORMATICA/PRACTICA 1/Respaldo/33_174658.txt'
with open(filename, 'r') as file:
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

                            
                            rut = linea[36:53]  # se obtiene el rut | limite [36:53] exacto
                            rut = rut.split(': ')
                            rut = rut[1]
                            rut = rut.split('-')
                            try:
                                numeros = int(rut[0])
                                numeros = str(numeros)
                                lista = []
                                for letra in numeros:
                                    lista.append(letra)
                                digito = calcular_verificador(lista)
                                rut = str(numeros) + '-' + str(digito)
                                print(rut)
                            except ValueError:
                                rut = None
                                print(rut)



                        elif  linea[0:5] == 'Razon' :  #Se obtiene el nombre del cliente.
                            nombre =linea.split(': ')
                            nombre = nombre[1]
                            cliente = nombre[:len(nombre)-1]
                            cliente = cliente.rstrip()
                            
                            

                        
                        elif linea[0:4] == 'Giro':
                            aux_lines = lines[i + 1]
                            auxlinea = aux_lines
                            auxlinea = auxlinea[0:len(auxlinea) - 1] #se obtiene la direccion
                            print(auxlinea)   

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
                        elif linea[0:8] == 'Telefono':
                            telefono = linea[9:23] 
                            print(telefono)  #se obtiene el telefono
                            print(f'longuitud: {str(len(telefono))}')
                            if telefono == '              ':
                                telefono = ''
                                print('telefono no encontrado')
                            else:
                                telefono = int(telefono)
                                print(telefono)
                                print(f'longuitud: {len(str(telefono))}')
                            
                            
                            
                        
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
                        #print('El dato leido no es descripcion o el telefono esta en formato no legible')      
                        pass      
                
                i += 1