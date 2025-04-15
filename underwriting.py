"""
Underwriting Analyzer agent implementation.
"""
from app.agents.tools.risk_model import RiskModelTool
from app.agents.tools.doc_analyzer import DocAnalyzerTool
from app.vision.image_processor import ImageProcessor
from app.database.supabase_client import SupabaseClient
from datetime import datetime
import json

class UnderwritingAnalyzer:
    """
    Underwriting Analyzer agent for risk assessment and coverage determination.
    """
    def __init__(self):
        """
        Initialize the Underwriting Analyzer agent with required tools.
        """
        self.risk_model = RiskModelTool()
        self.doc_analyzer = DocAnalyzerTool()
        self.image_processor = ImageProcessor()
        self.db_client = SupabaseClient()
    
    def analyze_risk_from_image(self, image_path, location):
        """
        Analyze risk based on image and location.
        
        Args:
            image_path: Path to the uploaded image.
            location: Customer location.
            
        Returns:
            Dictionary containing risk assessment results.
        """
        start_time = datetime.now()
        
        try:
            # Process the image
            image_analysis = self.image_processor.analyze_image(image_path)
            
            # Extract items from the analysis
            items = self._extract_items_from_analysis(image_analysis["raw_analysis"])
            
            # Extract location factors
            location_factors = self._extract_location_factors(location)
            
            # Use risk model to assess risk
            risk_assessment = self.risk_model.assess_risk(items, location_factors)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Image Risk Analysis", 
                                    {"image_path": image_path, "location": location},
                                    risk_assessment,
                                    True,
                                    execution_time)
            
            return {
                "success": True,
                "risk_assessment": risk_assessment,
                "image_analysis": image_analysis,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Image Risk Analysis", 
                                    {"image_path": image_path, "location": location},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def generate_policy_document(self, customer_info, coverage_details):
        """
        Generate an insurance policy document.
        
        Args:
            customer_info: Dictionary containing customer information.
            coverage_details: Dictionary containing coverage details.
            
        Returns:
            Dictionary containing policy document and metadata.
        """
        start_time = datetime.now()
        
        try:
            # Generate policy number
            policy_number = f"POL-{datetime.now().strftime('%Y%m%d')}-{hash(customer_info.get('email', '')) % 10000:04d}"
            
            # Calculate dates
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d')
            
            # Create policy document
            policy_document = f"""
# INSURANCE POLICY DOCUMENT

## POLICY NUMBER: {policy_number}

## POLICYHOLDER INFORMATION
- **Name**: {customer_info.get('name', 'Unknown')}
- **Email**: {customer_info.get('email', 'Unknown')}
- **Phone**: {customer_info.get('phone', 'Unknown')}
- **Address**: {customer_info.get('address', 'Unknown')}
- **Policy Start Date**: {start_date}
- **Policy End Date**: {end_date}

## COVERAGE DETAILS
- **Coverage Type**: {coverage_details.get('type', 'Property Insurance')}
- **Coverage Amount**: ${coverage_details.get('amount', 0):,.2f}
- **Annual Premium**: ${coverage_details.get('annual_premium', 0):,.2f}
- **Monthly Premium**: ${coverage_details.get('monthly_premium', 0):,.2f}
- **Deductible**: ${coverage_details.get('deductible', 500):,.2f}

## COVERED ITEMS
{coverage_details.get('covered_items', 'All items as per standard coverage.')}

## COVERAGE BREAKDOWN
- **Dwelling**: ${coverage_details.get('dwelling', 0):,.2f}
- **Personal Property**: ${coverage_details.get('personal_property', 0):,.2f}
- **Liability**: ${coverage_details.get('liability', 0):,.2f}
- **Additional Living Expenses**: ${coverage_details.get('additional_living', 0):,.2f}

## TERMS AND CONDITIONS
1. This policy is subject to the terms and conditions outlined in the full policy document.
2. Claims must be reported within 30 days of the incident.
3. A deductible of ${coverage_details.get('deductible', 500):,.2f} applies to all claims.
4. The policy is renewable annually.

## CONTACT INFORMATION
For claims or inquiries, please contact:
- **Phone**: 1-800-INSURTECH
- **Email**: claims@agentic-insurtech.com
- **Website**: www.agentic-insurtech.com

## SIGNATURES
- **Insurer**: AGENTIC InsurTech
- **Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Policyholder**: {customer_info.get('name', 'Unknown')}
            """
            
            # Save policy to database
            policy_data = {
                "policy_number": policy_number,
                "policy_type": coverage_details.get('type', 'Property Insurance'),
                "coverage_amount": coverage_details.get('amount', 0),
                "premium_amount": coverage_details.get('annual_premium', 0),
                "start_date": start_date,
                "end_date": end_date,
                "status": "Active",
                "risk_score": coverage_details.get('risk_score', 0.5)
            }
            
            try:
                db_result = self.db_client.create_policy(policy_data)
            except Exception as db_error:
                print(f"Database error: {db_error}")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Policy Document Generation", 
                                    {"customer_info": customer_info, "coverage_details": coverage_details},
                                    {"policy_number": policy_number},
                                    True,
                                    execution_time)
            
            return {
                "success": True,
                "policy_document": policy_document,
                "policy_number": policy_number,
                "policy_data": policy_data,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Policy Document Generation", 
                                    {"customer_info": customer_info, "coverage_details": coverage_details},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def generate_prevention_plan(self, image_analysis, location):
        """
        Generate a personalized prevention plan based on image analysis and location.
        
        Args:
            image_analysis: Analysis of the uploaded image.
            location: Customer location.
            
        Returns:
            Dictionary containing prevention plan.
        """
        start_time = datetime.now()
        
        try:
            # Extract risks from image analysis
            risks = []
            if isinstance(image_analysis, dict) and "structured_data" in image_analysis:
                risks = image_analysis["structured_data"].get("risks", [])
            elif isinstance(image_analysis, str):
                # Try to extract risks from text
                for line in image_analysis.split('\n'):
                    if "risk" in line.lower() or "hazard" in line.lower():
                        risks.append(line.strip())
            
            # Determine location-specific risks
            location_risks = self._get_location_risks(location)
            
            # Generate prevention recommendations
            general_recommendations = [
                "Install smoke detectors on every floor",
                "Use surge protectors for electronics",
                "Keep fire extinguishers accessible",
                "Install carbon monoxide detectors",
                "Keep valuables in a safe",
                "Use motion-sensor lighting outside",
                "Check plumbing for leaks regularly",
                "Service HVAC systems annually"
            ]
            
            # Select relevant recommendations based on risks
            specific_recommendations = self._get_specific_recommendations(risks)
            
            # Create prevention plan
            prevention_plan = f"""
# Personalized Risk Prevention Plan

## Identified Risks

### Property Risks:
{self._format_list_items(risks) if risks else "No specific property risks identified."}

### Location-Based Risks:
{self._format_list_items(location_risks)}

## Recommended Prevention Measures

### General Safety Recommendations:
{self._format_list_items(general_recommendations[:4])}

### Property-Specific Recommendations:
{self._format_list_items(specific_recommendations)}

### Location-Specific Recommendations:
{self._format_list_items(self._get_location_recommendations(location))}

### Maintenance Recommendations:
{self._format_list_items(general_recommendations[4:])}

## Benefits of Prevention
- Reduced risk of property damage and loss
- Potential premium discounts
- Increased safety for you and your family
- Peace of mind

## Next Steps
1. Implement the highest priority recommendations first
2. Schedule regular maintenance checks
3. Update your prevention plan as your needs change
4. Contact us for assistance with implementing these recommendations
            """
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Prevention Plan Generation", 
                                    {"image_analysis": "Image analysis data", "location": location},
                                    {"plan_length": len(prevention_plan)},
                                    True,
                                    execution_time)
            
            return {
                "success": True,
                "prevention_plan": prevention_plan,
                "risks": risks + location_risks,
                "recommendations": general_recommendations + specific_recommendations,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log agent activity
            self._log_agent_activity("Prevention Plan Generation", 
                                    {"image_analysis": "Image analysis data", "location": location},
                                    {"error": str(e)},
                                    False,
                                    execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def _extract_items_from_analysis(self, analysis_text):
        """
        Extract items from image analysis text.
        
        Args:
            analysis_text: Raw analysis text from vision LLM.
            
        Returns:
            Dictionary of item categories and counts.
        """
        items = {
            "electronics": 0,
            "furniture": 0,
            "appliances": 0,
            "jewelry": 0,
            "art": 0,
            "sports_equipment": 0,
            "musical_instruments": 0
        }
        
        # Simple keyword matching (in a real system, this would be more sophisticated)
        electronics_keywords = ["tv", "television", "computer", "laptop", "phone", "smartphone", "tablet"]
        furniture_keywords = ["sofa", "couch", "chair", "table", "desk", "bed", "cabinet", "shelf"]
        appliance_keywords = ["refrigerator", "fridge", "oven", "stove", "microwave", "washer", "dryer"]
        jewelry_keywords = ["jewelry", "watch", "ring", "necklace", "bracelet"]
        art_keywords = ["painting", "sculpture", "artwork", "art", "photograph"]
        sports_keywords = ["bicycle", "bike", "treadmill", "weights", "sports"]
        music_keywords = ["piano", "guitar", "instrument", "musical"]
        
        # Count items by category
        for line in analysis_text.lower().split('\n'):
            # Check for explicit counts
            for category in items.keys():
                if category in line:
                    # Look for numbers in the line
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        items[category] += int(numbers[0])
                        continue
            
            # Check for keywords
            for keyword in electronics_keywords:
                if keyword in line:
                    items["electronics"] += 1
                    break
                    
            for keyword in furniture_keywords:
                if keyword in line:
                    items["furniture"] += 1
                    break
                    
            for keyword in appliance_keywords:
                if keyword in line:
                    items["appliances"] += 1
                    break
                    
            for keyword in jewelry_keywords:
                if keyword in line:
                    items["jewelry"] += 1
                    break
                    
            for keyword in art_keywords:
                if keyword in line:
                    items["art"] += 1
                    break
                    
            for keyword in sports_keywords:
                if keyword in line:
                    items["sports_equipment"] += 1
                    break
                    
            for keyword in music_keywords:
                if keyword in line:
                    items["musical_instruments"] += 1
                    break
        
        # Remove categories with zero items
        return {k: v for k, v in items.items() if v > 0}
    
    def _extract_location_factors(self, location):
        """
        Extract risk factors based on location.
        
        Args:
            location: Customer location.
            
        Returns:
            List of location risk factors.
        """
        location_lower = location.lower()
        factors = []
        
        # Geographic risk factors
        coastal_cities = ["miami", "new orleans", "houston", "tampa", "charleston"]
        wildfire_areas = ["los angeles", "san diego", "phoenix", "denver", "portland"]
        earthquake_zones = ["san francisco", "seattle", "los angeles", "portland", "anchorage"]
        tornado_alley = ["oklahoma city", "kansas city", "dallas", "st. louis", "nashville"]
        flood_zones = ["new orleans", "houston", "miami", "charleston", "jacksonville"]
        
        # Urban/rural classification
        major_cities = ["new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia", 
                       "san antonio", "san diego", "dallas", "san jose"]
        
        # Check for specific risk factors
        if any(city in location_lower for city in coastal_cities):
            factors.append("hurricane_prone")
        
        if any(city in location_lower for city in wildfire_areas):
            factors.append("wildfire_prone")
        
        if any(city in location_lower for city in earthquake_zones):
            factors.append("earthquake_prone")
        
        if any(city in location_lower for city in tornado_alley):
            factors.append("tornado_prone")
        
        if any(city in location_lower for city in flood_zones):
            factors.append("flood_zone")
        
        # Determine urban/suburban/rural
        if any(city in location_lower for city in major_cities):
            factors.append("urban")
        elif "county" in location_lower or "township" in location_lower:
            factors.append("rural")
        else:
            factors.append("suburban")
        
        return factors
    
    def _get_location_risks(self, location):
        """
        Get location-specific risks.
        
        Args:
            location: Customer location.
            
        Returns:
            List of location-specific risks.
        """
        location_lower = location.lower()
        risks = []
        
        # Check for specific location risks
        if any(city in location_lower for city in ["miami", "new orleans", "houston", "tampa", "charleston"]):
            risks.append("Hurricane and tropical storm risk")
            risks.append("Flooding risk")
        
        if any(city in location_lower for city in ["los angeles", "san diego", "phoenix", "denver", "portland"]):
            risks.append("Wildfire risk")
            risks.append("Drought conditions")
        
        if any(city in location_lower for city in ["san francisco", "seattle", "los angeles", "portland", "anchorage"]):
            risks.append("Earthquake risk")
        
        if any(city in location_lower for city in ["oklahoma city", "kansas city", "dallas", "st. louis", "nashville"]):
            risks.append("Tornado risk")
            risks.append("Severe storm risk")
        
        # Add general risks based on urban/rural
        if any(city in location_lower for city in ["new york", "chicago", "los angeles"]):
            risks.append("Urban crime risk")
            risks.append("Higher property values")
        
        # Default risk if none identified
        if not risks:
            risks.append("Standard property risks")
        
        return risks
    
    def _get_specific_recommendations(self, risks):
        """
        Get specific recommendations based on identified risks.
        
        Args:
            risks: List of identified risks.
            
        Returns:
            List of specific recommendations.
        """
        recommendations = []
        
        # Convert risks to lowercase for easier matching
        risks_lower = [risk.lower() for risk in risks]
        
        # Check for specific risks and add relevant recommendations
        if any("water" in risk or "flood" in risk or "leak" in risk for risk in risks_lower):
            recommendations.extend([
                "Install water leak detectors",
                "Elevate valuable items in basement",
                "Check and maintain gutters and downspouts",
                "Consider a sump pump with battery backup"
            ])
        
        if any("fire" in risk or "electrical" in risk for risk in risks_lower):
            recommendations.extend([
                "Have electrical system inspected",
                "Don't overload electrical outlets",
                "Keep flammable materials away from heat sources",
                "Create a fire evacuation plan"
            ])
        
        if any("theft" in risk or "security" in risk or "break" in risk for risk in risks_lower):
            recommendations.extend([
                "Install deadbolt locks on exterior doors",
                "Consider a security system with monitoring",
                "Use timer switches for lights when away",
                "Secure sliding doors with security bars"
            ])
        
        if any("valuable" in risk or "jewelry" in risk or "art" in risk for risk in risks_lower):
            recommendations.extend([
                "Store valuables in a secure safe",
                "Consider additional scheduled personal property coverage",
                "Document valuables with photos and appraisals",
                "Install a security system with cameras"
            ])
        
        # Add general recommendations if no specific ones were added
        if not recommendations:
            recommendations = [
                "Conduct regular home maintenance checks",
                "Create a home inventory with photos",
                "Install quality locks on all doors and windows",
                "Consider a monitored security system"
            ]
        
        return recommendations
    
    def _get_location_recommendations(self, location):
        """
        Get location-specific recommendations.
        
        Args:
            location: Customer location.
            
        Returns:
            List of location-specific recommendations.
        """
        location_lower = location.lower()
        recommendations = []
        
        # Hurricane/flood prone areas
        if any(city in location_lower for city in ["miami", "new orleans", "houston", "tampa", "charleston"]):
            recommendations.extend([
                "Install hurricane shutters or impact-resistant windows",
                "Create an emergency evacuation plan",
                "Secure outdoor items before storms",
                "Consider flood insurance"
            ])
        
        # Wildfire prone areas
        if any(city in location_lower for city in ["los angeles", "san diego", "phoenix", "denver", "portland"]):
            recommendations.extend([
                "Create defensible space around your home",
                "Use fire-resistant building materials",
                "Keep gutters clear of debris",
                "Have an evacuation plan ready"
            ])
        
        # Earthquake prone areas
        if any(city in location_lower for city in ["san francisco", "seattle", "los angeles", "portland", "anchorage"]):
            recommendations.extend([
                "Secure heavy furniture to walls",
                "Install automatic gas shutoff valve",
                "Use flexible connections for gas appliances",
                "Have earthquake emergency kit ready"
            ])
        
        # Tornado prone areas
        if any(city in location_lower for city in ["oklahoma city", "kansas city", "dallas", "st. louis", "nashville"]):
            recommendations.extend([
                "Designate a safe room or shelter area",
                "Have a weather radio with alerts",
                "Secure outdoor items during storm season",
                "Create a family emergency plan"
            ])
        
        # Default recommendations if none identified
        if not recommendations:
            recommendations = [
                "Research local weather patterns and risks",
                "Create an emergency preparedness kit",
                "Know the location of utility shutoffs",
                "Have a family communication plan"
            ]
        
        return recommendations
    
    def _format_list_items(self, items):
        """
        Format a list of items as a markdown list.
        
        Args:
            items: List of items.
            
        Returns:
            Formatted markdown list.
        """
        if not items:
            return "None identified."
        
        return "\n".join([f"- {item}" for item in items])
    
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
                "agent_type": "Underwriting Analyzer",
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
