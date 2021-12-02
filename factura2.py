filename = '/Users/super/Desktop/INGENIERIA INFORMATICA/PRACTICA 1/Respaldo/33_174741.txt'
with open(filename, 'r') as file:

    lines = file.readlines()
    iterator = 1
    items = []
    i = 0
    while i < len(lines) :

        if lines[i] != '\n': #Chequear que la linea no sea vacia
            linea = lines[i]

            if(linea[0:4]  == 'Nume' ):
                nro_interno = linea.split('   ')
                nro_interno = int(nro_interno[1]) #Se obtiene el nro interno bruto. Tipo entero
                print(nro_interno)
               
            elif(linea[0:5] == 'Fecha' ):
                fecha = linea.split('  ')       #Se obtiene la fecha de tipo String
                print(fecha[1])

            elif(linea[0:4] == 'Hora' ):
                hora = linea.split(' ')         #Se obtiene la hora de tipo String
                print(hora[1])
            elif  linea[0:5] == 'Razon' :
                
                nombre =linea.split(': ')
                nombre = nombre[1]
                cliente = nombre[:len(nombre)-1]
                print(cliente)   #Se obtiene el nombre del cliente
            #elif linea[0:8] == 'Telefono':

            elif(linea[0:8] == 'Vendedor' ):
                vendedor = linea.split(': ')
                vendedor = vendedor[1]
                vendedor = vendedor[:len(vendedor)-1] #Se obtiene el nombre del vendedor de tipo string
                print(vendedor)


            elif(linea[0] == str(iterator) ):
                try:
                    aux = int(linea[0:4])

                    if(aux == iterator):
                        separador = linea[4:22].replace(',' , '.' , 1)
                        cantidad = float(separador)                      #Se obtiene la cantidad bruta como separator[0] de tipo string
                        codigo = linea[22:57].split(' ')                #Se obtiene el codigo del producto como codigo[0] de tipo string
                        descripcion = linea[58:138]                     #Se obtiene la descripcion bruta como descripcion[0] de tipo string
                        #print(p_unitario)
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
                            print(str(cantidad) + ' ' + codigo[0]  + ' ' + descripcion + ' ' + str(p_unitario) + ' ' + str(p_total))
                        item = (cantidad , codigo[0] , descripcion , p_unitario ,p_total)
                        items.append(item)

                        iterator +=1
                except ValueError:
                    print('El dato no es una descripcion')
                    
            elif(linea[0:5] == 'Total'):
                total = linea.split('     ')
                total = float(total[1])                   #Se obtiene el total de la venta de tipo float
                print(total)                              
        i += 1
    print(items)