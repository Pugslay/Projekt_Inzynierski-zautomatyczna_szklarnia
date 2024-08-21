from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'P0L1T36HN1K4'

@app.route('/centrum', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        temp = request.form.get('slider_temp')
        humandity = request.form.get('slider_humandity')
        light = True if request.form.get('light') == '1' else False

        session['temp'] = temp
        session['humandity'] = humandity
        session['light'] = light

        print(temp, humandity, light)

        return redirect(url_for('result'))

    return render_template('sliders.html')


@app.route('/results', methods=['GET','POST'])
def result():
    temp = session.get('temp')
    humandity = session.get('humandity')

    return render_template('results.html', slider_temp=temp, slider_humandity=humandity)
@app.route('/')
def str_start():
    return render_template('menu.html')


def run_flask():
    app.run()