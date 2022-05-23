from app import app
from eventlet import wsgi
import eventlet

if __name__ == '__main__':
    app.run()