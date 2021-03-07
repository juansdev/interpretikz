print("Debes de digitar un color tipo 'cyan!75!green'")
color = input("Digitar color:")
color_array = color.split("!")
color_1 = color_array[0].lower().strip()
porcentaje = color_array[1]
try:
    porcentaje = int(porcentaje)
except:
    print("El porcentaje debe de tener un valor INTEGER")
color_2 = color_array[2].lower().strip()
if color_1 == "cyan":
    color_1 = (0,1,1)
if color_2 == "green":
    color_2 = (0,1,0)
color_elegido = []
#cyan!100!green -> Cyan
#cyan!0!green -> Green
indice = 0
for color in color_2:
    if color != color_1[indice]:
        #0
        if not color:
            color_elegido.append((color+(porcentaje/100)))
        #1
        elif color:
            color_elegido.append((color-(porcentaje/100)))
    else:
        color_elegido.append(color)
    indice+=1