from flask import Flask, request, jsonify
import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta
from selenium.webdriver.support import expected_conditions as EC
import time

import requests
from bs4 import BeautifulSoup

def script(state, commodity, market):
    url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    # Attempt a GET (will only work if page loads data statically)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Try extracting dropdown values or data table (this may need refining)
    table = soup.find("table", {"id": "cphBody_GridPriceData"})

    if not table:
        return {"error": "Table not found. Likely a JavaScript-rendered site."}
    
    rows = table.find_all("tr")
    result = []
    for row in rows[1:]:  # skip header
        cols = row.find_all("td")
        result.append({
            "Commodity": commodity,
            "State": state,
            "Market": market,
            "Min Price": cols[6].text.strip(),
            "Max Price": cols[7].text.strip(),
            "Modal Price": cols[8].text.strip(),
            "Date": cols[9].text.strip()
        })
    return result


app = Flask(__name__)

@app.route('/', methods=['GET'])
def homePage():
    dataSet = {"Page": "Home Page navigate to request page", "Time Stamp": time.time()}
    return jsonify(dataSet)

@app.route('/request', methods=['GET'])
def requestPage():
    commodityQuery = request.args.get('commodity')
    stateQuery = request.args.get('state')
    marketQuery = request.args.get('market')

    if not commodityQuery or not stateQuery or not marketQuery:
        return jsonify({"error": "Missing query parameters"})

    try:
        json_data = json.dumps(script(stateQuery, commodityQuery, marketQuery), indent=4)
        return json_data
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
