import streamlit as st
import openai
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_data
def transcribe(audio_file):
  return openai.Audio.transcribe("whisper-1", audio_file)

@st.cache_data
def segmentation(long_text: str, min_length: int):
  segmented_texts = []

  start_idx = 0

  try:
    while True:
      space_idx = long_text.index(" ", start_idx+min_length)

      curr_segment = long_text[start_idx:space_idx]

      segmented_texts.append(curr_segment)

      start_idx = space_idx + 1
  except ValueError:
    # 最後まで分割した
    segmented_texts.append(long_text[start_idx:])

    return segmented_texts

@st.cache_data
def summarize(text: str):
  prompt = "次の内容を4文以内で日本語でまとめてください"
  content = f"{prompt}:「{text}」"
  
  completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {
              "role": "user",
              "content": content
          }
      ]
  )

  return completion.choices[0].message.content

@st.cache_data
def segment_and_summarize(long_text: str, segmentation_min_length: int):
    segmented_texts = segmentation(long_text, segmentation_min_length)

    segmented_summary = []
    for segment in segmented_texts:
        segmented_summary.append(summarize(segment))

        sleep(1) # sleep to avoid rate limit 各要約の生成の間に、sleep(1)を使って1秒間待機します。これは、APIのレート制限を避けるための処理

    return segmented_summary

@st.cache_data
def create_title(text: str):
  prompt = "次の内容に合うタイトルを書いてください"
  content = f"{prompt}:「{text}」"
  
  completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {
              "role": "user",
              "content": content
          }
      ]
  )

  return completion.choices[0].message.content

# Dall-E2へのプロンプトを英語にする
@st.cache_data
def translate_to_english(text: str):
    prompt = "このテキストを英語に翻訳してください"
    content = f"{prompt}:「{text}」"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return completion.choices[0].message.content

# Dall-E2へのプロンプトをコンパクトにする
@st.cache_data
def create_compact_prompt(text: str):
    prompt = "I would like to ask Dall-E2 to draw a picture inspired by the following text. Please make it a compact prompt text in about 15 sentences."
    content = f"{prompt}:「{text}」"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return completion.choices[0].message.content

# Dall-E2へ雑誌の表紙風の絵をオーダーする
@st.cache_data
def create_image(prompt: str, size:str="1024x1024", num_images=4):
    """
    return a list of urls to images
    """
    translated_prompt = translate_to_english(prompt)
    modified_prompt = f'Illustration style for magazine covers, "{translated_prompt}"'
    image_response = openai.Image.create(
        prompt=modified_prompt,
        n=num_images,
        size=size
    )

    image_urls = [img['url'] for img in image_response['data']]
    return image_urls

# 
@st.cache_data
def proofread_and_rewrite(text: str):
    prompt = "この文章を文法的に正しく、そして自然に聞こえるように日本語で体言止めや接続詞を適宜使いながら修正してください"
    content = f"{prompt}:「{text}」"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return completion.choices[0].message.content