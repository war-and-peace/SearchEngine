import os
from bs4 import BeautifulSoup
import codecs
import json
import requests
import time

class Crawler:
    def __init__(self, config):
        with open(config) as f:
            self.config = json.load(f)
        # self.config = config
        self.ids = set()

    def get_contents(self, ids, file_path):
        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            doc = f.read()
        soup = BeautifulSoup(doc)
        reuters = soup.find_all('reuters')
        collection = {}
        for x in reuters:
            id = x['newid']
            if id in ids:
                ids.remove(id)
                continue
            else:
                self.ids.add(id)
            title = str(x.find('title'))[7:-8]
            body = str(x.find('body'))[6:-9]
            collection[id] = [title, body]
        return collection

    def send_new_files(self, contents, deletions):
        res = requests.post(f'http://{self.config["server_url"]}', json={'additions': contents, 'deletions': deletions})
        print(res.json())

    def run(self):
        base_dir = self.config['dataset']
        files = [f for f in os.listdir(base_dir)
                    if os.path.isfile(os.path.join(base_dir, f))]
        new_ids = self.ids.copy()
        for file in files:
            file_path = os.path.join(base_dir, file)
            contents = self.get_contents(new_ids, file_path)
            self.send_new_files(contents, [])
            time.sleep(100)
        diff = self.ids.difference(new_ids)
        deletions = list(diff)
        print(f'deletions: {deletions}')
        self.send_new_files({}, deletions)

        # self.send_remove_ids(self, new_ids)

if __name__ == '__main__':
    crawler = Crawler('/home/abdurasul/Repos/SearchEngine/config.json')
    while True:
        crawler.run()
        time.sleep(3600)