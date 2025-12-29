"""
Property-based tests for simulation engine

**Feature: ai-persona-validator, Property 8: Simulation prompt generation consistency**
**Validates: Requirements 3.1**

**Feature: ai-persona-validator, Property 9: LLM response parsing reliability**
**Validates: Requirements 3.2, 3.4**

**Feature: ai-persona-validator, Property 11: Simulation caching effectiveness**
**Validates: Requirements 3.5**
"""

import pytest
import asyncio
from datetime import datetime
from hypothesis import given, strategies as st, settings
from app.models import (
    SyntheticPersona, FeatureDescription, Demographics, Psychographics, 
    BehaviorPatterns, ContextualFactors, SimulationResponse, SimulationDecision,
    TechnologyAdoption, RiskTolerance, ImplementationComplexity
)
from app.services.simulation_engine import SimulationEngine
from typing import List


# Generators for test data
@st.composite
def synthetic_persona_strategy(draw):
    """Generate valid SyntheticPersona instances for simulation testing"""
    return SyntheticPersona(
        id=draw(st.text(min_size=5, max_size=50).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
        name=draw(st.text(min_size=5, max_size=100).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
        demographics=Demographics(
            age=draw(st.integers(min_value=18, max_value=100)),
            role=draw(st.text(min_size=5, max_size=100).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
            company_size=draw(st.one_of(st.none(), st.text(min_size=3, max_size=50).filter(lambda x: '\n' not in x))),
            industry=draw(st.one_of(st.none(), st.text(min_size=3, max_size=100).filter(lambda x: '\n' not in x))),
            income=draw(st.one_of(st.none(), st.text(min_size=3, max_size=50).filter(lambda x: '\n' not in x)))
        ),
        psychographics=Psychographics(
            personality_traits=draw(st.lists(
                st.text(min_size=3, max_size=50).filter(lambda x: len(x.strip()) >= 3 and '\n' not in x),
                min_size=1, max_size=5
            )),
            values=draw(st.lists(
                st.text(min_size=3, max_size=50).filter(lambda x: len(x.strip()) >= 3 and '\n' not in x),
                min_size=1, max_size=5
            )),
            motivations=draw(st.lists(
                st.text(min_size=3, max_size=50).filter(lambda x: len(x.strip()) >= 3 and '\n' not in x),
                min_size=1, max_size=5
            )),
            pain_points=draw(st.lists(
                st.text(min_size=3, max_size=50).filter(lambda x: len(x.strip()) >= 3 and '\n' not in x),
                min_size=1, max_size=5
            ))
        ),
        behavior_patterns=BehaviorPatterns(
            technology_adoption=draw(st.sampled_from(list(TechnologyAdoption))),
            decision_making_style=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
            risk_tolerance=draw(st.sampled_from(list(RiskTolerance))),
            information_sources=draw(st.lists(
                st.text(min_size=3, max_size=50).filter(lambda x: len(x.strip()) >= 3 and '\n' not in x),
                min_size=1, max_size=5
            ))
        ),
        contextual_factors=ContextualFactors(
            current_solutions=draw(st.lists(
                st.text(min_size=3, max_size=50).filter(lambda x: len(x.strip()) >= 3 and '\n' not in x),
                min_size=0, max_size=5
            )),
            budget=draw(st.text(min_size=5, max_size=100).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
            time_constraints=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
            team_influence=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x))
        )
    )


@st.composite
def feature_description_strategy(draw):
    """Generate valid FeatureDescription instances for simulation testing"""
    return FeatureDescription(
        name=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
        description=draw(st.text(min_size=35, max_size=1000).filter(lambda x: len(x.strip()) >= 35 and '\n' not in x)),
        target_user=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5 and '\n' not in x)),
        value_proposition=draw(st.text(min_size=25, max_size=500).filter(lambda x: len(x.strip()) >= 25 and '\n' not in x)),
        pricing_model=draw(st.one_of(st.none(), st.text(min_size=5, max_size=200).filter(lambda x: '\n' not in x))),
        implementation_complexity=draw(st.one_of(st.none(), st.sampled_from(list(ImplementationComplexity)))),
        competitor_comparison=draw(st.one_of(st.none(), st.text(min_size=10, max_size=500).filter(lambda x: '\n' not in x)))
    )


class TestSimulationPromptGeneration:
    """Test simulation prompt generation consistency"""

    @given(synthetic_persona_strategy(), feature_description_strategy())
    @settings(max_examples=100, deadline=30000)
    def test_simulation_prompt_generation_consistency(self, persona: SyntheticPersona, feature: FeatureDescription):
        """
        Property 8: Simulation prompt generation consistency
        For any feature description and persona combination, a structured prompt should be 
        generated following the expected template format
        """
        engine = SimulationEngine()
        
        # Generate prompt
        prompt = engine._generate_prompt(persona, feature)
        
        # Verify prompt is non-empty string
        assert isinstance(prompt, str), "Prompt must be a string"
        assert len(prompt.strip()) > 0, "Prompt must be non-empty"
        
        # Verify prompt contains persona information
        assert persona.name in prompt, f"Prompt should contain persona name '{persona.name}'"
        assert persona.demographics.role in prompt, f"Prompt should contain persona role '{persona.demographics.role}'"
        
        # Verify prompt contains persona characteristics
        for trait in persona.psychographics.personality_traits:
            assert trait in prompt, f"Prompt should contain personality trait '{trait}'"
        
        for value in persona.psychographics.values:
            assert value in prompt, f"Prompt should contain value '{value}'"
        
        for pain_point in persona.psychographics.pain_points:
            assert pain_point in prompt, f"Prompt should contain pain point '{pain_point}'"
        
        # Verify prompt contains technology adoption and risk tolerance
        assert persona.behavior_patterns.technology_adoption.value in prompt, \
            f"Prompt should contain technology adoption '{persona.behavior_patterns.technology_adoption.value}'"
        
        # Verify prompt contains contextual factors
        for solution in persona.contextual_factors.current_solutions:
            assert solution in prompt, f"Prompt should contain current solution '{solution}'"
        
        assert persona.contextual_factors.budget in prompt, \
            f"Prompt should contain budget '{persona.contextual_factors.budget}'"
        assert persona.contextual_factors.time_constraints in prompt, \
            f"Prompt should contain time constraints '{persona.contextual_factors.time_constraints}'"
        
        # Verify prompt contains feature information
        assert feature.name in prompt, f"Prompt should contain feature name '{feature.name}'"
        assert feature.description in prompt, f"Prompt should contain feature description"
        assert feature.target_user in prompt, f"Prompt should contain target user '{feature.target_user}'"
        assert feature.value_proposition in prompt, f"Prompt should contain value proposition"
        
        # Verify prompt contains expected response format instructions
        expected_format_elements = [
            "DECISION: [ADOPT/REJECT/UNSURE]",
            "CONFIDENCE: [0.0-1.0]", 
            "REASONING: [One sentence explaining your decision]",
            "KEY_FACTORS: [List 2-3 most important factors in your decision]"
        ]
        
        for element in expected_format_elements:
            assert element in prompt, f"Prompt should contain format instruction '{element}'"
        
        # Verify prompt follows expected structure
        prompt_lines = prompt.split('\n')
        
        # Should start with persona introduction
        first_line = prompt_lines[0].strip()
        assert first_line.startswith(f"You are {persona.name}"), \
            f"Prompt should start with persona introduction, got: '{first_line}'"
        
        # Should contain characteristics section
        characteristics_found = any("Your characteristics:" in line for line in prompt_lines)
        assert characteristics_found, "Prompt should contain 'Your characteristics:' section"
        
        # Should contain feature section
        feature_section_found = any("A company is launching this feature:" in line for line in prompt_lines)
        assert feature_section_found, "Prompt should contain feature launch section"
        
        # Should end with response format
        response_format_found = any("Would you adopt this feature? Respond with:" in line for line in prompt_lines)
        assert response_format_found, "Prompt should contain response format instructions"

    @given(synthetic_persona_strategy(), feature_description_strategy())
    @settings(max_examples=50, deadline=30000)
    def test_prompt_generation_deterministic(self, persona: SyntheticPersona, feature: FeatureDescription):
        """
        Property 8: Prompt generation deterministic consistency
        For any identical persona-feature combination, the generated prompt should be identical
        """
        engine = SimulationEngine()
        
        # Generate prompt twice with same inputs
        prompt1 = engine._generate_prompt(persona, feature)
        prompt2 = engine._generate_prompt(persona, feature)
        
        # Should be identical
        assert prompt1 == prompt2, "Identical inputs should produce identical prompts"
        
        # Verify both prompts are valid
        assert len(prompt1.strip()) > 0
        assert len(prompt2.strip()) > 0

    @given(synthetic_persona_strategy(), feature_description_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_prompt_handles_optional_fields(self, persona: SyntheticPersona, feature: FeatureDescription):
        """
        Property 8: Prompt generation handles optional fields correctly
        For any persona-feature combination, optional fields should be handled gracefully
        """
        engine = SimulationEngine()
        
        # Generate prompt with original data
        prompt = engine._generate_prompt(persona, feature)
        
        # Verify optional fields are handled correctly
        if persona.demographics.company_size:
            assert persona.demographics.company_size in prompt
        
        if feature.pricing_model:
            assert feature.pricing_model in prompt
        
        # Test with None values for optional fields
        persona_copy = persona.model_copy()
        persona_copy.demographics.company_size = None
        persona_copy.demographics.industry = None
        persona_copy.demographics.income = None
        
        feature_copy = feature.model_copy()
        feature_copy.pricing_model = None
        feature_copy.implementation_complexity = None
        feature_copy.competitor_comparison = None
        
        # Should still generate valid prompt
        prompt_with_nones = engine._generate_prompt(persona_copy, feature_copy)
        assert len(prompt_with_nones.strip()) > 0
        assert persona.name in prompt_with_nones
        assert feature.name in prompt_with_nones


class TestLLMResponseParsing:
    """Test LLM response parsing reliability"""

    def test_llm_response_parsing_reliability_valid_responses(self):
        """
        Property 9: LLM response parsing reliability (Valid Responses)
        For any valid LLM response format, the system should parse it into the required structure
        or handle parsing errors gracefully
        """
        engine = SimulationEngine()
        
        # Test valid response formats
        valid_responses = [
            """DECISION: ADOPT
CONFIDENCE: 0.8
REASONING: This feature aligns well with my workflow needs
KEY_FACTORS: Cost-benefit analysis, Integration ease, Time savings""",
            
            """DECISION: REJECT
CONFIDENCE: 0.9
REASONING: Too expensive for our current budget constraints
KEY_FACTORS: Budget limitations, ROI concerns""",
            
            """DECISION: UNSURE
CONFIDENCE: 0.5
REASONING: Need more information about implementation timeline
KEY_FACTORS: Timeline uncertainty, Resource requirements, Risk assessment""",
            
            # Test with extra whitespace
            """  DECISION: ADOPT  
  CONFIDENCE: 0.7  
  REASONING: Good value proposition for our team  
  KEY_FACTORS: Team productivity, Cost effectiveness  """,
            
            # Test with different order
            """REASONING: This looks promising but needs evaluation
DECISION: UNSURE
KEY_FACTORS: Evaluation needed, Budget review
CONFIDENCE: 0.6"""
        ]
        
        for response_text in valid_responses:
            parsed = engine._parse_llm_response(response_text)
            
            # Verify all required fields are present
            assert "decision" in parsed, "Parsed response must contain decision"
            assert "confidence" in parsed, "Parsed response must contain confidence"
            assert "reasoning" in parsed, "Parsed response must contain reasoning"
            assert "key_factors" in parsed, "Parsed response must contain key_factors"
            
            # Verify field types and values
            assert isinstance(parsed["decision"], SimulationDecision), \
                "Decision must be SimulationDecision enum"
            assert isinstance(parsed["confidence"], (int, float)), \
                "Confidence must be numeric"
            assert 0.0 <= parsed["confidence"] <= 1.0, \
                f"Confidence must be between 0.0 and 1.0, got {parsed['confidence']}"
            assert isinstance(parsed["reasoning"], str), \
                "Reasoning must be string"
            assert len(parsed["reasoning"].strip()) > 0, \
                "Reasoning must be non-empty"
            assert isinstance(parsed["key_factors"], list), \
                "Key factors must be list"
            assert len(parsed["key_factors"]) > 0, \
                "Key factors must contain at least one factor"
            assert len(parsed["key_factors"]) <= 3, \
                "Key factors should contain at most 3 factors"

    def test_llm_response_parsing_reliability_malformed_responses(self):
        """
        Property 9: LLM response parsing reliability (Malformed Responses)
        For any malformed or invalid LLM response, the system should handle parsing errors gracefully
        """
        engine = SimulationEngine()
        
        # Test malformed responses
        malformed_responses = [
            "",  # Empty response
            "This is just random text without proper format",
            "DECISION: MAYBE\nCONFIDENCE: high\nREASONING: unclear",  # Invalid values
            "DECISION: ADOPT\nCONFIDENCE: 1.5\nREASONING: Good",  # Out of range confidence
            "DECISION: ADOPT\nCONFIDENCE: -0.2\nREASONING: Good",  # Negative confidence
            "DECISION: ADOPT\nCONFIDENCE: abc\nREASONING: Good",  # Non-numeric confidence
            "DECISION: ADOPT\nCONFIDENCE: 0.8",  # Missing fields
            "CONFIDENCE: 0.8\nREASONING: Good\nKEY_FACTORS: Factor1",  # Missing decision
            "DECISION: INVALID_DECISION\nCONFIDENCE: 0.8\nREASONING: Good",  # Invalid decision
        ]
        
        for response_text in malformed_responses:
            parsed = engine._parse_llm_response(response_text)
            
            # Should still return valid structure with fallback values
            assert "decision" in parsed, "Parsed response must contain decision field"
            assert "confidence" in parsed, "Parsed response must contain confidence field"
            assert "reasoning" in parsed, "Parsed response must contain reasoning field"
            assert "key_factors" in parsed, "Parsed response must contain key_factors field"
            
            # Verify fallback values are valid
            assert isinstance(parsed["decision"], SimulationDecision), \
                "Decision must be SimulationDecision enum even for malformed input"
            assert isinstance(parsed["confidence"], (int, float)), \
                "Confidence must be numeric even for malformed input"
            assert 0.0 <= parsed["confidence"] <= 1.0, \
                f"Confidence must be in valid range even for malformed input, got {parsed['confidence']}"
            assert isinstance(parsed["reasoning"], str), \
                "Reasoning must be string even for malformed input"
            assert len(parsed["reasoning"].strip()) > 0, \
                "Reasoning must be non-empty even for malformed input"
            assert isinstance(parsed["key_factors"], list), \
                "Key factors must be list even for malformed input"
            assert len(parsed["key_factors"]) > 0, \
                "Key factors must contain at least one factor even for malformed input"

    def test_llm_response_parsing_edge_cases(self):
        """
        Property 9: LLM response parsing reliability (Edge Cases)
        For any edge case LLM responses, parsing should handle them appropriately
        """
        engine = SimulationEngine()
        
        # Test edge cases
        edge_cases = [
            # Confidence boundary values
            "DECISION: ADOPT\nCONFIDENCE: 0.0\nREASONING: Minimum confidence\nKEY_FACTORS: Test",
            "DECISION: ADOPT\nCONFIDENCE: 1.0\nREASONING: Maximum confidence\nKEY_FACTORS: Test",
            
            # Very long reasoning
            f"DECISION: ADOPT\nCONFIDENCE: 0.8\nREASONING: {'Very long reasoning ' * 50}\nKEY_FACTORS: Test",
            
            # Many key factors
            "DECISION: ADOPT\nCONFIDENCE: 0.8\nREASONING: Good\nKEY_FACTORS: Factor1, Factor2, Factor3, Factor4, Factor5",
            
            # Empty key factors
            "DECISION: ADOPT\nCONFIDENCE: 0.8\nREASONING: Good\nKEY_FACTORS: ",
            
            # Special characters in text
            "DECISION: ADOPT\nCONFIDENCE: 0.8\nREASONING: Good with $pecial ch@rs!\nKEY_FACTORS: Cost-benefit, ROI%",
        ]
        
        for response_text in edge_cases:
            parsed = engine._parse_llm_response(response_text)
            
            # Should handle edge cases gracefully
            assert isinstance(parsed["decision"], SimulationDecision)
            assert 0.0 <= parsed["confidence"] <= 1.0
            assert isinstance(parsed["reasoning"], str)
            assert len(parsed["reasoning"].strip()) > 0
            assert isinstance(parsed["key_factors"], list)
            assert len(parsed["key_factors"]) > 0
            
            # Key factors should be limited to 3
            assert len(parsed["key_factors"]) <= 3


class TestSimulationCaching:
    """Test simulation caching effectiveness"""

    @given(synthetic_persona_strategy(), feature_description_strategy())
    @settings(max_examples=50, deadline=30000)
    def test_simulation_caching_effectiveness(self, persona: SyntheticPersona, feature: FeatureDescription):
        """
        Property 11: Simulation caching effectiveness
        For any identical simulation query, the second execution should use cached results 
        rather than re-running the LLM call
        """
        engine = SimulationEngine()
        
        # Clear cache to start fresh
        engine.cache.clear()
        
        # First simulation - should not be cached
        result1 = asyncio.run(engine.simulate_persona_reaction(persona, feature))
        
        # Verify result structure
        assert isinstance(result1, SimulationResponse)
        assert result1.persona_id == persona.id
        assert isinstance(result1.decision, SimulationDecision)
        assert 0.0 <= result1.confidence <= 1.0
        assert len(result1.reasoning.strip()) > 0
        assert len(result1.key_factors) > 0
        
        # Check that cache now contains the result
        cache_key = engine._generate_cache_key(persona, feature)
        assert cache_key in engine.cache, "Result should be cached after first simulation"
        
        # Second simulation - should use cache
        result2 = asyncio.run(engine.simulate_persona_reaction(persona, feature))
        
        # Results should be identical (same object from cache)
        assert result1 is result2, "Second call should return cached result (same object)"
        assert result1.persona_id == result2.persona_id
        assert result1.decision == result2.decision
        assert result1.confidence == result2.confidence
        assert result1.reasoning == result2.reasoning
        assert result1.key_factors == result2.key_factors
        assert result1.timestamp == result2.timestamp
        assert result1.model_used == result2.model_used

    @given(synthetic_persona_strategy(), feature_description_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_cache_key_generation_consistency(self, persona: SyntheticPersona, feature: FeatureDescription):
        """
        Property 11: Cache key generation consistency
        For any identical persona-feature combination, the cache key should be identical
        """
        engine = SimulationEngine()
        
        # Generate cache key multiple times
        key1 = engine._generate_cache_key(persona, feature)
        key2 = engine._generate_cache_key(persona, feature)
        key3 = engine._generate_cache_key(persona, feature)
        
        # Should be identical
        assert key1 == key2 == key3, "Cache keys should be identical for same inputs"
        
        # Should be non-empty string
        assert isinstance(key1, str)
        assert len(key1) > 0
        
        # Should be deterministic hash (MD5 produces 32 character hex string)
        assert len(key1) == 32, f"Cache key should be 32 character MD5 hash, got {len(key1)}"
        assert all(c in '0123456789abcdef' for c in key1), "Cache key should be valid hex string"

    @given(synthetic_persona_strategy(), feature_description_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_cache_key_uniqueness(self, persona: SyntheticPersona, feature: FeatureDescription):
        """
        Property 11: Cache key uniqueness
        For any different persona-feature combinations, cache keys should be different
        """
        engine = SimulationEngine()
        
        # Original cache key
        original_key = engine._generate_cache_key(persona, feature)
        
        # Modify persona slightly
        modified_persona = persona.model_copy()
        modified_persona.name = persona.name + "_modified"
        modified_key = engine._generate_cache_key(modified_persona, feature)
        
        # Keys should be different
        assert original_key != modified_key, "Different personas should produce different cache keys"
        
        # Modify feature slightly
        modified_feature = feature.model_copy()
        modified_feature.name = feature.name + "_modified"
        feature_modified_key = engine._generate_cache_key(persona, modified_feature)
        
        # Keys should be different
        assert original_key != feature_modified_key, "Different features should produce different cache keys"
        assert modified_key != feature_modified_key, "All different combinations should have unique keys"

    def test_cache_isolation_between_engines(self):
        """
        Property 11: Cache isolation between engine instances
        Different engine instances should have separate caches
        """
        # Create two engine instances
        engine1 = SimulationEngine()
        engine2 = SimulationEngine()
        
        # Clear both caches
        engine1.cache.clear()
        engine2.cache.clear()
        
        # Add something to engine1 cache
        test_key = "test_key"
        test_response = SimulationResponse(
            persona_id="test_persona",
            decision=SimulationDecision.ADOPT,
            confidence=0.8,
            reasoning="Test reasoning",
            key_factors=["Test factor"],
            timestamp=datetime.utcnow(),
            model_used="test_model"
        )
        
        engine1.cache[test_key] = test_response
        
        # Verify isolation
        assert test_key in engine1.cache, "Engine1 should have the cached item"
        assert test_key not in engine2.cache, "Engine2 should not have the cached item"
        assert len(engine1.cache) == 1, "Engine1 should have 1 cached item"
        assert len(engine2.cache) == 0, "Engine2 should have 0 cached items"


if __name__ == "__main__":
    pytest.main([__file__])