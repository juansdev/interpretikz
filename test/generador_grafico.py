str2=""
expresion_ant = ""
diagonal_der_arriba = False
diagonal_der_abajo = True
diagonal_izq_abajo = False
der = False
izq = False
arriba = False
abajo = False
#\draw[color=red] (140,100) rectangle (10,10);
x = 300
y = 300
ancho = str(10)
alto = str(10)
step = 10
cantidad_figuras = 10
def PatronMovimiento():
    if diagonal_der_arriba:
        patron_movimiento = [num+step for num in [x,y]]
    if diagonal_der_abajo:
        patron_movimiento = [num-step if int(num)-step > 0 and int(count)!=0 else "0" if int(num)-step <= 0 and int(count)!=0 else num+step for count,num in enumerate([x,y])]
    elif diagonal_izq_abajo:
        patron_movimiento = [num-step if int(num)-step > 0 else "0" for num in [x,y]]
    elif der:
        patron_movimiento = [num+step if int(count)!=1 else str(y) for count,num in enumerate([x,y])]
    elif izq:
        patron_movimiento = [num-step if int(num)-step > 0 and int(count)!=1 else str(y) if not int(count)!=1 else "0" for count,num in enumerate([x,y])]
    elif arriba:
        patron_movimiento = [num+step if int(count)!=0 else str(x) for count,num in enumerate([x,y])]
    elif abajo:
        patron_movimiento = [num-step if int(num)-step > 0 and int(count)!=0 else str(x) if not int(count)!=0 else "0" for count,num in enumerate([x,y])]
    return patron_movimiento

for n in range(0,cantidad_figuras+1):
    if expresion_ant:
        expresion_ant = expresion_ant.split(",")
        x = int(expresion_ant[0])
        y = int(expresion_ant[1])
    patron_movimiento = PatronMovimiento()
    if n == 0:
        str2 = "\draw[color=red] ("+str(x)+","+str(y)+") rectangle ("+ancho+","+alto+");"
        str2+= "\n"+str2.replace(str(x)+","+str(y),",".join([str(num) for num in patron_movimiento]))
        expresion_ant = ",".join([str(num) for num in patron_movimiento])
    else:
        expresion_ant = ",".join(expresion_ant)
        remplazar = ",".join([str(num) for num in patron_movimiento])
        str3 = "\n"+"\draw[color=red] ("+expresion_ant+")"+" rectangle ("+ancho+","+alto+");".replace(expresion_ant,remplazar)
        if n != 1:
            str2+=str3
        expresion_ant=remplazar
print(str2)