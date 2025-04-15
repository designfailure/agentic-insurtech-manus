"""
CrewAI orchestration manager for AGENTIC InsurTech.
"""
from app.agents.mock_crewai import Crew, Agent, Task, Process
from app.config import (
    UNDERWRITING_AGENT_MODEL, 
    CLAIMS_AGENT_MODEL, 
    CUSTOMER_AGENT_MODEL
)
from app.agents.tools.risk_model import RiskModelTool
from app.agents.tools.fraud_detector import FraudDetectorTool
from app.agents.tools.doc_analyzer import DocAnalyzerTool
from app.agents.tools.sentiment_analyzer import SentimentAnalyzerTool
from app.agents.tools.policy_lookup import PolicyLookupTool

class CrewManager:
    """
    Manager class for CrewAI orchestration.
    """
    def __init__(self):
        """
        Initialize the CrewAI manager with agents and tools.
        """
        # Initialize tools
        self.risk_model_tool = RiskModelTool()
        self.fraud_detector_tool = FraudDetectorTool()
        self.doc_analyzer_tool = DocAnalyzerTool()
        self.sentiment_analyzer_tool = SentimentAnalyzerTool()
        self.policy_lookup_tool = PolicyLookupTool()
        
        # Initialize agents
        self.underwriting_agent = self._create_underwriting_agent()
        self.claims_agent = self._create_claims_agent()
        self.customer_agent = self._create_customer_agent()
        
        # Initialize crew
        self.crew = self._create_crew()
    
    def _create_underwriting_agent(self):
        """
        Create the Underwriting Analyzer agent.
        
        Returns:
            CrewAI Agent for underwriting analysis.
        """
        return Agent(
            role="Underwriting Analyzer",
            goal="Assess insurance risks and determine appropriate coverage and pricing",
            backstory="""You are an expert insurance underwriter with years of experience in risk assessment.
            Your job is to analyze images and other data to identify potential risks and determine
            appropriate coverage and pricing for insurance policies.""",
            verbose=True,
            allow_delegation=True,
            tools=[
                self.risk_model_tool.get_tool(),
                self.doc_analyzer_tool.get_tool()
            ],
            llm=UNDERWRITING_AGENT_MODEL
        )
    
    def _create_claims_agent(self):
        """
        Create the Claims Processor agent.
        
        Returns:
            CrewAI Agent for claims processing.
        """
        return Agent(
            role="Claims Processor",
            goal="Process insurance claims efficiently and accurately while detecting potential fraud",
            backstory="""You are a skilled claims adjuster with a keen eye for detail.
            Your job is to process insurance claims quickly and accurately while identifying
            any potential fraud or discrepancies.""",
            verbose=True,
            allow_delegation=True,
            tools=[
                self.fraud_detector_tool.get_tool(),
                self.doc_analyzer_tool.get_tool()
            ],
            llm=CLAIMS_AGENT_MODEL
        )
    
    def _create_customer_agent(self):
        """
        Create the Customer Assistant agent.
        
        Returns:
            CrewAI Agent for customer support.
        """
        return Agent(
            role="Customer Assistant",
            goal="Provide helpful and accurate support to insurance customers",
            backstory="""You are a friendly and knowledgeable customer support specialist.
            Your job is to help customers understand their insurance options, answer their questions,
            and guide them through the insurance process.""",
            verbose=True,
            allow_delegation=True,
            tools=[
                self.sentiment_analyzer_tool.get_tool(),
                self.policy_lookup_tool.get_tool()
            ],
            llm=CUSTOMER_AGENT_MODEL
        )
    
    def _create_crew(self):
        """
        Create the CrewAI crew with all agents.
        
        Returns:
            CrewAI Crew instance.
        """
        return Crew(
            agents=[
                self.underwriting_agent,
                self.claims_agent,
                self.customer_agent
            ],
            tasks=[],
            verbose=2,
            process=Process.sequential
        )
    
    def analyze_risk(self, image_analysis, location):
        """
        Create and execute a risk analysis task.
        
        Args:
            image_analysis: Analysis of the uploaded image.
            location: Customer location.
            
        Returns:
            Risk analysis results.
        """
        task = Task(
            description=f"""
            Analyze the following image analysis and location to determine insurance risks and appropriate coverage:
            
            Image Analysis:
            {image_analysis}
            
            Location:
            {location}
            
            Provide a detailed risk assessment including:
            1. Identified risks
            2. Recommended coverage types
            3. Coverage amounts
            4. Premium calculation
            """,
            agent=self.underwriting_agent,
            expected_output="Detailed risk assessment with coverage recommendations and pricing"
        )
        
        self.crew.tasks = [task]
        result = self.crew.kickoff()
        return result
    
    def process_claim(self, image_analysis, policy_details, claim_description):
        """
        Create and execute a claim processing task.
        
        Args:
            image_analysis: Analysis of the claim image.
            policy_details: Details of the insurance policy.
            claim_description: Description of the claim.
            
        Returns:
            Claim processing results.
        """
        task = Task(
            description=f"""
            Process the following insurance claim:
            
            Image Analysis:
            {image_analysis}
            
            Policy Details:
            {policy_details}
            
            Claim Description:
            {claim_description}
            
            Provide a detailed claim assessment including:
            1. Claim validity
            2. Fraud detection results
            3. Coverage applicability
            4. Recommended payout amount
            5. Next steps
            """,
            agent=self.claims_agent,
            expected_output="Detailed claim assessment with payout recommendation"
        )
        
        self.crew.tasks = [task]
        result = self.crew.kickoff()
        return result
    
    def provide_customer_support(self, customer_query, policy_details=None):
        """
        Create and execute a customer support task.
        
        Args:
            customer_query: Customer's question or request.
            policy_details: Optional policy details for context.
            
        Returns:
            Customer support response.
        """
        policy_context = f"\nPolicy Details:\n{policy_details}" if policy_details else ""
        
        task = Task(
            description=f"""
            Respond to the following customer query:
            
            Customer Query:
            {customer_query}
            {policy_context}
            
            Provide a helpful, accurate, and empathetic response that addresses the customer's needs.
            Include any relevant policy information and next steps.
            """,
            agent=self.customer_agent,
            expected_output="Helpful and accurate customer support response"
        )
        
        self.crew.tasks = [task]
        result = self.crew.kickoff()
        return result
    
    def generate_prevention_plan(self, image_analysis, policy_details):
        """
        Create and execute a prevention plan generation task.
        
        Args:
            image_analysis: Analysis of the customer's property/items.
            policy_details: Details of the insurance policy.
            
        Returns:
            Personalized prevention plan.
        """
        task = Task(
            description=f"""
            Generate a personalized prevention plan based on the following information:
            
            Image Analysis:
            {image_analysis}
            
            Policy Details:
            {policy_details}
            
            Create a detailed prevention plan including:
            1. Identified risk factors
            2. Preventive measures
            3. Safety recommendations
            4. Maintenance tips
            5. Potential benefits (reduced premiums, etc.)
            """,
            agent=self.underwriting_agent,
            expected_output="Detailed personalized prevention plan"
        )
        
        self.crew.tasks = [task]
        result = self.crew.kickoff()
        return result
