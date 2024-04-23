# Sección 3

## Enrutamiento

En nuestro proyecto, necesitamos un algoritmo que permita encontrar rutas válidas entre un punto de origen y posibles destinos, sin que siempre sean necesariamente las mejores. La eficacia de la ruta obtenida puede depender de varios factores. Uno de los más relevantes es la habilidad del conductor, representada por una variable entre 0 y 1, la cual influirá significativamente en el camino que el algoritmo elija.

El algoritmo base que utilizamos es el A* debido a su capacidad para priorizar nodos según el costo. Este costo se estima como la suma del costo acumulado del camino hasta el nodo actual y el valor calculado por una heurística, que representa el costo para llegar al objetivo más cercano.

El uso de esta estructura permite que el algoritmo elija el siguiente nodo a explorar con base en la estimación del costo total, minimizando exploraciones innecesarias. Al avanzar en el proceso, sacamos nodos de la cola de prioridad, examinamos sus conexiones y determinamos si deben ser parte del camino final.

La elección de A* se justifica por su equilibrio entre costo acumulado y estimación heurística, lo que facilita la búsqueda eficiente de rutas en entornos complejos. Esto es particularmente útil para nuestro proyecto, donde la flexibilidad y la eficiencia son requisitos clave.

### Cotas

Es importante evitar desviaciones excesivas del destino objetivo. Nuestro algoritmo no es genérico; está específicamente diseñado para resolver nuestro problema. Cuando se ejecuta el algoritmo con un único objetivo, indica que hay un obstáculo que bloquea una ruta, requiriendo una reevaluación de la misma. Nuestro enfoque es claro: regresar a la ruta lo antes posible, asegurándonos de no desviarnos demasiado para mantener a los pasajeros cerca de su parada, en caso de que sea necesario omitirla. Si un nodo potencial se aleja demasiado del nodo objetivo, se excluye del camino.

### Condiciones de parada

1. Si se llega a uno de los nodos objetivo, el camino se construirá regresando a través de los padres de los nodos visitados, permitiendo generar la ruta resultante.

2. Se han visitado todos los nodos conectados al nodo incial por algún camino y no se llegó al nodo objetivo a través de ninguno de ellos. Cuando el algoritmo se ejecuta con un único objetivo, esta condición de parada puede alcanzarse más rápidamente. Esto se debe a que el algoritmo descarta las conexiones que se alejan demasiado del nodo objetivo, incluso si podrían llegar a él por un camino más largo. Al hacer esto, se reduce el tiempo y los recursos utilizados para buscar rutas que probablemente no serán útiles, acelerando la detección de caminos sin salida.

3. Ejecutar el algoritmo con múltiples objetivos nos permite buscar la estación de servicio más cercana. Para determinar cuándo detener la búsqueda, calculamos el promedio de bloques necesarios para alcanzar el objetivo más lejano y lo multiplicamos por un factor preestablecido. Esto nos da un límite en el número de iteraciones que podemos ejecutar antes de parar el algoritmo si no se encuentra una solución. La razón por la que esta condición de parada es importante es porque permite al algoritmo evitar búsquedas excesivas o interminables. Establecer un límite de iteraciones asegura que el algoritmo no gaste recursos innecesariamente si el objetivo es inalcanzable o demasiado lejano, ayudando a mantener la eficiencia general del sistema.

### Correctitud del algortimo

Para ser considerado correcto, el algoritmo debe devolver un camino válido y factible.

Podemos afirmar que el camino resultante de nuestro algoritmo, en caso de existir, siempre será válido, ya que partimos del nodo de origen y seguimos aristas legales hasta llegar al objetivo. Sin embargo, la factibilidad se refiere a que el camino obtenido cumpla con las condiciones del problema. En el caso de un único objetivo, el camino es factible si se mantiene dentro de un rango aceptable. Para múltiples objetivos, el camino es factible solo si puede calcularse en un número limitado de iteraciones.

Como nuestro algoritmo se basa en A* nuestra heurística base debe ser admisible y consistente:

- **Admisibilidad:** Una heurística es admisible si nunca sobreestima el costo para llegar al objetivo. En nuestro caso, la heurística se basa en la distancia entre el nodo actual y el objetivo, utilizando una estimación optimista que supone un camino directo sin obstáculos. Esto garantiza que la heurística no sobreestima, asegurando la admisibilidad.

- **Consistencia:** Nuestra heurísta es consistente porque para cualquier nodo su ancetecesor estaría mas lejos y como la velocidad que se toma para el valor de la heurísitca siempre es la misma, entonces para un nodo mas lejano devolveria un valor mayor. Por tanto el valor de la heurística para cualquier nodo n siempre será menor que para cualesquiera de sus antecesores.

Sin embargo, debemos tener en cuenta que al introducir un margen de error en la heurística, esta deja de ser admisible y consistente, lo que puede resultar en rutas que no sean óptimas. A pesar de esto, el margen de error cumple con el objetivo de nuestro problema, que es obtener una ruta acorde con la habilidad del conductor, ya que el error depende solamente de su capacidad.
