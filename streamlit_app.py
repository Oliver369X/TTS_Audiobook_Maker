import io
import streamlit as st
from PIL import Image
from gtts import gTTS
import fitz
import docx
import os

# Definir la lista de idiomas disponibles
available_languages = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    # Agregar más idiomas si es necesario
}

st.set_page_config(page_title='TTS Audiobook Maker', page_icon='https://i.postimg.cc/mk0CgTnh/logo-transparent-200.png',
                   layout='wide', initial_sidebar_state='expanded')

st.title('Audio Book Maker')
st.header(
    "[![GitHub release ("
    "latest by date)]()]("
    "https://github.com/Oliver369X/TTS_Audiobook_Maker)")
st.header('Preview Uploaded Document')
st.warning('Before converting, be sure to download any converted content or you will need to reconvert.')

def convert_document(doc_content, lang):
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=doc_content, lang=lang, slow=False, lang_check=False, tld='co.in')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)  # Reset the buffer to the beginning
        return mp3_fp
    except AssertionError:
        st.error('The document does not seem to have text.')

def convert(pdf_document, start, end, lang):
    try:
        text = ''
        for x in range(start - 1, end):
            page_current = pdf_document[x]
            text += page_current.get_text()
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang, slow=False, lang_check=False)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)  # Reset the buffer to the beginning
        return mp3_fp
    except AssertionError:
        st.error('The PDF does not seem to have text and maybe it\'s scanned')

def render_page(pdf_document, page):
    page_1 = pdf_document[page]
    pixmap = page_1.get_pixmap()
    pil_image = Image.frombytes(
        "RGB",
        (pixmap.width, pixmap.height),
        pixmap.samples,
        "raw",
        "RGB",
        pixmap.stride,
    )
    return pil_image

def preview(pdf_document):
    input_page = st.number_input('Page number', 1, step=1)
    total_pages = len(pdf_document)
    
    if 1 <= input_page <= total_pages:
        cols = st.columns(2)
        col1, col2 = cols[0], cols[1]
        col1.header(f"Page {input_page}")
        
        if input_page < total_pages:
            col2.header(f"Page {input_page + 1}")
            right_page = render_page(pdf_document, input_page)
            col2.image(right_page, use_column_width=True)
        else:
            col2.empty()
        
        left_page = render_page(pdf_document, input_page - 1)
        col1.image(left_page, use_column_width=True)
    elif total_pages == 0:
        st.warning("No pages found in the PDF.")
    else:
        st.error(f"Invalid page number. Please choose a page between 1 and {total_pages}.")

def main():
    with st.sidebar:
        st.title('Audio Book Maker')
        uploaded_file = st.file_uploader("Upload a Document", type=['pdf', 'docx', 'txt'])
        start_page = st.number_input("Start Page", 1)
        end_page = st.number_input("End Page", 1)
        st.info('Conversion takes time, so please be patient')
        
        selected_lang = st.selectbox("Select Language", list(available_languages.values()))
        
        convert_to_audio = st.button('Convert')
        
        if uploaded_file is not None:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            if file_extension == '.pdf':
                pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            elif file_extension == '.docx':
                doc = docx.Document(uploaded_file)
                doc_content = '\n'.join([para.text for para in doc.paragraphs])
            elif file_extension == '.txt':
                doc_content = uploaded_file.read().decode('utf-8')

        if start_page > end_page:
            st.error('Start Page cannot be greater than end page')
        elif start_page <= end_page:
            if convert_to_audio and uploaded_file is not None:
                lang_code = next(key for key, value in available_languages.items() if value == selected_lang)
                if file_extension == '.pdf':
                    audio_file = convert(pdf_document, start_page, end_page, lang_code)
                    st.audio(audio_file, format='audio/mp3')
                    st.download_button('Download Audio', data=audio_file.read(), file_name='audio.mp3')
                elif file_extension == '.docx':
                    audio_file = convert_document(doc_content, lang_code)
                    st.audio(audio_file, format='audio/mp3')
                    st.download_button('Download Audio', data=audio_file.read(), file_name='audio.mp3')
                elif file_extension == '.txt':
                    audio_file = convert_document(doc_content, lang_code)
                    st.audio(audio_file, format='audio/mp3')
                    st.download_button('Download Audio', data=audio_file.read(), file_name='audio.mp3')

    if uploaded_file is not None:
        if file_extension == '.pdf':
            preview(pdf_document)
        elif file_extension == '.docx':
            st.text(doc_content)  
        elif file_extension == '.txt':
            st.text(doc_content)  
    else:
        st.info('Upload a Document, check the sidebar on the left')

if __name__ == "__main__":
    main()
