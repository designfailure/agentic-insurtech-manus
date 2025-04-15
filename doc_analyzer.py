"""
Document analyzer tool for analyzing insurance documents and images.
"""
from app.agents.tools.mock_crewai import BaseTool
import json
import re
from datetime import datetime

class DocAnalyzerTool:
    """
    Tool for analyzing insurance documents and extracting relevant information.
    """
    def __init__(self):
        """
        Initialize the document analyzer tool.
        """
        # Document types and their key patterns
        self.document_patterns = {
            "policy": [
                r"policy\s+number",
                r"coverage\s+amount",
                r"premium",
                r"effective\s+date",
                r"expiration\s+date"
            ],
            "claim": [
                r"claim\s+number",
                r"incident\s+date",
                r"damage\s+description",
                r"estimated\s+loss"
            ],
            "invoice": [
                r"invoice\s+number",
                r"amount\s+due",
                r"payment\s+date",
                r"service\s+description"
            ],
            "receipt": [
                r"receipt\s+number",
                r"purchase\s+date",
                r"item\s+description",
                r"amount\s+paid"
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            "policy_number": r"policy\s+(?:number|#)[:.\s]*([A-Z0-9-]+)",
            "claim_number": r"claim\s+(?:number|#)[:.\s]*([A-Z0-9-]+)",
            "date": r"(?:date|effective|expiration)[:.\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})",
            "amount": r"(?:amount|coverage|premium|paid|due)[:.\s]*[$]?(\d+(?:,\d+)*(?:\.\d+)?)",
            "name": r"(?:name|insured|policyholder)[:.\s]*([A-Za-z\s]+)(?:\n|,|\.|$)",
            "address": r"(?:address|location)[:.\s]*([A-Za-z0-9\s,]+)(?:\n|,|\.|$)",
            "phone": r"(?:phone|tel|telephone)[:.\s]*(\+?[\d\s()-]{10,})",
            "email": r"(?:email|e-mail)[:.\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        }
    
    def analyze_document(self, document_text):
        """
        Analyze a document and extract relevant information.
        
        Args:
            document_text: The text content of the document.
            
        Returns:
            Dictionary containing analysis results.
        """
        # Determine document type
        doc_type = self._identify_document_type(document_text)
        
        # Extract entities
        entities = self._extract_entities(document_text)
        
        # Extract key-value pairs
        key_values = self._extract_key_values(document_text)
        
        return {
            "document_type": doc_type,
            "entities": entities,
            "key_values": key_values,
            "summary": self._generate_summary(doc_type, entities, key_values)
        }
    
    def _identify_document_type(self, text):
        """
        Identify the type of document based on pattern matching.
        
        Args:
            text: The document text.
            
        Returns:
            String indicating document type.
        """
        type_scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            type_scores[doc_type] = score
        
        # Get the document type with the highest score
        if not type_scores:
            return "unknown"
        
        max_score = max(type_scores.values())
        if max_score == 0:
            return "unknown"
        
        # Get all types with the max score
        max_types = [t for t, s in type_scores.items() if s == max_score]
        return max_types[0]  # Return the first one if there are ties
    
    def _extract_entities(self, text):
        """
        Extract entities from document text using regex patterns.
        
        Args:
            text: The document text.
            
        Returns:
            Dictionary of extracted entities.
        """
        entities = {}
        
        for entity_name, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_name] = matches[0].strip()
        
        return entities
    
    def _extract_key_values(self, text):
        """
        Extract key-value pairs from document text.
        
        Args:
            text: The document text.
            
        Returns:
            Dictionary of key-value pairs.
        """
        key_values = {}
        
        # Look for patterns like "Key: Value" or "Key - Value"
        kv_pattern = r"([A-Za-z\s]+)[:.-]\s*([A-Za-z0-9\s,.$-]+)(?:\n|$)"
        matches = re.findall(kv_pattern, text)
        
        for key, value in matches:
            key = key.strip().lower()
            value = value.strip()
            if key and value:
                key_values[key] = value
        
        return key_values
    
    def _generate_summary(self, doc_type, entities, key_values):
        """
        Generate a summary of the document analysis.
        
        Args:
            doc_type: The identified document type.
            entities: Extracted entities.
            key_values: Extracted key-value pairs.
            
        Returns:
            Summary string.
        """
        summary = f"This appears to be a {doc_type.upper()} document. "
        
        if doc_type == "policy":
            if "policy_number" in entities:
                summary += f"Policy number: {entities['policy_number']}. "
            if "name" in entities:
                summary += f"Policyholder: {entities['name']}. "
            if "amount" in entities:
                summary += f"Coverage amount: ${entities['amount']}. "
            if "date" in entities:
                summary += f"Effective date: {entities['date']}. "
        
        elif doc_type == "claim":
            if "claim_number" in entities:
                summary += f"Claim number: {entities['claim_number']}. "
            if "date" in entities:
                summary += f"Incident date: {entities['date']}. "
            if "amount" in entities:
                summary += f"Estimated loss: ${entities['amount']}. "
        
        elif doc_type == "invoice" or doc_type == "receipt":
            if "amount" in entities:
                summary += f"Amount: ${entities['amount']}. "
            if "date" in entities:
                summary += f"Date: {entities['date']}. "
        
        # Add any additional key-value information
        if key_values:
            summary += "Additional information: "
            for key, value in key_values.items():
                if key not in ["policy number", "claim number", "date", "amount", "name"]:
                    summary += f"{key}: {value}, "
            summary = summary.rstrip(", ") + "."
        
        return summary
    
    def get_tool(self):
        """
        Get the CrewAI tool for document analysis.
        
        Returns:
            CrewAI BaseTool instance.
        """
        return BaseTool(
            name="document_analysis_tool",
            description="Analyzes insurance documents and extracts relevant information",
            func=self._document_analysis_tool
        )
    
    def _document_analysis_tool(self, document_text):
        """
        Tool function for document analysis.
        
        Args:
            document_text: The text content of the document.
            
        Returns:
            JSON string of analysis results.
        """
        try:
            results = self.analyze_document(document_text)
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
