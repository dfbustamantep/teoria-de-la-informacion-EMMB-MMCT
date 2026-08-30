#pip install stable-baselines3 gymnasium numpy

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

class EntornoSemaforoInteligente(gym.Env):
    """
    Entorno de simulación de tráfico adaptativo basado en procesos de decisión de Markov (MDP).
    Optimiza la estacionariedad minimizando el tiempo acumulado de espera.
    """
    def __init__(self):
        super(EntornoSemaforoInteligente, self).__init__()
        
        # MÓDULO DE ACTUACIÓN: 
        # 0 = Luz Verde para Vehículos
        # 1 = Luz Verde para Peatones
        self.action_space = spaces.Discrete(2)
        
        # MÓDULO DE PERCEPCIÓN (Espacio de Observación):
        # [cola_vehiculos, tiempo_espera_vehiculos, cola_peatones, tiempo_espera_peatones, incidentes]
        limite_inferior = np.array([0, 0, 0, 0, 0], dtype=np.float32)
        # Límites máximos teóricos para normalización
        limite_superior = np.array([200, 1000, 200, 1000, 1], dtype=np.float32) 
        
        self.observation_space = spaces.Box(
            low=limite_inferior, 
            high=limite_superior, 
            dtype=np.float32
        )
        
        self.max_pasos_por_episodio = 200
        self.paso_actual = 0
        
    def reset(self, seed=None, options=None):
        """Reinicia la simulación para un nuevo episodio de entrenamiento."""
        super().reset(seed=seed)
        self.paso_actual = 0
        
        # Estado inicial aleatorio
        self.cola_vehiculos = np.random.randint(0, 15)
        self.tiempo_espera_vehiculos = 0.0
        self.cola_peatones = np.random.randint(0, 10)
        self.tiempo_espera_peatones = 0.0
        self.incidente = np.random.choice([0.0, 1.0], p=[0.95, 0.05]) # 5% probabilidad de incidente
        
        return self._obtener_estado(), {}

    def _obtener_estado(self):
        """Construye el vector matemático que procesará la red neuronal."""
        return np.array([
            self.cola_vehiculos,
            self.tiempo_espera_vehiculos,
            self.cola_peatones,
            self.tiempo_espera_peatones,
            self.incidente
        ], dtype=np.float32)

    def step(self, accion):
        """Dinámica del sistema: Aplica una acción, calcula consecuencias y otorga recompensas."""
        self.paso_actual += 1
        
        # 1. Simulación de llegada continua de actores viales (entropía del sistema)
        self.cola_vehiculos += np.random.randint(1, 6)
        self.cola_peatones += np.random.randint(0, 4)
        
        # 2. Transición de Estado basada en la acción de la IA
        if accion == 0: # Verde para Vehículos
            tasa_despeje = 15 if self.incidente == 0 else 5 # Un incidente frena el flujo vehicular
            self.cola_vehiculos = max(0, self.cola_vehiculos - tasa_despeje)
            
            # Se reinicia el tiempo de espera vehicular si se vacía la cola
            self.tiempo_espera_vehiculos = 0 if self.cola_vehiculos == 0 else self.tiempo_espera_vehiculos + self.cola_vehiculos
            # Los peatones siguen acumulando tiempo
            self.tiempo_espera_peatones += self.cola_peatones 
            
        elif accion == 1: # Verde para Peatones
            self.cola_peatones = max(0, self.cola_peatones - 20)
            
            self.tiempo_espera_peatones = 0 if self.cola_peatones == 0 else self.tiempo_espera_peatones + self.cola_peatones
            # Vehículos siguen acumulando tiempo
            self.tiempo_espera_vehiculos += self.cola_vehiculos
            
        # 3. MÓDULO DE EVALUACIÓN (Recompensa)
        # Castigamos severamente el tiempo total de estacionariedad (tiempo perdido).
        estacionariedad_total = (self.tiempo_espera_vehiculos * 1.5) + self.tiempo_espera_peatones
        recompensa = -float(estacionariedad_total)
        
        # 4. Condiciones de cierre
        terminado = bool(self.cola_vehiculos > 100 or self.cola_peatones > 100) # Colapso del cruce
        truncado = bool(self.paso_actual >= self.max_pasos_por_episodio) # Límite de pasos alcanzado
        
        return self._obtener_estado(), recompensa, terminado, truncado, {}


# ==========================================
# BLOQUE PRINCIPAL: ENTRENAMIENTO Y PRUEBA
# ==========================================
if __name__ == "__main__":
    print("Iniciando sistema de semaforización inteligente...\n")
    
    # 1. Instanciar y verificar la estructura del entorno
    env = EntornoSemaforoInteligente()
    check_env(env)
    print("[OK] Entorno validado correctamente bajo estándares de Gymnasium.\n")
    
    # 2. Entrenar el modelo con Proximal Policy Optimization (PPO)
    print("Iniciando entrenamiento de la Red Neuronal (20,000 pasos)...")
    # 'verbose=0' oculta los logs de entrenamiento para no saturar la consola
    modelo_ia = PPO("MlpPolicy", env, verbose=0)
    modelo_ia.learn(total_timesteps=20000)
    print("[OK] Entrenamiento finalizado. El agente ha mapeado la política óptima.\n")
    
    # 3. Prueba (Inferencia) para visualizar las decisiones en tiempo real
    estado, info = env.reset()
    print("===========================================")
    print("   SIMULACIÓN DE PRUEBA EN TIEMPO REAL     ")
    print("===========================================")
    
    for i in range(15):
        # La IA evalúa el estado y toma la decisión determinista óptima
        accion, _ = modelo_ia.predict(estado, deterministic=True)
        
        # Aplicamos la acción de la IA al entorno físico simulado
        estado, recompensa, terminado, truncado, info = env.step(accion)
        
        decision_txt = "VEHÍCULOS" if accion == 0 else "PEATONES"
        incidente_txt = "SÍ" if estado[4] == 1.0 else "NO"
        
        print(f"Turno {i+1} | Acción de la IA: LUZ VERDE A {decision_txt}")
        print(f"  -> Cola Vehículos: {estado[0]:.0f} (Tiempo en espera: {estado[1]:.0f})")
        print(f"  -> Cola Peatones:  {estado[2]:.0f} (Tiempo en espera: {estado[3]:.0f})")
        print(f"  -> Incidente en la vía: {incidente_txt}")
        print(f"  -> Castigo recibido: {recompensa}\n")
        
        if terminado:
            print("SIMULACIÓN ABORTADA: El sistema ha colapsado debido al tráfico excesivo.")
            break