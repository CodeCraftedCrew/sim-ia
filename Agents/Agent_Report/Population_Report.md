Para generar poblaciones de pasajeros que se monten en los ómnibus, se pueden utilizar varios enfoques.
Dado que se tienen datos reales sobre la cantidad de personas residentes en cada municipio, así como información sobre la cantidad de personas que se mueven en autobús en un año y la cantidad de personas que trabajan dentro y fuera de su municipio, se cuenta con una base sólida para generar poblaciones de pasajeros de manera más realista en la simulación.

Para definir la distribución poblacional en la simulación, se utilizarán datos de la cantidad de residentes en cada municipio, asignando pesos proporcionales a su población real. Por otro lado, los datos de movilidad en autobús permitirán determinar la proporción de pasajeros que optan por este medio de transporte frente a otros.

El modelado de comportamientos de viaje se basará en datos de movilidad laboral, adaptándose a diferentes perfiles de pasajeros, como los que viajan en horas pico por motivos laborales o de ocio. Para asignar destinos a los pasajeros, se emplearán datos sobre la movilidad entre municipios, considerando probabilidades de viaje basadas en la cantidad de desplazamientos entre ellos y teniendo en cuenta las rutas disponibles. 

Se pueden utilizar los perfiles de pasajeros generados y los datos sobre comportamientos de viaje para simular el comportamiento individual y colectivo de los pasajeros. Al seguir este enfoque, se podrán generar poblaciones de pasajeros que reflejen de manera realista los comportamientos de viaje observados en la realidad, utilizando datos reales sobre la movilidad de la población en la ciudad de La Habana.

Dado que simular a cada habitante de La Habana sería computacionalmente costoso, se utilizará una muestra representativa de la población en la simulación. Este enfoque implica seleccionar un subconjunto de individuos que reflejen de manera precisa las características demográficas y comportamientos de viaje de la población real. La muestra se seleccionará cuidadosamente utilizando datos demográficos disponibles y relevantes para la simulación. Se elegirá un tamaño de muestra lo suficientemente grande como para capturar la variabilidad en el comportamiento de los pasajeros y garantizar la representatividad de los resultados.

Una vez completada la simulación con la muestra representativa, los resultados obtenidos se extrapolarán para estimar la cantidad total de pasajeros en la población real de La Habana. Esto se realizará utilizando métodos estadísticos apropiados que tengan en cuenta la distribución de la población y los patrones de movilidad observados en la muestra.

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