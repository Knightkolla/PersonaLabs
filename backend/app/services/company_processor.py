from app.models import CompanyInput, CompanyContext, FeatureDescription
import uuid
from typing import List, Dict, Any
from pydantic import ValidationError

class ValidationError(Exception):
    """Custom validation error for company context processing"""
    def __init__(self, message: str, missing_fields: List[str] = None):
        self.message = message
        self.missing_fields = missing_fields or []
        super().__init__(self.message)

class CompanyContextProcessor:
    """Processes and enriches company input data"""
    
    def validate_company_input(self, company_input: CompanyInput) -> Dict[str, Any]:
        """
        Validate company input for completeness and quality
        
        Args:
            company_input: Company input to validate
            
        Returns:
            Dict containing validation results and missing information
            
        Raises:
            ValidationError: If input is insufficient for persona generation
        """
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "suggestions": [],
            "quality_score": 0.0
        }
        
        # Check required fields completeness
        required_checks = [
            ("name", company_input.name, "Company name is required"),
            ("industry", company_input.industry, "Industry information is required"),
            ("target_market", company_input.target_market, "Target market description is required")
        ]
        
        for field_name, field_value, error_msg in required_checks:
            if not field_value or len(field_value.strip()) < 3:
                validation_result["missing_fields"].append(field_name)
                validation_result["suggestions"].append(error_msg)
                validation_result["is_valid"] = False
        
        # Check for sufficient detail in target market description
        if company_input.target_market and len(company_input.target_market.strip()) < 20:
            validation_result["suggestions"].append(
                "Target market description should be more detailed (at least 20 characters) for better persona generation"
            )
            validation_result["quality_score"] -= 0.2
        
        # Check for description quality
        if not company_input.description or len(company_input.description.strip()) < 10:
            validation_result["suggestions"].append(
                "Company description would help generate more accurate personas"
            )
            validation_result["quality_score"] -= 0.1
        
        # Calculate quality score (0.0 to 1.0)
        base_score = 0.7  # Base score for having all required fields
        if validation_result["is_valid"]:
            validation_result["quality_score"] = base_score
            
            # Bonus for detailed target market
            if len(company_input.target_market.strip()) >= 50:
                validation_result["quality_score"] += 0.1
                
            # Bonus for company description
            if company_input.description and len(company_input.description.strip()) >= 50:
                validation_result["quality_score"] += 0.1
                
            # Bonus for specific industry
            if len(company_input.industry.strip()) >= 10:
                validation_result["quality_score"] += 0.1
        else:
            validation_result["quality_score"] = 0.0
        
        # Raise error if validation fails
        if not validation_result["is_valid"]:
            raise ValidationError(
                "Insufficient information for persona generation",
                validation_result["missing_fields"]
            )
        
        return validation_result
    
    def validate_feature_description(self, feature_description: FeatureDescription) -> Dict[str, Any]:
        """
        Validate feature description for completeness and quality
        
        Args:
            feature_description: Feature description to validate
            
        Returns:
            Dict containing validation results and missing information
            
        Raises:
            ValidationError: If description is insufficient for simulation
        """
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "suggestions": [],
            "quality_score": 0.0
        }
        
        # Check required fields completeness
        required_checks = [
            ("name", feature_description.name, "Feature name is required"),
            ("description", feature_description.description, "Feature description is required"),
            ("target_user", feature_description.target_user, "Target user information is required"),
            ("value_proposition", feature_description.value_proposition, "Value proposition is required")
        ]
        
        for field_name, field_value, error_msg in required_checks:
            if not field_value or len(field_value.strip()) < 3:
                validation_result["missing_fields"].append(field_name)
                validation_result["suggestions"].append(error_msg)
                validation_result["is_valid"] = False
        
        # Check for sufficient detail in description
        if feature_description.description and len(feature_description.description.strip()) < 30:
            validation_result["suggestions"].append(
                "Feature description should be more detailed (at least 30 characters) for better simulation"
            )
            validation_result["quality_score"] -= 0.2
        
        # Check for clear value proposition
        if feature_description.value_proposition and len(feature_description.value_proposition.strip()) < 20:
            validation_result["suggestions"].append(
                "Value proposition should be more detailed for better persona simulation"
            )
            validation_result["quality_score"] -= 0.1
        
        # Calculate quality score
        base_score = 0.7
        if validation_result["is_valid"]:
            validation_result["quality_score"] = base_score
            
            # Bonus for detailed description
            if len(feature_description.description.strip()) >= 100:
                validation_result["quality_score"] += 0.1
                
            # Bonus for detailed value proposition
            if len(feature_description.value_proposition.strip()) >= 50:
                validation_result["quality_score"] += 0.1
                
            # Bonus for pricing model
            if feature_description.pricing_model:
                validation_result["quality_score"] += 0.05
                
            # Bonus for implementation complexity
            if feature_description.implementation_complexity:
                validation_result["quality_score"] += 0.05
        else:
            validation_result["quality_score"] = 0.0
        
        # Raise error if validation fails
        if not validation_result["is_valid"]:
            raise ValidationError(
                "Insufficient feature information for simulation",
                validation_result["missing_fields"]
            )
        
        return validation_result
    
    async def process_company_input(self, company_input: CompanyInput) -> CompanyContext:
        """
        Process company input and create enriched context
        
        Args:
            company_input: Raw company information from user
            
        Returns:
            CompanyContext: Enriched context with additional insights
            
        Raises:
            ValidationError: If input validation fails
        """
        # Validate input first
        validation_result = self.validate_company_input(company_input)
        
        # Generate unique context ID
        context_id = str(uuid.uuid4())
        
        # Basic enrichment (placeholder for now)
        enriched_context = {
            "industry_characteristics": self._get_industry_characteristics(company_input.industry),
            "typical_customer_profiles": self._get_customer_profiles(company_input),
            "competitive_landscape": self._get_competitive_landscape(company_input),
            "adoption_patterns": self._get_adoption_patterns(company_input),
            "validation_quality_score": validation_result["quality_score"]
        }
        
        # Generate persona seeds
        persona_seeds = self._generate_persona_seeds(company_input)
        
        # Create CompanyContext manually to avoid Pydantic validation issues
        context = CompanyContext.model_construct(
            id=context_id,
            input=company_input,
            enriched_context=enriched_context,
            persona_seeds=persona_seeds
        )
        return context
    
    def _get_industry_characteristics(self, industry: str) -> list[str]:
        """Get characteristics specific to the industry"""
        # Placeholder implementation
        return [
            f"Operates in {industry} sector",
            "Subject to industry-specific regulations",
            "Follows industry best practices"
        ]
    
    def _get_customer_profiles(self, company_input: CompanyInput) -> list[str]:
        """Generate typical customer profiles based on company info"""
        # Placeholder implementation
        profiles = []
        
        if company_input.business_model == "B2B":
            profiles.extend([
                "Decision makers in target companies",
                "Technical evaluators and implementers",
                "Budget holders and procurement teams"
            ])
        elif company_input.business_model == "B2C":
            profiles.extend([
                "Individual consumers in target market",
                "Early adopters and tech enthusiasts",
                "Price-conscious mainstream users"
            ])
        
        return profiles
    
    def _get_competitive_landscape(self, company_input: CompanyInput) -> str:
        """Analyze competitive landscape"""
        # Placeholder implementation
        return f"Competitive landscape in {company_input.industry} with {company_input.business_model} model"
    
    def _get_adoption_patterns(self, company_input: CompanyInput) -> str:
        """Determine typical adoption patterns for this context"""
        # Placeholder implementation
        size_patterns = {
            "Startup": "Fast adoption, high risk tolerance",
            "SMB": "Moderate adoption, cost-conscious",
            "Mid-Market": "Careful evaluation, ROI-focused",
            "Enterprise": "Slow adoption, extensive evaluation"
        }
        
        return size_patterns.get(company_input.company_size.value, "Standard adoption patterns")
    
    def _generate_persona_seeds(self, company_input: CompanyInput) -> list[dict]:
        """Generate initial persona seeds for later enrichment"""
        # Placeholder implementation - basic seeds
        seeds = []
        
        # Generate 8-10 diverse seeds based on company context
        base_roles = self._get_base_roles(company_input)
        
        for i, role in enumerate(base_roles[:8]):
            seed = {
                "seed_id": f"seed_{i+1}",
                "base_role": role,
                "company_context": company_input.industry,
                "business_model": company_input.business_model.value
            }
            seeds.append(seed)
        
        return seeds
    
    def _get_base_roles(self, company_input: CompanyInput) -> list[str]:
        """Get base roles relevant to the company context"""
        if company_input.business_model == "B2B":
            return [
                "IT Director", "Product Manager", "Operations Manager",
                "CEO/Founder", "Finance Manager", "Sales Director",
                "Technical Lead", "Procurement Specialist"
            ]
        else:  # B2C, B2B2C, Marketplace
            return [
                "Tech-savvy Professional", "Budget-conscious Consumer",
                "Early Adopter", "Mainstream User", "Senior Executive",
                "Small Business Owner", "Freelancer", "Student"
            ]