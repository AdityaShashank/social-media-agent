import streamlit as st
import webbrowser

from social_media_agent import fetch_youtube_transcript, summarize_transcript_local, generate_social_media_content_gpt4o
from user_db import init_db, add_user, authenticate_user, subscribe_user, save_social_token, get_social_token

# --- IMAGE ANALYSIS PLACEHOLDER ---
def analyze_image_and_extract_context(image_file):
    """
    Analyze the uploaded image and extract context for post generation using OpenAI GPT-4o Vision API.
    Tries GitHub proxy first, then falls back to official OpenAI API if OPENAI_API_KEY is set.
    """
    try:
        import requests
        import base64
        import os
        from dotenv import load_dotenv
        import mimetypes
        load_dotenv()
        # Try GitHub proxy first
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        # Reset file pointer and read image bytes
        image_file.seek(0)
        image_bytes = image_file.read()
        mime_type, _ = mimetypes.guess_type(getattr(image_file, 'name', 'image.png'))
        if not mime_type:
            mime_type = 'image/png'
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:{mime_type};base64,{image_b64}"
        # 1. Try GitHub proxy (text only, will error for vision)
        if GITHUB_TOKEN:
            api_url = "https://models.github.ai/inference/openai/gpt-4o/chat/completions"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            }
            messages = [
                {"role": "system", "content": "You are a professional vision assistant. Describe the image in detail for social media post generation."},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]}
            ]
            data = {
                "model": "openai/gpt-4o",
                "messages": messages,
                "max_tokens": 300
            }
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 404 and OPENAI_API_KEY:
                # Fallback to OpenAI official API
                pass
            else:
                return f"Vision API error (GitHub proxy): {response.status_code} {response.text}"
        # 2. Fallback to OpenAI official API
        if OPENAI_API_KEY:
            api_url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            messages = [
                {"role": "system", "content": "You are a professional vision assistant. Describe the image in detail for social media post generation."},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]}
            ]
            data = {
                "model": "gpt-4o",
                "messages": messages,
                "max_tokens": 300
            }
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                return f"Vision API error (OpenAI): {response.status_code} {response.text}"
        return "Vision API is not available. Please set OPENAI_API_KEY in your .env for image analysis."
    except Exception as e:
        import traceback
        return f"Error analyzing image: {e}\n{traceback.format_exc()}"

# --- PLATFORM LOGIN CHECK ---
def is_platform_logged_in(username, platform):
    if platform.lower() == 'twitter':
        from user_db import get_twitter_tokens
        access_token, access_token_secret = get_twitter_tokens(username)
        return bool(access_token and access_token_secret)
    else:
        return get_social_token(username, platform.lower()) == 'LOGGED_IN'

def platform_login_url(platform):
    # Placeholder: In production, use real OAuth URLs
    urls = {
        "Linkedin": "https://www.linkedin.com/login",
        "Twitter": "https://twitter.com/login",
        "Facebook": "https://www.facebook.com/login",
        "Instagram": "https://www.instagram.com/accounts/login/"
    }
    return urls.get(platform, "https://google.com")

init_db()

# --- SESSION STATE FIXES ---
# Ensure session state is initialized only once
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'post_content' not in st.session_state:
    st.session_state['post_content'] = None
if 'platform_logged_in' not in st.session_state:
    st.session_state['platform_logged_in'] = False
if 'post_platform' not in st.session_state:
    st.session_state['post_platform'] = None
if 'twitter_linked' not in st.session_state:
    st.session_state['twitter_linked'] = False
if 'can_post' not in st.session_state:
    st.session_state['can_post'] = False

# --- LOGIN LOGIC ---
# Only rerun on successful login/signup, not on every refresh
if not st.session_state['logged_in']:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if authenticate_user(login_user, login_pass):
                st.session_state['logged_in'] = True
                st.session_state['username'] = login_user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with tab2:
        signup_user = st.text_input("New Username", key="signup_user")
        signup_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if add_user(signup_user, signup_pass):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")
else:
    st.success(f"Welcome, {st.session_state['username']}!")
    if st.button("Subscribe for Free"):
        subscribe_user(st.session_state['username'])
        st.success("You are now subscribed!")
    st.markdown("---")
    st.header("Save Social Media Login (for posting)")
    platform = st.selectbox("Platform", ["linkedin", "twitter", "facebook", "instagram"])
    already_logged_in = get_social_token(st.session_state['username'], platform) == 'LOGGED_IN'
    if already_logged_in:
        st.success(f"You are already logged in to {platform.capitalize()}!")
    else:
        if st.button(f"Log in to {platform.capitalize()}"):
            login_url = platform_login_url(platform.capitalize())
            webbrowser.open(login_url)
            save_social_token(st.session_state['username'], platform, 'LOGGED_IN')
            st.success(f"{platform.capitalize()} login recorded! (simulated)")
    st.markdown("---")
    st.header("Generate Social Media Post")
    input_mode = st.radio("Choose input type:", ["YouTube Video", "Document (PDF/TXT)", "Image/Photo"])
    post_platform = st.selectbox("Select social media platform:", ["Linkedin", "Twitter", "Facebook", "Instagram", "Other"])
    document_text = None
    video_url = ""
    image_context = None
    if input_mode == "YouTube Video":
        video_url = st.text_input("Enter a YouTube video URL:")
    elif input_mode == "Document (PDF/TXT)":
        uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/pdf":
                    try:
                        import PyPDF2
                    except ImportError:
                        st.error("PyPDF2 is required for PDF extraction. Please install it with 'pip install PyPDF2' and restart the app.")
                        document_text = None
                    else:
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        document_text = " ".join(page.extract_text() or '' for page in pdf_reader.pages)
                elif uploaded_file.type == "text/plain":
                    document_text = uploaded_file.read().decode("utf-8")
                else:
                    st.error("Unsupported file type.")
            except Exception as e:
                st.error(f"Error reading document: {e}")
    elif input_mode == "Image/Photo":
        uploaded_image = st.file_uploader("Upload an image/photo", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_image is not None:
            try:
                from PIL import Image
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                uploaded_image.seek(0)
                image_context = analyze_image_and_extract_context(uploaded_image)
                st.subheader("Image Context:")
                st.write(image_context)
            except Exception as e:
                st.error(f"Error analyzing image: {e}")
    # Only update session state on post generation
    if st.button("Generate Post"):
        if input_mode == "YouTube Video":
            if not video_url:
                st.error("Please enter a YouTube video URL.")
            else:
                with st.spinner("Fetching transcript..."):
                    transcript = fetch_youtube_transcript(video_url)
                if transcript.startswith("Error fetching transcript"):
                    st.error(transcript)
                else:
                    with st.spinner("Summarizing transcript..."):
                        summarized_transcript = summarize_transcript_local(transcript)
                    st.subheader("Summarized Transcript:")
                    st.write(summarized_transcript)
                    with st.spinner(f"Generating {post_platform} post..."):
                        post = generate_social_media_content_gpt4o(summarized_transcript, post_platform)
                    st.session_state['post_content'] = post
                    st.session_state['platform_logged_in'] = False
                    st.session_state['post_platform'] = post_platform
                    st.subheader(f"Generated Social Media Post for {post_platform}:")
                    st.write(post)
        elif input_mode == "Document (PDF/TXT)":
            if not document_text:
                st.error("Please upload a valid document.")
            else:
                with st.spinner("Summarizing document..."):
                    summarized_doc = summarize_transcript_local(document_text)
                st.subheader("Summarized Document:")
                st.write(summarized_doc)
                with st.spinner(f"Generating {post_platform} post..."):
                    post = generate_social_media_content_gpt4o(summarized_doc, post_platform)
                st.session_state['post_content'] = post
                st.session_state['platform_logged_in'] = False
                st.session_state['post_platform'] = post_platform
                st.subheader(f"Generated Social Media Post for {post_platform}:")
                st.write(post)
        elif input_mode == "Image/Photo":
            if not image_context:
                st.error("Please upload and analyze an image.")
            else:
                with st.spinner("Generating post from image context..."):
                    post = generate_social_media_content_gpt4o(image_context, post_platform)
                st.session_state['post_content'] = post
                st.session_state['platform_logged_in'] = False
                st.session_state['post_platform'] = post_platform
                st.subheader(f"Generated Social Media Post for {post_platform}:")
                st.write(post)
    # --- POSTING LOGIC ---
    post_platform = st.session_state.get('post_platform')
    if st.session_state['post_content'] and post_platform:
        platform_logged_in = is_platform_logged_in(st.session_state['username'], post_platform)
        if not platform_logged_in:
            st.info(f"Please log in to your {post_platform} account using the login button above.")
        else:
            st.success(f"Ready to post to {post_platform}!")
            edited_post = st.text_area(
                f"Edit your {post_platform} post before publishing:",
                value=st.session_state['post_content'],
                key="edit_post_content"
            )
            if st.button(f"Post to {post_platform}"):
                if post_platform.lower() == 'twitter':
                    from user_db import get_twitter_tokens, post_to_twitter
                    access_token, access_token_secret = get_twitter_tokens(st.session_state['username'])
                    if access_token and access_token_secret:
                        try:
                            post_to_twitter(access_token, access_token_secret, edited_post)
                            st.success(f"Post sent to Twitter!\n\nContent:\n{edited_post}")
                        except Exception as e:
                            st.error(f"Failed to post to Twitter: {e}")
                    else:
                        st.error("Twitter account not linked. Please log in via the Twitter login button above.")
                else:
                    st.success(f"Post sent to {post_platform} (simulated).\n\nContent:\n{edited_post}")
                st.session_state['post_content'] = None
                st.session_state['post_platform'] = None
