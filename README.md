# Sarah - AI Lead Qualification Voice Agent

An AI-powered voice agent that qualifies real estate leads and warm transfers qualified prospects to your team. Built in **1.75 hours** using Claude Code.

## The Problem

Manual lead qualification is expensive and inconsistent:
- Requires dedicated staff available during business hours
- Inconsistent script adherence and data entry
- Slow response times (speed-to-lead matters)
- Costs $3,000-5,000/month for a human SDR

## The Solution

**Sarah** - an AI voice agent that:
- Calls new leads automatically with personalized opening
- Qualifies using tactical empathy techniques
- Warm transfers qualified leads immediately
- Updates 10+ Salesforce fields automatically
- Creates call activity records with transcripts
- Costs ~$50-60/month at 150 calls/week

## Tech Stack

| Component | Purpose |
|-----------|---------|
| [Retell AI](https://retellai.com) | Voice agent platform |
| Claude Sonnet 4 | Conversation AI + transcript interpretation |
| Heroku | Webhook hosting |
| Salesforce | CRM integration |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Retell AI  │────▶│   Heroku    │────▶│ Salesforce  │
│  (Voice)    │     │  (Webhook)  │     │   (CRM)     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│   Claude    │     │   Claude    │
│  Sonnet 4   │     │  Sonnet 4   │
│ (Live Call) │     │(Transcript) │
└─────────────┘     └─────────────┘
```

## Features

### Call Flow
1. Sarah calls lead: "Hi [Name]... it's Sarah. You submitted a form online with us for [Street]. How can we help?"
2. Qualifies: motivation, timeline, ownership, agent status
3. If qualified → warm transfer to manager
4. After call → AI interprets transcript → updates Salesforce

### Qualification Criteria
A lead is **qualified** if ALL are true:
- Has motivation to sell (inherited, divorce, financial, repairs, etc.)
- Timeline within 3 months
- Is the owner or co-owner
- NOT working with a real estate agent

### Salesforce Fields Updated
- `Rating` - Hot/Warm/Cold
- `Status` - Warm (when transferred)
- `Motivation__c` - Hot/Warm/Cold level
- `Reason_for_Selling__c` - Divorce/Financial Stress/Inherited Property/Condition
- `Reason_for_Selling_Notes__c` - AI summary of call
- `Timeframe_to_sell__c` - Timeline
- `Listed_with_a_Realtor__c` - Yes/No
- `Property_Insights__c` - Property notes
- `Connected_with_Lead__c` - Call completed flag

## Setup

### 1. Create Retell Agent

```bash
curl -X POST "https://api.retellai.com/create-agent" \
  -H "Authorization: Bearer YOUR_RETELL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "REI Lead Qualifier",
    "voice_id": "11labs-Lily",
    "llm_websocket_url": "wss://api.retellai.com/llm-websocket/YOUR_LLM_ID",
    "ambient_sound": "coffee-shop",
    "ambient_sound_volume": 0.2
  }'
```

### 2. Deploy Webhook to Heroku

```bash
# Clone this repo
git clone https://github.com/tisa-pixel/sarah-rei-qualifier.git
cd sarah-rei-qualifier

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set SF_USERNAME=your_sf_user
heroku config:set SF_PASSWORD=your_sf_password
heroku config:set SF_SECURITY_TOKEN=your_sf_token
heroku config:set SF_DOMAIN=login

# Deploy
git push heroku main
```

### 3. Configure Retell Webhook

Set your Retell agent's webhook URL to:
```
https://your-app-name.herokuapp.com/webhook/retell
```

### 4. Make Calls

```bash
curl -X POST "https://api.retellai.com/v2/create-phone-call" \
  -H "Authorization: Bearer YOUR_RETELL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+1YOUR_RETELL_NUMBER",
    "to_number": "+1LEAD_PHONE",
    "override_agent_id": "YOUR_AGENT_ID",
    "retell_llm_dynamic_variables": {
      "seller_name": "John",
      "property_address": "Main Street"
    },
    "metadata": {
      "lead_id": "00QXXXXXXXXXX"
    }
  }'
```

## Files

| File | Purpose |
|------|---------|
| `app.py` | Main webhook server - handles Retell events, AI interpretation, SF updates |
| `prompt.py` | Sarah's conversation script and personality |
| `config.py` | Scoring weights and SF field mappings |
| `requirements.txt` | Python dependencies |
| `Procfile` | Heroku process definition |

## Cost Analysis

### Build Cost
| Approach | Time | Cost |
|----------|------|------|
| Traditional (SF admin + dev) | 4-6 weeks | $12,900+ |
| With Claude Code | 1.75 hours | ~$300 (your time) |

### Operating Cost (150 calls/week, 50 conversations)
| Component | Monthly Cost |
|-----------|-------------|
| Retell AI | ~$50-60 |
| Heroku (Basic) | $7 |
| Anthropic API | ~$5 |
| **Total** | **~$65/month** |

vs. Human SDR: **$3,000-5,000/month**

**Annual savings: $35,000-59,000**

## Customization

### Change Transfer Number
Update the `transfer_call` tool in your Retell LLM configuration.

### Modify Qualification Criteria
Edit the qualification logic in `app.py` in the `interpret_with_ai()` function.

### Add More Salesforce Fields
Update the `update_salesforce_lead()` function in `app.py`.

## Built With

- [Claude Code](https://claude.ai/claude-code) - AI-assisted development
- [Retell AI](https://retellai.com) - Voice agent platform
- [Anthropic Claude](https://anthropic.com) - AI models

## License

MIT

---

*Built in 1.75 hours with Claude Code*
