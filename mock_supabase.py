"""
Mock implementation of Supabase client for testing purposes.
This file provides a simplified version of the Supabase client to work around
the configuration issues during testing.
"""
import json
from datetime import datetime
import os

class MockSupabaseClient:
    """
    Mock implementation of Supabase client for testing.
    """
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern to ensure only one instance of the client exists.
        """
        if cls._instance is None:
            cls._instance = super(MockSupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        Initialize the mock database with sample data.
        """
        # Create data directory if it doesn't exist
        os.makedirs("/home/ubuntu/agentic-insurtech/tests/mock_db", exist_ok=True)
        
        # Initialize mock database tables
        self.tables = {
            "policies": [],
            "claims": [],
            "agent_activities": [],
            "escalations": []
        }
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """
        Load data from mock database files.
        """
        for table_name in self.tables.keys():
            file_path = f"/home/ubuntu/agentic-insurtech/tests/mock_db/{table_name}.json"
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        self.tables[table_name] = json.load(f)
                except Exception as e:
                    print(f"Error loading {table_name} data: {e}")
    
    def _save_data(self, table_name):
        """
        Save data to mock database files.
        """
        file_path = f"/home/ubuntu/agentic-insurtech/tests/mock_db/{table_name}.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(self.tables[table_name], f, indent=2)
        except Exception as e:
            print(f"Error saving {table_name} data: {e}")
    
    def create_policy(self, policy_data):
        """
        Create a new policy in the mock database.
        
        Args:
            policy_data: Dictionary containing policy data.
            
        Returns:
            Dictionary containing the created policy.
        """
        # Add ID and timestamps
        policy_data["id"] = str(len(self.tables["policies"]) + 1)
        policy_data["created_at"] = datetime.now().isoformat()
        policy_data["updated_at"] = datetime.now().isoformat()
        
        # Add to policies table
        self.tables["policies"].append(policy_data)
        
        # Save to file
        self._save_data("policies")
        
        return policy_data
    
    def create_claim(self, claim_data):
        """
        Create a new claim in the mock database.
        
        Args:
            claim_data: Dictionary containing claim data.
            
        Returns:
            Dictionary containing the created claim.
        """
        # Add ID and timestamps
        claim_data["id"] = str(len(self.tables["claims"]) + 1)
        claim_data["created_at"] = datetime.now().isoformat()
        claim_data["updated_at"] = datetime.now().isoformat()
        
        # Add to claims table
        self.tables["claims"].append(claim_data)
        
        # Save to file
        self._save_data("claims")
        
        return claim_data
    
    def log_agent_activity(self, log_data):
        """
        Log agent activity in the mock database.
        
        Args:
            log_data: Dictionary containing log data.
            
        Returns:
            Dictionary containing the created log.
        """
        # Add ID and timestamps
        log_data["id"] = str(len(self.tables["agent_activities"]) + 1)
        log_data["created_at"] = datetime.now().isoformat()
        
        # Add to agent_activities table
        self.tables["agent_activities"].append(log_data)
        
        # Save to file
        self._save_data("agent_activities")
        
        return log_data
    
    def create_escalation(self, escalation_data):
        """
        Create a new escalation in the mock database.
        
        Args:
            escalation_data: Dictionary containing escalation data.
            
        Returns:
            Dictionary containing the created escalation.
        """
        # Add ID and timestamps
        escalation_data["id"] = str(len(self.tables["escalations"]) + 1)
        escalation_data["created_at"] = datetime.now().isoformat()
        escalation_data["updated_at"] = datetime.now().isoformat()
        
        # Add to escalations table
        self.tables["escalations"].append(escalation_data)
        
        # Save to file
        self._save_data("escalations")
        
        return escalation_data
    
    def get_agent_activity_logs(self):
        """
        Get agent activity logs from the mock database.
        
        Returns:
            List of agent activity logs.
        """
        return self.tables["agent_activities"]
    
    def get_policies(self):
        """
        Get all policies from the mock database.
        
        Returns:
            List of policies.
        """
        return self.tables["policies"]
    
    def get_claims(self):
        """
        Get all claims from the mock database.
        
        Returns:
            List of claims.
        """
        return self.tables["claims"]
    
    def get_policy_by_number(self, policy_number):
        """
        Get a policy by policy number.
        
        Args:
            policy_number: Policy number to look up.
            
        Returns:
            Dictionary containing the policy or None if not found.
        """
        for policy in self.tables["policies"]:
            if policy.get("policy_number") == policy_number:
                return policy
        return None
    
    def get_claim_by_number(self, claim_number):
        """
        Get a claim by claim number.
        
        Args:
            claim_number: Claim number to look up.
            
        Returns:
            Dictionary containing the claim or None if not found.
        """
        for claim in self.tables["claims"]:
            if claim.get("claim_number") == claim_number:
                return claim
        return None

# Create alias for backward compatibility
SupabaseClient = MockSupabaseClient
