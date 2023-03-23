import streamlit as st

from utils import *

#
# Parameters
#

SEGMENTATION_MIN_LENGTH = 1000
LINER_NOTE_MAX_LENGTH = 1000
IMAGE_PROMPT_MAX_LENGTH = 500

st.header("音声データから、タイトル、ライナーノート、とジャケットを作成")

uploaded_file = st.file_uploader("音声データを選ぶ...", type=['mp3', 'm4a'])

segmented_summary = []

if uploaded_file is not None:
    audio_file_path = uploaded_file.name
    
    # 音声データからテキストを起こす
    transcript = transcribe(uploaded_file)

    # 文字起こしテキストがセグメント化され、各セグメントが要約されたリストになる
    # segment_and_summarize関数は、大きなテキストを一定の文字数ごとに分割し、それぞれのセグメントを要約した新しいリストを返す役割を果たす
    segmented_summary = segment_and_summarize(transcript.text, SEGMENTATION_MIN_LENGTH)

# segmented_summary内の各要約セグメントに対応するチェックボックスをStreamlitアプリに表示
# それぞれのチェックボックスがチェックされているかどうかの真偽値（TrueまたはFalse）をselected_segments_idxというリストに格納
selected_segments_idx = [ st.checkbox(segment) for segment in segmented_summary ]

# ユーザーがチェックした要約セグメントのみを含むリスト
selected_segments = [ segmented_summary[i] for i, selected in enumerate(selected_segments_idx) if selected ]

#
# Output
#

def generate_output():
    note = '\n'.join(selected_segments)

    title = create_title(note)

    liner_note = '\n'.join(segmented_summary)
    if len(liner_note) > LINER_NOTE_MAX_LENGTH:
        liner_note = summarize(liner_note)

    # 文章を整える
    liner_note = proofread_and_rewrite(liner_note)
    
    #画像生成
    image_text = note if len(note) < IMAGE_PROMPT_MAX_LENGTH else summarize(note)

    image_urls = create_image(image_text, "512x512", num_images=4)

    st.write(f'タイトル: {title}')
    st.write(f'ライナーノート:\n{liner_note}')
    st.write(f'画像のテキスト:\n{image_text}')
    for url in image_urls:
        st.image(url)
        st.write(f'画像 URL: {url}')

    json_data = {
        'transcript': transcript.text,
        'segmented_summary': segmented_summary,
        'title': title,
        'liner_note': liner_note,
        'image_urls': image_urls,
    }
    st.download_button('出力データをダウンロード', str(json_data), file_name='record_jacket.json', mime='application/json')

st.button('生成する！', on_click=generate_output, disabled=len(selected_segments) <= 0)