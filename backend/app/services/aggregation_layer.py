from app.models import SimulationResponse, AggregatedInsights, ObjectionCluster, SuccessFactor, Recommendations, SimulationDecision
from typing import List, Dict
import statistics
from collections import Counter

class AggregationLayer:
    """Aggregates simulation results into insights and recommendations"""
    
    def aggregate_results(self, simulation_results: List[SimulationResponse], personas: List['SyntheticPersona'] = None) -> AggregatedInsights:
        """
        Aggregate simulation results into comprehensive insights
        
        Args:
            simulation_results: List of simulation responses from all personas
            personas: Optional list of personas corresponding to results (required for segmentation)
            
        Returns:
            AggregatedInsights with adoption rates, objections, and recommendations
        """
        if not simulation_results:
            return self._empty_insights()
        
        # Calculate overall adoption rate
        adoption_rate = self._calculate_adoption_rate(simulation_results)
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(simulation_results)
        
        # Analyze adoption by segment
        adoption_by_segment = self._analyze_adoption_by_segment(simulation_results, personas)
        
        # Cluster objections
        top_objections = self._cluster_objections(simulation_results)
        
        # Identify success factors
        key_success_factors = self._identify_success_factors(simulation_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            simulation_results, adoption_rate, top_objections, key_success_factors
        )
        
        return AggregatedInsights(
            overall_adoption_rate=adoption_rate,
            confidence_interval=confidence_interval,
            adoption_by_segment=adoption_by_segment,
            top_objections=top_objections,
            key_success_factors=key_success_factors,
            recommendations=recommendations
        )
    
    def _calculate_adoption_rate(self, results: List[SimulationResponse]) -> float:
        """Calculate overall adoption rate"""
        if not results:
            return 0.0
        
        adopt_count = sum(1 for r in results if r.decision == SimulationDecision.ADOPT)
        return adopt_count / len(results)
    
    def _calculate_confidence_interval(self, results: List[SimulationResponse]) -> tuple[float, float]:
        """Calculate confidence interval for adoption rate"""
        if not results:
            return (0.0, 0.0)
        
        # Simple confidence interval calculation
        # In a real implementation, this would use proper statistical methods
        adoption_rate = self._calculate_adoption_rate(results)
        n = len(results)
        
        if n < 2:
            return (0.0, 1.0)
            
        # 95% confidence interval
        margin_of_error = 1.96 * (adoption_rate * (1 - adoption_rate) / n) ** 0.5
        
        lower_bound = max(0.0, adoption_rate - margin_of_error)
        upper_bound = min(1.0, adoption_rate + margin_of_error)
        
        return (lower_bound, upper_bound)
    
    def _analyze_adoption_by_segment(self, results: List[SimulationResponse], personas: List['SyntheticPersona'] = None) -> Dict[str, float]:
        """Analyze adoption rates by different segments"""
        segments = {}
        
        # Default segments by confidence if no persona data
        if not personas:
            return self._segment_by_confidence(results)
            
        # Map persona IDs to objects for easy lookup
        persona_map = {p.id: p for p in personas}
        
        # Segment by Role
        role_groups = {}
        for result in results:
            if result.persona_id in persona_map:
                role = persona_map[result.persona_id].demographics.role
                if role not in role_groups:
                    role_groups[role] = []
                role_groups[role].append(result)
                
        for role, group_results in role_groups.items():
            segments[f"Role: {role}"] = self._calculate_adoption_rate(group_results)
            
        # Segment by Company Size
        size_groups = {}
        for result in results:
            if result.persona_id in persona_map:
                size = persona_map[result.persona_id].demographics.company_size or "Unknown"
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(result)
                
        for size, group_results in size_groups.items():
            if size != "Unknown":
                segments[f"Company Size: {size}"] = self._calculate_adoption_rate(group_results)

        # Segment by Tech Adoption
        tech_groups = {}
        for result in results:
            if result.persona_id in persona_map:
                tech = persona_map[result.persona_id].behavior_patterns.technology_adoption.value
                if tech not in tech_groups:
                    tech_groups[tech] = []
                tech_groups[tech].append(result)
                
        for tech, group_results in tech_groups.items():
            segments[f"Tech Adoption: {tech}"] = self._calculate_adoption_rate(group_results)

        return segments
        
    def _segment_by_confidence(self, results: List[SimulationResponse]) -> Dict[str, float]:
        """Fallback segmentation by confidence levels"""
        segments = {
            "High Confidence": [],
            "Medium Confidence": [],
            "Low Confidence": []
        }
        
        for result in results:
            if result.confidence >= 0.8:
                segments["High Confidence"].append(result)
            elif result.confidence >= 0.5:
                segments["Medium Confidence"].append(result)
            else:
                segments["Low Confidence"].append(result)
        
        segment_rates = {}
        for segment_name, segment_results in segments.items():
            if segment_results:
                segment_rates[segment_name] = self._calculate_adoption_rate(segment_results)
            else:
                segment_rates[segment_name] = 0.0
                
        return segment_rates
    
    def _cluster_objections(self, results: List[SimulationResponse]) -> List[ObjectionCluster]:
        """Cluster similar objections from rejection reasons"""
        # Get all rejection reasons
        rejections = [r for r in results if r.decision == SimulationDecision.REJECT]
        
        if not rejections:
            return []
        
        # Simple clustering based on common keywords
        objection_keywords = {}
        
        for rejection in rejections:
            reasoning = rejection.reasoning.lower()
            key_factors = [f.lower() for f in rejection.key_factors]
            
            # Extract common objection themes
            themes = self._extract_objection_themes(reasoning, key_factors)
            
            for theme in themes:
                if theme not in objection_keywords:
                    objection_keywords[theme] = []
                objection_keywords[theme].append(rejection.persona_id)
        
        # Convert to ObjectionCluster objects
        clusters = []
        for theme, persona_ids in objection_keywords.items():
            cluster = ObjectionCluster(
                objection=theme,
                frequency=len(persona_ids),
                affected_personas=persona_ids
            )
            clusters.append(cluster)
        
        # Sort by frequency and return top objections
        clusters.sort(key=lambda x: x.frequency, reverse=True)
        return clusters[:5]  # Top 5 objections
    
    def _extract_objection_themes(self, reasoning: str, key_factors: List[str]) -> List[str]:
        """Extract objection themes from reasoning and key factors"""
        themes = []
        
        # Common objection patterns
        objection_patterns = {
            "cost": ["cost", "budget", "expensive", "price"],
            "complexity": ["complex", "difficult", "complicated", "integration"],
            "risk": ["risk", "uncertain", "unknown", "unproven"],
            "time": ["time", "timeline", "schedule", "urgent"],
            "value": ["value", "benefit", "roi", "return"],
            "fit": ["fit", "relevant", "applicable", "suitable"]
        }
        
        text = reasoning + " " + " ".join(key_factors)
        
        for theme, keywords in objection_patterns.items():
            if any(keyword in text for keyword in keywords):
                themes.append(theme.title() + " concerns")
        
        return themes if themes else ["General concerns"]
    
    def _identify_success_factors(self, results: List[SimulationResponse]) -> List[SuccessFactor]:
        """Identify key factors that drive adoption"""
        adoptions = [r for r in results if r.decision == SimulationDecision.ADOPT]
        
        if not adoptions:
            return []
        
        # Count key factors mentioned in adoptions
        factor_counts = Counter()
        factor_personas = {}
        
        for adoption in adoptions:
            cleaned_factors = set([f.lower().strip() for f in adoption.key_factors])
            for factor in cleaned_factors:
                if not factor: continue
                factor_counts[factor] += 1
                if factor not in factor_personas:
                    factor_personas[factor] = []
                factor_personas[factor].append(adoption.persona_id)
        
        # Convert to SuccessFactor objects
        success_factors = []
        total_adoptions = len(adoptions)
        
        for factor, count in factor_counts.most_common(5):
            importance = count / total_adoptions
            success_factor = SuccessFactor(
                factor=factor.title(),
                importance=importance,
                supporting_personas=factor_personas[factor]
            )
            success_factors.append(success_factor)
        
        return success_factors
    
    def _generate_recommendations(
        self, 
        results: List[SimulationResponse],
        adoption_rate: float,
        objections: List[ObjectionCluster],
        success_factors: List[SuccessFactor]
    ) -> Recommendations:
        """Generate actionable recommendations"""
        
        messaging_recommendations = []
        target_segment_recommendations = []
        feature_improvement_recommendations = []
        
        # Messaging recommendations based on success factors
        if success_factors:
            top_factor = success_factors[0].factor
            messaging_recommendations.append(f"Emphasize {top_factor.lower()} in marketing materials")
            messaging_recommendations.append(f"Lead with value proposition around {top_factor.lower()}")
        
        # Address top objections
        if objections:
            top_objection = objections[0].objection
            messaging_recommendations.append(f"Address {top_objection.lower()} proactively in communications")
            feature_improvement_recommendations.append(f"Consider improvements to address {top_objection.lower()}")
        
        # Target segment recommendations based on adoption patterns
        high_confidence_adopters = [r for r in results 
                                   if r.decision == SimulationDecision.ADOPT and r.confidence >= 0.8]
        
        if high_confidence_adopters:
            target_segment_recommendations.append("Focus initial launch on high-confidence early adopters")
            target_segment_recommendations.append("Use early adopters as case studies and references")
        
        # Feature improvement recommendations
        if adoption_rate < 0.3:
            feature_improvement_recommendations.append("Consider significant feature enhancements before launch")
            feature_improvement_recommendations.append("Conduct additional user research to identify missing value")
        elif adoption_rate < 0.6:
            feature_improvement_recommendations.append("Minor feature refinements could improve adoption")
        
        return Recommendations(
            messaging=messaging_recommendations,
            target_segments=target_segment_recommendations,
            feature_improvements=feature_improvement_recommendations
        )
    
    def generate_csv_export(self, experiment: 'Experiment') -> str:
        """
        Generate CSV export for an experiment
        
        Args:
            experiment: The experiment object containing results and personas
            
        Returns:
            CSV string content
        """
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Persona Name", "Role", "Company Size", "Industry", 
            "Age", "Decision", "Confidence", "Reasoning", "Key Factors"
        ])
        
        # Create a map for persona lookup
        persona_map = {p.id: p for p in experiment.personas}
        
        for result in experiment.simulation_results:
            persona = persona_map.get(result.persona_id)
            if not persona:
                continue
                
            writer.writerow([
                persona.name,
                persona.demographics.role,
                persona.demographics.company_size or "N/A",
                persona.demographics.industry or "N/A",
                persona.demographics.age,
                result.decision.value,
                f"{result.confidence:.2f}",
                result.reasoning,
                ", ".join(result.key_factors)
            ])
            
        return output.getvalue()

    def _empty_insights(self) -> AggregatedInsights:
        """Return empty insights when no results are available"""
        return AggregatedInsights(
            overall_adoption_rate=0.0,
            confidence_interval=(0.0, 0.0),
            adoption_by_segment={},
            top_objections=[],
            key_success_factors=[],
            recommendations=Recommendations(
                messaging=[],
                target_segments=[],
                feature_improvements=[]
            )
        )