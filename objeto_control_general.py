
""" En este modulo establesco las instancias para el control general de la señal de trade desde la interfaz """

"========================================================"
# importaciones necesarias

"========================================================"

class ControlGeneralSenalTrade:
    """Clase que controla la configuracion (cajas de textos)"""
    
    def __init__(self):
        
        self.nueva_url_de_video= "https://www.youtube.com/watch?v=-ps7V40GrA4"
        "video que se va a abrir"
        
        self.pixeles_a_observar= 90
        "ancho de la pantalla"
        
control_general= ControlGeneralSenalTrade()
"Desde la interfaz controla la señal que se observa"

