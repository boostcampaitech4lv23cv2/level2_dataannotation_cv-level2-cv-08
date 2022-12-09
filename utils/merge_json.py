import os
import json
from util import read_json
import argparse 

def check_words(data:dict):
    """
    annotation 이 없는 이미지를 제거합니다.
    """
    remove_list = []
    for k,v in data['images'].items():
        if v['words'] == {}:
            print(f"Nan words: {k}")
            remove_list.append(k)

    for rm in remove_list:
        del(data['images'][rm])
    
    return data

def check_polygon(data:dict):
    """
    point 좌표 개수가 4개 넘어가는 annotation을 제거합니다.
    """
    for key,val in data['images'].items():
        remove_list = []
        for k,word in val['words'].items():
            if len(word['points']) != 4:
                remove_list.append(k)
        
        if remove_list != []:
            print(f'remove anno {k} : {len(remove_list)}')
        
        for rm in remove_list:
            del(data['images'][key]['words'][rm])
            
    return data

def json_merge(path:str, merge_list:list, save_filename:str):
    data = {'images':{}}
    for i, filename in enumerate(merge_list):
        filename = '{}.json'.format(os.path.join(path, filename))
        temp = read_json(filename)
        # 무결성 검사
        temp = check_polygon(temp)
        temp = check_words(temp)
        data['images'].update(temp['images'])
    
    # with open(os.path.join(path, save_filename), 'w') as outfile:
    #     json.dump(data, outfile, indent=4)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='../input/data/ICDAR17_Korean/ufo')
    parser.add_argument('--merge_list', type=list, default=['train', 'train_aistage'])
    parser.add_argument('--save_filename', type=str, default='merge_json.json')

    args = parser.parse_args()

    json_merge(args.data_path, args.merge_list, args.save_filename)