"""
Customer Assistant agent implementation.
"""
from app.agents.tools.sentiment_analyzer import SentimentAnalyzerTool
from app.agents.tools.policy_lookup import PolicyLookupTool
from app.database.supabase_client import SupabaseClient
from datetime import datetime
import json
import re

class CustomerAssistant:
    """
    Customer Assistant agent for providing customer support.
    """
    def __init__(self):
        """
        Initialize the Customer Assistant agent with required tools.
        """
        self.sentiment_analyzer = SentimentAnalyzerTool()
        self.policy_lookup = PolicyLookupTool()
        self.db_client = SupabaseClient()
    
    def handle_customer_query(self, query, policy_number=None):
        """
        Handle a customer query.
        
        Args:
            query: Customer's question or request.
            policy_number: Optional policy number for context.
            
        Returns:
            Dictionary containing response.
        """
        start_time = datetime.now()
        
        try:
            # Analyze sentiment
            sentiment_result = self._analyze_sentiment(query)
            
            # Categorize query
            query_category = self._categorize_query(query)
            
            # Get policy details if provided
            policy_details = None
            if policy_number:
                policy_details = self._get_policy_details(policy_number)
            
            # Generate response
            response = self._generate_response(query, query_category, sentiment_result, policy_details)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Customer Query Handling", 
                                    {"query": query, "policy_number": policy_number},
                                    {"response": response, "sentiment": sentiment_result["sentiment"]},
                                    True,
                                    execution_time)
            
            return {
                "success": True,
                "response": response,
                "sentiment": sentiment_result,
                "query_category": query_category,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Customer Query Handling", 
                                    {"query": query, "policy_number": policy_number},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def provide_policy_information(self, policy_number=None, policyholder_name=None, policyholder_email=None):
        """
        Provide information about a policy.
        
        Args:
            policy_number: Optional policy number to look up.
            policyholder_name: Optional policyholder name to look up.
            policyholder_email: Optional policyholder email to look up.
            
        Returns:
            Dictionary containing policy information.
        """
        start_time = datetime.now()
        
        try:
            # Look up policy
            lookup_result = self._lookup_policy(policy_number, policyholder_name, policyholder_email)
            
            # Format policy information
            if lookup_result.get("found", False):
                if "policy" in lookup_result:
                    # Single policy found
                    policy_info = self._format_policy_info(lookup_result["policy"])
                elif "policies" in lookup_result:
                    # Multiple policies found
                    policies = lookup_result["policies"]
                    if len(policies) == 1:
                        policy_info = self._format_policy_info(policies[0])
                    else:
                        policy_info = self._format_multiple_policies_info(policies)
            else:
                policy_info = "No policy found with the provided information. Please check the details and try again."
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Policy Information Lookup", 
                                    {"policy_number": policy_number, "policyholder_name": policyholder_name, "policyholder_email": policyholder_email},
                                    {"found": lookup_result.get("found", False)},
                                    lookup_result.get("found", False),
                                    execution_time)
            
            return {
                "success": True,
                "policy_info": policy_info,
                "found": lookup_result.get("found", False),
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Policy Information Lookup", 
                                    {"policy_number": policy_number, "policyholder_name": policyholder_name, "policyholder_email": policyholder_email},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def escalate_to_human(self, query, sentiment_result, policy_number=None):
        """
        Escalate a customer query to a human agent.
        
        Args:
            query: Customer's question or request.
            sentiment_result: Sentiment analysis result.
            policy_number: Optional policy number for context.
            
        Returns:
            Dictionary containing escalation details.
        """
        start_time = datetime.now()
        
        try:
            # Determine priority based on sentiment
            priority = "Medium"
            if sentiment_result["sentiment"] == "negative" and sentiment_result["sentiment_score"] < -0.5:
                priority = "High"
            elif sentiment_result["sentiment"] == "positive" and sentiment_result["sentiment_score"] > 0.5:
                priority = "Low"
            
            # Generate escalation ID
            escalation_id = f"ESC-{datetime.now().strftime('%Y%m%d')}-{hash(query) % 10000:04d}"
            
            # Create escalation record
            escalation_data = {
                "escalation_id": escalation_id,
                "query": query,
                "policy_number": policy_number,
                "priority": priority,
                "sentiment": sentiment_result["sentiment"],
                "sentiment_score": sentiment_result["sentiment_score"],
                "status": "Pending",
                "created_at": datetime.now().isoformat()
            }
            
            # Save escalation to database
            try:
                self.db_client.create_escalation(escalation_data)
            except Exception as db_error:
                print(f"Database error: {db_error}")
            
            # Generate response message
            response = f"""
Your query has been escalated to a human agent. A customer service representative will contact you shortly.

Escalation ID: {escalation_id}
Priority: {priority}

Thank you for your patience.
            """
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Query Escalation", 
                                    {"query": query, "policy_number": policy_number, "sentiment": sentiment_result},
                                    {"escalation_id": escalation_id, "priority": priority},
                                    True,
                                    execution_time)
            
            return {
                "success": True,
                "response": response,
                "escalation_id": escalation_id,
                "priority": priority,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Query Escalation", 
                                    {"query": query, "policy_number": policy_number, "sentiment": sentiment_result},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def _analyze_sentiment(self, text):
        """
        Analyze sentiment in text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Sentiment analysis result.
        """
        try:
            # Call the sentiment analyzer tool
            sentiment_result_json = self.sentiment_analyzer._sentiment_analysis_tool(text)
            
            # Parse the result
            sentiment_result = json.loads(sentiment_result_json)
            
            return sentiment_result
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "emotions": {},
                "key_phrases": []
            }
    
    def _categorize_query(self, query):
        """
        Categorize a customer query.
        
        Args:
            query: Customer's question or request.
            
        Returns:
            Query category.
        """
        query_lower = query.lower()
        
        # Define category keywords
        categories = {
            "policy_info": ["policy", "coverage", "covered", "insured", "premium", "deductible"],
            "claim_status": ["claim", "status", "payment", "reimbursement", "approved", "denied", "process"],
            "billing": ["bill", "payment", "pay", "invoice", "charge", "fee", "cost", "price", "expensive"],
            "technical_support": ["website", "app", "login", "password", "reset", "account", "access", "error"],
            "coverage_question": ["cover", "covered", "include", "protect", "damage", "loss", "theft", "accident"],
            "complaint": ["unhappy", "dissatisfied", "disappointed", "problem", "issue", "wrong", "mistake", "error", "complaint"]
        }
        
        # Count category matches
        category_scores = {category: 0 for category in categories}
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in query_lower:
                    category_scores[category] += 1
        
        # Get the category with the highest score
        max_score = max(category_scores.values())
        if max_score == 0:
            return "general_inquiry"  # Default category
        
        # Get all categories with the max score
        max_categories = [c for c, s in category_scores.items() if s == max_score]
        return max_categories[0]  # Return the first one if there are ties
    
    def _get_policy_details(self, policy_number):
        """
        Get policy details.
        
        Args:
            policy_number: Policy number to look up.
            
        Returns:
            Policy details.
        """
        try:
            # Call the policy lookup tool
            lookup_result_json = self.policy_lookup._policy_lookup_tool(policy_number)
            
            # Parse the result
            lookup_result = json.loads(lookup_result_json)
            
            if lookup_result.get("found", False):
                return lookup_result.get("policy", None)
            else:
                return None
        except Exception as e:
            print(f"Policy lookup error: {e}")
            return None
    
    def _lookup_policy(self, policy_number=None, policyholder_name=None, policyholder_email=None):
        """
        Look up policy information.
        
        Args:
            policy_number: Optional policy number to look up.
            policyholder_name: Optional policyholder name to look up.
            policyholder_email: Optional policyholder email to look up.
            
        Returns:
            Policy lookup result.
        """
        try:
            # Call the policy lookup tool
            lookup_result_json = self.policy_lookup._policy_lookup_tool(
                policy_number, policyholder_name, policyholder_email
            )
            
            # Parse the result
            lookup_result = json.loads(lookup_result_json)
            
            return lookup_result
        except Exception as e:
            print(f"Policy lookup error: {e}")
            return {"found": False, "error": str(e)}
    
    def _generate_response(self, query, query_category, sentiment_result, policy_details):
        """
        Generate a response to a customer query.
        
        Args:
            query: Customer's question or request.
            query_category: Category of the query.
            sentiment_result: Sentiment analysis result.
            policy_details: Optional policy details.
            
        Returns:
            Response text.
        """
        # Get greeting based on sentiment
        greeting = self._get_greeting(sentiment_result)
        
        # Get response based on query category
        if query_category == "policy_info":
            if policy_details:
                category_response = f"Here are your policy details:\n\n{self._format_policy_info(policy_details)}"
            else:
                category_response = "I'd be happy to provide information about your policy. Could you please provide your policy number or policyholder details?"
        
        elif query_category == "claim_status":
            category_response = "To check the status of your claim, please provide your claim number. If you don't have it, I can look it up using your policy number."
        
        elif query_category == "billing":
            category_response = "For billing inquiries, I can help you understand your premium, payment options, and due dates. If you have a specific billing question, please provide more details."
        
        elif query_category == "technical_support":
            category_response = "I'm sorry to hear you're experiencing technical issues. Could you please describe the problem in more detail? This will help me provide the most relevant assistance."
        
        elif query_category == "coverage_question":
            if policy_details:
                coverage_details = policy_details.get("coverage_details", {})
                category_response = f"Based on your policy, here's what's covered:\n\n{self._format_coverage_info(coverage_details)}\n\nIf you have a specific coverage question, please provide more details."
            else:
                category_response = "I'd be happy to explain what's covered under your policy. Could you please provide your policy number so I can give you accurate information?"
        
        elif query_category == "complaint":
            category_response = "I'm sorry to hear that you're experiencing an issue. Your satisfaction is important to us. Could you please provide more details about your concern so we can address it properly?"
        
        else:  # general_inquiry
            category_response = "Thank you for your inquiry. I'm here to help with any insurance-related questions you may have. Could you please provide more details about what you're looking for?"
        
        # Get closing based on sentiment
        closing = self._get_closing(sentiment_result)
        
        # Combine all parts
        response = f"{greeting}\n\n{category_response}\n\n{closing}"
        
        return response
    
    def _get_greeting(self, sentiment_result):
        """
        Get a greeting based on sentiment.
        
        Args:
            sentiment_result: Sentiment analysis result.
            
        Returns:
            Greeting text.
        """
        sentiment = sentiment_result["sentiment"]
        
        if sentiment == "positive":
            return "Hello! It's great to hear from you today."
        elif sentiment == "negative":
            return "Hello. I'm sorry to hear you're experiencing difficulties."
        else:
            return "Hello! Thank you for contacting AGENTIC InsurTech customer support."
    
    def _get_closing(self, sentiment_result):
        """
        Get a closing based on sentiment.
        
        Args:
            sentiment_result: Sentiment analysis result.
            
        Returns:
            Closing text.
        """
        sentiment = sentiment_result["sentiment"]
        
        if sentiment == "positive":
            return "Is there anything else I can help you with today? I'm here to assist with any other questions you might have."
        elif sentiment == "negative":
            return "I want to ensure your concern is fully addressed. If you need further assistance, please let me know, or I can connect you with a human agent."
        else:
            return "If you have any other questions, please don't hesitate to ask. I'm here to help."
    
    def _format_policy_info(self, policy):
        """
        Format policy information for display.
        
        Args:
            policy: Policy data.
            
        Returns:
            Formatted policy information.
        """
        policyholder = policy.get("policyholder", {})
        coverage_details = policy.get("coverage_details", {})
        
        formatted_info = f"""
## Policy Information

- **Policy Number**: {policy.get("policy_number", "N/A")}
- **Policy Type**: {policy.get("policy_type", "N/A")}
- **Status**: {policy.get("status", "N/A")}
- **Coverage Amount**: ${policy.get("coverage_amount", 0):,.2f}
- **Premium**: ${policy.get("premium_amount", 0):,.2f}
- **Start Date**: {policy.get("start_date", "N/A")}
- **End Date**: {policy.get("end_date", "N/A")}

## Policyholder Information

- **Name**: {policyholder.get("name", "N/A")}
- **Email**: {policyholder.get("email", "N/A")}
- **Phone**: {policyholder.get("phone", "N/A")}
- **Address**: {policyholder.get("address", "N/A")}

## Coverage Details

- **Dwelling**: ${coverage_details.get("dwelling", 0):,.2f}
- **Personal Property**: ${coverage_details.get("personal_property", 0):,.2f}
- **Liability**: ${coverage_details.get("liability", 0):,.2f}
- **Deductible**: ${coverage_details.get("deductible", 0):,.2f}
        """
        
        return formatted_info
    
    def _format_multiple_policies_info(self, policies):
        """
        Format information for multiple policies.
        
        Args:
            policies: List of policy data.
            
        Returns:
            Formatted policy information.
        """
        formatted_info = "## Multiple Policies Found\n\n"
        
        for i, policy in enumerate(policies, 1):
            formatted_info += f"### Policy {i}\n\n"
            formatted_info += f"- **Policy Number**: {policy.get('policy_number', 'N/A')}\n"
            formatted_info += f"- **Policy Type**: {policy.get('policy_type', 'N/A')}\n"
            formatted_info += f"- **Status**: {policy.get('status', 'N/A')}\n"
            formatted_info += f"- **Coverage Amount**: ${policy.get('coverage_amount', 0):,.2f}\n"
            formatted_info += f"- **Premium**: ${policy.get('premium_amount', 0):,.2f}\n\n"
        
        formatted_info += "For detailed information about a specific policy, please provide the policy number."
        
        return formatted_info
    
    def _format_coverage_info(self, coverage_details):
        """
        Format coverage information for display.
        
        Args:
            coverage_details: Coverage details data.
            
        Returns:
            Formatted coverage information.
        """
        formatted_info = "## Coverage Details\n\n"
        
        for coverage_type, amount in coverage_details.items():
            if coverage_type != "deductible":
                formatted_info += f"- **{coverage_type.replace('_', ' ').title()}**: ${amount:,.2f}\n"
        
        formatted_info += f"\n**Deductible**: ${coverage_details.get('deductible', 0):,.2f}"
        
        return formatted_info
    
    def _log_agent_activity(self, action, input_data, output_data, success, execution_time):
        """
        Log agent activity to the database.
        
        Args:
            action: The action performed.
            input_data: Input data for the action.
            output_data: Output data from the action.
            success: Whether the action was successful.
            execution_time: Execution time in seconds.
        """
        try:
            log_data = {
                "agent_type": "Customer Assistant",
                "action": action,
                "input": input_data,
                "output": output_data,
                "success": success,
                "execution_time": execution_time,
                "created_at": datetime.now().isoformat()
            }
            
            self.db_client.log_agent_activity(log_data)
        except Exception as e:
            print(f"Error logging agent activity: {e}")
