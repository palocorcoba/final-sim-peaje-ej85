# Final - Simulación de Peaje

**Materia:** Simulación  
**Alumno:** Paloma Candelaria Corcoba  
**Legajo:** 85250  
**Cursada:** 4K2 - Año 2024  
**Tema:** 85

---

## Descripción

Proyecto para la materia Simulación en la Universidad Tecnológica Nacional – Facultad Regional Córdoba.

Se simula el funcionamiento de un peaje en el cual llegan vehículos respetando una distribución **exponencial negativa** con media **parametrizable** (por defecto 1.2 minutos entre llegadas).  
Los vehículos se clasifican en cinco categorías con distintas probabilidades, tiempos de atención y costos de peaje.

Las funciones de distribución de tiempo de atención para cada tipo de vehículo son **parametrizables**, permitiendo cambiar los valores *a* y *b* de la distribución uniforme según corresponda.

Además, la función acumulada de probabilidades está validada para garantizar que la suma total sea igual a 1.

---

## Categorías de vehículos

| Categoría | Probabilidad | Tiempo de atención | Costo ($) |
|-----------|---------------|---------------------|-----------|
| 1         | 0.10          | 30 segundos         | 0         |
| 2         | 0.50          | 50 segundos ± 5 s   | 3         |
| 3         | 0.15          | 1 min 10 s ± 15 s   | 6         |
| 4         | 0.15          | 1 min 50 s ± 20 s   | 9         |
| 5         | 0.10          | 3 min ± 30 s        | 12        |

---

## Reglas del sistema

- Si la cola de espera en una cabina supera los 4 vehículos, se habilita una nueva cabina, hasta un máximo de 4 cabinas.
- Si no hay cola, se deshabilita la cabina (pero siempre debe haber al menos una habilitada).

---

## Objetivos

Determinar a partir de la simulación:

a) Número promedio de cabinas habilitadas en función del tiempo.  
b) Monto recaudado en 100 horas.  
c) Porcentaje de tiempo en que se tienen distintas cantidades de cabinas habilitadas.  
d) Número máximo de cabinas habilitadas durante la simulación.

---

## Tecnologías

- **Backend:** Python 3.x con FastAPI para la simulación y API REST.
- **Frontend:** React para la interfaz web y visualización de resultados.

---

## Uso

1. Ingresar la cantidad de iteraciones a simular.  
2. Definir el rango de iteraciones a visualizar.  
3. Presionar **Simular** para ejecutar la simulación.  
4. Ver resultados resumen arriba y tabla de iteraciones abajo, incluyendo siempre la última iteración global.

---

## Autor

Paloma Candelaria Corcoba  
Legajo 85250  
Universidad Tecnológica Nacional – Facultad Regional Córdoba  
Materia Simulación, 4K2, 2024
