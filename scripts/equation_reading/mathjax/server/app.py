from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    print('Calling index()')
    return render_template('index.html')
    '''
    try:
        print('Calling index()')
        ctx = render_template('index.html')
        print(ctx)
        return ctx
    except Exception as e:
        print(f'ERROR index(): {str(e)}')
        return str(e)
    '''


# then end '/' is necessary...
@app.route('/interactive/')
def interactive():
    try:
        print('Calling interactive()')
        ctx = render_template('interactive.html')
        print('    SUCCESS render_template() - ctx:')
        print(ctx)
        return ctx
    except Exception as e:
        print(f'ERROR interactive(): {str(e)}')
        return str(e)


@app.route('/background_process')
def background_process():
    try:
        print('Calling background_process()')
        lang = request.args.get('proglang', 0, type=str)
        if lang.lower() == 'python':
            return jsonify(result='You are wise.')
        else:
            return jsonify(result='Try again.')
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
