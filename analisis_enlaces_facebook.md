# Análisis Detallado de Enlaces de Facebook Marketplace

Este documento explica en detalle la estructura general de las URLs proporcionadas y los parámetros de búsqueda específicos utilizados en cada uno de los enlaces de Facebook Marketplace.

## Desglose Estructural de la URL

Antes de analizar los filtros específicos, es importante entender la anatomía de la URL base que comparten todos estos enlaces. Tomemos como ejemplo el inicio de los enlaces:
`https://www.facebook.com/marketplace/106039289436408/search/`

*   **`https://` (Protocolo):** Indica que la conexión utiliza un protocolo seguro y encriptado (HyperText Transfer Protocol Secure) para transmitir los datos.
*   **`www.facebook.com` (Dominio principal):** Es el servidor o la dirección principal del sitio web al que se está accediendo.
*   **`/marketplace/` (Directorio/Ruta):** Apunta a la sección o aplicación específica dentro de la plataforma de Facebook dedicada a la compra y venta.
*   **`/106039289436408/` (Variable de Ruta / ID de Ubicación):** En lugar de un nombre, Facebook usa este identificador numérico único para definir la ciudad o área metropolitana central de la búsqueda.
*   **`/search/` (Endpoint/Acción):** Le indica al servidor que el usuario quiere ejecutar una acción de búsqueda dentro del marketplace y en la ubicación definida.
*   **`?` (Iniciador de Query String):** Este símbolo es la frontera entre la ruta del recurso y las instrucciones dinámicas. Todo lo que va después del signo de interrogación son variables que filtran o modifican la búsqueda.
*   **`&` (Concatenador):** El signo de "et" (ampersand) funciona como un conector ("y"). Permite encadenar múltiples condiciones o filtros en una misma solicitud (por ejemplo, `filtro1=A&filtro2=B`).

---

## Parámetros Comunes en la Búsqueda

Dentro del *Query String* (después del `?`), todos los enlaces comparten estas variables que definen el contexto de lo que se busca:

*   **`query=Veh%C3%ADculos`**: Define el término de búsqueda de texto. `%C3%AD` es la codificación URL (URL encoding) del carácter "í" con tilde, necesaria para que los navegadores interpreten correctamente los caracteres especiales.
*   **`category_id=546583916084032`**: Es el identificador numérico interno de Facebook para la categoría "Vehículos". Obliga al sistema a buscar solo en esa sección, ignorando otros artículos que puedan tener la palabra "vehículos" en su descripción.
*   **`referral_ui_component=category_menu_item`**: Un parámetro de analítica y seguimiento de Facebook. Le indica a sus servidores que el usuario llegó a esta búsqueda haciendo clic en un elemento del menú de categorías.
*   **`exact=false`**: (Presente en los enlaces 2, 3 y 4) Le indica al motor de búsqueda de Facebook que busque de forma flexible (coincidencia amplia), sin requerir que el texto de la publicación sea exactamente y únicamente la palabra buscada.

---

## Enlace 1: Búsqueda Base de Categoría

**URL:** `https://www.facebook.com/marketplace/106039289436408/search/?category_id=546583916084032&query=Veh%C3%ADculos&referral_ui_component=category_menu_item`

### ¿Qué hace?
Realiza una búsqueda estándar y general de vehículos dentro de la ubicación especificada.

### ¿Cómo lo hace?
Utiliza únicamente los parámetros comunes. Al carecer de variables de filtrado de tiempo (`daysSinceListed`) o de ordenación (`sortBy`), el sistema aplica su algoritmo por defecto. Esto significa que mostrará los resultados clasificados bajo el criterio de "Recomendados", basado en la relevancia algorítmica y el historial que Facebook considere mejor para el usuario.

---

## Enlace 2: Filtro por Fecha de Publicación (Últimas 24 horas)

**URL:** `https://www.facebook.com/marketplace/106039289436408/search?daysSinceListed=1&query=Veh%C3%ADculos&category_id=546583916084032&exact=false&referral_ui_component=category_menu_item`

### ¿Qué hace?
Busca vehículos, pero restringe drásticamente los resultados para mostrar **únicamente aquellos que fueron publicados durante el último día (últimas 24 horas)**.

### ¿Cómo lo hace?
Añade el parámetro clave de filtrado **`daysSinceListed=1`** (Días desde su publicación = 1). Este comando le indica a la base de datos de Facebook que excluya cualquier publicación cuya antigüedad sea superior a 24 horas, independientemente de su relevancia algorítmica. El orden visual de los resultados sigue siendo el de "Recomendados" por defecto.

---

## Enlace 3: Ordenado por Cercanía

**URL:** `https://www.facebook.com/marketplace/106039289436408/search?sortBy=distance_ascend&query=Veh%C3%ADculos&category_id=546583916084032&exact=false&referral_ui_component=category_menu_item`

### ¿Qué hace?
Busca vehículos y reordena la lista de resultados para priorizar la ubicación geográfica, asegurando que **los vendedores y vehículos físicamente más cercanos al centro de la búsqueda aparezcan de primeros**.

### ¿Cómo lo hace?
Introduce el parámetro de ordenación **`sortBy=distance_ascend`** (Ordenar por = distancia en modo ascendente). "Ascendente" indica una progresión de menor a mayor. El sistema calcula la distancia lineal o de ruta desde el ID de ubicación (`106039289436408`) y lista los resultados partiendo del kilómetro 0 hacia afuera. Este enlace no tiene límite de tiempo, por lo que mostrará vehículos cercanos sin importar hace cuánto se publicaron.

---

## Enlace 4: Búsqueda Combinada (Recientes + Orden Cronológico Estricto)

**URL:** `https://www.facebook.com/marketplace/106039289436408/search/?daysSinceListed=1&sortBy=creation_time_descend&query=Veh%C3%ADculos&category_id=546583916084032&exact=false&referral_ui_component=category_menu_item`

### ¿Qué hace?
Es una búsqueda altamente precisa y combinada. Su función es aislar **solo los vehículos publicados en las últimas 24 horas** y, dentro de ese grupo reciente, ordenarlos cronológicamente para que **las publicaciones absolutamente más nuevas (hechas hace minutos o segundos) aparezcan en la parte superior**.

### ¿Cómo lo hace?
Combina simultáneamente un filtro de exclusión (tiempo) y un parámetro de ordenación estricto:
1.  **Filtro:** `daysSinceListed=1` actúa como un embudo, descartando todo lo que tenga más de 24 horas de publicado.
2.  **Ordenación:** **`sortBy=creation_time_descend`** (Ordenar por = fecha de creación en modo descendente). Toma los resultados que pasaron el filtro anterior y los organiza de mayor a menor según su marca de tiempo (timestamp) de creación. En términos de tiempo, un valor "mayor" es más reciente (más cercano a la hora actual), garantizando que el usuario vea primero lo último que ingresó al sistema.
