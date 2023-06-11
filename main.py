import os
from flask import Flask , render_template

app = Flask(__name__)

app.app_context().push()


@app.route("/")
def hello_world():
    var='this is flask'
    return(render_template('landingPage.html', Var=var))



if __name__ == '__main__':
    app.debug = True
    app.run()

