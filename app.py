from PIL import Image,ImageDraw,ImageFont
import pytesseract
from pytesseract import pytesseract
import enum
import os
import streamlit as st
from googletrans import Translator
import pandas as pd
import json

st.set_page_config(layout='wide')
IMAGE_FOLDER = "images"
OUTPUT_FOLDER="images/output_boxes"

def main():
    if "translated_text_list_session" not in st.session_state:
        st.session_state.translated_text_list_session=""
    translated_list_text=""
    if "text_coordinates" not in st.session_state:
        st.session_state.text_coordinates=""
    

    st.title('Image to Text Extraction')
    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            
            with st.container(border=True):
                st.subheader("Step 1: Upload image and Read")
                uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
                if uploaded_image is not None:
                    image_path = save_image(uploaded_image)
                    
                    st.image(image_path, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
                    # st.image(image_path, use_column_width=True)
                    if st.button("Extract Words"):
                        text = extract_text(image_path,lang='eng')
                        st.session_state.text_coordinates=extract_text_with_coordinates(image_path,'eng')
                        st.write(st.session_state.text_coordinates)
                        df_aaa = pd.DataFrame(st.session_state.text_coordinates)
                        filtered_df = df_aaa[df_aaa['text'].str.len() > 0]
                        st.session_state.text_coordinates = filtered_df.to_json(orient='records', indent=4)
                        st.session_state.text_coordinates=json.loads(st.session_state.text_coordinates)
                        # st.write(filtered_df)
                        text = lines_to_list(text)
                        st.session_state.extracted_text = text

        with col2:
            with st.container(border=True):
                st.subheader("Step 2: Read List and Translate")
                if 'extracted_text' in st.session_state:
                    st.text_area("Extracted Text", st.session_state.extracted_text, height=100)
                else:
                    st.text_area("Extracted Text", "", height=100,key = "sr.text_")
                with st.expander("Extract to get Text Coordinats"):
                    word_list=[]
                    confidence_list=[]
                    coordinates_list=[]
                    for item in st.session_state.text_coordinates:
                        word_list.append(item['text'])
                        confidence_list.append(item['confidence'])
                        coordinates_list.append(item['coordinates'])
                        # st.write(f"Text: {item['text']} | Confidence: {item['confidence']} | Coordinates: {item['coordinates']}")
                
                    coordinates_tuple=(word_list,confidence_list,coordinates_list)
                    # st.write(coordinates_tuple)
                    df = pd.DataFrame({
                                'Word': coordinates_tuple[0],
                                'Cofidence': coordinates_tuple[1],
                                'Co-ordinates': coordinates_tuple[2]
                            })
                    
                    st.data_editor(df,use_container_width=True)
                
                sel_lan,translate_but_col=st.columns([3,1])
                with sel_lan:
                    select_language=st.radio("Select a language to translate",options=["Marathi","Hindi"],horizontal=True)
                with translate_but_col:
                    translated_text=st.button("Translate",type="primary",use_container_width=True)
                if select_language=="Marathi":
                    lang_selected="mr"
                elif select_language=="Hindi":
                    lang_selected="hi"
            with st.container(border=True):
                if translated_text:
                    translated_list_text=translate_list(st.session_state.extracted_text,lang_selected)
                    st.session_state.translated_text_list_session=translated_list_text
                    
                st.subheader("Step 3: Translated Text")
                st.text_area("Extracted Text", st.session_state.translated_text_list_session, height=100,key = "asd")
            mask_image_but=st.button("Mask Image",type="primary",use_container_width=True)
            with st.container(border=True):
                st.subheader("Step 4: Masked Image")
                output_path=f'{OUTPUT_FOLDER}/{uploaded_image.name}'
                if mask_image_but:
                    image = Image.open(image_path)
                    draw = ImageDraw.Draw(image)
                    font_path="Lohit-Devanagari.ttf"
                    # Use the default PIL font
                    font = ImageFont.truetype(font_path,50)

                    # draw_rectangles(image_path,st.session_state.text_coordinates,output_path)
                    st.image(output_path, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
                    # Replace each sentence with the translated text
                    for i, original_sentence in enumerate(st.session_state.extracted_text):
                        print(st.session_state.translated_text_list_session[i]+"---")
                        bounding_box = get_bounding_box(original_sentence, st.session_state.text_coordinates)
                        if bounding_box:
                            draw.rectangle(bounding_box, fill="white")  # Fill the bounding box with white color to cover the old text
                            draw.text((bounding_box[0], bounding_box[1]), st.session_state.translated_text_list_session[i], font=font, fill="black")  # Draw the new text

                    # Save the edited image
                    output_path = f"images/output_boxes/{uploaded_image.name}"
                    image.save(output_path)
                    


def draw_rectangles(image_path: str, text_data: list, output_path: str):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    for item in text_data:
        x1, y1, x2, y2 = item['coordinates']
        draw.rectangle([x1, y1, x2, y2], outline="white",fill="white", width=2)

    img.save(output_path)

def extract_text_with_coordinates(image: str, lang: str) -> list:
    img = Image.open(image)
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

    text_data = []
    num_boxes = len(data['level'])

    for i in range(num_boxes):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        text_info = {
            'text': data['text'][i],
            'confidence': data['conf'][i],
            'coordinates': (x, y, x + w, y + h)
        }
        text_data.append(text_info)
    
    return text_data

def translate_list(text_list, dest_language):
    # Initialize the translator
    translator = Translator()

    # Translate each text in the list
    translated_list = [translator.translate(text, dest=dest_language).text for text in text_list]
    return translated_list

def extract_text(image: str, lang:str)-> str:
    img=Image.open(image)
    get_text=pytesseract.image_to_string(img,lang='eng')
    return get_text

def lines_to_list(text):

    # Split the text by blank lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    return lines

def save_image(uploaded_file):
    # Convert the uploaded file to a byte stream
    image_bytes = uploaded_file.read()
    
    # Create a file path to save the image
    file_path = f"images/{uploaded_file.name}"
    
    # Save the image
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    st.success(f"Image saved as {file_path}")
    return file_path

def get_bounding_box(sentence, word_coordinates):
    words = sentence.split()
    first_word = words[0]
    last_word = words[-1]

    first_coord = None
    last_coord = None

    for coord in word_coordinates:
        if coord["text"] == first_word and not first_coord:
            first_coord = coord["coordinates"]
        if coord["text"] == last_word:
            last_coord = coord["coordinates"]
    
    if first_coord and last_coord:
        min_x = first_coord[0]
        min_y = first_coord[1]
        max_x = last_coord[2]
        max_y = last_coord[3]
        return (min_x, min_y, max_x, max_y)
    else:
        return None



if __name__=="__main__":
    main()
    # result = extract_text('images/hello.png',lang='eng')
    # print(result)
