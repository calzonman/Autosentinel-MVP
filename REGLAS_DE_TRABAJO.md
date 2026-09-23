# ATENCIÓN: ACTUALIZACIÓN DE DIRECTIVAS PRINCIPALES
A partir de este momento, adoptarás un nuevo protocolo de trabajo estricto para este proyecto. Tu objetivo ya no es la velocidad, sino la mantenibilidad, el orden y la transparencia. Debes cumplir obligatoriamente las siguientes 4 reglas antes de procesar cualquier nueva solicitud:

## REGLA 1: PAUSAS EXPLICATIVAS OBLIGATORIAS (CERO CÓDIGO SIN APROBACIÓN)
Cada vez que te pida una nueva funcionalidad o cambio, NO escribirás ni modificarás código inmediatamente. Tu flujo obligatorio será:

1. Explicar tu plan de acción en lenguaje claro.

2. Listar qué archivos vas a crear o modificar.

3. Detenerte y preguntar textualmente: "¿Estás de acuerdo con este enfoque? Responde SÍ para proceder."
Solo escribirás el código cuando yo te dé mi aprobación explícita.

## REGLA 2: ACTUALIZACIÓN CONTINUA DE LA ARQUITECTURA
Los archivo ARQUITECTURA_BACKEND.md y ARQUITECTURA_FRONTEND.md son sagrados. Si tu plan de acción (aprobado en la Regla 1) incluye la creación de un NUEVO archivo, tu primera acción en el código será añadir ese archivo y su propósito al ARQUITECTURA_BACKEND.md o ARQUITECTURA_FRONTEND.md, segun corresponda. Nunca debe existir un archivo en el proyecto que no esté documentado ahí.

## REGLA 3: DOCUMENTACIÓN EN EL CÓDIGO
Todo código que generes debe estar estrictamente comentado:

- Agrega encabezados (Docstrings / JSDoc) a cada clase, método o función principal explicando qué recibe, qué devuelve y qué hace.

- Agrega comentarios en línea (inline) antes de cualquier bloque de lógica compleja.

- El código debe ser autoexplicativo, pero los comentarios deben explicar el por qué de las decisiones técnicas.

## REGLA 4: BUENAS PRÁCTICAS Y CLEAN CODE

- Aplica principios SOLID. Evita funciones de más de 50 líneas.

- Si ves que un archivo está creciendo demasiado, propón modularizarlo antes de seguir agregando código.

- Utiliza nombres de variables y funciones descriptivos (nada de data1, temp, etc.).

- Maneja los errores explícitamente (Try/Catch, validaciones) en lugar de asumir que todo funcionará.