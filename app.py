from flask import Flask, request
import pandas as pd
import json
import numpy
import datetime
import calendar

app = Flask(__name__)

@app.route('/help')
def help():
    return 'Utilize o endpoint /projection para retornar a projecao dos proximos 3 meses.'

@app.route('/projection', methods=['POST'])

def proj():
    """
    Projeta a quantia salva na conta de PayBack para os 3 meses seguintes com base no historico acumulado.
    """
    req_data = request.get_json()
    safrapay_history = json.dumps(req_data)
    interest = req_data['interest']

    data = json.loads(safrapay_history)

    dates = [i for i in data['safrapay_history'].keys()]
    values = [i for i in data['safrapay_history'].values()]

    df = pd.DataFrame({'dates': dates, 'values': values})
    df['dates'] = [pd.to_datetime(i) for i in df['dates']]

    xis = []

    df['dates'] = pd.to_datetime(df['dates']).dt.date

    for i in range(len(df)):
        xis.append(i)

    df["x"] = xis
    df["w"] = df["values"].cumsum()

    mymodel = numpy.poly1d(numpy.polyfit(df["x"], df["w"], 4))

    for i in range(df["x"].max() + 1, df["x"].max() + 4):
        month = df["dates"].max().month - 1 + 1
        year = df["dates"].max().year + month // 12
        month = month % 12 + 1
        day = min(df["dates"].max().day, calendar.monthrange(year, month)[1])
        month = datetime.date(year, month, day)
        df = df.append({"dates": month,
                        "x": i,
                        "w": mymodel(i)},
                       ignore_index=True)

    df = df.drop(columns=['x', 'values'])
    df.columns = ['dates', 'values']
    ret_json = {"safrapay_history": {}, "interest": interest}

    for key, value in enumerate(df.values):
        dates = value[0].strftime("%Y-%m-%d")
        ret_json["safrapay_history"][dates] = value[1]

    return ret_json

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False, port=5000)