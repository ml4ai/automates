from flask import Flask, render_template, request, redirect
import subprocess as sp

app = Flask(__name__)

@app.route('/')
def show_index():
    """ Show the index page. """
    return render_template('index.html',
                           text = "Input text to be processed here")


@app.route("/processCode")
def process_text():
    """ Process the input code. """
    code = request.args.get('codeToProcess', '')
    print(code)
    return redirect('/')

if __name__=="__main__":
    app.run()
