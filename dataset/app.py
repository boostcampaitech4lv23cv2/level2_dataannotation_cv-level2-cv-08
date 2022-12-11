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
        st.session_state["anno_index"] = 0
    else:
        anno.set_annotation_files(st.session_state["annotation_files"])
    
    def refresh():
        st.session_state["annotation_files"] = anno.get_annotation_file()
        st.session_state['files'] = anno.get_image_files()
        st.session_state["image_index"] = 0
        st.session_state["anno_index"] = 0
        
    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
            st.session_state["anno_index"] = 0
        else:
            st.warning('This is the last image.')

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
            st.session_state["anno_index"] = 0
        else:
            st.warning('This is the first image.')

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index
        st.session_state['anno_index'] = 0
    
    def go_to_idx():
        file_index = st.session_state["input_idx"]
        st.session_state["image_index"] = file_index
        st.session_state['anno_index'] = 0

        
    def next_anno():
        anno_index = st.session_state["anno_index"]
        if anno_index < len(st.session_state["annotation"]['words']) -1:
            st.session_state["anno_index"] += 1
        else:
            st.warning('This is the last annotation')
            
    def previous_anno():
        anno_index = st.session_state["anno_index"]
        if anno_index > 0:
            st.session_state["anno_index"] -= 1
        else:
            st.warning('This is the first annotation.')
            
    def update_anno():
        st.session_state["annotation_files"]['images'][img_file_name]['words'][anno_keys[st.session_state['anno_index']]].update({'transcription' : st.session_state['update']})
        save_anno()
        
    def save_anno():
        with open(os.path.join(args.root_dir, args.annotation_file_name), 'w') as f:
            json.dump(st.session_state["annotation_files"], f, indent=4)
    
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
    
    st.sidebar.number_input(
        'Search idx',
        min_value=0,
        max_value=n_files,
        format='%d',
        on_change=go_to_idx,
        key="input_idx"
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image)
    with col2:
        st.button(label="Next image", on_click=next_image)
    st.sidebar.button(label="Refresh", on_click=refresh)

    img_file_name = st.session_state['files'][st.session_state["image_index"]]
    img_path = os.path.join(args.root_dir, img_file_name)
    st.session_state["annotation"] = st.session_state["annotation_files"]['images'][img_file_name]
    im = ImageManager(img_path, st.session_state["annotation"])
    st.image(im.read_img(img_path))
    
    
    col3, col4 = st.columns(2)
    with col3:
        st.button(label="Previous annotation", on_click=previous_anno)
    with col4:
        st.button(label="Next annotation", on_click=next_anno)
        
    col5, col6 = st.columns(2)
    anno_keys = list(st.session_state["annotation"]['words'].keys())
    anno_words = st.session_state["annotation"]['words']
    with col5:
        st.image(im.crop_img(img_path, anno_words[anno_keys[st.session_state['anno_index']]]['points'] ))
    with col6:
        st.text_input(label=anno_words[anno_keys[st.session_state['anno_index']]]['transcription'], on_change=update_anno, key="update")
    
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
        default='/opt/ml/dataset/upstage_data.json',
        help='어노테이션 파일 명 (.json 생략)',
    )
    args = parser.parse_args()
    
    run(args)