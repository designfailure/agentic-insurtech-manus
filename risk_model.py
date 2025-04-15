"""
Risk model tool for the Underwriting Analyzer agent.
"""
from app.agents.tools.mock_crewai import BaseTool
import numpy as np

class RiskModelTool:
    """
    Tool for assessing insurance risks based on property and location data.
    """
    def __init__(self):
        """
        Initialize the risk model tool.
        """
        # Risk factors by category (simplified model)
        self.property_risk_factors = {
            "electronics": 1.2,
            "jewelry": 1.5,
            "art": 1.3,
            "furniture": 1.1,
            "appliances": 1.15,
            "sports_equipment": 1.05,
            "musical_instruments": 1.25
        }
        
        self.location_risk_factors = {
            "flood_zone": 1.4,
            "high_crime": 1.3,
            "wildfire_prone": 1.35,
            "hurricane_prone": 1.45,
            "earthquake_prone": 1.5,
            "urban": 1.1,
            "suburban": 1.0,
            "rural": 0.95
        }
    
    def assess_risk(self, items, location_factors):
        """
        Assess insurance risk based on items and location factors.
        
        Args:
            items: Dictionary of item categories and counts.
            location_factors: List of location risk factors.
            
        Returns:
            Dictionary containing risk assessment results.
        """
        # Calculate base risk score
        base_risk = 1.0
        
        # Add item risk factors
        item_risk = 0
        total_items = 0
        
        for item_category, count in items.items():
            risk_factor = self.property_risk_factors.get(item_category.lower(), 1.0)
            item_risk += risk_factor * count
            total_items += count
        
        # Normalize item risk
        if total_items > 0:
            item_risk = item_risk / total_items
        
        # Add location risk factors
        location_risk = 1.0
        for factor in location_factors:
            if factor.lower() in self.location_risk_factors:
                location_risk *= self.location_risk_factors[factor.lower()]
        
        # Calculate overall risk score
        overall_risk = base_risk * item_risk * location_risk
        
        # Determine risk category
        risk_category = "Medium"
        if overall_risk < 1.0:
            risk_category = "Low"
        elif overall_risk > 1.5:
            risk_category = "High"
        
        # Calculate recommended coverage
        base_coverage = 50000
        per_item_coverage = 1000
        total_coverage = base_coverage + (total_items * per_item_coverage)
        adjusted_coverage = total_coverage * overall_risk
        
        # Calculate premium
        annual_premium = adjusted_coverage * 0.02
        monthly_premium = annual_premium / 12
        
        return {
            "risk_score": overall_risk,
            "risk_category": risk_category,
            "recommended_coverage": adjusted_coverage,
            "annual_premium": annual_premium,
            "monthly_premium": monthly_premium,
            "item_risk_contribution": item_risk,
            "location_risk_contribution": location_risk
        }
    
    def get_tool(self):
        """
        Get the CrewAI tool for risk assessment.
        
        Returns:
            CrewAI BaseTool instance.
        """
        return BaseTool(
            name="risk_assessment_tool",
            description="Assesses insurance risks based on property items and location factors",
            func=self._risk_assessment_tool
        )
    
    def _risk_assessment_tool(self, items_json, location_factors_json):
        """
        Tool function for risk assessment.
        
        Args:
            items_json: JSON string of item categories and counts.
            location_factors_json: JSON string of location risk factors.
            
        Returns:
            JSON string of risk assessment results.
        """
        import json
        
        try:
            items = json.loads(items_json)
            location_factors = json.loads(location_factors_json)
            
            results = self.assess_risk(items, location_factors)
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
