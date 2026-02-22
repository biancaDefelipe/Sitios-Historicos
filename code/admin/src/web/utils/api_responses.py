"""
Este módulo quedó obsoleto: las respuestas de error se inyectaron inline
en los controladores. Se mantiene este archivo como marcador para evitar
roturas si algún import externo aún lo referenciara temporalmente.

No exporta la función `error_response` para que los controladores usen
`jsonify(...)` directamente.
"""
