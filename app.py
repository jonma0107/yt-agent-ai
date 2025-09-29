import django_setup
import os

# Initialize Django before importing any Django models
django_setup.setup()

import streamlit as st
from translation_generator_app.views import views_app

def main():
    st.title("YouTube Agent")
    st.write("Translate and get the lyrics of your favorite song from YouTube. Download the video and audio of your favorite song from YouTube.")

    with st.sidebar:
        st.header("Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        st.info("This app uses OpenAI models. Please ensure your API key has access to at least one of the following: `gpt-4o`, `gpt-5-nano`, `gpt-4-turbo`, or `gpt-3.5-turbo`.")
        if st.button("Clear Chat"):
            # Clear the results from the session state
            if 'result' in st.session_state:
                del st.session_state.result
            st.rerun()

    youtube_url = st.text_input("Enter YouTube URL")

    if st.button("Generate Translation"):
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not youtube_url:
            st.error("Please enter a YouTube URL.")
        else:
            with st.spinner("Processing..."):
                try:
                    # Store the result in the session state
                    st.session_state.result = views_app.process_youtube_video(youtube_url, openai_api_key)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    # Also clear previous results if an error occurs
                    if 'result' in st.session_state:
                        del st.session_state.result

    # If there are results in the session state, display them
    if 'result' in st.session_state:
        result = st.session_state.result
        st.success("Translation Generated!")
        st.subheader("Title")
        st.write(result['title'])
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Transcription")
            st.text_area("", result['original_transcription'], height=300)

        with col2:
            st.subheader("Translation")
            st.text_area("", result['translation'], height=300)


        st.subheader("Downloads")
        video_file_path = result['video_file']
        with open(video_file_path, "rb") as file:
            st.download_button(
                label="Download Video",
                data=file,
                file_name=os.path.basename(video_file_path),
                mime="video/mp4"
            )
        
        audio_file_path = result['audio_file']
        with open(audio_file_path, "rb") as file:
            st.download_button(
                label="Download Audio (MP3)",
                data=file,
                file_name=os.path.basename(audio_file_path),
                mime="audio/mpeg"
            )

if __name__ == "__main__":
    main() 