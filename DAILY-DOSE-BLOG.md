# Daily Dose - Build Post: Sarah - AI Lead Qualifier
**For conversionisourgame.com**
**Created:** December 11, 2025

---

## 1. BUILD TITLE
How I Built an AI Voice Agent to Qualify Real Estate Leads (And Replaced a $5K/Month SDR for $65)

---

## 2. THE PROBLEM
Manual lead qualification in real estate investing is expensive and broken. You're paying $3,000-5,000/month for an SDR who:
- Only works business hours (leads call at night and weekends)
- Misses calls, forgets to update Salesforce, doesn't follow the script
- Gets tired, has bad days, lets bias affect qualification
- Quits after 6 months and you start over

Speed-to-lead matters - if you don't call a lead back within 5 minutes, your connect rate drops 10x. But you can't afford staff sitting idle waiting for leads 24/7.

You need someone who answers instantly, never sleeps, follows the script perfectly, and costs pennies per call.

---

## 3. THE SOLUTION
Built **Sarah** - an AI voice agent that calls new leads automatically, qualifies them using tactical empathy techniques (Chris Voss style), and warm transfers qualified prospects to your team immediately.

When a lead submits a form, Sarah calls within 60 seconds: "Hi [Name]... it's Sarah. You submitted a form online with us for [Street Address]. How can we help?"

She asks about motivation, timeline, ownership, and agent status. If they're qualified (motivated + timeline + owner + no agent), she transfers them live to your account executive. After the call, Claude analyzes the transcript and updates 10+ Salesforce fields automatically.

Built the entire system in **1.75 hours** using Claude Code. Deployed to Heroku. Costs ~$65/month vs $5k/month for a human.

---

## 4. WATCH ME BUILD IT
[YouTube embed code - TBD]

Watch the full walkthrough on YouTube where I break down the Retell AI setup, tactical empathy script, Claude transcript interpretation, and Salesforce integration.

---

## 5. WHAT YOU'LL LEARN
- How to build an AI voice agent with Retell AI
- How to use Claude Sonnet 4 for live conversation + transcript analysis
- Writing tactical empathy scripts (Chris Voss methodology)
- Automating Salesforce updates via REST API
- Scoring and qualifying leads programmatically
- Deploying Flask webhooks to Heroku
- Warm transferring calls to human agents
- Cost optimization strategies for AI voice systems
- Building outbound calling automation

---

## 6. BUILD DETAILS

### 6.1 Time Investment
| Who | Time Required |
|-----|---------------|
| **If You Hire a Dev** | 4-6 weeks ($12,900+) |
| **If You Build It (with this guide)** | 1.75 hours |

### 6.2 Cost Breakdown
| Approach | Cost |
|----------|------|
| **Developer Rate** | $150/hour |
| **Estimated Dev Cost** | $12,900+ (SF admin + dev over 4-6 weeks) |
| **DIY Cost (Your Time)** | 1.75 hours + API usage fees |
| **Human SDR (Salary + Benefits)** | $3,000-5,000/month |

**Operating Costs (150 calls/week, 50 conversations/week):**
| Component | Monthly Cost |
|-----------|-------------|
| Retell AI | $50-60 |
| Heroku (Basic dyno) | $7 |
| Anthropic API (Claude) | $5 |
| **Total** | **$62-72/month** |

**Annual savings vs Human SDR:** $35,000-59,000

---

## 7. TECH STACK
🔧 **Tools Used:**
- **Retell AI** (Voice agent platform - handles calls, speech-to-text, text-to-speech)
- **Claude Sonnet 4** (Conversation AI during live calls + transcript interpretation after)
- **Flask** (Python webhook server)
- **Heroku** (Webhook hosting)
- **Salesforce REST API** (CRM integration)
- **simple-salesforce** (Python library for SF)

---

## 8. STEP-BY-STEP BREAKDOWN

### 1. **Set Up Retell AI Account**

Sign up at [Retell AI](https://retellai.com) and get:
- API key
- Phone number (for outbound calling)

**Why Retell AI?**
- Handles all the hard parts: telephony, speech recognition, TTS
- Built-in Claude Sonnet 4 integration
- Warm transfer functionality
- Webhook events for call lifecycle

---

### 2. **Create the LLM Configuration**

In Retell dashboard, create a new LLM with Claude Sonnet 4:

**Model Settings:**
- Model: `claude-sonnet-4-20250514`
- Temperature: 0.7 (balanced creativity + consistency)
- Max tokens: 500 per response

**Dynamic Variables:**
```json
{
  "seller_name": "{{lead.FirstName}}",
  "property_address": "{{lead.Street}}",
  "company_name": "Your Company Name",
  "agent_name": "Sarah"
}
```

These get injected into the prompt for personalization.

---

### 3. **Write the Tactical Empathy Script**

Create `prompt.py` with Chris Voss-style tactical empathy:

```python
SYSTEM_PROMPT = """You are an AI voice agent for {company_name}.
Your role is to qualify motivated seller leads using tactical empathy
and warm transfer them to an Account Executive.

## Your Voice & Personality
- Calm, curious, understated confidence (late-night FM DJ tone)
- Let silence work for you - count to 5 after questions
- Mirror and label instead of pushing through objections
- Sound like a helpful neighbor, not a telemarketer

## CRITICAL: Words to NEVER Use
- "Is now a good time?"
- "I'm sorry for bothering you"
- "Trust me"
- "To be honest"
- "Are you looking to sell?"

## CALL FLOW

### 1. INTRO - Disarm & Hook
"Hi {seller_name}... (pause)... it's Sarah. You submitted a form online
with us for {property_address}... how can WE help?"

### 2. DISCOVERY - Build Curiosity
"What would make this call a win for you today?"

### 3. QUALIFICATION - Tactical Questions
**Motivation:**
- "What's got you thinking about selling?"
- "Why is now important?"

**Timeline:**
- "When are you hoping to have this wrapped up?"
- "What happens if you don't sell by then?"

**Decision Maker:**
- "Is there anyone else involved in this decision?"

**Agent Status:**
- "Why aren't you listing with an agent?"

### 4. WARM TRANSFER (if qualified)
"Based on what you've shared, I think it makes sense for you to speak
with [Manager Name]. They handle our options meetings. Let me connect
you now - stay on the line."

[Use transfer_call tool]
"""
```

**Key techniques:**
- **Mirroring:** Repeat last 3 words they said
- **Labeling:** "It sounds like..." or "It seems like..."
- **Calibrated questions:** "What" and "How" questions, not "Why"
- **Silence:** Let awkward pauses work for you

---

### 4. **Create Retell Agent**

```bash
curl -X POST "https://api.retellai.com/create-agent" \
  -H "Authorization: Bearer YOUR_RETELL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "Sarah - REI Lead Qualifier",
    "voice_id": "11labs-Lily",
    "llm_websocket_url": "wss://api.retellai.com/llm-websocket/YOUR_LLM_ID",
    "ambient_sound": "coffee-shop",
    "ambient_sound_volume": 0.2,
    "enable_backchannel": true,
    "normalize_for_speech": true,
    "opt_out_sensitive_data_storage": false
  }'
```

**Voice Selection:**
- 11labs-Lily: Warm, professional, empathetic (best for REI)
- Test different voices - tone matters!

**Ambient sound:**
- Subtle coffee shop background = sounds human
- Volume 0.2 = barely noticeable but adds realism

---

### 5. **Build Flask Webhook Server**

Create `app.py`:

```python
from flask import Flask, request, jsonify
import anthropic
from simple_salesforce import Salesforce

app = Flask(__name__)

# Salesforce client
sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain='login'
)

# Anthropic client
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route('/webhook/retell', methods=['POST'])
def retell_webhook():
    """Handle Retell webhook events"""
    data = request.json
    event_type = data.get('event')

    if event_type == 'call_ended':
        # Call finished - interpret transcript and update SF
        call_id = data['call']['call_id']
        transcript = data['call']['transcript']
        lead_id = data['call']['metadata'].get('lead_id')

        # Use Claude to interpret the call
        interpretation = interpret_with_ai(transcript)

        # Update Salesforce
        update_salesforce_lead(lead_id, interpretation)

    return jsonify({"status": "success"})

def interpret_with_ai(transcript: str) -> dict:
    """Use Claude to interpret call transcript and extract data"""

    prompt = f"""Analyze this sales call transcript and extract:

    1. Motivation for selling (foreclosure, divorce, inherited, relocation, etc.)
    2. Timeline (immediately, 30 days, 1-3 months, 3-6 months, etc.)
    3. Is the caller the owner or decision maker? (yes/no)
    4. Do they have a real estate agent? (yes/no)
    5. Overall lead quality: Hot/Warm/Cold
    6. Brief summary of their situation

    Transcript:
    {transcript}

    Return JSON only.
    """

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)

def update_salesforce_lead(lead_id: str, data: dict):
    """Update Salesforce lead with call data"""

    # Map AI interpretation to SF fields
    sf_update = {
        'Rating': data['lead_quality'],  # Hot/Warm/Cold
        'Status': 'Warm' if data['lead_quality'] == 'Hot' else 'Contacted',
        'Motivation__c': data['lead_quality'],
        'Reason_for_Selling__c': data['motivation'],
        'Reason_for_Selling_Notes__c': data['summary'],
        'Timeframe_to_sell__c': data['timeline'],
        'Listed_with_a_Realtor__c': data['has_agent'],
        'Connected_with_Lead__c': True
    }

    # Update the lead
    sf.Lead.update(lead_id, sf_update)

    # Create call activity
    sf.Task.create({
        'WhoId': lead_id,
        'Subject': 'Inbound Lead Call - Sarah AI',
        'Status': 'Completed',
        'Description': f"AI Call Summary:\n\n{data['summary']}\n\n---\n{transcript}",
        'ActivityDate': datetime.now().strftime('%Y-%m-%d')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

**Key Flow:**
1. Retell calls webhook when call ends
2. Extract transcript from webhook payload
3. Use Claude to interpret transcript → structured JSON
4. Update Salesforce lead with extracted data
5. Create Task record with full transcript

---

### 6. **Implement Lead Scoring**

Create `config.py`:

```python
# Scoring weights
TIMELINE_SCORES = {
    "immediately": 100,
    "within_30_days": 80,
    "1_3_months": 60,
    "3_6_months": 40,
    "6_plus_months": 20,
}

MOTIVATION_SCORES = {
    "foreclosure": 100,
    "divorce": 90,
    "inherited": 85,
    "relocation": 70,
    "repairs_needed": 65,
}

CLASSIFICATION_THRESHOLDS = {
    "hot": 80,   # Score >= 80
    "warm": 50,  # Score >= 50
    "cold": 20,  # Score < 50
}

def calculate_score(answers: dict) -> int:
    """Calculate qualification score"""
    score = 0

    # Timeline weight
    score += TIMELINE_SCORES.get(answers.get("timeline"), 30)

    # Motivation weight
    score += MOTIVATION_SCORES.get(answers.get("motivation"), 40)

    # No agent = +100, has agent = +0
    score += 0 if answers.get("has_agent") else 100

    # Decision maker = +100
    score += 100 if answers.get("decision_maker") else 0

    return score / 4  # Average score

def classify_lead(score: int) -> str:
    """Classify lead as Hot/Warm/Cold"""
    if score >= CLASSIFICATION_THRESHOLDS["hot"]:
        return "Hot"
    elif score >= CLASSIFICATION_THRESHOLDS["warm"]:
        return "Warm"
    else:
        return "Cold"
```

**Qualification Criteria:**
A lead is **qualified for transfer** if ALL are true:
- Score >= 80 (Hot)
- Timeline within 3 months
- Is owner or decision maker
- No real estate agent

---

### 7. **Deploy to Heroku**

Create `requirements.txt`:
```
flask==3.0.0
anthropic==0.39.0
simple-salesforce==1.12.5
gunicorn==21.2.0
```

Create `Procfile`:
```
web: gunicorn app:app
```

**Deploy:**
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-rei-qualifier

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set SF_USERNAME=your_sf_user
heroku config:set SF_PASSWORD=your_sf_password
heroku config:set SF_SECURITY_TOKEN=your_sf_token
heroku config:set SF_DOMAIN=login

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

Your webhook is live at: `https://your-rei-qualifier.herokuapp.com/webhook/retell`

---

### 8. **Configure Retell Webhook**

In Retell dashboard:
- Go to your agent settings
- Set webhook URL: `https://your-rei-qualifier.herokuapp.com/webhook/retell`
- Enable events: `call_started`, `call_ended`

Now Retell will POST to your webhook when calls start/end.

---

### 9. **Trigger Outbound Calls**

**Option 1: API Call (from Zapier, n8n, or code)**

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
      "property_address": "123 Main Street"
    },
    "metadata": {
      "lead_id": "00QXXXXXXXXXX"
    }
  }'
```

**Option 2: Salesforce Flow (Automated)**

Create a Record-Triggered Flow:
- Trigger: When Lead is created
- Condition: If `Status = New`
- Action: HTTP Callout to Retell API (above)

**Option 3: Zapier/n8n**

- Trigger: New Salesforce Lead
- Action: HTTP POST to Retell API

---

### 10. **Test & Iterate**

**Testing Checklist:**
1. Call a test number → verify Sarah intro is personalized
2. Answer questions → verify she follows the script
3. Get qualified → verify warm transfer works
4. Hang up → check Salesforce updates
5. Review transcript → verify accuracy

**Common Issues:**
- **Sarah interrupts:** Adjust `interruption_sensitivity` in Retell (lower = less sensitive)
- **Doesn't transfer:** Check transfer_call tool configuration
- **SF not updating:** Check webhook logs (`heroku logs --tail`)
- **Voice sounds robotic:** Try different voice IDs or adjust speed/pitch

---

## 9. GITHUB REPO
📂 **Get the Code:**
[View on GitHub: github.com/tisa-pixel/rei-lead-qualifier](https://github.com/tisa-pixel/rei-lead-qualifier)

**What's included in the repo:**
- Complete Flask webhook server
- Tactical empathy script (Chris Voss style)
- Salesforce integration code
- Lead scoring algorithm
- Environment variable template
- Heroku deployment config
- README with setup instructions

---

## 10. DOWNLOAD THE TEMPLATE
⬇️ **Download Resources:**
- [Clone the repo](https://github.com/tisa-pixel/rei-lead-qualifier) - Full source code
- [Tactical Empathy Script](https://github.com/tisa-pixel/rei-lead-qualifier/blob/main/prompt.py) - Complete conversation flow
- [Heroku Config](https://github.com/tisa-pixel/rei-lead-qualifier/blob/main/Procfile) - Deployment setup

**Setup Checklist:**
1. Sign up for Retell AI
2. Get Retell phone number + API key
3. Create LLM configuration in Retell
4. Clone this repo
5. Set up Heroku app
6. Configure environment variables
7. Deploy webhook
8. Create Retell agent
9. Point agent webhook to your Heroku URL
10. Test with a call
11. Automate with Salesforce Flow or Zapier

---

## 11. QUESTIONS? DROP THEM BELOW
💬 **Have questions or want to share your results?**
- Comment on the [YouTube video](#) (TBD)
- DM me on Instagram: [@donottakeifallergictorevenue](https://www.instagram.com/donottakeifallergictorevenue/)
- Open an issue on [GitHub](https://github.com/tisa-pixel/rei-lead-qualifier/issues)

---

## 12. RELATED BUILDS
| Build 1 | Build 2 | Build 3 |
|---------|---------|---------|
| **Am I Spam? - Phone Reputation Checker** | **Check Yo Rep - Find Your Elected Officials** | **How I Automated Lead Routing in Salesforce** |
| Check if your DIDs are flagged before campaigns | Civic engagement tool for finding representatives | Smart lead distribution based on capacity and time zones |
| [View Build](https://github.com/tisa-pixel/am-i-spam) | [View Build](https://github.com/tisa-pixel/check-yo-rep) | [View Build] |

---

## Additional Metadata (for SEO / Backend)

**Published:** December 11, 2025
**Author:** Tisa Daniels
**Category:** Real Estate Tech / AI Voice Agents / Sales Automation
**Tags:** #RealEstateInvesting #AIVoiceAgent #RetellAI #SalesAutomation #LeadQualification #Salesforce #TacticalEmpathy #OutboundCalling
**Estimated Read Time:** 18 minutes
**Video Duration:** TBD

---

## Design Notes for Wix Implementation

### Layout Style:
- **Dark background** (charcoal #1B1C1D)
- **High contrast text** (white headings, light gray body)
- **Accent colors:** Blue (#2563eb), Green (#16a34a), Red (#dc2626 for cost savings callouts)
- **Clean, modern, mobile-first**

### Call-to-Action Buttons:
- **Primary CTA** (Clone on GitHub): Purple (#7c3aed)
- **Secondary CTA** (Watch on YouTube): Blue (#2563eb)

### Visual Elements:
- Architecture diagram (Retell → Heroku → Salesforce)
- Cost comparison table (Human SDR vs AI)
- Call flow diagram
- Sample transcript with annotations
- Before/After Salesforce screenshots

---

## Real-World Results

**After 30 days of using Sarah:**

| Metric | Before (Human SDR) | After (Sarah AI) |
|--------|-------------------|------------------|
| Connect Rate | 12% | 18% |
| Speed to Lead | 45 minutes avg | 60 seconds |
| Calls Handled | 40-50/week | 150/week |
| Cost per Qualified Lead | $125 | $8 |
| Hours Worked | 40/week (business hours) | 168/week (24/7) |
| SF Data Quality | 60% complete | 95% complete |
| Monthly Cost | $5,000 | $65 |

**Annual ROI:** $59,000+ saved

---

## Use Cases Beyond REI

This same system works for:
- **B2B Lead Qualification:** SaaS demos, discovery calls
- **Appointment Setting:** Medical offices, consultants
- **Customer Support:** Tier 1 support, FAQ handling
- **Follow-Up Calls:** Nurture sequences, event reminders
- **Surveys & Feedback:** Post-purchase NPS calls

Just change the script and Salesforce fields.

---

## Advanced Customization

### Add More Salesforce Fields

In `app.py`, update the `update_salesforce_lead()` function:

```python
sf_update = {
    'Your_Custom_Field__c': data['extracted_value'],
    # Add as many as you want
}
```

### Change Transfer Number

Update your Retell LLM's `transfer_call` tool configuration.

### Multi-Language Support

Retell supports 15+ languages. Just change the prompt language and voice ID.

### A/B Test Scripts

Clone the agent, modify the script, split traffic 50/50, compare conversion rates.

---

**Template Version:** 1.0
**Created:** December 11, 2025
**Build Time:** 1.75 hours with Claude Code
