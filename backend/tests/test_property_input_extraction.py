"""
Property-based tests for input field extraction completeness and validation effectiveness

**Feature: ai-persona-validator, Property 1: Input field extraction completeness**
**Validates: Requirements 1.1, 1.2**

**Feature: ai-persona-validator, Property 2: Input validation effectiveness**
**Validates: Requirements 1.3, 1.4**
"""

import pytest
import asyncio
from hypothesis import given, strategies as st
from app.models import CompanyInput, FeatureDescription, BusinessModel, CompanySize, ImplementationComplexity
from app.services.company_processor import CompanyContextProcessor, ValidationError


# Generators for valid input data
@st.composite
def company_input_strategy(draw):
    """Generate valid CompanyInput instances that pass business validation"""
    return CompanyInput(
        name=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5)),
        industry=draw(st.text(min_size=5, max_size=100).filter(lambda x: len(x.strip()) >= 5)),
        business_model=draw(st.sampled_from(list(BusinessModel))),
        target_market=draw(st.text(min_size=25, max_size=500).filter(lambda x: len(x.strip()) >= 25)),
        company_size=draw(st.sampled_from(list(CompanySize))),
        description=draw(st.one_of(st.none(), st.text(min_size=15, max_size=1000).filter(lambda x: len(x.strip()) >= 15)))
    )

# Generators for incomplete/invalid input data
@st.composite
def incomplete_company_input_strategy(draw):
    """Generate CompanyInput instances with missing or insufficient data"""
    # Generate potentially invalid fields (but still pass Pydantic validation)
    name = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=200).filter(lambda x: x.strip())  # Valid
    ))
    
    industry = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=100).filter(lambda x: x.strip())  # Valid
    ))
    
    target_market = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=500).filter(lambda x: x.strip())  # Valid
    ))
    
    return CompanyInput(
        name=name,
        industry=industry,
        business_model=draw(st.sampled_from(list(BusinessModel))),
        target_market=target_market,
        company_size=draw(st.sampled_from(list(CompanySize))),
        description=draw(st.one_of(st.none(), st.text(max_size=1000)))
    )

@st.composite
def incomplete_feature_description_strategy(draw):
    """Generate FeatureDescription instances with missing or insufficient data"""
    name = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=200).filter(lambda x: x.strip())  # Valid
    ))
    
    description = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=1000).filter(lambda x: x.strip())  # Valid
    ))
    
    target_user = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=200).filter(lambda x: x.strip())  # Valid
    ))
    
    value_proposition = draw(st.one_of(
        st.text(min_size=1, max_size=2),  # Too short for business logic
        st.text(min_size=3, max_size=500).filter(lambda x: x.strip())  # Valid
    ))
    
    return FeatureDescription(
        name=name,
        description=description,
        target_user=target_user,
        value_proposition=value_proposition,
        pricing_model=draw(st.one_of(st.none(), st.text(max_size=200))),
        implementation_complexity=draw(st.one_of(st.none(), st.sampled_from(list(ImplementationComplexity)))),
        competitor_comparison=draw(st.one_of(st.none(), st.text(max_size=500)))
    )


@st.composite
def feature_description_strategy(draw):
    """Generate valid FeatureDescription instances that pass business validation"""
    return FeatureDescription(
        name=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5)),
        description=draw(st.text(min_size=35, max_size=1000).filter(lambda x: len(x.strip()) >= 35)),
        target_user=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5)),
        value_proposition=draw(st.text(min_size=25, max_size=500).filter(lambda x: len(x.strip()) >= 25)),
        pricing_model=draw(st.one_of(st.none(), st.text(max_size=200))),
        implementation_complexity=draw(st.one_of(st.none(), st.sampled_from(list(ImplementationComplexity)))),
        competitor_comparison=draw(st.one_of(st.none(), st.text(max_size=500)))
    )


class TestInputFieldExtraction:
    """Test input field extraction completeness"""

    @given(company_input_strategy())
    def test_company_input_field_extraction_completeness(self, company_input: CompanyInput):
        """
        Property 1: Input field extraction completeness
        For any company input, all required fields should be correctly extracted and stored
        """
        processor = CompanyContextProcessor()
        
        # Process the company input
        company_context = asyncio.run(processor.process_company_input(company_input))
        
        # Verify all required fields are extracted and preserved
        assert company_context.input.name == company_input.name
        assert company_context.input.industry == company_input.industry
        assert company_context.input.business_model == company_input.business_model
        assert company_context.input.target_market == company_input.target_market
        assert company_context.input.company_size == company_input.company_size
        assert company_context.input.description == company_input.description
        
        # Verify context has required structure
        assert company_context.id is not None
        assert len(company_context.id) > 0
        assert isinstance(company_context.enriched_context, dict)
        assert isinstance(company_context.persona_seeds, list)
        
        # Verify enriched context contains expected keys
        expected_keys = [
            "industry_characteristics",
            "typical_customer_profiles", 
            "competitive_landscape",
            "adoption_patterns"
        ]
        for key in expected_keys:
            assert key in company_context.enriched_context
        
        # Verify persona seeds are generated
        assert len(company_context.persona_seeds) > 0
        assert len(company_context.persona_seeds) <= 10  # Should generate 8-10 seeds

    @given(feature_description_strategy())
    def test_feature_description_field_extraction_completeness(self, feature_description: FeatureDescription):
        """
        Property 1: Input field extraction completeness (Feature Description)
        For any feature description input, all required fields should be correctly extracted and stored
        """
        # Verify all required fields are present and valid
        assert feature_description.name is not None
        assert len(feature_description.name.strip()) > 0
        assert len(feature_description.name) <= 200
        
        assert feature_description.description is not None
        assert len(feature_description.description.strip()) > 0
        assert len(feature_description.description) <= 1000
        
        assert feature_description.target_user is not None
        assert len(feature_description.target_user.strip()) > 0
        assert len(feature_description.target_user) <= 200
        
        assert feature_description.value_proposition is not None
        assert len(feature_description.value_proposition.strip()) > 0
        assert len(feature_description.value_proposition) <= 500
        
        # Verify optional fields are handled correctly
        if feature_description.pricing_model is not None:
            assert len(feature_description.pricing_model) <= 200
            
        if feature_description.competitor_comparison is not None:
            assert len(feature_description.competitor_comparison) <= 500

    @given(company_input_strategy())
    def test_company_context_enrichment_consistency(self, company_input: CompanyInput):
        """
        Property 1: Input field extraction completeness (Enrichment Consistency)
        For any company input, enrichment should be consistent and contextually relevant
        """
        processor = CompanyContextProcessor()
        
        # Process the same input twice
        context1 = asyncio.run(processor.process_company_input(company_input))
        context2 = asyncio.run(processor.process_company_input(company_input))
        
        # Verify enrichment is consistent (same input produces similar structure)
        assert len(context1.enriched_context) == len(context2.enriched_context)
        assert set(context1.enriched_context.keys()) == set(context2.enriched_context.keys())
        
        # Verify persona seeds are generated consistently
        assert len(context1.persona_seeds) == len(context2.persona_seeds)
        
        # Verify industry appears in enriched context
        industry_mentioned = any(
            company_input.industry.lower() in str(value).lower()
            for value in context1.enriched_context.values()
            if isinstance(value, (str, list))
        )
        assert industry_mentioned, f"Industry '{company_input.industry}' should be mentioned in enriched context"


class TestInputValidationEffectiveness:
    """Test input validation effectiveness"""

    @given(incomplete_company_input_strategy())
    def test_company_input_validation_effectiveness(self, company_input: CompanyInput):
        """
        Property 2: Input validation effectiveness
        For any incomplete input data, the system should identify missing required information
        and prompt for additional details
        """
        processor = CompanyContextProcessor()
        
        # Check if input has insufficient data
        has_insufficient_name = not company_input.name or len(company_input.name.strip()) < 3
        has_insufficient_industry = not company_input.industry or len(company_input.industry.strip()) < 3
        has_insufficient_target_market = not company_input.target_market or len(company_input.target_market.strip()) < 3
        
        is_insufficient = has_insufficient_name or has_insufficient_industry or has_insufficient_target_market
        
        if is_insufficient:
            # Should raise ValidationError for insufficient input
            with pytest.raises(ValidationError) as exc_info:
                processor.validate_company_input(company_input)
            
            # Verify error contains missing fields information
            error = exc_info.value
            assert error.missing_fields is not None
            assert len(error.missing_fields) > 0
            assert "Insufficient information for persona generation" in error.message
            
            # Verify specific missing fields are identified
            if has_insufficient_name:
                assert "name" in error.missing_fields
            if has_insufficient_industry:
                assert "industry" in error.missing_fields
            if has_insufficient_target_market:
                assert "target_market" in error.missing_fields
        else:
            # Should pass validation for sufficient input
            validation_result = processor.validate_company_input(company_input)
            assert validation_result["is_valid"] is True
            assert len(validation_result["missing_fields"]) == 0
            assert validation_result["quality_score"] > 0.0

    @given(incomplete_feature_description_strategy())
    def test_feature_description_validation_effectiveness(self, feature_description: FeatureDescription):
        """
        Property 2: Input validation effectiveness (Feature Description)
        For any incomplete feature description, the system should identify missing required information
        and prompt for additional details
        """
        processor = CompanyContextProcessor()
        
        # Check if input has insufficient data
        has_insufficient_name = not feature_description.name or len(feature_description.name.strip()) < 3
        has_insufficient_description = not feature_description.description or len(feature_description.description.strip()) < 3
        has_insufficient_target_user = not feature_description.target_user or len(feature_description.target_user.strip()) < 3
        has_insufficient_value_prop = not feature_description.value_proposition or len(feature_description.value_proposition.strip()) < 3
        
        is_insufficient = (has_insufficient_name or has_insufficient_description or 
                          has_insufficient_target_user or has_insufficient_value_prop)
        
        if is_insufficient:
            # Should raise ValidationError for insufficient input
            with pytest.raises(ValidationError) as exc_info:
                processor.validate_feature_description(feature_description)
            
            # Verify error contains missing fields information
            error = exc_info.value
            assert error.missing_fields is not None
            assert len(error.missing_fields) > 0
            assert "Insufficient feature information for simulation" in error.message
            
            # Verify specific missing fields are identified
            if has_insufficient_name:
                assert "name" in error.missing_fields
            if has_insufficient_description:
                assert "description" in error.missing_fields
            if has_insufficient_target_user:
                assert "target_user" in error.missing_fields
            if has_insufficient_value_prop:
                assert "value_proposition" in error.missing_fields
        else:
            # Should pass validation for sufficient input
            validation_result = processor.validate_feature_description(feature_description)
            assert validation_result["is_valid"] is True
            assert len(validation_result["missing_fields"]) == 0
            assert validation_result["quality_score"] > 0.0

    @given(company_input_strategy())
    def test_validation_quality_scoring(self, company_input: CompanyInput):
        """
        Property 2: Input validation effectiveness (Quality Scoring)
        For any valid company input, validation should provide quality scores and suggestions
        """
        processor = CompanyContextProcessor()
        
        try:
            validation_result = processor.validate_company_input(company_input)
            
            # Verify validation result structure
            assert "is_valid" in validation_result
            assert "missing_fields" in validation_result
            assert "suggestions" in validation_result
            assert "quality_score" in validation_result
            
            # Verify quality score is in valid range
            assert 0.0 <= validation_result["quality_score"] <= 1.0
            
            # For valid inputs, should have positive quality score
            if validation_result["is_valid"]:
                assert validation_result["quality_score"] > 0.0
                assert len(validation_result["missing_fields"]) == 0
            
            # Quality score should reflect input completeness
            if company_input.description and len(company_input.description.strip()) >= 50:
                # Should get bonus for detailed description
                assert validation_result["quality_score"] >= 0.7
            
            if len(company_input.target_market.strip()) >= 50:
                # Should get bonus for detailed target market
                assert validation_result["quality_score"] >= 0.7
                
        except ValidationError as e:
            # If validation fails, it should be due to insufficient field length
            assert e.missing_fields is not None
            assert len(e.missing_fields) > 0
            
            # Check that the failing fields are indeed too short
            if "name" in e.missing_fields:
                assert len(company_input.name.strip()) < 3
            if "industry" in e.missing_fields:
                assert len(company_input.industry.strip()) < 3
            if "target_market" in e.missing_fields:
                assert len(company_input.target_market.strip()) < 3

    @given(feature_description_strategy())
    def test_feature_validation_quality_scoring(self, feature_description: FeatureDescription):
        """
        Property 2: Input validation effectiveness (Feature Quality Scoring)
        For any valid feature description, validation should provide quality scores and suggestions
        """
        processor = CompanyContextProcessor()
        
        try:
            validation_result = processor.validate_feature_description(feature_description)
            
            # Verify validation result structure
            assert "is_valid" in validation_result
            assert "missing_fields" in validation_result
            assert "suggestions" in validation_result
            assert "quality_score" in validation_result
            
            # Verify quality score is in valid range
            assert 0.0 <= validation_result["quality_score"] <= 1.0
            
            # For valid inputs, should have positive quality score
            if validation_result["is_valid"]:
                assert validation_result["quality_score"] > 0.0
                assert len(validation_result["missing_fields"]) == 0
            
            # Quality score should reflect input completeness
            if len(feature_description.description.strip()) >= 100:
                # Should get bonus for detailed description
                assert validation_result["quality_score"] >= 0.7
            
            if feature_description.pricing_model:
                # Should get bonus for pricing model
                assert validation_result["quality_score"] >= 0.7
                
        except ValidationError as e:
            # If validation fails, it should be due to insufficient field length
            assert e.missing_fields is not None
            assert len(e.missing_fields) > 0
            
            # Check that the failing fields are indeed too short
            if "name" in e.missing_fields:
                assert len(feature_description.name.strip()) < 3
            if "description" in e.missing_fields:
                assert len(feature_description.description.strip()) < 3
            if "target_user" in e.missing_fields:
                assert len(feature_description.target_user.strip()) < 3
            if "value_proposition" in e.missing_fields:
                assert len(feature_description.value_proposition.strip()) < 3


if __name__ == "__main__":
    pytest.main([__file__])