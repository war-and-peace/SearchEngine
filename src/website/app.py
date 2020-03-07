from flask import Flask, escape, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():

    return render_template('main.html')

@app.route('/', methods=['POST'])
def search():
    query = None
    for key, value in request.form.items():
        query = value
    if query is None or query == '':
        return redirect(url_for('main'))
    return render_template('search.html', query=query)

if __name__ == '__main__':
    app.run(debug=True)