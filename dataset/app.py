import argparse
import json
import os

import streamlit as st

from manage.anno import ReadManager, ImageManager
# streamlit run app.py --server.port=30001 --server.fileWatcherType none

def run(args):
    
    anno = ReadManager(args.annotation_file_name, args.root_dir)
    if "annotation_files" not in st.session_state:
        st.session_state["annotation_files"] = anno.get_annotation_file()
        st.session_state['files'] = anno.get_image_files()
        st.session_state["image_index"] = 0
    else:
        anno.set_annotation_files(st.session_state["annotation_files"])
    
    def refresh():
        st.session_state["annotation_files"] = anno.get_annotation_file()
        st.session_state['files'] = anno.get_image_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning('This is the last image.')

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning('This is the first image.')

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index
    
    def go_to_idx(input_idx):
        st.session_state["image_index"] = input_idx
    
    n_files = len(st.session_state["files"])
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Now Image Idx:", st.session_state["image_index"])
    st.sidebar.write("Remaining files:", n_files - st.session_state["image_index"])
    
    st.sidebar.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="file",
    )
    
    number = st.sidebar.number_input(
        'Search idx',
        min_value=0,
        max_value=n_files,
        format='%d',
    )
    st.sidebar.button("", on_click=go_to_idx(number))
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image)
    with col2:
        st.button(label="Next image", on_click=next_image)
    st.sidebar.button(label="Refresh", on_click=refresh)

    img_file_name = st.session_state['files'][st.session_state["image_index"]]
    img_path = os.path.join(args.root_dir, img_file_name)
    img_anno = st.session_state["annotation_files"]['images'][img_file_name]
    im = ImageManager(img_path, img_anno)
    st.image(im.read_img(img_path))
    
    for k, i in img_anno['words'].items():
        col3, col4 = st.columns(2)
        with col3:
            st.image(im.crop_img(img_path,i['points']))
        with col4:
            st.text_input(i['transcription'])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dataset Visualization')
    parser.add_argument(
        '--root_dir',
        type=str,
        default='/opt/ml/input/data/ICDAR17_Korean/images',
        help='데이터 루트 디렉토리',
    )
    parser.add_argument(
        '--annotation_file_name', 
        type=str, 
        default='/opt/ml/input/data/ICDAR17_Korean/ufo/train.json',
        help='어노테이션 파일 명 (.json 생략)',
    )
    args = parser.parse_args()
    
    run(args)