import argparse
import json
import os
from itertools import chain
from PIL import ImageOps, Image, ImageDraw
from typing import Sequence, Tuple

import plotly.express as px
from dash import Dash, html, dcc, callback_context
from dash.dependencies import Input, Output, State

# -- argparse
parser = argparse.ArgumentParser(description='Dataset Visualization')
parser.add_argument(
    '--root_dir',
    type=str,
    default='/opt/ml/input/data/ICDAR17_Korean/images/',
    help='데이터 루트 디렉토리',
)
parser.add_argument(
    '--annotation_file_name', 
    type=str, 
    default='/opt/ml/input/data/ICDAR17_Korean/ufo/train.json',
    help='어노테이션 파일 명 (.json 생략)',
)
parser.add_argument(
    '--port',
    type=int,
    default=6006,
    help='dash app을 올릴 포트',
)
parser.add_argument(
    '--image_h',
    type=int,
    default=1000,
    help='출력 이미지의 세로 크기 (종횡비 유지)',
)

args = parser.parse_args()

# --
point = Tuple[int, int]

def read_img(path: str, target_h: int = 1000) -> Image:
    """이미지 로드 후 텍스트 영역 폴리곤을 표시하여 반환한다."""
    # load image, annotation
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # 이미지 정보에 따라 이미지를 회전
    ann = anno['images'][os.path.basename(path)]
    words = ann['words']

    # resize
    h, w = img.height, img.width
    ratio = target_h/h
    target_w = int(ratio * w)
    img = img.resize((target_w, target_h))

    # draw polygon
    for key, val in words.items():
        poly = val['points']
        poly_resize = [[v * ratio for v in pt] for pt in poly]
        illegibility = val['illegibility']
        draw_polygon(img, poly_resize, illegibility)

    return img

def draw_polygon(img: Image, pts: Sequence[point], illegibility: bool):
    """이미지에 폴리곤을 그린다. illegibility의 여부에 따라 라인 색상이 다르다."""
    pts = list(chain(*pts)) + pts[0]  # flatten 후 첫번째 점을 마지막에 붙인다.
    img_draw = ImageDraw.Draw(img)
    # 폴리곤 선 너비 지정이 안되어 line으로 표시
    img_draw.line(pts, width=3, fill=(0, 255, 255) if not illegibility else (255, 0, 255))

# -- load annotations
with open(args.annotation_file_name, 'r') as f:
    anno = json.load(f)

fnames = tuple(anno['images'].keys())
num_files = len(fnames)

img_idx = -1

app = Dash(__name__)
app.layout = html.Div(
    [
        html.H3(id='img_name'),
        html.Button('prev', id='btn-prev', n_clicks=0),
        html.Button('next', id='btn-next', n_clicks=0),
        dcc.Input(
            id='idx_input',
            type='number', 
            placeholder='input image index', 
            min=0, 
            max=num_files-1,
        ),
        html.Button('go', id='btn-go', n_clicks=0),
        dcc.Graph(id='graph'),
    ]
)

@app.callback(
    Output('graph', 'figure'),
    Output('img_name', 'children'),
    Output('idx_input', 'value'),
    Input('btn-next', 'n_clicks'),
    Input('btn-prev', 'n_clicks'),
    Input('btn-go', 'n_clicks'),
    State('idx_input', 'value')
)
def update_img(btn_n, btn_p, btn_g, go_idx: int):
    """버튼 이벤트에 반응, 이미지 업데이트"""
    global img_idx
    change_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-next' in change_id:  # 다음
        img_idx = (img_idx + 1) % num_files
    elif 'btn-prev' in change_id:  # 이전
        img_idx = num_files-1 if img_idx == 0 else img_idx - 1
    elif 'btn-go' in change_id:  # 특정 인덱스로 이동
        img_idx = int(go_idx)
    else:  # 초기화
        img_idx = 0

    img_path = os.path.join(args.root_dir, fnames[img_idx])
    img, word = read_img(img_path, args.image_h)
    fig = px.imshow(img)
    fig.update_layout(height=args.image_h)
    return fig, f'[{img_idx+1}/{num_files}] ' + os.path.basename(img_path), img_idx


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=args.port)