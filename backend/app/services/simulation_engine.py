from app.models import SyntheticPersona, FeatureDescription, SimulationResponse, SimulationDecision, TechnologyAdoption, RiskTolerance
from datetime import datetime
import random
import asyncio
import hashlib
import json
import os
import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai

class SimulationEngine:
    """Simulates persona reactions to features using LLMs"""
    
    def __init__(self):
        self.gemini_model = None
        self.cache: Dict[str, SimulationResponse] = {}
        self.rate_limit_delay = 1.0  # Base delay between API calls
        self.max_retries = 3
        self.batch_size = 10  # Process personas in batches
        
        # Initialize LLM clients
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize LLM API clients"""
        google_key = os.getenv("GOOGLE_API_KEY")
        
        if google_key and google_key != "your_google_api_key_here":
            genai.configure(api_key=google_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.model_name = "gemini-1.5-flash"
        else:
            # Fallback to simulation mode
            self.model_name = "simulation-mode"
    
    async def simulate_persona_reaction(
        self, 
        persona: SyntheticPersona, 
        feature: FeatureDescription
    ) -> SimulationResponse:
        """
        Simulate a single persona's reaction to a feature
        
        Args:
            persona: The synthetic persona
            feature: The feature description
            
        Returns:
            SimulationResponse with decision, confidence, and reasoning
        """
        # Check cache first
        cache_key = self._generate_cache_key(persona, feature)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate structured prompt
        prompt = self._generate_prompt(persona, feature)
        
        # Call LLM API or fallback to simulation
        response = await self._call_llm_api(prompt, persona, feature)
        
        # Create simulation response
        simulation_response = SimulationResponse(
            persona_id=persona.id,
            decision=response["decision"],
            confidence=response["confidence"],
            reasoning=response["reasoning"],
            key_factors=response["key_factors"],
            timestamp=datetime.utcnow(),
            model_used=self.model_name
        )
        
        # Cache the response
        self.cache[cache_key] = simulation_response
        
        return simulation_response
    
    async def simulate_batch_reactions(
        self,
        personas: List[SyntheticPersona],
        feature: FeatureDescription,
        progress_callback: Optional[callable] = None
    ) -> List[SimulationResponse]:
        """
        Simulate reactions for a batch of personas with progress tracking
        
        Args:
            personas: List of personas to simulate
            feature: The feature description
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of SimulationResponse objects
        """
        results = []
        total_personas = len(personas)
        
        # Process in batches to manage rate limits
        for i in range(0, total_personas, self.batch_size):
            batch = personas[i:i + self.batch_size]
            
            # Process batch sequentially with rate limiting
            for persona in batch:
                try:
                    result = await self.simulate_persona_reaction(persona, feature)
                    results.append(result)
                    
                    # Rate limiting delay
                    if self.gemini_model:
                        await asyncio.sleep(self.rate_limit_delay)
                        
                except Exception as e:
                    # Create error response for failed simulations
                    error_response = SimulationResponse(
                        persona_id=persona.id,
                        decision=SimulationDecision.UNSURE,
                        confidence=0.0,
                        reasoning=f"Simulation failed: {str(e)}",
                        key_factors=["API Error", "Retry Required"],
                        timestamp=datetime.utcnow(),
                        model_used=self.model_name
                    )
                    results.append(error_response)
                
                # Progress callback after each persona
                if progress_callback:
                    progress = len(results) / total_personas
                    progress_callback(progress, len(results), total_personas)
        
        return results
    
    def _generate_cache_key(self, persona: SyntheticPersona, feature: FeatureDescription) -> str:
        """Generate a cache key for persona-feature combination"""
        # Create a hash of the persona and feature content
        persona_content = f"{persona.id}_{persona.name}_{persona.demographics.role}_{persona.behavior_patterns.technology_adoption.value}_{persona.behavior_patterns.risk_tolerance.value}"
        feature_content = f"{feature.name}_{feature.description}_{feature.value_proposition}"
        
        combined_content = f"{persona_content}_{feature_content}"
        return hashlib.md5(combined_content.encode()).hexdigest()
    
    async def _call_llm_api(self, prompt: str, persona: SyntheticPersona, feature: FeatureDescription) -> Dict[str, Any]:
        """
        Call LLM API with proper error handling and rate limiting
        
        Args:
            prompt: The structured prompt
            persona: The persona for fallback simulation
            feature: The feature for fallback simulation
            
        Returns:
            Dictionary with decision, confidence, reasoning, and key_factors
        """
        for attempt in range(self.max_retries):
            try:
                if self.gemini_model:
                    return await self._call_gemini_api(prompt)
                else:
                    # Fallback to simulation
                    return await self._simulate_llm_response(persona, feature)
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Final attempt failed, use simulation fallback
                    return await self._simulate_llm_response(persona, feature)
                
                # Exponential backoff
                wait_time = (2 ** attempt) * self.rate_limit_delay
                await asyncio.sleep(wait_time)
        
        # Should never reach here, but fallback just in case
        return await self._simulate_llm_response(persona, feature)
    
    async def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API"""
        # Add system instruction to the prompt
        full_prompt = """You are a user persona responding to a feature proposal. Follow the exact format requested.

""" + prompt
        
        # Generate response using Gemini
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500,
            )
        )
        
        content = response.text
        return self._parse_llm_response(content)
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format
        
        Args:
            content: Raw LLM response text
            
        Returns:
            Dictionary with parsed decision, confidence, reasoning, and key_factors
        """
        try:
            lines = content.strip().split('\n')
            parsed = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('DECISION:'):
                    decision_text = line.replace('DECISION:', '').strip().upper()
                    if decision_text in ['ADOPT', 'REJECT', 'UNSURE']:
                        parsed['decision'] = SimulationDecision(decision_text)
                    else:
                        parsed['decision'] = SimulationDecision.UNSURE
                        
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence_text = line.replace('CONFIDENCE:', '').strip()
                        confidence = float(confidence_text)
                        parsed['confidence'] = max(0.0, min(1.0, confidence))
                    except ValueError:
                        parsed['confidence'] = 0.5
                        
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()
                    parsed['reasoning'] = reasoning if reasoning else "No reasoning provided"
                    
                elif line.startswith('KEY_FACTORS:'):
                    factors_text = line.replace('KEY_FACTORS:', '').strip()
                    # Parse comma-separated factors
                    factors = [f.strip() for f in factors_text.split(',') if f.strip()]
                    parsed['key_factors'] = factors[:3] if factors else ["Unknown factors"]
            
            # Ensure all required fields are present
            if 'decision' not in parsed:
                parsed['decision'] = SimulationDecision.UNSURE
            if 'confidence' not in parsed:
                parsed['confidence'] = 0.5
            if 'reasoning' not in parsed:
                parsed['reasoning'] = "Unable to parse reasoning from response"
            if 'key_factors' not in parsed:
                parsed['key_factors'] = ["Parsing error", "Response format issue"]
                
            return parsed
            
        except Exception as e:
            # Fallback parsing failed
            return {
                'decision': SimulationDecision.UNSURE,
                'confidence': 0.0,
                'reasoning': f"Failed to parse LLM response: {str(e)}",
                'key_factors': ["Parsing error", "Response format issue"]
            }
    
    def _generate_prompt(self, persona: SyntheticPersona, feature: FeatureDescription) -> str:
        """Generate structured prompt for LLM"""
        prompt = f"""You are {persona.name}, a {persona.demographics.role}"""
        
        if persona.demographics.company_size:
            prompt += f" at a {persona.demographics.company_size} company"
        
        prompt += f".\n\nYour characteristics:\n"
        prompt += f"- Personality: {', '.join(persona.psychographics.personality_traits)}\n"
        prompt += f"- Values: {', '.join(persona.psychographics.values)}\n"
        prompt += f"- Pain points: {', '.join(persona.psychographics.pain_points)}\n"
        prompt += f"- Technology adoption: {persona.behavior_patterns.technology_adoption.value}\n"
        prompt += f"- Current solutions: {', '.join(persona.contextual_factors.current_solutions)}\n"
        prompt += f"- Budget: {persona.contextual_factors.budget}\n"
        prompt += f"- Time constraints: {persona.contextual_factors.time_constraints}\n"
        
        prompt += f"\nA company is launching this feature:\n"
        prompt += f"Feature: {feature.name}\n"
        prompt += f"Description: {feature.description}\n"
        prompt += f"Target user: {feature.target_user}\n"
        prompt += f"Value proposition: {feature.value_proposition}\n"
        
        if feature.pricing_model:
            prompt += f"Pricing: {feature.pricing_model}\n"
        
        prompt += f"\nWould you adopt this feature? Respond with:\n"
        prompt += f"DECISION: [ADOPT/REJECT/UNSURE]\n"
        prompt += f"CONFIDENCE: [0.0-1.0]\n"
        prompt += f"REASONING: [One sentence explaining your decision]\n"
        prompt += f"KEY_FACTORS: [List 2-3 most important factors in your decision]"
        
        return prompt
    
    async def _simulate_llm_response(self, persona: SyntheticPersona, feature: FeatureDescription) -> dict:
        """
        Simulate LLM response (placeholder implementation)
        In real implementation, this would call the actual LLM API
        """
        # Simple simulation based on persona characteristics
        adoption_probability = self._calculate_adoption_probability(persona, feature)
        
        # Make decision based on probability
        rand = random.random()
        if rand < adoption_probability * 0.7:
            decision = SimulationDecision.ADOPT
            confidence = min(0.9, adoption_probability + random.uniform(0.1, 0.3))
            reasoning = self._generate_positive_reasoning(persona, feature)
        elif rand < adoption_probability:
            decision = SimulationDecision.UNSURE
            confidence = random.uniform(0.3, 0.7)
            reasoning = self._generate_unsure_reasoning(persona, feature)
        else:
            decision = SimulationDecision.REJECT
            confidence = min(0.9, (1 - adoption_probability) + random.uniform(0.1, 0.3))
            reasoning = self._generate_negative_reasoning(persona, feature)
        
        key_factors = self._generate_key_factors(persona, feature, decision)
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors
        }
    
    def _calculate_adoption_probability(self, persona: SyntheticPersona, feature: FeatureDescription) -> float:
        """Calculate base adoption probability based on persona characteristics"""
        probability = 0.5  # Base probability
        
        # Adjust based on technology adoption pattern
        tech_adoption_weights = {
            TechnologyAdoption.EARLY_ADOPTER: 0.3,
            TechnologyAdoption.EARLY_MAJORITY: 0.1,
            TechnologyAdoption.LATE_MAJORITY: -0.1,
            TechnologyAdoption.LAGGARD: -0.3
        }
        probability += tech_adoption_weights.get(persona.behavior_patterns.technology_adoption, 0)
        
        # Adjust based on risk tolerance
        risk_weights = {
            RiskTolerance.HIGH: 0.2,
            RiskTolerance.MEDIUM: 0.0,
            RiskTolerance.LOW: -0.2
        }
        probability += risk_weights.get(persona.behavior_patterns.risk_tolerance, 0)
        
        # Adjust based on pain points alignment
        if any(pain in feature.description.lower() or pain in feature.value_proposition.lower() 
               for pain in [p.lower() for p in persona.psychographics.pain_points]):
            probability += 0.2
        
        # Adjust based on values alignment
        if any(value in feature.description.lower() or value in feature.value_proposition.lower()
               for value in [v.lower() for v in persona.psychographics.values]):
            probability += 0.15
        
        return max(0.0, min(1.0, probability))
    
    def _generate_positive_reasoning(self, persona: SyntheticPersona, feature: FeatureDescription) -> str:
        """Generate positive reasoning for adoption"""
        reasons = [
            f"This feature aligns well with my focus on {random.choice(persona.psychographics.values).lower()}",
            f"The {feature.name} addresses my key pain point around {random.choice(persona.psychographics.pain_points).lower()}",
            f"As someone who values {random.choice(persona.psychographics.values).lower()}, this feature provides clear value",
            f"The value proposition resonates with my need for {random.choice(persona.psychographics.motivations).lower()}"
        ]
        return random.choice(reasons)
    
    def _generate_negative_reasoning(self, persona: SyntheticPersona, feature: FeatureDescription) -> str:
        """Generate negative reasoning for rejection"""
        reasons = [
            f"This doesn't address my main concern about {random.choice(persona.psychographics.pain_points).lower()}",
            f"Given my {persona.behavior_patterns.risk_tolerance.value.lower()} risk tolerance, this seems too uncertain",
            f"My current solution already handles this adequately",
            f"The implementation complexity doesn't justify the benefits for my use case",
            f"Budget constraints make this difficult to justify right now"
        ]
        return random.choice(reasons)
    
    def _generate_unsure_reasoning(self, persona: SyntheticPersona, feature: FeatureDescription) -> str:
        """Generate reasoning for uncertainty"""
        reasons = [
            f"I need more information about how this integrates with {random.choice(persona.contextual_factors.current_solutions)}",
            f"The value proposition is interesting but I'm concerned about {random.choice(persona.psychographics.pain_points).lower()}",
            f"This could be valuable but I need to understand the total cost of ownership better",
            f"I'd want to see a pilot or trial before making a full commitment"
        ]
        return random.choice(reasons)
    
    def _generate_key_factors(self, persona: SyntheticPersona, feature: FeatureDescription, decision: SimulationDecision) -> list[str]:
        """Generate key factors that influenced the decision"""
        all_factors = [
            "Cost-benefit analysis",
            "Integration complexity",
            "Time to value",
            "Risk assessment",
            "Team adoption",
            "Competitive advantage",
            "ROI potential",
            "Implementation effort",
            "Vendor reliability",
            "Feature completeness"
        ]
        
        # Select 2-3 factors that align with persona characteristics
        relevant_factors = []
        
        if "Cost" in persona.psychographics.values or "budget" in persona.contextual_factors.budget.lower():
            relevant_factors.append("Cost-benefit analysis")
        
        if persona.behavior_patterns.risk_tolerance == RiskTolerance.LOW:
            relevant_factors.append("Risk assessment")
        
        if "Integration" in persona.psychographics.pain_points:
            relevant_factors.append("Integration complexity")
        
        # Fill remaining slots with random factors
        remaining_factors = [f for f in all_factors if f not in relevant_factors]
        needed = max(0, 3 - len(relevant_factors))
        relevant_factors.extend(random.sample(remaining_factors, min(needed, len(remaining_factors))))
        
        return relevant_factors[:3]