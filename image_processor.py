"""
Image processor module for vision LLM integration.
"""
import os
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from openai import OpenAI
from app.config import OPENAI_API_KEY, VISION_MODEL

class ImageProcessor:
    """
    Class for processing images using vision LLM.
    """
    def __init__(self):
        """
        Initialize the image processor with OpenAI client.
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_image(self, image_path):
        """
        Analyze an image using the vision LLM.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Dictionary containing analysis results.
        """
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Call vision model
        response = self.client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert insurance assessor. Analyze the image and identify all relevant objects, people, animals, furniture, appliances, electronics, sports equipment, etc. Count the items and assess potential risks and insurance needs."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image for insurance purposes. Identify all items, count them, and assess potential risks."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=1000
        )
        
        analysis = response.choices[0].message.content
        
        # Process the analysis to extract structured data
        return {
            "raw_analysis": analysis,
            "structured_data": self._extract_structured_data(analysis),
            "image_path": image_path
        }
    
    def _extract_structured_data(self, analysis_text):
        """
        Extract structured data from the analysis text.
        
        Args:
            analysis_text: The raw analysis text from the vision LLM.
            
        Returns:
            Dictionary containing structured data.
        """
        # This is a simplified implementation
        # In a real application, we would use more sophisticated NLP techniques
        
        # Try to identify items and counts
        items = []
        risks = []
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for items with counts
            if any(char.isdigit() for char in line) and any(word in line.lower() for word in ["item", "object", "furniture", "electronic", "appliance"]):
                items.append(line)
            
            # Look for risk assessments
            if any(word in line.lower() for word in ["risk", "hazard", "danger", "safety", "concern"]):
                risks.append(line)
        
        return {
            "items": items,
            "risks": risks,
            "item_count": len(items)
        }
    
    def detect_objects(self, image_path):
        """
        Detect objects in an image using OpenCV.
        This is a fallback method if the vision LLM is not available.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Dictionary containing detected objects.
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Failed to load image"}
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Simple object detection using contours
        # This is a placeholder for more sophisticated object detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size
        min_contour_area = 500
        significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
        
        return {
            "object_count": len(significant_contours),
            "image_path": image_path
        }
    
    def save_processed_image(self, image_path, output_path):
        """
        Save a processed version of the image with detected objects highlighted.
        
        Args:
            image_path: Path to the original image.
            output_path: Path to save the processed image.
            
        Returns:
            Path to the processed image.
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Process image (placeholder for more sophisticated processing)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours on the original image
        result = image.copy()
        cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
        
        # Save the result
        cv2.imwrite(output_path, result)
        
        return output_path
