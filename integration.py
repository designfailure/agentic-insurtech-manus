"""
Integration module to connect frontend UI with backend agents.
"""
from app.agents.underwriting import UnderwritingAnalyzer
from app.agents.claims import ClaimsProcessor
from app.agents.customer import CustomerAssistant
from app.vision.image_processor import ImageProcessor
from app.database.supabase_client import SupabaseClient
import os
import json
from datetime import datetime

class AgentIntegration:
    """
    Integration class to connect frontend UI with backend agents.
    """
    def __init__(self):
        """
        Initialize the agent integration with all required agents.
        """
        self.underwriting_agent = UnderwritingAnalyzer()
        self.claims_agent = ClaimsProcessor()
        self.customer_agent = CustomerAssistant()
        self.image_processor = ImageProcessor()
        self.db_client = SupabaseClient()
        
        # Create necessary directories
        os.makedirs("static/uploads", exist_ok=True)
        os.makedirs("static/templates/policies", exist_ok=True)
    
    def analyze_risk(self, image_path, location):
        """
        Analyze risk using the Underwriting Analyzer agent.
        
        Args:
            image_path: Path to the uploaded image.
            location: Customer location.
            
        Returns:
            Risk analysis results.
        """
        return self.underwriting_agent.analyze_risk_from_image(image_path, location)
    
    def generate_policy(self, customer_info, coverage_details):
        """
        Generate a policy document using the Underwriting Analyzer agent.
        
        Args:
            customer_info: Dictionary containing customer information.
            coverage_details: Dictionary containing coverage details.
            
        Returns:
            Policy document and metadata.
        """
        return self.underwriting_agent.generate_policy_document(customer_info, coverage_details)
    
    def generate_prevention_plan(self, image_analysis, location):
        """
        Generate a prevention plan using the Underwriting Analyzer agent.
        
        Args:
            image_analysis: Analysis of the uploaded image.
            location: Customer location.
            
        Returns:
            Prevention plan.
        """
        return self.underwriting_agent.generate_prevention_plan(image_analysis, location)
    
    def process_claim(self, image_path, policy_number, claim_description):
        """
        Process a claim using the Claims Processor agent.
        
        Args:
            image_path: Path to the claim image.
            policy_number: Policy number for the claim.
            claim_description: Description of the claim.
            
        Returns:
            Claim assessment results.
        """
        return self.claims_agent.process_claim(image_path, policy_number, claim_description)
    
    def handle_customer_query(self, query, policy_number=None):
        """
        Handle a customer query using the Customer Assistant agent.
        
        Args:
            query: Customer's question or request.
            policy_number: Optional policy number for context.
            
        Returns:
            Response to the query.
        """
        return self.customer_agent.handle_customer_query(query, policy_number)
    
    def provide_policy_information(self, policy_number=None, policyholder_name=None, policyholder_email=None):
        """
        Provide policy information using the Customer Assistant agent.
        
        Args:
            policy_number: Optional policy number to look up.
            policyholder_name: Optional policyholder name to look up.
            policyholder_email: Optional policyholder email to look up.
            
        Returns:
            Policy information.
        """
        return self.customer_agent.provide_policy_information(policy_number, policyholder_name, policyholder_email)
    
    def escalate_to_human(self, query, sentiment_result, policy_number=None):
        """
        Escalate a customer query to a human agent using the Customer Assistant agent.
        
        Args:
            query: Customer's question or request.
            sentiment_result: Sentiment analysis result.
            policy_number: Optional policy number for context.
            
        Returns:
            Escalation details.
        """
        return self.customer_agent.escalate_to_human(query, sentiment_result, policy_number)
    
    def get_agent_performance(self):
        """
        Get performance metrics for all agents.
        
        Returns:
            Dictionary containing agent performance metrics.
        """
        try:
            # Get agent activity logs from database
            agent_logs = self.db_client.get_agent_activity_logs()
            
            # Calculate performance metrics
            underwriting_metrics = self._calculate_agent_metrics(agent_logs, "Underwriting Analyzer")
            claims_metrics = self._calculate_agent_metrics(agent_logs, "Claims Processor")
            customer_metrics = self._calculate_agent_metrics(agent_logs, "Customer Assistant")
            
            return {
                "underwriting": underwriting_metrics,
                "claims": claims_metrics,
                "customer": customer_metrics,
                "system_health": self._get_system_health()
            }
        except Exception as e:
            print(f"Error getting agent performance: {e}")
            return {
                "error": str(e)
            }
    
    def _calculate_agent_metrics(self, logs, agent_type):
        """
        Calculate performance metrics for an agent.
        
        Args:
            logs: Agent activity logs.
            agent_type: Type of agent.
            
        Returns:
            Dictionary containing agent metrics.
        """
        # Filter logs for this agent
        agent_logs = [log for log in logs if log.get("agent_type") == agent_type]
        
        if not agent_logs:
            return {
                "success_rate": 0,
                "total_tasks": 0,
                "avg_time": 0,
                "recent_activities": []
            }
        
        # Calculate metrics
        total_tasks = len(agent_logs)
        successful_tasks = len([log for log in agent_logs if log.get("success", False)])
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Calculate average execution time
        execution_times = [log.get("execution_time", 0) for log in agent_logs]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Get recent activities
        recent_activities = sorted(agent_logs, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        
        return {
            "success_rate": success_rate,
            "total_tasks": total_tasks,
            "avg_time": avg_time,
            "recent_activities": recent_activities
        }
    
    def _get_system_health(self):
        """
        Get system health metrics.
        
        Returns:
            Dictionary containing system health metrics.
        """
        # Simplified system health metrics
        return {
            "agent_coordination": "Optimal",
            "api_latency": "Moderate",
            "memory_usage": "Good",
            "error_rate": "Low"
        }
    
    def save_uploaded_image(self, image_data, filename):
        """
        Save an uploaded image to the uploads directory.
        
        Args:
            image_data: Image data.
            filename: Original filename.
            
        Returns:
            Path to the saved image.
        """
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        save_path = os.path.join("static/uploads", unique_filename)
        
        # Save the image
        with open(save_path, "wb") as f:
            f.write(image_data)
        
        return save_path
    
    def save_policy_document(self, policy_document, policy_number):
        """
        Save a policy document to the templates directory.
        
        Args:
            policy_document: Policy document text.
            policy_number: Policy number.
            
        Returns:
            Path to the saved document.
        """
        # Generate filename
        filename = f"{policy_number}.md"
        save_path = os.path.join("static/templates/policies", filename)
        
        # Save the document
        with open(save_path, "w") as f:
            f.write(policy_document)
        
        return save_path
