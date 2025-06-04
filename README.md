# Streamlit Social Media Agent

A Streamlit-based social media agent that allows users to:

- Log in and subscribe for free
- Generate social media posts from YouTube video transcripts, documents (PDF/TXT), or images/photos
- Edit and post content to platforms (Twitter, LinkedIn, Facebook, Instagram)
- Authenticate and post to Twitter using real OAuth tokens
- Analyze images/photos using OpenAI Vision (GPT-4o) or fallback to OpenAI API
- Maintain robust session state and avoid repeated login prompts or state loss on refresh

## Features

- **User Authentication:** Sign up, log in, and subscribe for free.
- **Content Generation:**
  - Generate posts from YouTube video transcripts (auto-summarized).
  - Generate posts from uploaded PDF/TXT documents.
  - Generate posts from uploaded images/photos using vision AI.
- **Social Media Integration:**
  - Real Twitter OAuth login and posting (via Flask + Tweepy).
  - Simulated login and posting for LinkedIn, Facebook, Instagram.
- **Session Management:** Robust session state to avoid repeated logins and state loss.
- **Post Editing:** Edit generated posts before publishing.
- **Error Handling:** User-friendly error messages for all flows.

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   - Create a `.env` file in the project root with the following (see `.gitignore`):
     ```env
     GITHUB_TOKEN=your_github_token_for_gpt-4o
     OPENAI_API_KEY=your_openai_api_key  # (optional, for vision support)
     TWITTER_CONSUMER_KEY=your_twitter_consumer_key
     TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
     FLASK_SECRET_KEY=your_flask_secret
     TWITTER_CALLBACK_URL=http://localhost:5000/twitter/callback
     ```
   - **Do not commit your `.env` file!**

4. **Run the Streamlit app:**
   ```sh
   streamlit run app.py
   ```

5. **(Optional) Run the Twitter OAuth server:**
   ```sh
   python twitter_oauth_server.py
   ```

## File Structure

- `app.py` - Main Streamlit UI and logic
- `user_db.py` - User management, token storage, Twitter posting logic
- `social_media_agent.py` - YouTube transcript fetching, summarization, post generation
- `twitter_oauth_server.py` - Flask server for Twitter OAuth login/callback
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed)
- `.gitignore` - Files to ignore in git

## Notes
- Only Twitter uses real OAuth and posting; other platforms are simulated.
- For image/photo analysis, OpenAI Vision (GPT-4o) is used if available, otherwise falls back to OpenAI API if key is set.
- The app is for educational/demo purposes. Do not use real credentials in production without proper security review.

## License
MIT License
