
""" modulo para optener la señal de trade a partir de la señal generada """


"========================================================"
# importaciones necesarias
from procesar_señal_trade.observado.viendo_video import fluctuacion_señal, datos
#from observado.viendo_video import fluctuacion_señal, datos

"========================================================"

class UltimoMomentoSenalTrade:
    """Clase para almacenar el último momento de la señal de trade."""
    
    def __init__(self):
        self.ultimo_momento= 2 # con esto retengo durante mas tiempo la señal obtenida
        
bandeja= UltimoMomentoSenalTrade()

def extraccion_senal_trade(algun_momento_de_la_senal):
    return algun_momento_de_la_senal.devuelve_estado_vivo()

def optengo_senales_trading():
    
    # Obteniendo la señales de trading
    moment= extraccion_senal_trade(fluctuacion_señal)
    
    print('Señales obtenidas: ', str(bandeja.ultimo_momento), str(moment[0]))
    
    if moment is not None:
        momento_presente= moment[0]
        
        #  Decidir acción de trade, retornando True para comprar y False para vender
        if (bandeja.ultimo_momento == 1) and (momento_presente == 0):
            print("Señal de TRADE DETECTADA: ABRIR_EN_VENDER")
            bandeja.ultimo_momento= 0
            return False
        elif (bandeja.ultimo_momento == 0) and (momento_presente == 1):
            print("Señal de TRADE DETECTADA: ABRIR_EN_COMPRAR")
            bandeja.ultimo_momento= 1
            return True
        elif (bandeja.ultimo_momento == 2):
            print("apenas iniciando la aplicacion.")
            bandeja.ultimo_momento= momento_presente
            return None
        else: 
            # print("No hay señal de trade nueva.")
            return None
        
    else:
        print("No se pudo obtener la señal de trading")
        return None
    
def un_analizis():
    
    condicion= optengo_senales_trading()

    if condicion == True:
        print(">>> A COMPRAR")
        return True
    elif condicion == False:
        print(">>> A VENDER")
        return False
    else:
        print("NO HACER NADA")
        return None
    
