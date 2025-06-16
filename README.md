# Language Buddy
### Portland State University Group Project


### Contributors
Andrew Niven, Lee Hoang, Nicolas Oliver, Greg Witt, Bahareh Golchin

[GoodGuyGregory](https://github.com/GoodGuyGregory)

[baharehgl](https://github.com/baharehgl)

[leevhoang](https://github.com/leevhoang)

[dnoliver](https://github.com/dnoliver)

[thedragonmask](https://github.com/TheDragonMask)

## About 

TBD

## Installation 

Install Python 3.10.11

Windows:

```ps1
# Create virtual environment using venv (more details to come)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate.ps1

# Install dependencies
pip install -r requirements.txt

# Export OpenAI API Key
$env:OPENAI_API_KEY="sk-proj-xxxx"

# Run the app
streamlit run app.py

# Run LibreTranslate (use another terminal)
libretranslate
```


## Documentation 

[Tatoeba API](https://api.dev.tatoeba.org/unstable#?route=cmp--schemas-audio)

## Troubleshooting

### Allow external traffic to Streamlit app running locally

This should be automatic, but if for some reason is not working,
try this:

In a powershell console with Admin privileges, do: 

```ps1
New-NetFirewallRule `
    -DisplayName "Allow Inbound Traffic on Port 8501" `
    -Direction Inbound `
    -LocalPort 8501 `
    -Protocol TCP `
    -Action Allow
```

## Other

This project uses LibreTranslate, which is a free and open source machine translation API. 
You can find more information about it on [pypi.org](https://pypi.org/project/libretranslate/) and on the [official website](https://libretranslate.com/).
The source code of LibreTranslate can be found on [GitHub.](https://github.com/LibreTranslate/LibreTranslate)

## License

[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)