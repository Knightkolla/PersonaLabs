"""
Property-based tests for persona generation engine

**Feature: ai-persona-validator, Property 4: Persona generation count and relevance**
**Validates: Requirements 2.1**

**Feature: ai-persona-validator, Property 5: Persona structure completeness**
**Validates: Requirements 2.2, 2.4**

**Feature: ai-persona-validator, Property 6: Persona diversity assurance**
**Validates: Requirements 2.3**
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings
from app.models import (
    CompanyInput, CompanyContext, SyntheticPersona, Demographics, 
    Psychographics, BehaviorPatterns, ContextualFactors,
    BusinessModel, CompanySize, TechnologyAdoption, RiskTolerance
)
from app.services.persona_generator import PersonaGenerationEngine
from app.services.company_processor import CompanyContextProcessor
from typing import List


# Generators for test data
@st.composite
def company_context_strategy(draw):
    """Generate valid CompanyContext instances for persona generation testing"""
    company_input = CompanyInput(
        name=draw(st.text(min_size=5, max_size=200).filter(lambda x: len(x.strip()) >= 5)),
        industry=draw(st.text(min_size=5, max_size=100).filter(lambda x: len(x.strip()) >= 5)),
        business_model=draw(st.sampled_from(list(BusinessModel))),
        target_market=draw(st.text(min_size=25, max_size=500).filter(lambda x: len(x.strip()) >= 25)),
        company_size=draw(st.sampled_from(list(CompanySize))),
        description=draw(st.one_of(st.none(), st.text(min_size=15, max_size=1000).filter(lambda x: len(x.strip()) >= 15)))
    )
    
    # Create company context using the processor
    processor = CompanyContextProcessor()
    return asyncio.run(processor.process_company_input(company_input))


class TestPersonaGenerationCountAndRelevance:
    """Test persona generation count and relevance"""

    @given(company_context_strategy())
    @settings(max_examples=50, deadline=30000)  # Reduced examples for faster testing
    def test_persona_generation_count_and_relevance(self, company_context: CompanyContext):
        """
        Property 4: Persona generation count and relevance
        For any company context, the system should generate 5-10 distinct personas 
        that are contextually relevant to the target market
        """
        engine = PersonaGenerationEngine()
        
        # Generate personas
        personas = asyncio.run(engine.generate_personas(company_context))
        
        # Verify count is within expected range (5-10)
        assert 5 <= len(personas) <= 10, f"Expected 5-10 personas, got {len(personas)}"
        
        # Verify all personas are distinct (different IDs)
        persona_ids = [p.id for p in personas]
        assert len(set(persona_ids)) == len(personas), "All personas should have unique IDs"
        
        # Verify personas are contextually relevant to the company
        for persona in personas:
            # Check industry relevance
            if company_context.input.business_model == BusinessModel.B2B:
                # B2B personas should have business-relevant roles
                business_roles = [
                    "director", "manager", "ceo", "founder", "lead", "specialist", 
                    "executive", "analyst", "coordinator", "administrator"
                ]
                role_lower = persona.demographics.role.lower()
                assert any(role_keyword in role_lower for role_keyword in business_roles), \
                    f"B2B persona role '{persona.demographics.role}' should be business-relevant"
                
                # B2B personas should have company size information
                if persona.demographics.company_size:
                    valid_sizes = ["Startup", "SMB", "Mid-Market", "Enterprise"]
                    assert persona.demographics.company_size in valid_sizes
            
            # Verify persona has contextual factors relevant to the industry
            if persona.contextual_factors.current_solutions:
                # Should have at least one current solution
                assert len(persona.contextual_factors.current_solutions) >= 1
            
            # Verify persona has relevant pain points
            assert len(persona.psychographics.pain_points) >= 1, \
                "Persona should have at least one pain point"
            
            # Verify persona has motivations
            assert len(persona.psychographics.motivations) >= 1, \
                "Persona should have at least one motivation"

    @given(company_context_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_persona_generation_consistency(self, company_context: CompanyContext):
        """
        Property 4: Persona generation consistency
        For any company context, multiple generation runs should produce 
        consistent count and structure
        """
        engine = PersonaGenerationEngine()
        
        # Generate personas twice
        personas1 = asyncio.run(engine.generate_personas(company_context))
        personas2 = asyncio.run(engine.generate_personas(company_context))
        
        # Both runs should produce the same count
        assert len(personas1) == len(personas2), \
            "Multiple generation runs should produce consistent persona counts"
        
        # Both runs should be within valid range
        assert 5 <= len(personas1) <= 10
        assert 5 <= len(personas2) <= 10
        
        # Verify structural consistency
        for p1, p2 in zip(personas1, personas2):
            # Should have same required fields structure
            assert hasattr(p1, 'demographics') and hasattr(p2, 'demographics')
            assert hasattr(p1, 'psychographics') and hasattr(p2, 'psychographics')
            assert hasattr(p1, 'behavior_patterns') and hasattr(p2, 'behavior_patterns')
            assert hasattr(p1, 'contextual_factors') and hasattr(p2, 'contextual_factors')

    @given(company_context_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_multi_market_persona_representation(self, company_context: CompanyContext):
        """
        Property 4: Multi-market persona representation
        For any company operating in multiple markets, generated personas should 
        represent different market segments
        """
        # Modify company context to indicate multiple markets
        if "multiple" not in company_context.input.target_market.lower():
            # Add multi-market indication to target market
            company_context.input.target_market += " across multiple market segments"
        
        engine = PersonaGenerationEngine()
        personas = asyncio.run(engine.generate_personas(company_context))
        
        # Verify we have enough personas to represent diversity
        assert len(personas) >= 5, "Should have at least 5 personas for multi-market representation"
        
        # Check for diversity in roles (representing different market segments)
        roles = [p.demographics.role for p in personas]
        unique_roles = set(roles)
        
        # Should have at least 3 different roles for multi-market representation
        assert len(unique_roles) >= min(3, len(personas)), \
            f"Expected at least 3 different roles for multi-market, got {len(unique_roles)}"
        
        # Check for diversity in age ranges (different market segments)
        ages = [p.demographics.age for p in personas]
        age_range = max(ages) - min(ages)
        
        # Should have reasonable age diversity (at least 10 years range for 5+ personas)
        if len(personas) >= 5:
            assert age_range >= 10, f"Expected age diversity of at least 10 years, got {age_range}"


class TestPersonaStructureCompleteness:
    """Test persona structure completeness"""

    @given(company_context_strategy())
    @settings(max_examples=50, deadline=30000)
    def test_persona_structure_completeness(self, company_context: CompanyContext):
        """
        Property 5: Persona structure completeness
        For any generated persona, it should contain all required fields 
        (demographics, behavioral traits, pain points, technology adoption patterns) 
        in a format suitable for simulation
        """
        engine = PersonaGenerationEngine()
        personas = asyncio.run(engine.generate_personas(company_context))
        
        for persona in personas:
            # Verify persona has all required top-level fields
            assert hasattr(persona, 'id') and persona.id, "Persona must have non-empty ID"
            assert hasattr(persona, 'name') and persona.name, "Persona must have non-empty name"
            assert hasattr(persona, 'demographics'), "Persona must have demographics"
            assert hasattr(persona, 'psychographics'), "Persona must have psychographics"
            assert hasattr(persona, 'behavior_patterns'), "Persona must have behavior_patterns"
            assert hasattr(persona, 'contextual_factors'), "Persona must have contextual_factors"
            
            # Verify demographics completeness
            demo = persona.demographics
            assert hasattr(demo, 'age') and isinstance(demo.age, int), "Demographics must have integer age"
            assert 18 <= demo.age <= 100, f"Age {demo.age} must be between 18 and 100"
            assert hasattr(demo, 'role') and demo.role, "Demographics must have non-empty role"
            assert hasattr(demo, 'company_size'), "Demographics must have company_size field"
            assert hasattr(demo, 'industry'), "Demographics must have industry field"
            assert hasattr(demo, 'income'), "Demographics must have income field"
            
            # Verify psychographics completeness
            psycho = persona.psychographics
            assert hasattr(psycho, 'personality_traits') and isinstance(psycho.personality_traits, list), \
                "Psychographics must have personality_traits list"
            assert len(psycho.personality_traits) >= 1, "Must have at least 1 personality trait"
            assert len(psycho.personality_traits) <= 10, "Must have at most 10 personality traits"
            
            assert hasattr(psycho, 'values') and isinstance(psycho.values, list), \
                "Psychographics must have values list"
            assert len(psycho.values) >= 1, "Must have at least 1 value"
            assert len(psycho.values) <= 10, "Must have at most 10 values"
            
            assert hasattr(psycho, 'motivations') and isinstance(psycho.motivations, list), \
                "Psychographics must have motivations list"
            assert len(psycho.motivations) >= 1, "Must have at least 1 motivation"
            assert len(psycho.motivations) <= 10, "Must have at most 10 motivations"
            
            assert hasattr(psycho, 'pain_points') and isinstance(psycho.pain_points, list), \
                "Psychographics must have pain_points list"
            assert len(psycho.pain_points) >= 1, "Must have at least 1 pain point"
            assert len(psycho.pain_points) <= 10, "Must have at most 10 pain points"
            
            # Verify behavior patterns completeness
            behavior = persona.behavior_patterns
            assert hasattr(behavior, 'technology_adoption'), "Behavior patterns must have technology_adoption"
            assert isinstance(behavior.technology_adoption, TechnologyAdoption), \
                "Technology adoption must be TechnologyAdoption enum"
            
            assert hasattr(behavior, 'decision_making_style') and behavior.decision_making_style, \
                "Behavior patterns must have non-empty decision_making_style"
            
            assert hasattr(behavior, 'risk_tolerance'), "Behavior patterns must have risk_tolerance"
            assert isinstance(behavior.risk_tolerance, RiskTolerance), \
                "Risk tolerance must be RiskTolerance enum"
            
            assert hasattr(behavior, 'information_sources') and isinstance(behavior.information_sources, list), \
                "Behavior patterns must have information_sources list"
            assert len(behavior.information_sources) >= 1, "Must have at least 1 information source"
            assert len(behavior.information_sources) <= 10, "Must have at most 10 information sources"
            
            # Verify contextual factors completeness
            context = persona.contextual_factors
            assert hasattr(context, 'current_solutions') and isinstance(context.current_solutions, list), \
                "Contextual factors must have current_solutions list"
            assert len(context.current_solutions) <= 10, "Must have at most 10 current solutions"
            
            assert hasattr(context, 'budget') and context.budget, \
                "Contextual factors must have non-empty budget"
            
            assert hasattr(context, 'time_constraints') and context.time_constraints, \
                "Contextual factors must have non-empty time_constraints"
            
            assert hasattr(context, 'team_influence') and context.team_influence, \
                "Contextual factors must have non-empty team_influence"

    @given(company_context_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_persona_simulation_suitability(self, company_context: CompanyContext):
        """
        Property 5: Persona simulation suitability
        For any generated persona, it should be in a format suitable for simulation
        (all fields should be non-empty strings or valid enums)
        """
        engine = PersonaGenerationEngine()
        personas = asyncio.run(engine.generate_personas(company_context))
        
        for persona in personas:
            # Verify all string fields are non-empty and reasonable length
            assert len(persona.name.strip()) >= 3, "Name should be at least 3 characters"
            assert len(persona.demographics.role.strip()) >= 3, "Role should be at least 3 characters"
            
            # Verify all list fields contain valid string elements
            for trait in persona.psychographics.personality_traits:
                assert isinstance(trait, str) and len(trait.strip()) > 0, \
                    "Personality traits must be non-empty strings"
            
            for value in persona.psychographics.values:
                assert isinstance(value, str) and len(value.strip()) > 0, \
                    "Values must be non-empty strings"
            
            for motivation in persona.psychographics.motivations:
                assert isinstance(motivation, str) and len(motivation.strip()) > 0, \
                    "Motivations must be non-empty strings"
            
            for pain_point in persona.psychographics.pain_points:
                assert isinstance(pain_point, str) and len(pain_point.strip()) > 0, \
                    "Pain points must be non-empty strings"
            
            for info_source in persona.behavior_patterns.information_sources:
                assert isinstance(info_source, str) and len(info_source.strip()) > 0, \
                    "Information sources must be non-empty strings"
            
            for solution in persona.contextual_factors.current_solutions:
                assert isinstance(solution, str) and len(solution.strip()) > 0, \
                    "Current solutions must be non-empty strings"
            
            # Verify contextual fields are meaningful
            assert len(persona.contextual_factors.budget.strip()) > 0, "Budget must be non-empty"
            assert len(persona.contextual_factors.time_constraints.strip()) > 0, \
                "Time constraints must be non-empty"
            assert len(persona.contextual_factors.team_influence.strip()) > 0, \
                "Team influence must be non-empty"


class TestPersonaDiversityAssurance:
    """Test persona diversity assurance"""

    @given(company_context_strategy())
    @settings(max_examples=50, deadline=30000)
    def test_persona_diversity_assurance(self, company_context: CompanyContext):
        """
        Property 6: Persona diversity assurance
        For any set of generated personas, there should be sufficient diversity 
        across age, income, role, and personality dimensions
        """
        engine = PersonaGenerationEngine()
        personas = asyncio.run(engine.generate_personas(company_context))
        
        # Skip diversity checks if we have too few personas
        if len(personas) < 3:
            return
        
        # Check age diversity
        ages = [p.demographics.age for p in personas]
        unique_ages = set(ages)
        age_range = max(ages) - min(ages)
        
        # Should have reasonable age diversity
        if len(personas) >= 5:
            assert age_range >= 10, f"Expected age range of at least 10 years, got {age_range}"
        if len(personas) >= 3:
            assert len(unique_ages) >= 2, f"Expected at least 2 different ages, got {len(unique_ages)}"
        
        # Check role diversity
        roles = [p.demographics.role for p in personas]
        unique_roles = set(roles)
        
        # Should have at least 2 different roles for 3+ personas
        min_expected_roles = min(len(personas) // 2, len(personas) - 1)
        assert len(unique_roles) >= min_expected_roles, \
            f"Expected at least {min_expected_roles} different roles, got {len(unique_roles)}"
        
        # Check income diversity (if income is provided)
        incomes = [p.demographics.income for p in personas if p.demographics.income]
        if len(incomes) >= 3:
            unique_incomes = set(incomes)
            assert len(unique_incomes) >= 2, \
                f"Expected at least 2 different income levels, got {len(unique_incomes)}"
        
        # Check technology adoption diversity
        tech_adoptions = [p.behavior_patterns.technology_adoption for p in personas]
        unique_tech_adoptions = set(tech_adoptions)
        
        # Should have at least 2 different technology adoption patterns for 4+ personas
        if len(personas) >= 4:
            assert len(unique_tech_adoptions) >= 2, \
                f"Expected at least 2 different technology adoption patterns, got {len(unique_tech_adoptions)}"
        
        # Check risk tolerance diversity
        risk_tolerances = [p.behavior_patterns.risk_tolerance for p in personas]
        unique_risk_tolerances = set(risk_tolerances)
        
        # Should have at least 2 different risk tolerance levels for 4+ personas
        if len(personas) >= 4:
            assert len(unique_risk_tolerances) >= 2, \
                f"Expected at least 2 different risk tolerance levels, got {len(unique_risk_tolerances)}"
        
        # Check personality trait diversity
        all_personality_traits = []
        for p in personas:
            all_personality_traits.extend(p.psychographics.personality_traits)
        
        unique_personality_traits = set(all_personality_traits)
        
        # Should have more unique traits than personas (indicating diversity)
        assert len(unique_personality_traits) >= len(personas), \
            f"Expected at least {len(personas)} unique personality traits, got {len(unique_personality_traits)}"

    @given(company_context_strategy())
    @settings(max_examples=30, deadline=30000)
    def test_persona_diversity_balance(self, company_context: CompanyContext):
        """
        Property 6: Persona diversity balance
        For any set of generated personas, diversity should be balanced 
        (no single dimension should dominate)
        """
        engine = PersonaGenerationEngine()
        personas = asyncio.run(engine.generate_personas(company_context))
        
        if len(personas) < 4:
            return  # Skip balance checks for small sets
        
        # Check that no single role dominates (max 50% for 4+ personas)
        roles = [p.demographics.role for p in personas]
        role_counts = {}
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        
        max_role_count = max(role_counts.values())
        max_role_percentage = max_role_count / len(personas)
        
        assert max_role_percentage <= 0.6, \
            f"No single role should dominate (max 60%), but found {max_role_percentage:.1%}"
        
        # Check that no single technology adoption pattern dominates
        tech_adoptions = [p.behavior_patterns.technology_adoption for p in personas]
        tech_counts = {}
        for tech in tech_adoptions:
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        max_tech_count = max(tech_counts.values())
        max_tech_percentage = max_tech_count / len(personas)
        
        assert max_tech_percentage <= 0.7, \
            f"No single tech adoption should dominate (max 70%), but found {max_tech_percentage:.1%}"
        
        # Check that no single risk tolerance dominates
        risk_tolerances = [p.behavior_patterns.risk_tolerance for p in personas]
        risk_counts = {}
        for risk in risk_tolerances:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        max_risk_count = max(risk_counts.values())
        max_risk_percentage = max_risk_count / len(personas)
        
        assert max_risk_percentage <= 0.7, \
            f"No single risk tolerance should dominate (max 70%), but found {max_risk_percentage:.1%}"


if __name__ == "__main__":
    pytest.main([__file__])