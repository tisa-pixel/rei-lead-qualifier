"""
REI Lead Qualifier - Retell Webhook Server
Deployable to Heroku with Salesforce REST API integration
Purpose: New Lead Call Back / Attempting Call Back - calling leads we haven't spoken to yet
"""

import os
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
RETELL_WEBHOOK_SECRET = os.getenv("RETELL_WEBHOOK_SECRET", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Salesforce credentials
SF_USERNAME = os.getenv("SF_USERNAME", "")
SF_PASSWORD = os.getenv("SF_PASSWORD", "")
SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN", "")
SF_DOMAIN = os.getenv("SF_DOMAIN", "login")  # 'login' for prod, 'test' for sandbox

# Scoring weights
TIMELINE_SCORES = {
    "immediately": 100,
    "within_30_days": 80,
    "1_3_months": 60,
    "3_6_months": 40,
    "6_plus_months": 20,
    "not_sure": 30,
}

MOTIVATION_SCORES = {
    "foreclosure": 100,
    "divorce": 90,
    "inherited": 85,
    "relocation": 70,
    "downsizing": 60,
    "repairs_needed": 65,
    "tired_landlord": 80,
    "vacant": 70,
    "other": 40,
}

CLASSIFICATION_THRESHOLDS = {
    "hot": 80,
    "warm": 50,
    "cold": 20,
}

# Salesforce connection (lazy loaded)
_sf_client = None


def get_sf_client():
    """Get or create Salesforce client"""
    global _sf_client
    if _sf_client is None and SF_USERNAME and SF_PASSWORD:
        try:
            from simple_salesforce import Salesforce
            _sf_client = Salesforce(
                username=SF_USERNAME,
                password=SF_PASSWORD,
                security_token=SF_SECURITY_TOKEN,
                domain=SF_DOMAIN
            )
            print("Salesforce connected successfully")
        except Exception as e:
            print(f"Salesforce connection failed: {e}")
            _sf_client = None
    return _sf_client


def calculate_score(answers: dict) -> int:
    """Calculate qualification score from answers"""
    score = 0
    count = 0

    timeline = answers.get("timeline", "not_sure")
    if timeline in TIMELINE_SCORES:
        score += TIMELINE_SCORES[timeline]
        count += 1

    motivation = answers.get("motivation", "").lower() if answers.get("motivation") else ""
    for key, value in MOTIVATION_SCORES.items():
        if key in motivation:
            score += value
            count += 1
            break
    else:
        score += 40
        count += 1

    has_agent = answers.get("has_agent", False)
    score += 0 if has_agent else 100
    count += 1

    decision_maker = answers.get("decision_maker", "")
    if decision_maker in ["sole_owner", "sole_decision"]:
        score += 100
    elif decision_maker in ["co_owner", "joint_decision"]:
        score += 70
    else:
        score += 40
    count += 1

    return int(score / count) if count > 0 else 50


def classify_lead(score: int) -> str:
    """Classify lead based on score"""
    if score >= CLASSIFICATION_THRESHOLDS["hot"]:
        return "Hot"
    elif score >= CLASSIFICATION_THRESHOLDS["warm"]:
        return "Warm"
    elif score >= CLASSIFICATION_THRESHOLDS["cold"]:
        return "Cold"
    else:
        return "Disqualified"


def interpret_call_with_ai(transcript: str, call_summary: str = "") -> dict:
    """Use Claude to intelligently interpret the call and extract structured data"""
    if not ANTHROPIC_API_KEY or not transcript:
        return {}

    prompt = f"""Analyze this sales call transcript and extract the following information.
Return ONLY a valid JSON object with these fields (use null if not mentioned):

{{
    "timeline": "immediately" | "within_30_days" | "1_3_months" | "3_6_months" | "6_plus_months" | "not_sure",
    "motivation": "foreclosure" | "divorce" | "inherited" | "relocation" | "downsizing" | "repairs_needed" | "tired_landlord" | "vacant" | "financial_hardship" | "other",
    "motivation_notes": "brief description of their situation in 1-2 sentences",
    "has_agent": true | false,
    "decision_maker": "sole_owner" | "co_owner" | "not_owner",
    "price_expectation": number or null,
    "property_condition": "excellent" | "good" | "fair" | "poor" | "unknown",
    "property_notes": "any details about the property mentioned",
    "is_motivated": true | false,
    "next_step": "transfer_to_setter" | "schedule_callback" | "not_interested" | "needs_followup" | "disqualified",
    "call_summary": "2-3 sentence summary of the call outcome",
    "obstacles": "any objections or concerns they raised",
    "call_disposition": "connected" | "voicemail" | "no_answer" | "wrong_number" | "disconnected",
    "how_heard_about_us": "referral" | "google" | "facebook" | "mailer" | "driving_for_dollars" | "other" | null,
    "callback_datetime": "ISO datetime string if they requested a specific callback time, otherwise null",
    "is_qualified": true | false,
    "qualifying_notes": "brief notes on why qualified or not qualified"
}}

IMPORTANT: Set is_qualified=true if ALL of these are met:
1. They have a need/pain/motivation to sell
2. They have a timeframe (not 6+ months out)
3. They are the decision maker (sole_owner or co_owner)
4. They do NOT have an agent listed

If is_qualified=true, set next_step="transfer_to_setter"

Call Summary: {call_summary}

Transcript:
{transcript[:8000]}
"""

    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            content = result.get("content", [{}])[0].get("text", "{}")
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print(f"AI interpretation error: {e}")

    return {}


def update_salesforce_lead(lead_id: str, data: dict) -> bool:
    """Update Salesforce lead with interpreted data using REST API"""
    sf = get_sf_client()
    if not sf or not lead_id:
        print(f"SF client: {bool(sf)}, lead_id: {lead_id}")
        return False

    update_fields = {}

    # Timeline
    if data.get("timeline"):
        timeline_map = {
            "immediately": "Immediate",
            "within_30_days": "30 Days",
            "1_3_months": "1-3 Months",
            "3_6_months": "3-6 Months",
            "6_plus_months": "6+ Months",
            "not_sure": "Not Sure",
        }
        update_fields["Timeframe_to_sell__c"] = timeline_map.get(data["timeline"], "Not Sure")

    # Reason for Selling - multipicklist field
    # Valid values: Divorce, Financial Stress, Inherited Property, Condition
    if data.get("motivation"):
        reason_map = {
            "divorce": "Divorce",
            "inherited": "Inherited Property",
            "foreclosure": "Financial Stress",
            "financial_hardship": "Financial Stress",
            "repairs_needed": "Condition",
            "condition": "Condition",
        }
        reason_value = reason_map.get(data["motivation"].lower())
        if reason_value:
            update_fields["Reason_for_Selling__c"] = reason_value

    # Motivation__c is Hot/Warm/Cold (motivation LEVEL, not reason)
    # Set based on whether transferred to Lynn
    if data.get("transferred_to_lynn") or data.get("next_step") == "transfer_to_setter":
        update_fields["Motivation__c"] = "Warm"  # Transferred = Warm status
    elif data.get("is_qualified"):
        update_fields["Motivation__c"] = "Hot"
    elif data.get("classification"):
        update_fields["Motivation__c"] = data["classification"]  # Hot/Warm/Cold

    # Reason for Selling Notes - put the AI summary here!
    # Field is only 255 chars, so prioritize call_summary
    if data.get("call_summary"):
        update_fields["Reason_for_Selling_Notes__c"] = data["call_summary"][:255]
    elif data.get("motivation_notes"):
        update_fields["Reason_for_Selling_Notes__c"] = data["motivation_notes"][:255]

    # Agent status
    if "has_agent" in data:
        update_fields["Listed_with_a_Realtor__c"] = "Yes" if data["has_agent"] else "No"

    # Rating (standard field)
    if data.get("classification"):
        update_fields["Rating"] = data["classification"]

    # Property condition
    if data.get("property_condition") and data["property_condition"] != "unknown":
        condition_map = {"excellent": "Excellent", "good": "Good", "fair": "Fair", "poor": "Poor"}
        if data["property_condition"] in condition_map:
            update_fields["Property_Condition__c"] = condition_map[data["property_condition"]]

    # Property notes
    if data.get("property_notes"):
        update_fields["Property_Insights__c"] = data["property_notes"][:500]

    # Obstacles
    if data.get("obstacles"):
        update_fields["Obstacle_to_Setting_appointment__c"] = data["obstacles"][:500]

    # Status update based on transfer/qualification
    if data.get("transferred_to_lynn") or data.get("next_step") == "transfer_to_setter":
        update_fields["Status"] = "Warm"  # Transferred to Lynn = Warm
    elif data.get("is_qualified"):
        update_fields["Status"] = "Qualified"
    elif data.get("next_step") == "not_interested":
        update_fields["Status"] = "Unqualified"

    # Connected with lead - always true if we processed the call
    update_fields["Connected_with_Lead__c"] = True

    if not update_fields:
        print("No fields to update")
        return False

    print(f"Attempting to update Lead {lead_id} with fields: {list(update_fields.keys())}")

    try:
        sf.Lead.update(lead_id, update_fields)
        print(f"Salesforce Lead updated: {lead_id}")
        return True
    except Exception as e:
        print(f"SF Lead update error: {e}")
        # Try field by field to identify which one fails
        successful_fields = {}
        for field, value in update_fields.items():
            try:
                sf.Lead.update(lead_id, {field: value})
                successful_fields[field] = value
                print(f"  Updated {field} successfully")
            except Exception as field_error:
                print(f"  Failed to update {field}: {field_error}")
        return len(successful_fields) > 0


def create_call_activity(lead_id: str, data: dict) -> bool:
    """Create a Call activity (Task) in Salesforce with transcript and recording"""
    sf = get_sf_client()
    if not sf or not lead_id:
        return False

    # Build description with full details
    description_parts = [
        "=== AI QUALIFICATION CALL ===",
        "",
        f"Score: {data.get('score', 0)}/100",
        f"Classification: {data.get('classification', 'Unknown')}",
        f"Duration: {data.get('duration', 0)} seconds",
        "",
        "--- EXTRACTED INFO ---",
        f"Timeline: {data.get('timeline', 'Not provided')}",
        f"Motivation: {data.get('motivation', 'Not provided')}",
        f"Has Agent: {'Yes' if data.get('has_agent') else 'No'}",
        f"Decision Maker: {data.get('decision_maker', 'Unknown')}",
        f"Property Condition: {data.get('property_condition', 'Unknown')}",
        f"Next Step: {data.get('next_step', 'Unknown')}",
        "",
        "--- AI SUMMARY ---",
        f"{data.get('call_summary', 'No summary available')}",
        "",
    ]

    # Add recording link if available
    if data.get("recording_url"):
        description_parts.append("--- RECORDING ---")
        description_parts.append(data["recording_url"])
        description_parts.append("")

    # Add transcript
    if data.get("transcript"):
        description_parts.append("--- FULL TRANSCRIPT ---")
        transcript = data["transcript"][:25000]
        description_parts.append(transcript)

    description = "\n".join(description_parts)[:32000]

    # Determine subject and priority
    classification = data.get("classification", "Unknown")
    subject = f"AI Qualification Call - {classification}"
    priority = "High" if classification == "Hot" else "Normal"

    task_data = {
        "WhoId": lead_id,
        "Subject": subject,
        "Priority": priority,
        "Status": "Completed",
        "Type": "Call",
        "CallType": "Outbound",
        "Description": description,
    }

    # Add call duration if available
    duration = data.get("duration", 0)
    if duration > 0:
        task_data["CallDurationInSeconds"] = duration

    try:
        result = sf.Task.create(task_data)
        print(f"Call Activity created: {result.get('id')}")
        return True
    except Exception as e:
        print(f"Call Activity creation error: {e}")
        # Try without CallDurationInSeconds
        try:
            task_data.pop("CallDurationInSeconds", None)
            result = sf.Task.create(task_data)
            print(f"Call Activity created (fallback): {result.get('id')}")
            return True
        except Exception as e2:
            print(f"Call Activity fallback error: {e2}")
            return False


def extract_answers_from_analysis(call_analysis: dict) -> dict:
    """Extract structured answers from Retell call analysis (fallback if AI unavailable)"""
    answers = {}

    if not call_analysis:
        return answers

    custom_data = call_analysis.get("custom_analysis_data", {})
    if custom_data:
        return custom_data

    summary = call_analysis.get("call_summary", "").lower()

    if "immediate" in summary or "asap" in summary or "right away" in summary:
        answers["timeline"] = "immediately"
    elif "30 day" in summary or "month" in summary:
        answers["timeline"] = "within_30_days"
    elif "3 month" in summary or "few months" in summary:
        answers["timeline"] = "1_3_months"

    for motivation in MOTIVATION_SCORES.keys():
        if motivation.replace("_", " ") in summary:
            answers["motivation"] = motivation
            break

    answers["has_agent"] = "realtor" in summary or "agent" in summary or "listed" in summary

    return answers


@app.route("/webhook/retell", methods=["POST"])
def retell_webhook():
    """Main Retell webhook endpoint"""
    payload = request.json
    event_type = payload.get("event", "unknown")
    call_data = payload.get("call", {})

    call_id = call_data.get("call_id", "")
    metadata = call_data.get("metadata", {})
    lead_id = metadata.get("lead_id", "")

    print(f"Webhook received: {event_type} for call {call_id}")

    if event_type == "call_started":
        print(f"  Call started - Lead: {lead_id}")
        return jsonify({"status": "acknowledged"}), 200

    elif event_type == "call_ended":
        duration = call_data.get("call_duration_seconds", 0)
        reason = call_data.get("disconnection_reason", "unknown")
        print(f"  Call ended - Duration: {duration}s, Reason: {reason}")
        return jsonify({"status": "acknowledged", "duration": duration}), 200

    elif event_type == "call_analyzed":
        call_analysis = call_data.get("call_analysis", {})
        transcript = call_data.get("transcript", "")
        recording_url = call_data.get("recording_url", "")
        duration = call_data.get("call_duration_seconds", 0)
        call_summary = call_analysis.get("call_summary", "") if call_analysis else ""

        # Use AI to interpret the call
        ai_interpretation = {}
        if ANTHROPIC_API_KEY and transcript:
            print("  Using AI to interpret call...")
            ai_interpretation = interpret_call_with_ai(transcript, call_summary)
            print(f"  AI interpretation: {json.dumps(ai_interpretation, indent=2)}")

        # Fall back to basic extraction if AI fails
        if not ai_interpretation:
            ai_interpretation = extract_answers_from_analysis(call_analysis)

        # Calculate score and classification
        score = calculate_score(ai_interpretation)
        classification = classify_lead(score)

        print(f"  Score: {score}/100, Classification: {classification}")

        # Merge all data
        update_data = {
            **ai_interpretation,
            "classification": classification,
            "score": score,
            "duration": duration,
            "transcript": transcript,
            "recording_url": recording_url,
            "call_summary": ai_interpretation.get("call_summary", call_summary),
        }

        # Update Salesforce Lead and create Call Activity
        sf_updated = False
        activity_created = False
        if lead_id:
            sf_updated = update_salesforce_lead(lead_id, update_data)
            activity_created = create_call_activity(lead_id, update_data)
            print(f"  SF Lead Updated: {sf_updated}, Call Activity Created: {activity_created}")
        else:
            print("  No lead_id in metadata - skipping SF updates")

        return jsonify({
            "status": "processed",
            "call_id": call_id,
            "lead_id": lead_id,
            "score": score,
            "classification": classification,
            "ai_interpreted": bool(ai_interpretation),
            "sf_updated": sf_updated,
            "activity_created": activity_created,
        }), 200

    else:
        print(f"  Unknown event type: {event_type}")
        return jsonify({"status": "ignored"}), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    sf = get_sf_client()
    return jsonify({
        "status": "healthy",
        "service": "rei-qualifier-webhook",
        "ai_enabled": bool(ANTHROPIC_API_KEY),
        "sf_connected": sf is not None,
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


@app.route("/", methods=["GET"])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "REI Lead Qualifier Webhook",
        "endpoints": {
            "/webhook/retell": "POST - Retell webhook events",
            "/health": "GET - Health check",
        }
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

