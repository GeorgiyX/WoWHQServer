from Core import app

if __name__=="__main__":
    app.run(debug=app.config.get('DEBUG'))