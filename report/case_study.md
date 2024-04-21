# Sección 2

## Caso de estudio

Nuestro caso de estudio es la ciudad de la Habana en Cuba. Esta ciudad posee una población de alrededor de  2 137 847 habitantes y una densidad poblacional de aproximadamente 2924.2 habitantes por $km^2$.

### División por zonas

Se utilizará la división de zonas por municipios como método de análisis, fundamentándose en la necesidad de emplear áreas administrativas oficiales. Esta aproximación facilitará la asociación de cada zona con datos estadísticos disponibles, tales como población, empleo, entre otros.

### Red básica

Se empleará un grafo dirigido en el que cada nodo representa una cuadra, definida como un segmento de calle entre dos intersecciones. Durante la construcción del grafo, se determina según las direcciones de las calles y las restricciones de giro las aristas del grafo. Para cualquier par de nodos (cuadras) $x$ y $y$, existe una arista desde $x$ hasta $y$ si hay una intersección que los conecta y es posible avanzar desde $x$ hasta $y$ , ya sea doblando a la derecha, a la izquierda, siguiendo recto o realizando un giro en U.

Cada nodo también contiene información sobre la longitud de la cuadra y elementos que pueden afectar la velocidad de desplazamiento, como cruces peatonales, semáforos o señales de Pare  y Ceda el paso. Además, proporciona información sobre las rutas que tienen puntos de parada en esta cuadra y posibles puntos de interés.

### Dimensiones temporales

El análisis se desarrollará a lo largo de un período temporal de al menos un año, dividido en trimestres para facilitar la comprensión de las variaciones estacionales en la demanda de transporte. Se presupondrá que a largo plazo, la población de La Habana y sus patrones de movilidad experimentarán cambios graduales debido al crecimiento demográfico, desarrollos urbanos y modificaciones en la economía y el estilo de vida de la población.

Se tomará el año 2019 como referencia para establecer los patrones de demanda de transporte, debido a la disponibilidad de datos detallados para dicho año. Se considerará que los parámetros del sistema, como la capacidad de los vehículos de transporte público, la disponibilidad de servicios y la infraestructura vial, pueden experimentar ligeras variaciones dentro de cada período de referencia, pero se mantendrán dentro de rangos aceptables para la simulación.

Los promedios de pasajeros transportados en cada trimestre del año son los siguientes, en orden cronológico: 1 029 100, 1 069 100, 932 500 y 901 400. Se destaca que los meses de septiembre y octubre, marcados por la situación conocida en Cuba como "la conyuntura", experimentaron una severa afectación en el transporte del país debido a la situación del petróleo. Estos datos se considerarán relevantes, dado que este tipo de situaciones no son poco comunes en la realidad actual del país.

En las urbes de gran tamaño, las horas pico suelen concentrarse durante las horas de la mañana y la tarde, coincidiendo con los horarios de entrada y salida del trabajo y la escuela. Dado que no se dispone de información específica sobre las horas pico en la capital del país, se hará una suposición general considerando las horas pico como aquellas comprendidas entre las 7:00 a.m. y las 10:00 a.m., y entre las 5:00 p.m. y las 8:00 p.m.

### Estimación de la demanda

Para estimar la demanda de transporte público en La Habana, tomaremos en consideración los desplazamientos relacionados con el trabajo y la educación. Aunque no contamos con datos específicos sobre la población económicamente activa (PEA) por municipios, haremos una aproximación basada en los siguientes datos:

- La población total de La Habana con 15 años o más es de 1,827,259 personas.
- De estas, la población económicamente activa (PEA) es de 854,061 personas.
  - 836,564 de ellas están empleadas, mientras que 17,497 están desempleadas.

Esto significa que aproximadamente el 47% de la población de 15 años o más es económicamente activa, y el 98% de la PEA está empleada. Basándonos en estas estadísticas, la distribución de la PEA por municipio y su ocupación se resume en la siguiente tabla:

|Municipio | 15+y | PEA | Ocupados | Desocupados |
|----------|------|-----|----------|-------------|
| Playa | 156.937 | 73.352 | 71.848 | 1.504 |
| Plaza | 125.200 | 58.518 | 57.318 | 1.200 |
| Centro Habana | 115.228 | 53.858 | 52.754 | 1.104 |
| Habana Vieja | 68.911 | 32.209 | 31.549 | 660 |
| Regla | 37.345 | 17.455 | 17.097 | 358 |
| Habana del Este | 149.688 | 69.964 | 68.530 | 1.434 |
| Guanabacoa | 107.579 | 50.282 | 49.251 | 1.031 |
| San Miguel del Padron | 133.905 | 62.587 | 61.304 | 1.283 |
| Diez de Octubre | 172.873 | 80.801 | 79.145 | 1.656 |
| Cerro | 107.548 | 50.268 | 49.238 | 1.030 |
| Marianao | 114.859 | 53.685 | 52.584 | 1.101 |
| La Lisa | 124.020 | 57.967 | 56.779 | 1.188 |
| Boyeros | 171.666 | 80.237 | 78.592 | 1.645 |
| Arroyo Naranjo | 172.213 | 80.492 | 78.842 | 1.650 |
| Cotorro | 69.287 | 32.385 | 31.721 | 664 |
| Total | 1.827.259 | 854.060 | 836.552 | 17.508 |

Además, para comprender la distribución de la fuerza laboral, consideraremos la relación entre los municipios de residencia de los empleados y los municipios donde se encuentran las entidades empleadoras. La siguiente tabla muestra la distribución porcentual de los empleados por municipio:

| Municipio | Playa | Plaza | Centro Habana | Habana Vieja | Regla | Habana del Este | Guanabacoa | San Miguel del Padron | Diez de Octubre | Cerro | Marianao | La Lisa | Boyeros | Arroyo Naranjo | Cotorro | Total |
|-----------|-------|-------|---------------|--------------|-------|-----------------|------------|-----------------------|-----------------|-------|----------| --------|---------|----------------|---------|-------|
| Playa | 53.8 | 19.1 | 3.1 | 5.1 | 0.5 | 0.8 | 0.2 | 0.3 | 0.7 | 3.3 | 4.7 | 2.4 | 4.6 | 1.1 | 0.4 | 46.2 |
| Plaza | 20.2 | 52.6 | 4.8 | 6.6 | 0.9 | 0.6 | 0.3 | 0.6 | 0.8 | 4.2 | 2.1 | 0.8 | 4.4 | 0.9 | 0.1 | 47.4 |
| Centro Habana | 17.2 | 26.9 | 16.3 | 15.1 | 2.1 | 1.2 | 0.6 | 0.5 | 0.9 | 6 | 1.9 | 1.0 | 6.9 | 2.5 | 0.7 |  83.7 |
| Habana Vieja | 12.9 | 18.1 | 5.4 | 43.2 | 3.3 | 1.3 | 0.5 | 0.6 | 1.2 | 4.5 | 1.9 | 0.7 | 4.6 | 1.2 | 0.7 |  56.8 |
| Regla | 9.4 | 11.8 | 3.9 | 15.6 | 36.2 | 4.7 | 4 | 1.2 | 1.1 | 4.3 | 2.3 | 0.3 | 2.0 | 2.0 | 1.1 | 63.8 |
| Habana del Este | 18 | 18.9 | 4.2 | 14.9 | 6.3 | 18.2 | 3.1 | 1.4 | 1.4 | 4.9 | 1.9 | 0.6 | 3.5 | 2.4 | 0.4 | 81.8 |
| Guanabacoa | 11.8 | 11.9 | 3.5 | 11.5 | 9.8 | 10.1 | 18.6 | 2.9 | 2.0 | 6.9 | 1.9 | 0.5 | 4.6 | 2.7 | 1.5 | 81.4 |
| San Miguel del Padron | 16.1 | 15.0 | 3.5 | 10.9 | 4.4 | 3.9 | 3.3 | 14.0 | 3.9 | 8.2 | 2.5 | 0.8 | 5.6 | 4.1 | 3.9 | 86.0 |
| Diez de Octubre | 19.8 | 19.6 | 4.1 | 11.4 | 2.1 | 1.4 | 0.7 | 1.5 | 17.1 | 8.4 | 2.5 | 0.8 | 7.2 | 2.4 | 0.8 | 82.9 |
| Cerro | 19.2 | 22.7 | 4.9 | 11.0 | 1.3 | 1.0 | 1.1 | 0.5 | 2.9 | 22.8 | 2.9 | 1.3 | 6.2 | 1.6 | 0.5 | 77.2 |
| Marianao | 30.1 | 16.3 | 3.2 | 4.4 | 1.0 | 0.8 | 0.3 | 0.4 | 1.2 | 5.7 | 21.2 | 3.6 | 9.1 | 2.0 | 0.7 | 78.8 |
| La Lisa | 36.3 | 17.0 | 3.0 | 3.5 | 0.6 | 0.7 | 0.7 | 0.2 | 1.0 | 3.5 | 6.2 | 18.7 | 5.9 | 2.3 | 0.5 | 81.3 |
| Boyeros | 16.8 | 15.5 | 2.0 | 3.5 | 0.4 | 0.6 | 0.2 | 0.3 | 1.3 | 4.5 | 3.1 | 2.6 | 44.8 | 3.5 | 0.6 | 55.2 |
| Arroyo Naranjo | 16 | 15.8 | 3.4 | 7.4 | 1.7 | 1.6 | 0.6 | 1.2 | 2.4 | 7.0 | 3.9 | 1.0 | 15.4 | 21.2 | 1.4 | 78.8 |
| Cotorro | 10.5 | 13.2 | 2.2 | 5.6 | 1.5 | 4.2 | 1.5 | 1.6 | 2.5 | 6.6 | 1.2 | 1.7 | 7.4 | 5.0 | 35.2 | 64.8 |


En este análisis se considerarán únicamente los estudiantes de niveles preuniversitario, educación técnica y profesional, formación de personal pedagógico y educación superior. Se excluyen las etapas de educación infantil, primaria y secundaria, ya que la mayoría de estos estudiantes son asignados a centros educativos cercanos a sus lugares de residencia. Cabe señalar que, en el caso del nivel preuniversitario, la mayoría de los estudiantes se ubican dentro de su mismo municipio.

A continuación se presenta una tabla que muestra la cantidad de instituciones educativas por municipio para los niveles preuniversitario, técnica y profesional, formación de personal pedagógico y educación especial:

| Municipio | Preuniversitario | Técnica y profesional | Formación Personal Pedagógico | Especial |
|-----------|------------------|-----------------------|-------------------------------|----------|
| Playa | 3 | 5 | - | 2 |
| Plaza | 3 | 4 | - | 4 |
| Centro Habana | 1 | 3 | - | 4 |
| Habana Vieja | 1 | 2 | - | 2 |
| Regla | 1 | 2 | - | 2 |
| Habana del Este | 3 | 4 | - | 4 |
| Guanabacoa | 2 | 2 | - | 4 |
| San Miguel del Padron | 2 | 2 | - | 4 |
| Diez de Octubre | 4 | 4 | - | 4 |
| Cerro | 2 | 3 | 1 | 5 |
| Marianao | 2 | 3 | - | 5 |
| La Lisa | 2 | 3 | - | 4 |
| Boyeros | 2 | 6 | 2 | 5 |
| Arroyo Naranjo | 4 | 4 | - | 4 |
| Cotorro | 2 | 4 | - | 2 |

Asimismo, se muestra la matrícula de estudiantes para cada municipio y nivel educativo:

| Municipio | Preuniversitario | Técnica y profesional | Formación Personal Pedagógico | Especial |
|-----------|------------------|-----------------------|----------------------------------|----------|
| Playa | 2 191 |  31 832 | - | 352 |
| Plaza |  2 389 |  3 599 | - | 275 |
| Centro Habana |  726 | 1 330 | - | 285 |
| Habana Vieja |  831 | 139 | - | 178 |
| Regla |  563 | 697 | - | 165 |
| Habana del Este | 2 023 | 2 068 | - | 374 |
| Guanabacoa |  746 | 1 340 | - | 580 |
| San Miguel del Padron |  1 087 |  2 059 | - | 399 |
| Diez de Octubre |  2 368 |  3 036 | - | 371 |
| Cerro |  1 020 |  1 766 | 1 178 | 506 |
| Marianao |  1 166 |  1 724 | - | 470 |
| La Lisa | 1 221 |  1 341 | - | 868 |
| Boyeros | 2 444 |  5 025 | 1 842 | 737 |
| Arroyo Naranjo |  3 047 |  1 422 | - | 742 |
| Cotorro | 861 | 1 626 | - | 200 |

Para obtener una estimación del número de estudiantes de educación superior, hemos utilizado los siguientes datos:

- La población no económicamente activa en La Habana es de aproximadamente 973,198 personas.
- De esta población, aproximadamente el 16.1% son estudiantes, lo que equivale a unos 156,685 estudiantes.
- A partir de los 15 años, en niveles de educación no superior, se calcula que hay alrededor de 64,194 estudiantes, lo que deja un total estimado de 92,491 estudiantes de educación superior.

Con base en cifras nacionales disponibles, se estima que la distribución de estudiantes de educación superior es la siguiente:

- 28,672 estudiantes de medicina
- 6,474 de deportes
- 465 de arte
- 21,272 de formación pedagógica
- 12,838 de la Universidad de La Habana
- 10,174 de la CUJAE

El resto de los estudiantes de educación superior residentes en la Habana se distribuye entre universidades de diversas provincias del país.  
