from datos_iniciales import DatosIniciales

datos = DatosIniciales(
    numero_peatones=10, 
    numero_vehiculos=5, 
    congestion="media", 
    incidentes=True
    )

datos.procesar_datos()