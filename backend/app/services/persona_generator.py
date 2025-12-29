from app.models import CompanyContext, SyntheticPersona, Demographics, Psychographics, BehaviorPatterns, ContextualFactors, TechnologyAdoption, RiskTolerance
import uuid
import random
import os
import json
import asyncio
from typing import List, Dict, Any
import httpx

class PersonaGenerationEngine:
    """Generates diverse synthetic personas based on company context"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        
    async def generate_personas(self, company_context: CompanyContext) -> List[SyntheticPersona]:
        """
        Generate 5-10 diverse personas based on company context
        
        Args:
            company_context: Enriched company context
            
        Returns:
            List of synthetic personas (5-10 personas)
        """
        personas = []
        
        # Generate initial persona seeds if not enough
        if len(company_context.persona_seeds) < 5:
            additional_seeds = self._generate_additional_seeds(company_context, 8 - len(company_context.persona_seeds))
            company_context.persona_seeds.extend(additional_seeds)
        
        # Limit to maximum 10 personas
        seeds_to_use = company_context.persona_seeds[:10]
        
        # Generate personas from seeds with LLM enrichment
        for i, seed in enumerate(seeds_to_use):
            persona = await self._generate_persona_from_seed(seed, company_context, i)
            personas.append(persona)
        
        # Ensure diversity across key dimensions
        personas = self._ensure_diversity(personas)
        
        # Ensure we have 5-10 personas
        if len(personas) < 5:
            # Generate additional personas if needed
            additional_personas = await self._generate_additional_personas(company_context, 5 - len(personas))
            personas.extend(additional_personas)
        
        return personas[:10]  # Cap at 10 personas
    
    async def _generate_persona_from_seed(self, seed: dict, context: CompanyContext, index: int) -> SyntheticPersona:
        """Generate a full persona from a seed with LLM enrichment"""
        persona_id = str(uuid.uuid4())
        
        # Generate base persona structure
        demographics = self._generate_demographics(seed, context)
        psychographics = self._generate_psychographics(seed, context)
        behavior_patterns = self._generate_behavior_patterns(seed, context)
        contextual_factors = self._generate_contextual_factors(seed, context)
        name = self._generate_name(demographics, index)
        
        # Create base persona
        base_persona = SyntheticPersona(
            id=persona_id,
            name=name,
            demographics=demographics,
            psychographics=psychographics,
            behavior_patterns=behavior_patterns,
            contextual_factors=contextual_factors
        )
        
        # Enrich with LLM if API keys are available
        if self.openai_api_key or self.claude_api_key:
            try:
                enriched_persona = await self._enrich_persona_with_llm(base_persona, context)
                return enriched_persona
            except Exception as e:
                # Fall back to base persona if LLM enrichment fails
                print(f"LLM enrichment failed: {e}")
                return base_persona
        
        return base_persona
    
    def _generate_demographics(self, seed: dict, context: CompanyContext) -> Demographics:
        """Generate demographic information"""
        # Age distribution based on role
        age_ranges = {
            "CEO/Founder": (35, 55),
            "IT Director": (30, 50),
            "Product Manager": (28, 45),
            "Tech-savvy Professional": (25, 40),
            "Student": (18, 25),
            "Senior Executive": (40, 60)
        }
        
        base_role = seed.get("base_role", "Professional")
        age_range = age_ranges.get(base_role, (25, 50))
        age = random.randint(*age_range)
        
        # Company size for B2B personas
        company_size = None
        if context.input.business_model.value == "B2B":
            company_size = random.choice(["Startup", "SMB", "Mid-Market", "Enterprise"])
        
        return Demographics(
            age=age,
            role=base_role,
            company_size=company_size,
            industry=context.input.industry if random.random() > 0.3 else None,
            income=self._generate_income_bracket(age, base_role)
        )
    
    def _generate_psychographics(self, seed: dict, context: CompanyContext) -> Psychographics:
        """Generate psychological traits"""
        personality_pools = {
            "traits": [
                "Analytical", "Creative", "Detail-oriented", "Big-picture thinker",
                "Risk-averse", "Innovative", "Collaborative", "Independent",
                "Results-driven", "Process-oriented"
            ],
            "values": [
                "Efficiency", "Innovation", "Reliability", "Cost-effectiveness",
                "User experience", "Security", "Scalability", "Simplicity",
                "Quality", "Speed"
            ],
            "motivations": [
                "Career advancement", "Problem solving", "Cost reduction",
                "Competitive advantage", "User satisfaction", "Process improvement",
                "Risk mitigation", "Growth", "Recognition", "Learning"
            ],
            "pain_points": [
                "Limited budget", "Time constraints", "Technical complexity",
                "Integration challenges", "Training requirements", "Security concerns",
                "Scalability issues", "Vendor lock-in", "Change resistance", "ROI uncertainty"
            ]
        }
        
        return Psychographics(
            personality_traits=random.sample(personality_pools["traits"], random.randint(2, 4)),
            values=random.sample(personality_pools["values"], random.randint(2, 4)),
            motivations=random.sample(personality_pools["motivations"], random.randint(2, 4)),
            pain_points=random.sample(personality_pools["pain_points"], random.randint(2, 4))
        )
    
    def _generate_behavior_patterns(self, seed: dict, context: CompanyContext) -> BehaviorPatterns:
        """Generate behavioral patterns"""
        tech_adoption = random.choice(list(TechnologyAdoption))
        risk_tolerance = random.choice(list(RiskTolerance))
        
        decision_styles = [
            "Data-driven analysis", "Consensus building", "Quick decisive action",
            "Extensive research", "Peer consultation", "Trial and error",
            "Expert recommendation", "Cost-benefit analysis"
        ]
        
        info_sources = [
            "Industry publications", "Peer networks", "Vendor demos",
            "Online reviews", "Conference presentations", "Internal research",
            "Consultant recommendations", "Social media", "Trade shows"
        ]
        
        return BehaviorPatterns(
            technology_adoption=tech_adoption,
            decision_making_style=random.choice(decision_styles),
            risk_tolerance=risk_tolerance,
            information_sources=random.sample(info_sources, random.randint(2, 4))
        )
    
    def _generate_contextual_factors(self, seed: dict, context: CompanyContext) -> ContextualFactors:
        """Generate contextual factors"""
        current_solutions = [
            "Legacy system", "Manual processes", "Spreadsheets",
            "Custom-built solution", "Competitor product", "Open source tool",
            "No current solution"
        ]
        
        budgets = [
            "Very limited (<$1K)", "Small ($1K-$10K)", "Moderate ($10K-$50K)",
            "Substantial ($50K-$200K)", "Large (>$200K)"
        ]
        
        time_constraints = [
            "Immediate need", "Within 3 months", "6-month timeline",
            "Annual planning cycle", "No rush", "Dependent on other projects"
        ]
        
        team_influences = [
            "Individual decision", "Team consensus required", "Manager approval needed",
            "Committee decision", "Board approval required", "IT department involvement",
            "Budget holder sign-off", "User acceptance critical"
        ]
        
        return ContextualFactors(
            current_solutions=random.sample(current_solutions, random.randint(1, 3)),
            budget=random.choice(budgets),
            time_constraints=random.choice(time_constraints),
            team_influence=random.choice(team_influences)
        )
    
    def _generate_income_bracket(self, age: int, role: str) -> str:
        """Generate income bracket based on age and role"""
        income_brackets = [
            "$30K-$50K", "$50K-$75K", "$75K-$100K",
            "$100K-$150K", "$150K-$200K", "$200K+"
        ]
        
        # Simple logic based on role and age
        if "CEO" in role or "Director" in role:
            return random.choice(income_brackets[3:])  # Higher brackets
        elif "Manager" in role:
            return random.choice(income_brackets[2:5])  # Mid to high brackets
        elif "Student" in role:
            return income_brackets[0]  # Lowest bracket
        else:
            return random.choice(income_brackets[1:4])  # Mid brackets
    
    def _generate_name(self, demographics: Demographics, index: int) -> str:
        """Generate a realistic name for the persona"""
        first_names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley",
            "Avery", "Quinn", "Sage", "River", "Phoenix", "Rowan"
        ]
        
        last_names = [
            "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    async def _enrich_persona_with_llm(self, persona: SyntheticPersona, context: CompanyContext) -> SyntheticPersona:
        """Enrich persona with LLM-generated insights"""
        prompt = self._create_persona_enrichment_prompt(persona, context)
        
        try:
            if self.openai_api_key:
                enrichment = await self._call_openai(prompt)
            elif self.claude_api_key:
                enrichment = await self._call_claude(prompt)
            else:
                return persona
            
            # Parse and apply enrichment
            return self._apply_llm_enrichment(persona, enrichment)
        except Exception as e:
            print(f"LLM enrichment error: {e}")
            return persona
    
    def _create_persona_enrichment_prompt(self, persona: SyntheticPersona, context: CompanyContext) -> str:
        """Create prompt for LLM persona enrichment"""
        return f"""
You are helping create a realistic synthetic persona for market research. 

Company Context:
- Industry: {context.input.industry}
- Business Model: {context.input.business_model.value}
- Target Market: {context.input.target_market}
- Company Size: {context.input.company_size.value}

Current Persona:
- Name: {persona.name}
- Age: {persona.demographics.age}
- Role: {persona.demographics.role}
- Technology Adoption: {persona.behavior_patterns.technology_adoption.value}
- Risk Tolerance: {persona.behavior_patterns.risk_tolerance.value}

Please enhance this persona by providing:
1. More specific and realistic personality traits (2-4 traits)
2. More contextual pain points relevant to their role and industry (2-4 points)
3. More specific motivations that align with their demographics (2-4 motivations)
4. More realistic current solutions they might be using (1-3 solutions)

Respond in JSON format:
{{
    "personality_traits": ["trait1", "trait2", ...],
    "pain_points": ["pain1", "pain2", ...],
    "motivations": ["motivation1", "motivation2", ...],
    "current_solutions": ["solution1", "solution2", ...]
}}
"""
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API for persona enrichment"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
    
    async def _call_claude(self, prompt: str) -> Dict[str, Any]:
        """Call Claude API for persona enrichment"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.claude_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            content = result["content"][0]["text"]
            return json.loads(content)
    
    def _apply_llm_enrichment(self, persona: SyntheticPersona, enrichment: Dict[str, Any]) -> SyntheticPersona:
        """Apply LLM enrichment to persona"""
        # Update personality traits if provided
        if "personality_traits" in enrichment and enrichment["personality_traits"]:
            persona.psychographics.personality_traits = enrichment["personality_traits"][:4]
        
        # Update pain points if provided
        if "pain_points" in enrichment and enrichment["pain_points"]:
            persona.psychographics.pain_points = enrichment["pain_points"][:4]
        
        # Update motivations if provided
        if "motivations" in enrichment and enrichment["motivations"]:
            persona.psychographics.motivations = enrichment["motivations"][:4]
        
        # Update current solutions if provided
        if "current_solutions" in enrichment and enrichment["current_solutions"]:
            persona.contextual_factors.current_solutions = enrichment["current_solutions"][:3]
        
        return persona
    
    def _generate_additional_seeds(self, context: CompanyContext, count: int) -> List[Dict[str, Any]]:
        """Generate additional persona seeds if needed"""
        base_roles = self._get_base_roles(context)
        additional_seeds = []
        
        for i in range(count):
            role_index = (len(context.persona_seeds) + i) % len(base_roles)
            seed = {
                "seed_id": f"additional_seed_{i+1}",
                "base_role": base_roles[role_index],
                "company_context": context.input.industry,
                "business_model": context.input.business_model.value
            }
            additional_seeds.append(seed)
        
        return additional_seeds
    
    async def _generate_additional_personas(self, context: CompanyContext, count: int) -> List[SyntheticPersona]:
        """Generate additional personas if we don't have enough"""
        additional_personas = []
        base_roles = self._get_base_roles(context)
        
        for i in range(count):
            seed = {
                "seed_id": f"fallback_seed_{i+1}",
                "base_role": base_roles[i % len(base_roles)],
                "company_context": context.input.industry,
                "business_model": context.input.business_model.value
            }
            persona = await self._generate_persona_from_seed(seed, context, i + 100)
            additional_personas.append(persona)
        
        return additional_personas
    
    def _get_base_roles(self, context: CompanyContext) -> List[str]:
        """Get base roles relevant to the company context"""
        if context.input.business_model.value == "B2B":
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
    
    def _ensure_diversity(self, personas: List[SyntheticPersona]) -> List[SyntheticPersona]:
        """Ensure diversity across key dimensions"""
        if len(personas) <= 1:
            return personas
        
        # Check age diversity
        ages = [p.demographics.age for p in personas]
        age_range = max(ages) - min(ages)
        
        # If age range is too narrow, adjust some personas
        if age_range < 15 and len(personas) > 3:
            # Spread ages more evenly
            for i, persona in enumerate(personas[1::2]):  # Every other persona starting from index 1
                if i % 2 == 0:
                    persona.demographics.age = min(ages) + (i + 1) * 5
                else:
                    persona.demographics.age = max(ages) - (i + 1) * 3
        
        # Ensure role diversity
        roles = [p.demographics.role for p in personas]
        unique_roles = set(roles)
        
        # If we have too many duplicate roles, diversify
        if len(unique_roles) < len(personas) // 2:
            base_roles = self._get_base_roles_from_personas(personas)
            for i, persona in enumerate(personas):
                if roles.count(persona.demographics.role) > 2:
                    # Find an unused or less used role
                    for role in base_roles:
                        if roles.count(role) < 2:
                            persona.demographics.role = role
                            roles[i] = role
                            break
        
        # Ensure technology adoption diversity
        tech_adoptions = [p.behavior_patterns.technology_adoption for p in personas]
        unique_adoptions = set(tech_adoptions)
        
        if len(unique_adoptions) < min(3, len(personas)):
            adoption_types = list(TechnologyAdoption)
            for i, persona in enumerate(personas):
                if i < len(adoption_types):
                    persona.behavior_patterns.technology_adoption = adoption_types[i]
        
        # Ensure risk tolerance diversity
        risk_tolerances = [p.behavior_patterns.risk_tolerance for p in personas]
        unique_risks = set(risk_tolerances)
        
        if len(unique_risks) < min(3, len(personas)):
            risk_types = list(RiskTolerance)
            for i, persona in enumerate(personas):
                if i < len(risk_types):
                    persona.behavior_patterns.risk_tolerance = risk_types[i]
        
        return personas
    
    def _get_base_roles_from_personas(self, personas: List[SyntheticPersona]) -> List[str]:
        """Extract base roles from existing personas for diversity checking"""
        if not personas:
            return []
        
        # Determine business model from first persona's context
        sample_persona = personas[0]
        
        # Default role sets based on common patterns
        b2b_roles = [
            "IT Director", "Product Manager", "Operations Manager",
            "CEO/Founder", "Finance Manager", "Sales Director",
            "Technical Lead", "Procurement Specialist", "Marketing Manager", "HR Director"
        ]
        
        b2c_roles = [
            "Tech-savvy Professional", "Budget-conscious Consumer",
            "Early Adopter", "Mainstream User", "Senior Executive",
            "Small Business Owner", "Freelancer", "Student", "Retiree", "Parent"
        ]
        
        # Return appropriate role set (default to B2C if unclear)
        return b2b_roles if "Director" in sample_persona.demographics.role or "Manager" in sample_persona.demographics.role else b2c_roles