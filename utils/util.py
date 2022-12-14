import json
from pathlib import Path
import os
import random

def read_json(filename):
    with Path(filename).open(encoding='utf8') as handle:
        ann = json.load(handle)
    return ann

def test_train_split(filename, rate=0.2, seed=42):
    data = read_json(filename)
    temp = list(data['images'].keys())
    random.seed(seed)
    random.shuffle(temp)
    test_num = int(len(temp)*(rate))
    test = {"images": {}}
    for i in range(test_num):
        t = temp[i]
        test['images'][t] = data['images'].pop(t)
    
    return data, test

def save_json(data, path, save_filename):
    with open(os.path.join(path, save_filename), 'w') as outfile:
        json.dump(data, outfile, indent=4)