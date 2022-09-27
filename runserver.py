from waitress import serve

from workcomp.wsgi import application
# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    serve(application, host = '0.0.0.0', port='8001', threads=6)