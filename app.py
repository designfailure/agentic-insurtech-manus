"""
Main Gradio UI application for AGENTIC InsurTech.
"""
import os
import gradio as gr
import numpy as np
from datetime import datetime
from PIL import Image

from app.config import APP_NAME, APP_VERSION
from app.vision.image_processor import ImageProcessor
from app.database.supabase_client import SupabaseClient

# Initialize components
image_processor = ImageProcessor()
db_client = SupabaseClient()

# Create upload directory if it doesn't exist
os.makedirs("static/uploads", exist_ok=True)

def save_uploaded_image(image):
    """
    Save an uploaded image to the uploads directory.
    
    Args:
        image: The uploaded image.
        
    Returns:
        Path to the saved image.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"static/uploads/upload_{timestamp}.jpg"
    
    if isinstance(image, np.ndarray):
        # Convert numpy array to PIL Image
        img = Image.fromarray(image)
        img.save(image_path)
    else:
        # Already a file path
        os.rename(image, image_path)
    
    return image_path

def analyze_image_handler(image):
    """
    Handle image analysis for insurance purposes.
    
    Args:
        image: The uploaded image.
        
    Returns:
        Analysis results.
    """
    if image is None:
        return "Please upload an image to analyze."
    
    # Save the uploaded image
    image_path = save_uploaded_image(image)
    
    # Analyze the image
    analysis_results = image_processor.analyze_image(image_path)
    
    # Format the results
    raw_analysis = analysis_results["raw_analysis"]
    structured_data = analysis_results["structured_data"]
    
    items_list = "\n".join(structured_data["items"]) if structured_data["items"] else "No specific items identified."
    risks_list = "\n".join(structured_data["risks"]) if structured_data["risks"] else "No specific risks identified."
    
    result = f"""
## Image Analysis Results

### Identified Items:
{items_list}

### Potential Risks:
{risks_list}

### Total Items Detected: {structured_data["item_count"]}

### Raw Analysis:
{raw_analysis}
    """
    
    # Log the analysis in the database
    try:
        db_client.log_agent_activity({
            "agent_type": "Underwriting Analyzer",
            "action": "Image Analysis",
            "input": {"image_path": image_path},
            "output": {"item_count": structured_data["item_count"]},
            "success": True,
            "execution_time": 2.1,  # Placeholder
            "created_at": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Database logging error: {e}")
    
    return result

def get_coverage_recommendations(image_analysis, location):
    """
    Get coverage recommendations based on image analysis and location.
    
    Args:
        image_analysis: The image analysis results.
        location: The location input.
        
    Returns:
        Coverage recommendations.
    """
    # This is a placeholder implementation
    # In a real application, this would use more sophisticated logic
    
    if not image_analysis or "Please upload an image" in image_analysis:
        return "Please analyze an image first to get coverage recommendations."
    
    if not location:
        return "Please enter a location to get coverage recommendations."
    
    # Extract item count from the analysis
    item_count = 0
    for line in image_analysis.split('\n'):
        if "Total Items Detected:" in line:
            try:
                item_count = int(line.split(':')[1].strip())
            except:
                item_count = 0
    
    # Simple logic for coverage recommendations
    base_coverage = 10000
    per_item_coverage = 1000
    location_factor = 1.0
    
    # Adjust location factor based on location
    high_cost_locations = ["new york", "san francisco", "london", "tokyo", "paris"]
    medium_cost_locations = ["chicago", "miami", "berlin", "sydney", "toronto"]
    
    location_lower = location.lower()
    if any(city in location_lower for city in high_cost_locations):
        location_factor = 1.5
    elif any(city in location_lower for city in medium_cost_locations):
        location_factor = 1.2
    
    # Calculate recommended coverage
    recommended_coverage = (base_coverage + (item_count * per_item_coverage)) * location_factor
    
    # Calculate premium (simplified)
    annual_premium = recommended_coverage * 0.02
    monthly_premium = annual_premium / 12
    
    result = f"""
## Coverage Recommendations for {location}

### Property Coverage
Based on the {item_count} items detected in your image, we recommend:

- **Recommended Coverage Amount**: ${recommended_coverage:,.2f}
- **Annual Premium**: ${annual_premium:,.2f}
- **Monthly Premium**: ${monthly_premium:,.2f}

### Coverage Details
- Personal Property Protection
- Liability Protection
- Additional Living Expenses
- Medical Payments to Others

### Risk Factors
- Location-based risk assessment
- Item value and quantity
- Potential hazards identified in the image

### Next Steps
1. Review the coverage details
2. Adjust coverage amount if needed
3. Proceed to policy acceptance
    """
    
    return result

def create_policy_document(image_analysis, coverage_details, customer_name, email):
    """
    Create a policy document based on the provided information.
    
    Args:
        image_analysis: The image analysis results.
        coverage_details: The coverage details.
        customer_name: The customer's name.
        email: The customer's email.
        
    Returns:
        Policy document text.
    """
    if not all([image_analysis, coverage_details, customer_name, email]):
        return "Please provide all required information to generate a policy document."
    
    # Extract coverage amount from the coverage details
    coverage_amount = 0
    annual_premium = 0
    for line in coverage_details.split('\n'):
        if "Recommended Coverage Amount" in line:
            try:
                coverage_amount = float(line.split('$')[1].replace(',', '').strip())
            except:
                coverage_amount = 0
        if "Annual Premium" in line:
            try:
                annual_premium = float(line.split('$')[1].replace(',', '').strip())
            except:
                annual_premium = 0
    
    # Generate policy number
    policy_number = f"POL-{datetime.now().strftime('%Y%m%d')}-{hash(customer_name + email) % 10000:04d}"
    
    # Generate policy document
    policy_document = f"""
# INSURANCE POLICY DOCUMENT

## POLICY NUMBER: {policy_number}

## POLICYHOLDER INFORMATION
- **Name**: {customer_name}
- **Email**: {email}
- **Policy Start Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Policy End Date**: {datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d')}

## COVERAGE DETAILS
- **Coverage Amount**: ${coverage_amount:,.2f}
- **Annual Premium**: ${annual_premium:,.2f}
- **Monthly Premium**: ${annual_premium/12:,.2f}

## COVERED ITEMS
The following items are covered under this policy:
{image_analysis.split('### Identified Items:')[1].split('###')[0] if '### Identified Items:' in image_analysis else 'All items as per standard coverage.'}

## TERMS AND CONDITIONS
1. This policy is subject to the terms and conditions outlined in the full policy document.
2. Claims must be reported within 30 days of the incident.
3. A deductible of $500 applies to all claims.
4. The policy is renewable annually.

## CONTACT INFORMATION
For claims or inquiries, please contact:
- **Phone**: 1-800-INSURTECH
- **Email**: claims@agentic-insurtech.com
- **Website**: www.agentic-insurtech.com

## SIGNATURES
- **Insurer**: AGENTIC InsurTech
- **Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Policyholder**: {customer_name}
    """
    
    # Save policy to database
    try:
        db_client.create_policy({
            "policy_number": policy_number,
            "policy_type": "Property",
            "coverage_amount": coverage_amount,
            "premium_amount": annual_premium,
            "start_date": datetime.now().strftime('%Y-%m-%d'),
            "end_date": datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d'),
            "status": "Active",
            "risk_score": 0.5,  # Placeholder
            "created_at": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Database error: {e}")
    
    return policy_document

def process_claim(image, policy_number, claim_description):
    """
    Process an insurance claim.
    
    Args:
        image: The claim image.
        policy_number: The policy number.
        claim_description: Description of the claim.
        
    Returns:
        Claim assessment results.
    """
    if not all([image, policy_number, claim_description]):
        return "Please provide all required information to process the claim."
    
    # Save the uploaded image
    image_path = save_uploaded_image(image)
    
    # Analyze the image
    analysis_results = image_processor.analyze_image(image_path)
    
    # Simple claim assessment logic
    # In a real application, this would use more sophisticated AI
    
    # Generate claim number
    claim_number = f"CLM-{datetime.now().strftime('%Y%m%d')}-{hash(policy_number + claim_description) % 10000:04d}"
    
    # Placeholder fraud detection
    fraud_score = 0.1  # Low fraud score
    if "water damage" in claim_description.lower() and "flood" not in claim_description.lower():
        fraud_score = 0.3  # Medium fraud score
    if "stolen" in claim_description.lower() and "door" not in claim_description.lower() and "window" not in claim_description.lower():
        fraud_score = 0.6  # High fraud score
    
    # Determine claim status
    claim_status = "Approved"
    if fraud_score > 0.5:
        claim_status = "Under Review"
    
    # Calculate claim amount (simplified)
    base_amount = 1000
    severity_factor = 1.0
    
    if "severe" in claim_description.lower() or "complete" in claim_description.lower():
        severity_factor = 2.0
    elif "minor" in claim_description.lower() or "partial" in claim_description.lower():
        severity_factor = 0.5
    
    claim_amount = base_amount * severity_factor
    
    # Save claim to database
    try:
        db_client.create_claim({
            "claim_number": claim_number,
            "incident_date": datetime.now().strftime('%Y-%m-%d'),
            "description": claim_description,
            "status": claim_status,
            "amount_requested": claim_amount,
            "amount_approved": claim_amount if claim_status == "Approved" else 0,
            "fraud_score": fraud_score,
            "created_at": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Database error: {e}")
    
    result = f"""
## Claim Assessment Results

### Claim Information
- **Claim Number**: {claim_number}
- **Policy Number**: {policy_number}
- **Incident Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Description**: {claim_description}

### Assessment Results
- **Claim Status**: {claim_status}
- **Estimated Payout**: ${claim_amount:,.2f}
- **Fraud Detection Score**: {fraud_score:.2f}

### Next Steps
{"Your claim has been approved. You will receive payment within 5-7 business days." if claim_status == "Approved" else "Your claim is under review. Our claims adjuster will contact you within 48 hours."}

### Image Analysis
{analysis_results["raw_analysis"]}
    """
    
    return result

def create_ui():
    """
    Create the Gradio UI for the AGENTIC InsurTech application.
    
    Returns:
        Gradio interface.
    """
    with gr.Blocks(title=f"{APP_NAME} v{APP_VERSION}") as app:
        gr.Markdown(f"# {APP_NAME}")
        gr.Markdown("## AI-Powered Insurance Solutions")
        
        with gr.Tab("Dashboard"):
            gr.Markdown("### Agent Performance")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Underwriting Analyzer")
                    gr.Markdown("Risk assessment specialist")
                    gr.Markdown("Success Rate: 75%")
                    gr.Markdown("92 tasks | Avg. Time: 2.1s")
                
                with gr.Column():
                    gr.Markdown("#### Claims Processor")
                    gr.Markdown("Automated claims handling")
                    gr.Markdown("Success Rate: 85%")
                    gr.Markdown("147 tasks | Avg. Time: 1.8s")
                
                with gr.Column():
                    gr.Markdown("#### Customer Assistant")
                    gr.Markdown("24/7 support agent")
                    gr.Markdown("Success Rate: 60%")
                    gr.Markdown("203 tasks | Avg. Time: 3.2s")
            
            gr.Markdown("### System Health")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("Agent Coordination: Optimal")
                    gr.Markdown("API Latency: Moderate")
                
                with gr.Column():
                    gr.Markdown("Memory Usage: Good")
                    gr.Markdown("Error Rate: High")
        
        with gr.Tab("Image Analysis"):
            gr.Markdown("### Upload an image to analyze for insurance purposes")
            
            with gr.Row():
                with gr.Column():
                    image_input = gr.Image(type="filepath", label="Upload Image")
                    analyze_button = gr.Button("Analyze Image")
                
                with gr.Column():
                    analysis_output = gr.Markdown(label="Analysis Results")
            
            analyze_button.click(
                fn=analyze_image_handler,
                inputs=[image_input],
                outputs=[analysis_output]
            )
        
        with gr.Tab("Coverage Recommendations"):
            gr.Markdown("### Get personalized coverage recommendations")
            
            with gr.Row():
                with gr.Column():
                    coverage_analysis_input = gr.Markdown(label="Image Analysis Results")
                    location_input = gr.Textbox(label="Location")
                    get_coverage_button = gr.Button("Get Coverage Recommendations")
                
                with gr.Column():
                    coverage_output = gr.Markdown(label="Coverage Recommendations")
            
            get_coverage_button.click(
                fn=get_coverage_recommendations,
                inputs=[coverage_analysis_input, location_input],
                outputs=[coverage_output]
            )
        
        with gr.Tab("Policy Issuance"):
            gr.Markdown("### Generate insurance policy document")
            
            with gr.Row():
                with gr.Column():
                    policy_analysis_input = gr.Markdown(label="Image Analysis Results")
                    policy_coverage_input = gr.Markdown(label="Coverage Details")
                    customer_name_input = gr.Textbox(label="Customer Name")
                    email_input = gr.Textbox(label="Email Address")
                    create_policy_button = gr.Button("Create Policy Document")
                
                with gr.Column():
                    policy_output = gr.Markdown(label="Policy Document")
            
            create_policy_button.click(
                fn=create_policy_document,
                inputs=[policy_analysis_input, policy_coverage_input, customer_name_input, email_input],
                outputs=[policy_output]
            )
        
        with gr.Tab("Claims Processing"):
            gr.Markdown("### Submit and process insurance claims")
            
            with gr.Row():
                with gr.Column():
                    claim_image_input = gr.Image(type="filepath", label="Upload Claim Image")
                    policy_number_input = gr.Textbox(label="Policy Number")
                    claim_description_input = gr.Textbox(label="Claim Description", lines=5)
                    process_claim_button = gr.Button("Process Claim")
                
                with gr.Column():
                    claim_output = gr.Markdown(label="Claim Assessment")
            
            process_claim_button.click(
                fn=process_claim,
                inputs=[claim_image_input, policy_number_input, claim_description_input],
                outputs=[claim_output]
            )
        
        with gr.Tab("Prevention Services"):
            gr.Markdown("### Risk prevention recommendations")
            
            with gr.Row():
                with gr.Column():
                    prevention_analysis_input = gr.Markdown(label="Image Analysis Results")
                    prevention_button = gr.Button("Get Prevention Recommendations")
                
                with gr.Column():
                    prevention_output = gr.Markdown(label="Prevention Recommendations")
            
            # Placeholder function for prevention recommendations
            def get_prevention_recommendations(analysis):
                if not analysis or "Please upload an image" in analysis:
                    return "Please analyze an image first to get prevention recommendations."
                
                # Simple prevention recommendations
                return """
## Risk Prevention Recommendations

### Home Safety
- Install smoke detectors on every floor
- Use surge protectors for electronics
- Keep fire extinguishers accessible
- Install carbon monoxide detectors

### Security Measures
- Install deadbolt locks on exterior doors
- Consider a security system
- Use motion-sensor lighting outside
- Keep valuables in a safe

### Weather Protection
- Clean gutters regularly
- Trim trees away from your home
- Check roof for damage annually
- Consider flood barriers if in a flood zone

### Maintenance Tips
- Check plumbing for leaks regularly
- Inspect electrical wiring
- Service HVAC systems annually
- Check for foundation cracks
                """
            
            prevention_button.click(
                fn=get_prevention_recommendations,
                inputs=[prevention_analysis_input],
                outputs=[prevention_output]
            )
    
    return app

# Create the Gradio UI
ui = create_ui()

def launch_app():
    """
    Launch the Gradio application.
    """
    ui.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    launch_app()
