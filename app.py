"""Launcher minimal: importa la app Flask desde controllers.web y la ejecuta."""

from controllers.web import app


if __name__ == '__main__':
    app.run(debug=True, port=5000)
