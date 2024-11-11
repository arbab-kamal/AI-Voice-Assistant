import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64

def setup_openai_client(api_key):
    return openai.OpenAI(api_key=api_key)

def transcribe_audio(client, audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text 

def fetch_ai_response(client, input_text):
    messages = [{"role": "user", "content": input_text}]
    response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages)
    return response.choices[0].message.content  # Return text response

def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(audio_path)

def create_text_card(text,title="Response"): 
    card_html=f"""
    <style>
        .card{{
            background-color: #ffffff; /* Light background for contrast */
            color: #333333; /* Darker text color */
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
            transition: 0.3s;
            border-radius: 5px;
            padding: 15px;
            max-width: 300px; /* Optional: limits card width */
        }}
        .card:hover{{
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }}
        .container{{
            padding:2px 16px;
        }}
    </style>
    <div class="card">
        <div class="container">
            <h4><b>{title}</b></h4>
            <p>{text}</p>
        </div>
    </div>
    """
    st.markdown(card_html,unsafe_allow_html=True)

def auto_play_audio(audio_file):
    with open(audio_file,"rb") as audio_file:
        audio_bytes=audio_file.read()
    base64_audio=base64.b64encode(audio_bytes).decode("utf-8")
    audio_html=f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html,unsafe_allow_html=True)
def main():
    st.sidebar.title("API KEY CONFIGURATION")
    api_key = st.sidebar.text_input("Enter your API key", type="password")
    st.title("🔊 Aurora SpeakEasy")
    st.write("Hi there! Click on the voice recorder to interact with me. How can I assist you today?")

    if api_key:
        client = setup_openai_client(api_key)
        recorded_audio = audio_recorder()
        
        if recorded_audio:
            audio_file = "audio.mp3"
            with open(audio_file, "wb") as f:
                f.write(recorded_audio)
                
            transcribed_text = transcribe_audio(client, audio_file)
            create_text_card(transcribed_text,"Transcribe Audio") 
            
            # Get AI response text
            ai_response = fetch_ai_response(client, transcribed_text)
            
            # Convert response text to audio
            response_audio_file = "audio_response.mp3"
            text_to_audio(client, ai_response, response_audio_file)
            
            auto_play_audio(response_audio_file)
            create_text_card(ai_response,"Audio Transcription")

if __name__ == "__main__":
    main()
