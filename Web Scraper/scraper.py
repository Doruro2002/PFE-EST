from numpy import var
import pandas as pd
import scrapy
import yaml
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from yaml.loader import SafeLoader
import requests
from tkinter import *
ws = Tk()
ws.title("PythonGuides")
ws.geometry('400x300')
ws['bg'] = '#ffbf00'

def printValue():
    MONGO_DB = db.get()
    MONGO_USER = user.get()
    MONGO_PASS = password.get()
    #print(MONGO_DB)
    #print(MONGO_USER)
    #print(MONGO_PASS)
    # Label(ws, text=f'{MONGO_PASS}, Registered!', pady=20, bg='#ffbf00').pack()
def start():
    
    with open('childs.yml', 'w') as file:
        response = requests.get('https://cov-lineages.org/data/lineages.yml')
        file.write(response.text)
    def get_auth(reqs):
        for req in reqs:
            if 'authorization' in dict(req.headers):
                return dict(req.headers)['authorization']
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://outbreak.info/situation-reports?pango=A.4')
    auth = get_auth(driver.requests)
    driver.close()
    # MONGO_DB = "db_cov"
    # MONGO_USER = 'python'
    # MONGO_PASS = 'python123'
    class VariantsSpider(scrapy.Spider):
        name = 'extractor'
        def __init__(self, auth):
            self.headers = {
                'authorization': auth
            }
            self.df = pd.read_html('https://cov-lineages.org/lineage_list.html')[0]
            self.df['children'] = pd.Series()
            self.df['mutations'] = pd.Series()
            with open('childs.yml', 'r') as f:
                self.config = list(yaml.load_all(f, Loader=SafeLoader))[0]
                self.mutation_template = 'https://api.outbreak.info/genomics/lineage-mutations?pangolin_lineage={' \
                                        '}&frequency=0.75 '
        def start_requests(self):
            for index, row in self.df.iterrows():
                yield Request(
                    self.mutation_template.format(row['Lineage']),
                    headers=self.headers,
                    meta={
                        'Lineage': row['Lineage'],
                        'index': index
                    },
                    callback=self.parse_mutations
                )
        def get_children(self, name):
            return [item['name'] for item in self.config if item.get('parent') == name]
        def parse_mutations(self, response):
            try:
                mutations = [mut['mutation'] for mut in response.json()['results'][response.meta['Lineage']]]
            except KeyError:
                mutations = []
            self.df.loc[self.df['Lineage'] == response.meta['Lineage'], 'mutations'] = '\n'.join(mutations)
            self.df.loc[response.meta['index'], 'children'] = '\n'.join(
                self.get_children(self.df.loc[response.meta['index']]['Lineage']))
            item_dict = self.df.loc[response.meta['index']].to_dict()
            yield item_dict
        def close(self, reason):
            self.df.to_excel('output.xlsx')
    process = CrawlerProcess({
        'MONGO_USER': MONGO_USER,
        'MONGO_PASS': MONGO_PASS,
        'MONGO_DB': MONGO_DB,
        'ITEM_PIPELINES': {
            'pipeline.VariantsPipeline': 300
        }
    })
    process.crawl(VariantsSpider, auth)
    process.start()

db = Entry(ws)
db.pack(pady=30)
user = Entry(ws)
user.pack(pady=30)
password = Entry(ws)
password.pack(pady=30)
Button(
    ws,
    text="Register Player", 
    padx=10,
    pady=5,
    command=printValue
    ).pack()
Button(
    ws,
    text="GO", 
    padx=10, 
    pady=5,
    command=start
    ).pack()
ws.mainloop()
