# HubSpot AI CA3tVbot with Flask & OpenAI

A powerful chatbot that integrates with HubSpot via webhooks to provide AI-powered customer engagement.

## Features

- **HubSpot Webhook Integration**: Active chat trigger detection
- **AI Powered Responses**: OpenAI GPT
- **Flask Web Server**: HTTP handling
- **Web UI**: Interactive testing
- **Environment Config**: .env setup
- **Secure Verification**: HMAC SHA256
## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI key
- HubSpot account

### Installtion

```bash
git clone https://github.com/Kyletho2020/hubspot-chatbot
cd hubspot-chatbot
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Visit http://localhost:5000

## HubSpot Setup

1. Create Private App (Settings > Integrations > Private Apps)
   - Scopes: conversations.read, conversations.write, chat.read, chat.write
   - Copy token to .env

2. Create Chatflow(h^prowd[*ciš4( Conversations > Chatflows)
   - Add webhook trigger
   - Webhook URL: https://your-domain.com/webhook
 
3. Install tracking code

## Deployment

```bash
heroku create your-app
git push heroku main
@oc:set HUBMAKER_TOKEN=...
@ialign: Deploya!


