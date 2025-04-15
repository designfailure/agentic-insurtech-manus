"""
Fraud detector tool for the Claims Processor agent.
"""
from app.agents.tools.mock_crewai import BaseTool
import re
import json
from datetime import datetime

class FraudDetectorTool:
    """
    Tool for detecting potential fraud in insurance claims.
    """
    def __init__(self):
        """
        Initialize the fraud detector tool.
        """
        # Fraud indicators (simplified model)
        self.fraud_indicators = {
            "timing": {
                "recent_policy": 0.7,  # Policy created within 30 days
                "weekend_claim": 0.3,  # Claim filed on weekend
                "night_claim": 0.4,    # Claim filed at night
                "holiday_claim": 0.5   # Claim filed on holiday
            },
            "content": {
                "vague_description": 0.6,
                "excessive_items": 0.5,
                "high_value_items": 0.4,
                "no_receipts": 0.3,
                "no_photos": 0.5
            },
            "history": {
                "multiple_claims": 0.7,
                "previous_denials": 0.8,
                "policy_changes": 0.5
            },
            "red_flags": {
                "water_damage_no_weather": 0.7,
                "theft_no_police_report": 0.8,
                "fire_no_fire_dept": 0.7,
                "inconsistent_statements": 0.9
            }
        }
    
    def detect_fraud(self, claim_data, policy_data, customer_history):
        """
        Detect potential fraud in an insurance claim.
        
        Args:
            claim_data: Dictionary containing claim details.
            policy_data: Dictionary containing policy details.
            customer_history: Dictionary containing customer claim history.
            
        Returns:
            Dictionary containing fraud detection results.
        """
        # Initialize fraud score
        fraud_score = 0.0
        fraud_indicators_found = []
        
        # Check timing indicators
        if self._check_recent_policy(policy_data):
            fraud_score += self.fraud_indicators["timing"]["recent_policy"]
            fraud_indicators_found.append("Recent policy creation")
        
        if self._check_weekend_claim(claim_data):
            fraud_score += self.fraud_indicators["timing"]["weekend_claim"]
            fraud_indicators_found.append("Claim filed on weekend")
        
        # Check content indicators
        if self._check_vague_description(claim_data):
            fraud_score += self.fraud_indicators["content"]["vague_description"]
            fraud_indicators_found.append("Vague claim description")
        
        if self._check_excessive_items(claim_data):
            fraud_score += self.fraud_indicators["content"]["excessive_items"]
            fraud_indicators_found.append("Excessive number of items claimed")
        
        # Check history indicators
        if self._check_multiple_claims(customer_history):
            fraud_score += self.fraud_indicators["history"]["multiple_claims"]
            fraud_indicators_found.append("Multiple recent claims")
        
        # Check red flags
        if self._check_water_damage_no_weather(claim_data):
            fraud_score += self.fraud_indicators["red_flags"]["water_damage_no_weather"]
            fraud_indicators_found.append("Water damage claim without weather event")
        
        if self._check_theft_no_police_report(claim_data):
            fraud_score += self.fraud_indicators["red_flags"]["theft_no_police_report"]
            fraud_indicators_found.append("Theft claim without police report")
        
        # Normalize fraud score (0-1 range)
        normalized_score = min(fraud_score / 5.0, 1.0)
        
        # Determine fraud risk category
        risk_category = "Low"
        if normalized_score > 0.7:
            risk_category = "High"
        elif normalized_score > 0.3:
            risk_category = "Medium"
        
        # Determine recommended action
        recommended_action = "Process claim normally"
        if risk_category == "High":
            recommended_action = "Escalate for investigation"
        elif risk_category == "Medium":
            recommended_action = "Request additional documentation"
        
        return {
            "fraud_score": normalized_score,
            "risk_category": risk_category,
            "indicators_found": fraud_indicators_found,
            "recommended_action": recommended_action
        }
    
    def _check_recent_policy(self, policy_data):
        """Check if policy was created within 30 days of claim."""
        try:
            policy_start = datetime.strptime(policy_data.get("start_date", ""), "%Y-%m-%d")
            days_active = (datetime.now() - policy_start).days
            return days_active < 30
        except:
            return False
    
    def _check_weekend_claim(self, claim_data):
        """Check if claim was filed on a weekend."""
        try:
            claim_date = datetime.strptime(claim_data.get("report_date", ""), "%Y-%m-%d")
            return claim_date.weekday() >= 5  # 5=Saturday, 6=Sunday
        except:
            return False
    
    def _check_vague_description(self, claim_data):
        """Check if claim description is vague."""
        description = claim_data.get("description", "")
        word_count = len(description.split())
        return word_count < 20
    
    def _check_excessive_items(self, claim_data):
        """Check if claim includes an excessive number of items."""
        items = claim_data.get("items", [])
        return len(items) > 15
    
    def _check_multiple_claims(self, customer_history):
        """Check if customer has multiple recent claims."""
        recent_claims = customer_history.get("recent_claims", 0)
        return recent_claims >= 3
    
    def _check_water_damage_no_weather(self, claim_data):
        """Check for water damage claim without corresponding weather event."""
        description = claim_data.get("description", "").lower()
        has_water_damage = "water damage" in description or "flood" in description
        has_weather_event = "rain" in description or "storm" in description
        return has_water_damage and not has_weather_event
    
    def _check_theft_no_police_report(self, claim_data):
        """Check for theft claim without police report."""
        description = claim_data.get("description", "").lower()
        has_theft = "theft" in description or "stolen" in description
        has_police_report = claim_data.get("police_report", False)
        return has_theft and not has_police_report
    
    def get_tool(self):
        """
        Get the CrewAI tool for fraud detection.
        
        Returns:
            CrewAI BaseTool instance.
        """
        return BaseTool(
            name="fraud_detection_tool",
            description="Detects potential fraud in insurance claims",
            func=self._fraud_detection_tool
        )
    
    def _fraud_detection_tool(self, claim_data_json, policy_data_json, customer_history_json):
        """
        Tool function for fraud detection.
        
        Args:
            claim_data_json: JSON string of claim details.
            policy_data_json: JSON string of policy details.
            customer_history_json: JSON string of customer claim history.
            
        Returns:
            JSON string of fraud detection results.
        """
        try:
            claim_data = json.loads(claim_data_json)
            policy_data = json.loads(policy_data_json)
            customer_history = json.loads(customer_history_json)
            
            results = self.detect_fraud(claim_data, policy_data, customer_history)
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
