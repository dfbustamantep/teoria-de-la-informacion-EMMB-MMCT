class DatosIniciales:
    
    def __init__(self, numero_peatones:int=0, numero_vehiculos:int=0, congestion:str="baja", incidentes:bool=False):
        self.numero_peatones=numero_peatones;
        self.numero_vehiculos=numero_vehiculos;
        self.congestion=congestion;
        self.incidentes=incidentes;
        
    def procesar_datos(self):
        ''' variables donde vamos a asignarle prioridad a los peatones o a los vehiculos
            esto de acuerdo al estado de las diferentes vairables y con esto determinar la estrategia
            a seguir
        '''
        self.puntos_peatones=0
        self.puntos_vehiculos=0
        
        if self.numero_peatones !=0:
            if self.numero_peatones > 50:
                self.puntos_peatones+=5 
            elif self.numero_peatones > 30:
                self.puntos_peatones+=3    
            elif self.numero_peatones > 15:
                self.puntos_peatones+=2
            else:
                self.puntos_peatones+=1
        
        if self.numero_vehiculos !=0:
            if self.numero_vehiculos > 50:
                self.puntos_vehiculos+=5   
            elif self.numero_vehiculos > 30:
                self.puntos_vehiculos+=3   
            elif self.numero_vehiculos > 15:
               self.puntos_vehiculos+=2                        
            else:
                self.puntos_vehiculos+=1
                
        if self.congestion == "baja":
            self.puntos_vehiculos-=1            
        if self.congestion == "media":
            self.puntos_vehiculos+=1            
        if self.congestion == "alta":
            self.puntos_vehiculos+=2
            
        if self.incidentes:
            self.puntos_vehiculos+=3
            
        self.diferencia = self.puntos_peatones - self.puntos_vehiculos
        
        if self.diferencia > 2:
            self.estrategia = "Prioridad a los peatones"
        elif self.diferencia < -1:
            self.estrategia = "Prioridad a los vehiculos"
        else:
            self.estrategia = "Mantener estrategia"

        print(f"Despues de procesar los datos iniciales, la estrategia a seguir es:{self.estrategia}")
        
        