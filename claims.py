"""
Claims Processor agent implementation.
"""
from app.agents.tools.fraud_detector import FraudDetectorTool
from app.agents.tools.doc_analyzer import DocAnalyzerTool
from app.vision.image_processor import ImageProcessor
from app.database.supabase_client import SupabaseClient
from datetime import datetime
import json
import re

class ClaimsProcessor:
    """
    Claims Processor agent for handling insurance claims.
    """
    def __init__(self):
        """
        Initialize the Claims Processor agent with required tools.
        """
        self.fraud_detector = FraudDetectorTool()
        self.doc_analyzer = DocAnalyzerTool()
        self.image_processor = ImageProcessor()
        self.db_client = SupabaseClient()
    
    def process_claim(self, image_path, policy_number, claim_description):
        """
        Process an insurance claim.
        
        Args:
            image_path: Path to the claim image.
            policy_number: Policy number for the claim.
            claim_description: Description of the claim.
            
        Returns:
            Dictionary containing claim assessment results.
        """
        start_time = datetime.now()
        
        try:
            # Process the image
            image_analysis = self.image_processor.analyze_image(image_path)
            
            # Get policy details (simplified for now)
            policy_data = self._get_policy_data(policy_number)
            
            # Get customer history (simplified for now)
            customer_history = self._get_customer_history(policy_data.get("policyholder", {}).get("email", ""))
            
            # Prepare claim data for fraud detection
            claim_data = {
                "description": claim_description,
                "report_date": datetime.now().strftime("%Y-%m-%d"),
                "items": self._extract_items_from_analysis(image_analysis["raw_analysis"]),
                "image_analysis": image_analysis["raw_analysis"],
                "police_report": "police report" in claim_description.lower()
            }
            
            # Detect potential fraud
            fraud_detection_result = self._detect_fraud(claim_data, policy_data, customer_history)
            
            # Determine claim status
            claim_status = "Approved"
            if fraud_detection_result["fraud_score"] > 0.5:
                claim_status = "Under Review"
            elif fraud_detection_result["fraud_score"] > 0.7:
                claim_status = "Rejected"
            
            # Calculate claim amount (simplified)
            claim_amount = self._calculate_claim_amount(claim_data, policy_data)
            
            # Generate claim number
            claim_number = f"CLM-{datetime.now().strftime('%Y%m%d')}-{hash(policy_number + claim_description) % 10000:04d}"
            
            # Create claim assessment
            claim_assessment = {
                "claim_number": claim_number,
                "policy_number": policy_number,
                "status": claim_status,
                "fraud_score": fraud_detection_result["fraud_score"],
                "fraud_indicators": fraud_detection_result["indicators_found"],
                "claim_amount": claim_amount,
                "items_claimed": claim_data["items"],
                "next_steps": self._get_next_steps(claim_status)
            }
            
            # Save claim to database
            try:
                db_claim_data = {
                    "claim_number": claim_number,
                    "policy_id": policy_data.get("id", "unknown"),
                    "incident_date": datetime.now().strftime('%Y-%m-%d'),
                    "report_date": datetime.now().isoformat(),
                    "description": claim_description,
                    "status": claim_status,
                    "amount_requested": claim_amount,
                    "amount_approved": claim_amount if claim_status == "Approved" else 0,
                    "fraud_score": fraud_detection_result["fraud_score"],
                    "created_at": datetime.now().isoformat()
                }
                
                self.db_client.create_claim(db_claim_data)
            except Exception as db_error:
                print(f"Database error: {db_error}")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Claim Processing", 
                                    {"image_path": image_path, "policy_number": policy_number, "claim_description": claim_description},
                                    claim_assessment,
                                    True,
                                    execution_time)
            
            # Format the claim assessment for display
            formatted_assessment = self._format_claim_assessment(claim_assessment, image_analysis["raw_analysis"])
            
            return {
                "success": True,
                "claim_assessment": claim_assessment,
                "formatted_assessment": formatted_assessment,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Claim Processing", 
                                    {"image_path": image_path, "policy_number": policy_number, "claim_description": claim_description},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def _detect_fraud(self, claim_data, policy_data, customer_history):
        """
        Detect potential fraud in a claim.
        
        Args:
            claim_data: Claim data.
            policy_data: Policy data.
            customer_history: Customer history.
            
        Returns:
            Fraud detection results.
        """
        try:
            # Convert data to JSON strings for the fraud detector tool
            claim_data_json = json.dumps(claim_data)
            policy_data_json = json.dumps(policy_data)
            customer_history_json = json.dumps(customer_history)
            
            # Call the fraud detector tool
            fraud_result_json = self.fraud_detector._fraud_detection_tool(
                claim_data_json, policy_data_json, customer_history_json
            )
            
            # Parse the result
            fraud_result = json.loads(fraud_result_json)
            
            return fraud_result
        except Exception as e:
            print(f"Fraud detection error: {e}")
            return {
                "fraud_score": 0.1,
                "risk_category": "Low",
                "indicators_found": [],
                "recommended_action": "Process claim normally"
            }
    
    def _calculate_claim_amount(self, claim_data, policy_data):
        """
        Calculate the claim amount.
        
        Args:
            claim_data: Claim data.
            policy_data: Policy data.
            
        Returns:
            Calculated claim amount.
        """
        # Simple calculation based on items claimed
        base_amount = 1000
        items_value = sum(self._get_item_value(item) for item in claim_data["items"])
        
        # Apply policy limits
        coverage_amount = policy_data.get("coverage_amount", 50000)
        max_claim = min(items_value + base_amount, coverage_amount)
        
        # Apply deductible
        deductible = policy_data.get("coverage_details", {}).get("deductible", 500)
        final_amount = max(0, max_claim - deductible)
        
        return final_amount
    
    def _get_item_value(self, item):
        """
        Get the estimated value of an item.
        
        Args:
            item: Item name.
            
        Returns:
            Estimated value.
        """
        # Simplified item value estimation
        item_lower = item.lower()
        
        if "tv" in item_lower or "television" in item_lower:
            return 500
        elif "computer" in item_lower or "laptop" in item_lower:
            return 1000
        elif "phone" in item_lower or "smartphone" in item_lower:
            return 800
        elif "jewelry" in item_lower:
            return 2000
        elif "furniture" in item_lower:
            return 1500
        elif "appliance" in item_lower:
            return 1200
        else:
            return 500  # Default value
    
    def _get_next_steps(self, claim_status):
        """
        Get next steps based on claim status.
        
        Args:
            claim_status: Status of the claim.
            
        Returns:
            List of next steps.
        """
        if claim_status == "Approved":
            return [
                "Claim has been approved",
                "Payment will be processed within 5-7 business days",
                "You will receive an email confirmation once payment is sent",
                "Contact customer support if you have any questions"
            ]
        elif claim_status == "Under Review":
            return [
                "Claim requires additional review",
                "A claims adjuster will contact you within 48 hours",
                "Please have any supporting documentation ready",
                "You may be asked to provide additional information"
            ]
        else:  # Rejected
            return [
                "Claim has been rejected",
                "Please review the rejection reasons provided",
                "You may appeal this decision within 30 days",
                "Contact customer support for assistance with the appeal process"
            ]
    
    def _format_claim_assessment(self, assessment, image_analysis):
        """
        Format claim assessment for display.
        
        Args:
            assessment: Claim assessment data.
            image_analysis: Image analysis text.
            
        Returns:
            Formatted claim assessment text.
        """
        fraud_indicators = "\n".join([f"- {indicator}" for indicator in assessment["fraud_indicators"]]) if assessment["fraud_indicators"] else "None detected"
        next_steps = "\n".join([f"- {step}" for step in assessment["next_steps"]])
        
        formatted_text = f"""
## Claim Assessment Results

### Claim Information
- **Claim Number**: {assessment["claim_number"]}
- **Policy Number**: {assessment["policy_number"]}
- **Status**: {assessment["status"]}

### Assessment Details
- **Estimated Payout**: ${assessment["claim_amount"]:,.2f}
- **Fraud Detection Score**: {assessment["fraud_score"]:.2f}

### Potential Fraud Indicators
{fraud_indicators}

### Next Steps
{next_steps}

### Image Analysis Summary
{self._summarize_image_analysis(image_analysis)}
        """
        
        return formatted_text
    
    def _summarize_image_analysis(self, analysis_text):
        """
        Summarize image analysis text.
        
        Args:
            analysis_text: Full image analysis text.
            
        Returns:
            Summarized text.
        """
        # Extract key sentences
        sentences = re.split(r'[.!?]', analysis_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Select important sentences (simplified approach)
        important_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ["damage", "item", "object", "identify", "detect", "risk"]):
                important_sentences.append(sentence)
        
        # Limit to 3-5 sentences
        if len(important_sentences) > 5:
            important_sentences = important_sentences[:5]
        
        # If no important sentences found, use the first few sentences
        if not important_sentences and sentences:
            important_sentences = sentences[:3]
        
        return ". ".join(important_sentences) + "."
    
    def _extract_items_from_analysis(self, analysis_text):
        """
        Extract items from image analysis text.
        
        Args:
            analysis_text: Raw analysis text from vision LLM.
            
        Returns:
            List of items.
        """
        items = []
        
        # Look for items in the analysis text
        for line in analysis_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Look for item descriptions
            if any(word in line.lower() for word in ["item", "object", "damaged", "broken", "stolen"]):
                items.append(line)
        
        # If no items found, extract sentences with potential items
        if not items:
            sentences = re.split(r'[.!?]', analysis_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if any(word in sentence.lower() for word in ["see", "visible", "appears", "showing", "contains"]):
                    items.append(sentence)
        
        # Limit to 10 items
        return items[:10]
    
    def _get_policy_data(self, policy_number):
        """
        Get policy data for a given policy number.
        
        Args:
            policy_number: Policy number to look up.
            
        Returns:
            Policy data.
        """
        # Simplified policy data (would be retrieved from database in production)
        return {
            "id": "policy_123",
            "policy_number": policy_number,
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
        }
    
    def _get_customer_history(self, email):
        """
        Get customer claim history.
        
        Args:
            email: Customer email.
            
        Returns:
            Customer history data.
        """
        # Simplified customer history (would be retrieved from database in production)
        return {
            "email": email,
            "total_claims": 2,
            "recent_claims": 1,
            "claim_history": [
                {
                    "claim_number": "CLM-20240315-1234",
                    "date": "2024-03-15",
                    "amount": 1500.00,
                    "status": "Paid"
                },
                {
                    "claim_number": "CLM-20230710-5678",
                    "date": "2023-07-10",
                    "amount": 2200.00,
                    "status": "Paid"
                }
            ]
        }
    
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
                "agent_type": "Claims Processor",
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
