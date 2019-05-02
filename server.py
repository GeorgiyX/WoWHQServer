from Core import app
import sys

if __name__=="__main__":
    if sys.argv[1] == 'l':
        app.run(debug=app.config.get('DEBUG'), port = 8000)
    else:
        app.run(debug=app.config.get('DEBUG'))