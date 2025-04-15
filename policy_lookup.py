"""
Policy lookup tool for the Customer Assistant agent.
"""
from app.agents.tools.mock_crewai import BaseTool
import json
from datetime import datetime

class PolicyLookupTool:
    """
    Tool for looking up insurance policy details.
    """
    def __init__(self):
        """
        Initialize the policy lookup tool.
        """
        # Sample policy data (would be replaced with database access in production)
        self.sample_policies = {
            "POL-20250101-1234": {
                "policy_number": "POL-20250101-1234",
                "policy_type": "Home Insurance",
                "coverage_amount": 250000.00,
                "premium_amount": 1200.00,
                "start_date": "2025-01-01",
                "end_date": "2026-01-01",
                "status": "Active",
                "policyholder": {
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "phone": "555-123-4567",
                    "address": "123 Main St, Anytown, USA"
                },
                "coverage_details": {
                    "dwelling": 200000.00,
                    "personal_property": 100000.00,
                    "liability": 300000.00,
                    "deductible": 1000.00
                }
            },
            "POL-20250215-5678": {
                "policy_number": "POL-20250215-5678",
                "policy_type": "Auto Insurance",
                "coverage_amount": 50000.00,
                "premium_amount": 800.00,
                "start_date": "2025-02-15",
                "end_date": "2026-02-15",
                "status": "Active",
                "policyholder": {
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "phone": "555-987-6543",
                    "address": "456 Oak Ave, Somewhere, USA"
                },
                "coverage_details": {
                    "liability": 100000.00,
                    "collision": 25000.00,
                    "comprehensive": 25000.00,
                    "deductible": 500.00
                }
            },
            "POL-20250320-9012": {
                "policy_number": "POL-20250320-9012",
                "policy_type": "Renters Insurance",
                "coverage_amount": 30000.00,
                "premium_amount": 300.00,
                "start_date": "2025-03-20",
                "end_date": "2026-03-20",
                "status": "Active",
                "policyholder": {
                    "name": "Bob Johnson",
                    "email": "bob.johnson@example.com",
                    "phone": "555-456-7890",
                    "address": "789 Pine St, Nowhere, USA"
                },
                "coverage_details": {
                    "personal_property": 30000.00,
                    "liability": 100000.00,
                    "loss_of_use": 10000.00,
                    "deductible": 500.00
                }
            }
        }
    
    def lookup_policy(self, policy_number=None, policyholder_name=None, policyholder_email=None):
        """
        Look up policy details by policy number or policyholder information.
        
        Args:
            policy_number: Optional policy number to search for.
            policyholder_name: Optional policyholder name to search for.
            policyholder_email: Optional policyholder email to search for.
            
        Returns:
            Dictionary containing policy details or error message.
        """
        # Look up by policy number (most direct method)
        if policy_number and policy_number in self.sample_policies:
            return {
                "found": True,
                "policy": self.sample_policies[policy_number]
            }
        
        # Look up by policyholder information
        if policyholder_name or policyholder_email:
            matching_policies = []
            
            for policy_id, policy in self.sample_policies.items():
                policyholder = policy.get("policyholder", {})
                
                name_match = (policyholder_name and 
                             policyholder_name.lower() in policyholder.get("name", "").lower())
                
                email_match = (policyholder_email and 
                              policyholder_email.lower() == policyholder.get("email", "").lower())
                
                if name_match or email_match:
                    matching_policies.append(policy)
            
            if matching_policies:
                return {
                    "found": True,
                    "policies": matching_policies
                }
        
        # No matching policy found
        return {
            "found": False,
            "error": "No matching policy found"
        }
    
    def get_coverage_summary(self, policy_number):
        """
        Get a summary of policy coverage.
        
        Args:
            policy_number: The policy number to look up.
            
        Returns:
            Dictionary containing coverage summary or error message.
        """
        if policy_number not in self.sample_policies:
            return {
                "found": False,
                "error": "Policy not found"
            }
        
        policy = self.sample_policies[policy_number]
        
        # Calculate days remaining on policy
        try:
            end_date = datetime.strptime(policy["end_date"], "%Y-%m-%d")
            days_remaining = (end_date - datetime.now()).days
        except:
            days_remaining = "Unknown"
        
        # Create coverage summary
        coverage_details = policy.get("coverage_details", {})
        
        summary = {
            "found": True,
            "policy_number": policy["policy_number"],
            "policy_type": policy["policy_type"],
            "status": policy["status"],
            "total_coverage": policy["coverage_amount"],
            "premium": policy["premium_amount"],
            "days_remaining": days_remaining,
            "coverage_breakdown": coverage_details,
            "deductible": coverage_details.get("deductible", "Unknown")
        }
        
        return summary
    
    def get_tool(self):
        """
        Get the CrewAI tool for policy lookup.
        
        Returns:
            CrewAI BaseTool instance.
        """
        return BaseTool(
            name="policy_lookup_tool",
            description="Looks up insurance policy details by policy number or policyholder information",
            func=self._policy_lookup_tool
        )
    
    def _policy_lookup_tool(self, policy_number=None, policyholder_name=None, policyholder_email=None):
        """
        Tool function for policy lookup.
        
        Args:
            policy_number: Optional policy number to search for.
            policyholder_name: Optional policyholder name to search for.
            policyholder_email: Optional policyholder email to search for.
            
        Returns:
            JSON string of policy lookup results.
        """
        try:
            if policy_number and policy_number.startswith("summary:"):
                # Get coverage summary
                actual_policy_number = policy_number.replace("summary:", "")
                results = self.get_coverage_summary(actual_policy_number)
            else:
                # Regular policy lookup
                results = self.lookup_policy(policy_number, policyholder_name, policyholder_email)
                
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
