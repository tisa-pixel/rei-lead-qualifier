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

Sign up at Retell AI and grab your API key and a phone number for outbound calling. Retell handles all the hard parts: telephony infrastructure, speech recognition, text-to-speech, and they have built-in Claude integration.

The platform also supports warm transfer functionality and webhook events for call lifecycle management - essential for connecting to Salesforce after calls end.

---

### 2. **Create the LLM Configuration**

In the Retell dashboard, create a new LLM configuration using Claude Sonnet 4. Set the temperature to 0.7 for balanced creativity and consistency, with a max of 500 tokens per response to keep answers concise.

Configure dynamic variables for personalization - seller name, property address, company name, and agent name. These get injected into your prompt so Sarah can greet each lead by name and reference their specific property.

---

### 3. **Write the Tactical Empathy Script**

Create your system prompt using Chris Voss-style tactical empathy techniques. The key is making Sarah sound like a helpful neighbor, not a telemarketer. She uses a calm, curious tone - think late-night FM DJ energy.

Structure the conversation flow: disarm with a soft intro, build curiosity with open questions, qualify with tactical questions about motivation/timeline/decision-maker/agent-status, then warm transfer qualified leads. Include words to never use ("Is now a good time?", "Trust me") and techniques like mirroring, labeling, and calibrated "what/how" questions.

---

### 4. **Create Retell Agent**

Use the Retell API to create your agent with the right voice and ambient settings. We use 11labs-Lily for a warm, professional, empathetic tone that works well for real estate.

Add subtle coffee shop ambient sound at low volume - it sounds more human than dead silence. Enable backchannel responses so Sarah says natural "mm-hmm" and "yeah" sounds. Set speech normalization for cleaner output.

---

### 5. **Build Flask Webhook Server**

Create a Python Flask application with a webhook endpoint that Retell calls when conversations end. The server receives the full transcript and call metadata, then processes everything.

The webhook handler does three things: extracts the transcript from Retell's payload, sends it to Claude for interpretation (extracting motivation, timeline, decision-maker status, agent status, and lead quality), then updates Salesforce with the structured data and creates a Task record with the full transcript.

---

### 6. **Implement Lead Scoring**

Build a scoring algorithm that weights different qualification factors. Timeline urgency gets scored (immediately = 100 points, 6+ months = 20 points). Motivation type matters (foreclosure = 100, relocation = 70). No agent and being the decision-maker each add significant points.

Average the scores and classify leads as Hot (80+), Warm (50-79), or Cold (under 50). A lead qualifies for warm transfer only if they hit all criteria: Hot score, timeline within 3 months, is the owner/decision-maker, and has no real estate agent.

---

### 7. **Deploy to Heroku**

Set up your Flask app for Heroku deployment. Create a requirements file listing Flask, Anthropic, simple-salesforce, and gunicorn as dependencies. Add a Procfile that tells Heroku to run gunicorn.

Create your Heroku app, configure environment variables for all your API keys and Salesforce credentials, then push your code. Your webhook is now live at your Heroku URL.

---

### 8. **Configure Retell Webhook**

In the Retell dashboard, go to your agent settings and add your Heroku webhook URL. Enable the call_started and call_ended events so Retell posts to your server when calls begin and finish.

The call_ended event is where the magic happens - that's when you receive the full transcript and can trigger your Salesforce updates.

---

### 9. **Trigger Outbound Calls**

Set up automation to call new leads instantly. You can trigger calls via the Retell API from Zapier, n8n, or a Salesforce Flow. Pass the lead's phone number, your Retell phone number, agent ID, and dynamic variables (name, address).

Include the Salesforce Lead ID in the metadata so your webhook knows which record to update when the call ends. For Salesforce-native automation, create a Record-Triggered Flow that fires on new Lead creation and makes an HTTP callout to Retell.

---

### 10. **Test & Iterate**

Run through your testing checklist: verify Sarah's intro is personalized, check she follows the script through qualification questions, test that warm transfer works for qualified leads, confirm Salesforce updates correctly after hangup, and review transcript accuracy.

Common issues to watch for: if Sarah interrupts too much, lower interruption sensitivity in Retell; if transfers fail, check the transfer_call tool configuration; if SF isn't updating, check your Heroku logs for errors.

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
| **Attempting Contact Cadence** | **Am I Spam? - Phone Reputation Checker** | **Poppy - AE Voice Assistant** |
| 17-touch automated follow-up system in Salesforce | Check if your DIDs are flagged before campaigns | Voice AI that updates Salesforce after appointments |
| [View Build](https://github.com/tisa-pixel/attempting-contact) | [View Build](https://github.com/tisa-pixel/am-i-spam) | [View Build](https://github.com/tisa-pixel/ae-voice-assistant) |

---

## Additional Metadata (for SEO / Backend)

**Published:** December 11, 2025
**Author:** Tisa Daniels
**Category:** Real Estate Tech / AI Voice Agents / Sales Automation
**Tags:** #RealEstateInvesting #AIVoiceAgent #RetellAI #SalesAutomation #LeadQualification #Salesforce #TacticalEmpathy
**Estimated Read Time:** 10 minutes
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

---

**Template Version:** 1.0
**Created:** December 11, 2025
**Build Time:** 1.75 hours with Claude Code
