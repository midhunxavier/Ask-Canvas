# 🎈 Ask Canvas 

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://laughing-waddle-5v596g6prpvc79wj.github.dev/)

Chat with your Canvas!

## Overview of the App

This app is provides give information about your Canvas based on your given access token


## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://askcanvas.streamlit.app/)

### Get an Get a Canvas Access Token  (Example (LTU))

You can get your own Canvas Access Token by following the following instructions:

1. Go to https://canvas.ltu.se/profile/settings.
2. Click on the `+ Create new secret key` button.



### Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:

1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.


## Run it locally

```sh
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run Chatbot.py
```
