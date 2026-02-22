
import tkinter as tk
import threading
import time

from procesar_señal_trade.opteniendo_señal import un_analizis
from procesar_señal_trade.configurando_analisis import *
from procesar_sonido.reprodusco_alerta import procesar_senales_trading

class opciones_para_programa:
    
    def __init__(self):
        
        ADVETENCIA= "Este programa es solo una herramienta.\
        \nEl autor no se hace responsable de pérdidas financieras.\
        \nEsta prohibido la copia o alteracion \
        \nde este programa sin permiso del autor."
        self.password= "Dios-es-mi-luz-gracias-ael-sonrio"
        self.situacion= None
        self.deten= None
        
        self.candado= threading.Lock()
        
        self.ventana= tk.Tk()
        self.ventana.title("Señales de Trading")
        self.ventana.geometry("350x200")
        
        self.area_0= tk.LabelFrame(self.ventana)
        self.area_0.pack(expand= True, fill= tk.BOTH)
        self.area_1= tk.LabelFrame(self.ventana)
        self.area_1.pack(expand= True, fill= tk.BOTH)
        self.area_2= tk.LabelFrame(self.ventana)
        self.area_2.pack(expand= True, fill= tk.BOTH)
        
        self.mensaje_abvertencia= tk.Label(self.area_0, text= ADVETENCIA)
        self.mensaje_abvertencia.pack()
        
        # indicacion de que aqui va el area de password al lado izquierdo
        self.etiqueta_de_password= tk.Label(self.area_1, text= "Ingrese la contraseña:")
        self.etiqueta_de_password.pack(side= "left")
        # caja de texto para password al lado derecho
        self.area_de_password= tk.Entry(self.area_1, show="*", width= 30)
        self.area_de_password.pack(side= "left")
        
        # boton para iniciar sesion
        self.boton_de_inicio= tk.Button(self.area_2, text= "Iniciar Sesión", command= self.iniciar_sesion)
        self.boton_de_inicio.pack()
        
        self.ventana.mainloop()
        
    def iniciar_sesion(self):
        password_ingresado= self.area_de_password.get()
        # Aqui se puede agregar la logica para verificar el password
        if password_ingresado == self.password:
            self.si_contraseña_es_correcta_crea_subventana()
            self.ventana.withdraw()  # ocultar la ventana despues de iniciar sesion 
        else:
            self.mensaje_abvertencia.config(text="\
                \nPassword incorrecto. \
                \nIntente de nuevo.\
                \n")
                
    def si_contraseña_es_correcta_crea_subventana(self):
        self.sub_ventana= tk.Toplevel(self.ventana)
        self.sub_ventana.title("Subventana de Trading")
        self.sub_ventana.geometry("400x250")
        
        # Configurar el protocolo de cierre
        self.sub_ventana.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        self.area_trabajo_0= tk.LabelFrame(self.sub_ventana)
        self.area_trabajo_0.pack(expand= True, fill= tk.BOTH)
        self.area_trabajo_1= tk.LabelFrame(self.sub_ventana)
        self.area_trabajo_1.pack(expand= True, fill= tk.BOTH)
        self.area_trabajo_2= tk.LabelFrame(self.sub_ventana)
        self.area_trabajo_2.pack(expand= True, fill= tk.BOTH)

        "------------------------------------------------"
        # primera area de trabajo (solo cambia de color )
        self.area_trabajo_0.config(bg="yellow")
        self.area_trabajo_2.config(bg="yellow")
            
        "------------------------------------------------"
        # configurando el programa (si el usuario lo quiere hacer)
        
        self.seccion_0= tk.LabelFrame(self.area_trabajo_1, relief="flat", bd=0)
        self.seccion_0.pack(expand= True, fill= tk.BOTH)
        self.seccion_1= tk.LabelFrame(self.area_trabajo_1, relief="flat", bd=0)
        self.seccion_1.pack(expand= True, fill= tk.BOTH)
        self.seccion_2= tk.LabelFrame(self.area_trabajo_1, relief="flat", bd=0)
        self.seccion_2.pack(expand= True, fill= tk.BOTH)
        self.seccion_3= tk.LabelFrame(self.area_trabajo_1)
        self.seccion_3.pack(expand= True, fill= tk.BOTH)
        
        if True: # cajas de txto para nueva URL y pixeles
            
            # si el usuario quiere puede ingresar una nueva URL 
            self.etiqueta_nueva_url= tk.Label(self.seccion_0, text= "Nueva URL:")
            self.etiqueta_nueva_url.pack(side= "left")
            # caja de texto para nueva URL al lado derecho
            self.ingreso_nueva_url= tk.Entry(self.seccion_0)
            self.ingreso_nueva_url.pack(side= "left")
            
            # si el usuario quiere puede redistribuir los pixeles que quiere ver 
            self.etiqueta_para_pixeles= tk.Label(self.seccion_0, text= "pixeles:")
            self.etiqueta_para_pixeles.pack(side= "left")
            # caja de texto para 
            self.ingreso_para_pixeles= tk.Entry(self.seccion_0)
            self.ingreso_para_pixeles.pack(side= "left")
        
        if True: # espacio vacio
            espacio_vacio= tk.Label(self.seccion_1, text=" \n")
            espacio_vacio.pack()
        
        if True: # botones para guardar y visualizar configuracion

            self.separacion_a0= tk.Label(self.seccion_2, text="         ")
            self.separacion_a0.grid(row=0, column=0)

            self.boton_de_guardar_configuracion= tk.Button(self.seccion_2, text= "Guardar Configuración", command= lambda: self.tratando_datos(2))
            self.boton_de_guardar_configuracion.grid(row=0, column=1)
            
            self.separacion_a1= tk.Label(self.seccion_2, text="         ")
            self.separacion_a1.grid(row=0, column=2)
            
            self.boton_para_visualizar_configuracion= tk.Button(self.seccion_2, text= "Ver Configuración Actual", command= lambda: self.tratando_datos(3))
            self.boton_para_visualizar_configuracion.grid(row=0, column=3)
        
        if True: # mensaje de estado del programa
            
            self.mensaje_de_estado= tk.Label(self.seccion_3, text= "Estado del Programa: Inactivo")
            self.mensaje_de_estado.pack()
        
        "------------------------------------------------"
        # area de ejecucion del programa (boton Activar/Desactivar)
        
        self.separacion_b0= tk.Label(self.area_trabajo_2, text="         ", bg= "yellow")
        self.separacion_b0.grid(row=0, column=0)
        
        self.activate_button= tk.Button(self.area_trabajo_2, text="Activar Programa", command= lambda: self.tratando_datos(1))
        self.activate_button.config(padx=10, pady=5)
        self.activate_button.grid(row=0, column=1)
        
        self.separacion_b1= tk.Label(self.area_trabajo_2, text="         ", bg= "yellow")
        self.separacion_b1.grid(row=0, column=2)

        self.desactivate_button= tk.Button(self.area_trabajo_2, text=" Desactivar Programa", command= lambda: self.tratando_datos(0))
        self.desactivate_button.config(padx=10, pady=5)
        self.desactivate_button.grid(row=0, column=3)

        "------------------------------------------------"
        
    def establesco_visual_del_programa(self, estado):
        if estado == "activado":
            self.area_trabajo_0.config(bg="green")
            self.mensaje_de_estado.config(text="Estado del Programa: Activo")
        else:
            self.area_trabajo_0.config(bg="lightcoral")
            self.mensaje_de_estado.config(text="Estado del Programa: Inactivo")
            
    def cerrar_aplicacion(self):
        """Método para cerrar tanto la subventana como la ventana principal"""
        if hasattr(self, 'sub_ventana'):
            self.sub_ventana.destroy()
        self.ventana.quit()
        self.ventana.destroy()
        self.deten.set()  # Asegurarse de detener los hilos si están corriendo
        
    def reformula(self, numero):
        convirtiendo= numero * 2
        return convirtiendo + 1
        
    def tratando_datos(self, dato):
        # redefino los numeros para adaptarlos a turn_final
        if dato == 0:
            dato += 1
            new= self.reformula(dato)
            self.ejecutar_turn_final(new)
        elif dato == 1:
            dato += 1
            new= self.reformula(dato)
            self.ejecutar_turn_final(new)
        elif dato == 2:
            dato += 1
            new= self.reformula(dato)
            self.ejecutar_turn_final(new)
        elif dato == 3:
            dato += 1
            new= self.reformula(dato)
            self.ejecutar_turn_final(new)
        
    def hacer_un_analizis(self, parare):
        
        while not parare.is_set():
            with self.candado:
                if self.situacion is None:
                    
                    self.situacion= un_analizis()
                        
    def hacer_sonido(self, parar):
        
        while not parar.is_set():
            with self.candado:
                if self.situacion == True:
                    print(">>> ACCIÓN REALIZADA: ABRIR EN COMPRA")
                    self.area_trabajo_0.config(bg="green")
                    procesar_senales_trading(modo= False, tendencia= True)
                    self.situacion= None
                if self.situacion == False:
                    print(">>> ACCIÓN REALIZADA: ABRIR EN VENTA")
                    self.area_trabajo_0.config(bg="red")
                    procesar_senales_trading(modo= False, tendencia= False)
                    self.situacion= None
                        
                time.sleep(0.3)
                
    def ejecutar_turn_final(self, entrada):
        self.indaga= entrada
        self.sub_paso= None
        
        while self.indaga < 100:
            while self.indaga < 8:
                while self.indaga < 6:
                    while self.indaga < 4:
                        while self.indaga < 2:
                            
                            self.indaga= 101 # salir de todos los bucles
                            continue
                        
                        if self.indaga == 3:
                            # desactiva el programa
                            "primero cambio el color del area de trabajo"
                            self.area_trabajo_0.config(bg="yellow")
                            
                            self.deten.set()
                            
                            print("Programa desactivado. Deteniendo tareas...")
                            self.mensaje_de_estado["text"]= "El programa está detenido."                        
                            
                            self.indaga= 101 # salir de todos los bucles
                            continue
                        else:
                            break
                    
                    if self.indaga == 5:
                        # activa el programa
                        
                        "primero cambio el color del area de trabajo"
                        self.area_trabajo_0.config(bg="blue")
                        
                        self.mensaje_de_estado["text"]= "El programa está funcionando."                        
                        self.deten= threading.Event()
                        
                        "luego simulo la activacion del programa"
                        hilo_analisis= threading.Thread(target= self.hacer_un_analizis, args=(self.deten,))
                        hilo_analisis.start()
                        
                        hilo_sonido= threading.Thread(target= self.hacer_sonido, args=(self.deten,))
                        hilo_sonido.start()
                                                
                        self.indaga= 101 # salir de todos los bucles
                        continue
                        
                    else:
                        break

                if self.indaga == 7:
                    # guarda la configuracion
                    
                    url = self.ingreso_nueva_url.get()
                    ancho_region = self.ingreso_para_pixeles.get()
                    
                    str_url= str(url)
                    int_ancho_region= int(ancho_region)
                    
                    actualiza_configuracion_analisis(str_url, int_ancho_region)
                    print("Configuración Guardada.")

                    self.indaga= 101 # salir de todos los bucles
                    continue
                else:
                    break

            if self.indaga == 9:
                # muestra la configuracion actual
                print("Mostrando configuración actual...")
                visualizar_region_analisis()
                
                self.indaga= 101 # salir de todos los bucles
                continue
            else:
                break
            
