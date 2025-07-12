Proyecto Final - Simulación de Peaje
Materia: Simulación
Alumno: Paloma Candelaria Corcoba
Legajo: 85250
Cursada: 4K2 - Año 2024
Tema: 85

Descripción
Proyecto para la materia Simulación en la Universidad Tecnológica Nacional – Facultad Regional Córdoba.

Se simula el funcionamiento de un peaje en el cual llegan vehículos respetando una distribución exponencial negativa con media de 1.2 minutos entre llegadas.
Los vehículos se clasifican en cinco categorías con distintas probabilidades, tiempos de atención y costos de peaje.

Categorías de vehículos, probabilidades, tiempos de atención y costos:

Categoría	Probabilidad	Tiempo de atención	Costo ($)
1	0.10	30 segundos	0
2	0.50	50 segundos ± 5 segundos	3
3	0.15	1 minuto 10 segundos ± 15 segundos	6
4	0.15	1 minuto 50 segundos ± 20 segundos	9
5	0.10	3 minutos ± 30 segundos	12

Reglas del sistema:

Si la cola de espera en una cabina supera los 4 vehículos, se habilita una nueva cabina, hasta un máximo de 4 cabinas.

Si no hay cola, se deshabilita la cabina (pero siempre debe haber al menos una habilitada).

Objetivos
Determinar a partir de la simulación:

a) Número promedio de cabinas habilitadas en función del tiempo.

b) Monto recaudado en 100 horas.

c) Porcentaje de tiempo en que se tienen distintas cantidades de cabinas habilitadas.

d) Número máximo de cabinas habilitadas durante la simulación.

Tecnologías
Backend: Python 3.x con FastAPI para la simulación y API REST.

Frontend: React para la interfaz web y visualización de resultados.

Uso
Ingresar la cantidad de iteraciones a simular.

Definir el rango de iteraciones a visualizar.

Presionar Simular para ejecutar la simulación.

Ver resultados resumen arriba y tabla de iteraciones abajo, incluyendo siempre la última iteración global.

Autor
Paloma Candelaria Corcoba
Legajo 85250
Universidad Tecnológica Nacional – Facultad Regional Córdoba
Materia Simulación, 4K2, 2024
