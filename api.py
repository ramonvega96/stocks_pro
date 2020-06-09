import flask
from bs4 import BeautifulSoup
import csv
from os import mkdir
from os.path import exists, join
import urllib
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return str(process())


source = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
cache = join("tmp", "List_of_S%26P_500_companies.html")

def prepare():
    datadir = "data"
    if not exists(datadir):
        mkdir(datadir)

    tmpdir = "tmp"
    if not exists(tmpdir):
        mkdir(tmpdir)

def retrieve():
    urllib.urlretrieve(source, filename=cache)

def extract():
    source_page = open(cache).read()
    soup = BeautifulSoup(source_page, "html.parser")
    table = soup.find("table", {"class": "wikitable sortable"})

    # Fail now if we haven't found the right table
    header = table.findAll("th")
    if header[0].text.rstrip() != "Symbol" or header[1].string != "Security":
        raise Exception("Can't parse Wikipedia's table!")

    # Retrieve the values in the table
    records = []
    symbols = []
    rows = table.findAll("tr")
    for row in rows:
        fields = row.findAll("td")
        if fields:
            symbol = fields[0].text.rstrip()
            # fix as now they have links to the companies on WP
            name = fields[1].text.replace(",", "")
            sector = fields[3].text.rstrip()
            records.append([symbol, name, sector])
            symbols.append(symbol + "\n")

    # Sorting ensure easy tracking of modifications
    records.sort(key=lambda s: s[1].lower())
    writer = csv.writer(
        open("data/constituents.csv", "w"), lineterminator="\n"
    )   
    
    header = ["Symbol", "Name", "Sector"]    
    writer.writerow(header)
    
    for x in records:
        writer.writerow([unicode(s).encode("utf-8") for s in x])

    with open("data/constituents_symbols.txt", "w") as f:
        # Sorting ensure easy tracking of modifications
        symbols.sort(key=lambda s: s[0].lower())
        f.writelines(symbols)
    
    #JSON experiment
    f = open("data/constituents.csv", "r")
    reader = csv.DictReader( f, fieldnames = ( "Symbol","Name","Sector" ))
    
    records_2 = []
    for x in records:
        records_2.append([unicode(s).encode("utf-8") for s in x])
    return records_2

def process():
    prepare()
    retrieve()
    return extract()

app.run()