from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
@app.route('/home')
def index():
    keyword = request.args.get('keyword')
    print "keyword: " + str(keyword)
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='::', debug=True, port=4000)
