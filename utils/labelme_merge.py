import os
import re
import csv
import json
import argparse

from util import read_json

def run(args):
    main = read_json(args.main_json)

    hangul = re.compile('[ㄱ-힣]')
    en = re.compile('[A-z]')

    log = []
    for filename in os.listdir(args.merge_json_path):
        for ext in ['jpg', 'jpeg', 'png']:
            img_filename = os.path.splitext(filename)[0]+f".{ext}"
            if main['images'].get(img_filename):
                break
        
        data = read_json(os.path.join(args.merge_json_path, filename))
        last_label = list(main['images'][img_filename]['words'].keys())[-1]
        last_label = int(last_label)
        
        for shape in data['shapes']:
            last_label += 1
            
            transcription = shape['label']
            points = shape['points']
            language = []
            if hangul.findall(transcription):
                language.append('ko')
            if en.findall(transcription):
                language.append('en')
            if language == []:
                language = None

            update_data = dict()
            update_data[f"{str(last_label).zfill(4)}"] = {
                "transcription": transcription,
                        "points": points,
                        "orientation": "Horizontal",
                        "language": language,
                        "tags": [],
                        "confidence": None,
                        "illegibility": False
            }
            log.append([img_filename, last_label, transcription])
            main['images'][img_filename]['words'].update(update_data)

    
    path = os.path.dirname(args.main_json)
    print("merging json file")
    with open(os.path.join(path, args.save_filename), 'w') as outfile:
            json.dump(main, outfile, indent=4)
    print("done!")

    fields = ['filename', 'idx', 'transcription']
    print("make log file")
    with open(os.path.join(path, 'log.csv'), 'w') as f:
            write = csv.writer(f)   
            write.writerow(fields)
            write.writerows(log)
    print("done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--main_json", type=str, default='../dataset/upstage_data.json', help="전체 데이터를 가진 json 파일")
    parser.add_argument("--merge_json_path", type=str, default="../labelme_data", help="labelme 결과 json들을 모아둔 폴더 위치")
    parser.add_argument("--save_filename", type=str, default="update.json", help="저장할 파일 이름")
    
    args = parser.parse_args()
    
    run(args)