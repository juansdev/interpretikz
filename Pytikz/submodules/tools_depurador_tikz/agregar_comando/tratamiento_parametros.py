from bisect import bisect, insort

class TratamientoParametros():
    def __init__(self,delimitadores_parametros_comando):
        self.delimitadores_parametros_comando = delimitadores_parametros_comando
    def extraerParametrosSinDefinir(self,posiciones_parametrizados=[],estilos_parametrizados={},comando_invocado=False):
        def result_extraer(valor,comando_invocado):
            if valor.find("#")!=-1:
                for delimitador in self.delimitadores_parametros_comando:
                    array_valor = [s for s in valor.split(delimitador)]
                    if len(array_valor):
                        for valor in array_valor:
                            if valor.find("#")!=-1:
                                if not comando_invocado:
                                    valor = valor.replace("#","")
                                    if valor.isdigit():
                                        return int(valor)
                                else:
                                    return valor
        parametros_sin_definir = []
        if len(posiciones_parametrizados):
            for valor_arr in posiciones_parametrizados:#('#3', '-1')
                for valor in valor_arr:
                    result_valor = result_extraer(valor,comando_invocado)
                    if result_valor:
                        parametros_sin_definir.append(result_valor)
        elif len(list(estilos_parametrizados.values())):
            #{'top color': '#7!30!white', 'bottom color': '#7!70!black', ' line width ': ' 1pt', 'rounded corners': '2ex', 'xshift': '0cm', 'yshift': '0cm'}
            for valor in list(estilos_parametrizados.values()):
                result_valor = result_extraer(valor,comando_invocado)
                if result_valor:
                    parametros_sin_definir.append(result_valor)
        return parametros_sin_definir
    def validarSecuenciaNumerica(self,cantidad_parametros,array_secuencia_numerica):
        #Los parametros deben ser secuenciales #1,#2,#3. ETC
        parametros_sin_definir_ordenado = []
        indice = 0
        for e in array_secuencia_numerica:
            _ = bisect(parametros_sin_definir_ordenado, e)
            insort(parametros_sin_definir_ordenado, e)
            indice+=1
        indice = 0
        #Hay parametros a definir..
        if len(parametros_sin_definir_ordenado):
            for _ in parametros_sin_definir_ordenado:
                if indice>0:
                    if parametros_sin_definir_ordenado[indice-1] != parametros_sin_definir_ordenado[indice] and parametros_sin_definir_ordenado[indice-1]+1 != parametros_sin_definir_ordenado[indice]:
                        parametros_sin_definir_ordenado = []
                        break
                indice+=1
            if not len(parametros_sin_definir_ordenado):
                return {"error":"Error cerca de '#' se esperaba una secuencia numerica de parametros, ej: #1,#2,#3"}
            else:
                try:
                    int(cantidad_parametros)
                except:
                    return {"error":"Error cerca de la cantidad de parametros '#' se esperaba un numero INTEGER."}
                cantidad_parametros = int(cantidad_parametros)
                array_secuencia_numerica = set(array_secuencia_numerica)
                if len(array_secuencia_numerica) != cantidad_parametros:
                    return {"error":str(cantidad_parametros)+" es diferente a la cantidad de parametros definidos (#) "+str(len(array_secuencia_numerica))}
                else:
                    return True
        #No hay parametros a definir
        else:
            return True