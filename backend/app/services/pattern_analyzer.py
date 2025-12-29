from app.models import SimulationResponse, ReasoningPattern
from typing import List, Dict, Set
from collections import Counter, defaultdict
import re

class PatternAnalyzer:
    """Analyzes reasoning patterns from simulation results"""
    
    def analyze_patterns(self, simulation_results: List[SimulationResponse]) -> List[ReasoningPattern]:
        """
        Analyze simulation results to identify reasoning patterns
        
        Args:
            simulation_results: List of simulation responses
            
        Returns:
            List of identified reasoning patterns
        """
        patterns = []
        
        # Identify common themes in reasoning
        theme_patterns = self._identify_themes(simulation_results)
        patterns.extend(theme_patterns)
        
        # Cluster similar objections
        objection_patterns = self._cluster_objections(simulation_results)
        patterns.extend(objection_patterns)
        
        # Find success drivers
        success_patterns = self._identify_success_drivers(simulation_results)
        patterns.extend(success_patterns)
        
        return patterns
    
    def _identify_themes(self, results: List[SimulationResponse]) -> List[ReasoningPattern]:
        """Identify common themes across all reasoning"""
        themes = []
        
        # Extract key phrases from reasoning
        all_reasoning = [r.reasoning for r in results]
        
        # Simple keyword-based theme extraction
        theme_keywords = {
            "cost": ["cost", "price", "expensive", "budget", "affordable"],
            "time": ["time", "quick", "slow", "delay", "schedule"],
            "complexity": ["complex", "simple", "easy", "difficult", "learning curve"],
            "integration": ["integrate", "compatibility", "existing", "current system"],
            "security": ["security", "safe", "risk", "privacy", "data protection"],
            "scalability": ["scale", "growth", "expand", "capacity"]
        }
        
        for theme_name, keywords in theme_keywords.items():
            matching_results = []
            example_quotes = []
            
            for result in results:
                reasoning_lower = result.reasoning.lower()
                if any(keyword in reasoning_lower for keyword in keywords):
                    matching_results.append(result)
                    # Extract a relevant sentence
                    sentences = result.reasoning.split('.')
                    for sentence in sentences:
                        if any(keyword in sentence.lower() for keyword in keywords):
                            example_quotes.append(sentence.strip())
                            break
            
            if len(matching_results) >= 2:  # Only include if at least 2 personas mention it
                themes.append(ReasoningPattern(
                    pattern_type="theme",
                    description=f"Common concern about {theme_name}",
                    frequency=len(matching_results),
                    example_quotes=example_quotes[:3],
                    affected_personas=[r.persona_id for r in matching_results]
                ))
        
        return themes
    
    def _cluster_objections(self, results: List[SimulationResponse]) -> List[ReasoningPattern]:
        """Cluster similar objections from REJECT decisions"""
        objections = []
        
        # Get all rejections
        rejections = [r for r in results if r.decision.value == "REJECT"]
        
        if not rejections:
            return []
        
        # Group by key factors (simple clustering)
        factor_groups = defaultdict(list)
        for rejection in rejections:
            for factor in rejection.key_factors:
                factor_groups[factor.lower()].append(rejection)
        
        # Create patterns for common objection factors
        for factor, related_rejections in factor_groups.items():
            if len(related_rejections) >= 2:
                objections.append(ReasoningPattern(
                    pattern_type="objection_cluster",
                    description=f"Objection: {factor}",
                    frequency=len(related_rejections),
                    example_quotes=[r.reasoning[:100] + "..." for r in related_rejections[:3]],
                    affected_personas=[r.persona_id for r in related_rejections]
                ))
        
        return objections
    
    def _identify_success_drivers(self, results: List[SimulationResponse]) -> List[ReasoningPattern]:
        """Identify what drives adoption"""
        drivers = []
        
        # Get all adoptions
        adoptions = [r for r in results if r.decision.value == "ADOPT"]
        
        if not adoptions:
            return []
        
        # Group by key factors
        factor_groups = defaultdict(list)
        for adoption in adoptions:
            for factor in adoption.key_factors:
                factor_groups[factor.lower()].append(adoption)
        
        # Create patterns for common success factors
        for factor, related_adoptions in factor_groups.items():
            if len(related_adoptions) >= 2:
                drivers.append(ReasoningPattern(
                    pattern_type="success_driver",
                    description=f"Success driver: {factor}",
                    frequency=len(related_adoptions),
                    example_quotes=[r.reasoning[:100] + "..." for r in related_adoptions[:3]],
                    affected_personas=[r.persona_id for r in related_adoptions]
                ))
        
        return drivers
    
    def generate_insights_summary(self, patterns: List[ReasoningPattern]) -> str:
        """Generate a human-readable summary of patterns"""
        summary_parts = []
        
        themes = [p for p in patterns if p.pattern_type == "theme"]
        objections = [p for p in patterns if p.pattern_type == "objection_cluster"]
        drivers = [p for p in patterns if p.pattern_type == "success_driver"]
        
        if themes:
            summary_parts.append(f"Key themes: {', '.join([p.description for p in themes[:3]])}")
        
        if objections:
            summary_parts.append(f"Main objections: {', '.join([p.description for p in objections[:3]])}")
        
        if drivers:
            summary_parts.append(f"Success drivers: {', '.join([p.description for p in drivers[:3]])}")
        
        return ". ".join(summary_parts) if summary_parts else "No significant patterns identified."
