"""
REI Lead Qualification Agent Configuration
Voice agent for qualifying motivated seller leads
"""

# Agent Identity
AGENT_NAME = "REI Lead Qualifier"
AGENT_DESCRIPTION = "AI voice agent that qualifies motivated seller leads for real estate investors"

# Voice Configuration (Retell AI voices)
VOICE_CONFIG = {
    "voice_id": "eleven_turbo_v2",  # Natural conversational voice
    "voice_speed": 1.0,
    "voice_temperature": 0.7,
}

# Qualification Criteria Weights
QUALIFICATION_WEIGHTS = {
    "timeline": {
        "immediately": 100,
        "within_30_days": 80,
        "1_3_months": 60,
        "3_6_months": 40,
        "6_plus_months": 20,
        "not_sure": 30,
    },
    "motivation": {
        "foreclosure": 100,
        "divorce": 90,
        "inherited": 85,
        "relocation": 70,
        "downsizing": 60,
        "financial": 80,
        "tired_landlord": 75,
        "repairs_needed": 65,
        "just_curious": 10,
    },
    "agent_status": {
        "no_agent": 100,
        "expired_listing": 80,
        "considering": 50,
        "has_agent": 0,  # Disqualify
    },
    "decision_maker": {
        "sole_owner": 100,
        "joint_decision": 70,
        "not_owner": 0,  # Disqualify
    }
}

# Lead Classification Thresholds
LEAD_CLASSIFICATION = {
    "hot": 80,      # Score >= 80: Immediate callback
    "warm": 50,     # Score 50-79: Schedule follow-up
    "cold": 20,     # Score 20-49: Nurture campaign
    "disqualified": 0,  # Score < 20: Remove from list
}

# Salesforce Field Mappings
SF_FIELD_MAPPINGS = {
    "timeline": "Timeframe_to_sell__c",
    "motivation": "Reason_for_Selling__c",
    "has_agent": "Listed_with_a_Realtor__c",
    "asking_price": "Zestimate__c",  # Use as reference
    "call_outcome": "Description",
    "qualification_score": "Rating",  # Hot/Warm/Cold
    "call_notes": "Description",
}

# Call Outcomes for Salesforce Task
CALL_OUTCOMES = {
    "qualified_hot": "Qualified - Hot Lead",
    "qualified_warm": "Qualified - Warm Lead",
    "qualified_cold": "Qualified - Cold Lead",
    "not_interested": "Not Interested",
    "wrong_number": "Wrong Number",
    "no_answer": "No Answer",
    "voicemail": "Left Voicemail",
    "callback_requested": "Callback Requested",
    "disqualified": "Disqualified",
}
