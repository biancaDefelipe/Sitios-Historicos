"""
Inicializa y ejecuta la aplicación Flask cuando el módulo se ejecuta directamente.
"""

from src.web import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
