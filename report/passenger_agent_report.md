## Agente pasajero.

Los pasajeros serán modelados como agentes individuales que representan a personas en una muestra representativa de la población. Estos agentes se moverán dinámicamente por la ciudad, interactuando con el entorno y otros agentes, como los conductores de autobuses.

Características del Agente Pasajero:

- Perfil Demográfico: Cada agente pasajero tendrá un perfil demográfico que reflejará características relevantes para la simulació generadas en base a los datos demográficos disponibles.

- Objetivos de Viaje: Cada agente pasajero tendrá objetivos de viaje específicos, como llegar a su lugar de trabajo, hogar, o destino de ocio. Estos objetivos guiarán las decisiones de ruta y comportamiento del agente.

Reglas del Agente Pasajero:

Decisión de Abordaje:

- El agente evalúa las condiciones actuales, como la distancia a la parada de autobús más cercana, la disponibilidad de autobuses en esa parada y su destino.
- Si el tiempo de espera es aceptable y hay espacio disponible en el autobús, el agente decide abordar.
- Si el tiempo de espera es largo o el autobús está lleno, el agente puede optar por esperar en la parada o buscar alternativas de transporte.

Selección de Ruta:

- Una vez a bordo, el agente determina la ruta óptima para llegar a su destino. Esto puede implicar realizar transbordos si es necesario.
- El agente considera factores como la duración del viaje, la cantidad de transbordos, la congestión del tráfico, etc. al elegir la ruta.

Interacción con el Entorno:

- Durante el viaje, el agente monitorea activamente el entorno, detectando cambios en la ruta, condiciones del tráfico, paradas adicionales, etc.
- El agente ajusta su comportamiento en respuesta a estos cambios, como decidir bajarse del autobús en una parada no planificada si es más conveniente para llegar a su destino.

Propiedades del Agente Pasajero:

- Reactividad: El agente muestra reactividad al percibir su entorno y responder de manera oportuna a los cambios que ocurren durante su viaje en autobús. Por ejemplo, decide abordar el autobús en función del tiempo de espera y la disponibilidad de espacio, así como adapta su comportamiento en respuesta a cambios en la ruta o condiciones del tráfico durante el viaje.

- Proactividad: El agente pasajero demuestra proactividad al mostrar un comportamiento dirigido a objetivos (principalmente llegar a un destino) y tomar la iniciativa para lograrlos durante su viaje en autobús. Por ejemplo, planifica su ruta de manera anticipada considerando diversos factores como la duración del viaje y la congestión del tráfico.