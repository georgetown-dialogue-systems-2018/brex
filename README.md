# Introduction
B. Rex is a dialogue system for book recommendations.

# Installation
Create your config file. Populate it with your Wit.ai and Goodreads API
tokens, and change any other variables you want to (see below)

```
cp src/brex/config.py.example src/brex/config.py
```

Install dependencies, and run from the `src/` directory:

```
pip3 install -r requirements.txt
cd src/
python3 main.py
```

# Configuration variables

| variable                     | values              | description                                                                                 |
|------------------------------|---------------------|---------------------------------------------------------------------------------------------|
| debug                        | True, False         | if set to True, produces more logging output.                                               |
| mode                         | 'terminal', 'flask' | Controls which interface is used. 'flask' is an HTML interface.                             |
| convo_logging_dir            | None, str           | The directory (relative to main.py) where conversation logs should be saved.                |
| gr_api_key                   | str                 | Goodreads API key. Obtained from https://www.goodreads.com/api/keys                         |
| gr_api_secret                | str                 | Goodreads API secret. Obtained from https://www.goodreads.com/api/keys                      |
| wit_access_token             | str                 | The token for your Wit.ai app. See the settings section of your app.                        |
| summarization_language       | str                 | The language the review summarizer is expecting your review to be in.                       |
| summarization_sentence_count | int                 | The number of sentences the summarizer will attempt to summarize to.                        |
| summarization_max_chars      | int                 | The maximum string length the summarizer will attempt to be under.                          |
| flask_secret                 | str                 | A randomly generated string with high entropy. See: http://flask.pocoo.org/docs/1.0/config/ |
| flask_host                   | str                 | IP address to bind the Flask app to. 127.0.0.1 for localhost, 0.0.0.0 for the world.        |
| flask_port                   | int                 | Port to bind the Flask app to.                                                              |
