from pymongo import MongoClient
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def curr_df(date):
    url = "http://www.xe.com/currencytables/?from=USD&date={}".format(date)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table", {"id": "historicalRateTbl"})
    df = pd.read_html(str(table))
    df = df[0]
    df.columns = ['curr_code', 'curr_name', 'usd_to_x', 'x_to_usd']
    return df


def normalize_and_flatten(data):
    ndata = []
    min_val = min(data, key=lambda x: x[2])[2]
    max_val = max(data, key=lambda x: x[2])[2]
    diff = max_val - min_val
    
    if max_val == 0:
        return []

    for lat, lng, mag in data:
        ndata.append(lat)
        ndata.append(lng)
        normed = (mag - min_val) / diff
        ndata.append(normed)

    return ndata


def get_new_data():
    with open("./countries.txt", "r") as f:
        countries = f.read()
    countries = eval(countries.replace("\n", ""))

    dt = datetime.now() - timedelta(days=1)
    df = curr_df(dt.strftime("%Y-%m-%d"))

    data = []

    for ct, lat, lng, mag in countries:
        ct_df = df[df['curr_code'] == ct]
        if len(ct_df):
            mag = ct_df['x_to_usd'].tolist()[0]
        data.append((lat, lng, mag))

    ndata = normalize_and_flatten(data)

    if len(ndata) == 0:
        print("Something went wrong")
        return []

    return ndata


def main():
    client = MongoClient(os.environ["MONGODB_URI"])
    db = client.get_default_database()
    curr_data = db.data.find_one()['data']

    new_data = get_new_data()

    if len(new_data):
        curr_data[0][0] = '2016'
        curr_data[0][1] = new_data

        db.data.replace_one(db.data.find_one(), {"data": curr_data})
        print("Data has been successfully updated")

    client.close()

if __name__ == '__main__':
    main()
