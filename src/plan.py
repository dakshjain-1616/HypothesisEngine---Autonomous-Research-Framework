"""
Research Plan Builder Module
Constructs research plans with 3-6 sub-questions categorized by method.
"""

import json
import re
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Import from parse module
from parse import ParsedHypothesis, ResearchDomain


class ResearchMethod(Enum):
    """Types of research methods available."""
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    LOGICAL_REASONING = "logical_reasoning"


class EvidenceStatus(Enum):
    """Status of evidence evaluation."""
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    PARTIAL = "partial"


@dataclass
class SubQuestion:
    """Represents a sub-question in the research plan."""
    id: str
    question: str
    method: ResearchMethod
    rationale: str
    evidence: Optional[Any] = None
    findings: str = ""
    status: EvidenceStatus = EvidenceStatus.INCONCLUSIVE
    sources: List[Dict] = field(default_factory=list)
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "question": self.question,
            "method": self.method.value,
            "rationale": self.rationale,
            "findings": self.findings,
            "status": self.status.value,
            "sources": self.sources,
            "priority": self.priority,
            "dependencies": self.dependencies
        }


@dataclass
class ResearchPlan:
    """Complete research plan for a hypothesis."""
    hypothesis: str
    domain: str
    core_claims: List[str]
    variables: Dict[str, str]
    sub_questions: List[SubQuestion]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    estimated_duration: str = "unknown"
    required_resources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "hypothesis": self.hypothesis,
            "domain": self.domain,
            "core_claims": self.core_claims,
            "variables": self.variables,
            "sub_questions": [sq.to_dict() for sq in self.sub_questions],
            "created_at": self.created_at,
            "estimated_duration": self.estimated_duration,
            "required_resources": self.required_resources
        }


class QuestionTemplateLibrary:
    """Library of question templates for different research methods."""
    
    TEMPLATES = {
        ResearchMethod.WEB_SEARCH: {
            "evidence": [
                "What is the current scientific consensus on {topic}?",
                "What empirical evidence exists for {topic}?",
                "What are the latest research findings on {topic}?",
                "What do experts say about {topic}?",
                "What statistics or data are available on {topic}?",
            ],
            "mechanism": [
                "What mechanisms explain {topic}?",
                "What processes underlie {topic}?",
                "What causal pathways are involved in {topic}?",
            ],
            "context": [
                "What is the historical context of {topic}?",
                "What are the contextual factors affecting {topic}?",
                "What populations or groups are affected by {topic}?",
            ]
        },
        ResearchMethod.CODE_EXECUTION: {
            "calculation": [
                "Can we calculate or simulate {topic} using available data?",
                "What quantitative relationships exist in {topic}?",
                "Can we model {topic} mathematically?",
            ],
            "analysis": [
                "What patterns emerge when analyzing data on {topic}?",
                "Can we validate {topic} through statistical analysis?",
                "What correlations exist in {topic}?",
            ],
            "simulation": [
                "Can we simulate {topic} to test predictions?",
                "What outcomes does modeling {topic} produce?",
            ]
        },
        ResearchMethod.LOGICAL_REASONING: {
            "implications": [
                "What are the logical implications of {topic}?",
                "What would follow if {topic} were true?",
            ],
            "assumptions": [
                "What assumptions underlie {topic}?",
                "What premises must be true for {topic} to hold?",
            ],
            "consistency": [
                "Are there contradictions in the claims about {topic}?",
                "Is {topic} internally consistent?",
            ],
            "comparison": [
                "How does {topic} compare to established principles?",
                "What analogies support or challenge {topic}?",
            ]
        }
    }
    
    @classmethod
    def get_template(cls, method: ResearchMethod, category: str = None, 
                     topic: str = "this topic") -> str:
        """Get a question template for a research method."""
        if method not in cls.TEMPLATES:
            return f"What can we learn about {topic}?"
        
        templates = cls.TEMPLATES[method]
        
        if category and category in templates:
            import random
            template = random.choice(templates[category])
        else:
            import random
            all_templates = []
            for cat_templates in templates.values():
                all_templates.extend(cat_templates)
            template = random.choice(all_templates)
        
        return template.format(topic=topic)
    
    @classmethod
    def get_all_categories(cls, method: ResearchMethod) -> List[str]:
        """Get all available categories for a method."""
        if method not in cls.TEMPLATES:
            return []
        return list(cls.TEMPLATES[method].keys())


class ResearchPlanBuilder:
    """Builds research plans from parsed hypotheses."""
    
    def __init__(self):
        self.template_library = QuestionTemplateLibrary()
    
    def build(self, parsed, num_questions: int = 6) -> List[SubQuestion]:
        """Build a research plan with sub-questions."""
        num_questions = max(3, min(6, num_questions))
        
        sub_questions = []
        question_id = 0
        
        # Determine method distribution
        method_distribution = self._determine_method_distribution(parsed, num_questions)
        
        # Generate questions for each method
        for method, count in method_distribution.items():
            for i in range(count):
                question_id += 1
                sq = self._generate_subquestion(parsed, method, question_id, i, count)
                sub_questions.append(sq)
        
        # Sort by priority and ID
        sub_questions.sort(key=lambda x: (x.priority, x.id))
        
        return sub_questions[:num_questions]
    
    def _determine_method_distribution(self, parsed: ParsedHypothesis, total: int) -> Dict[ResearchMethod, int]:
        """Determine how many questions per method."""
        distribution = {method: 0 for method in ResearchMethod}
        
        # Base distribution depends on domain
        empirical_domains = [ResearchDomain.HEALTH, ResearchDomain.ECONOMICS, 
                            ResearchDomain.ENVIRONMENT, ResearchDomain.SOCIAL]
        
        if parsed.domain in empirical_domains:
            distribution[ResearchMethod.WEB_SEARCH] = max(2, total // 2)
            distribution[ResearchMethod.CODE_EXECUTION] = max(1, total // 4)
            distribution[ResearchMethod.LOGICAL_REASONING] = max(1, total - 
                distribution[ResearchMethod.WEB_SEARCH] - 
                distribution[ResearchMethod.CODE_EXECUTION])
        elif parsed.domain == ResearchDomain.TECHNOLOGY:
            distribution[ResearchMethod.WEB_SEARCH] = max(2, total // 3)
            distribution[ResearchMethod.CODE_EXECUTION] = max(1, total // 3)
            distribution[ResearchMethod.LOGICAL_REASONING] = max(1, total // 3)
        else:
            # General/philosophical domains
            distribution[ResearchMethod.WEB_SEARCH] = max(1, total // 3)
            distribution[ResearchMethod.CODE_EXECUTION] = 0
            distribution[ResearchMethod.LOGICAL_REASONING] = max(2, 2 * total // 3)
        
        # Adjust to match total
        current_total = sum(distribution.values())
        if current_total < total:
            distribution[ResearchMethod.WEB_SEARCH] += (total - current_total)
        elif current_total > total:
            excess = current_total - total
            if distribution[ResearchMethod.LOGICAL_REASONING] >= excess:
                distribution[ResearchMethod.LOGICAL_REASONING] -= excess
            else:
                excess -= distribution[ResearchMethod.LOGICAL_REASONING]
                distribution[ResearchMethod.LOGICAL_REASONING] = 0
                if distribution[ResearchMethod.CODE_EXECUTION] >= excess:
                    distribution[ResearchMethod.CODE_EXECUTION] -= excess
        
        return distribution
    
    def _generate_subquestion(self, parsed: ParsedHypothesis, method: ResearchMethod,
                              question_id: int, index: int, total_for_method: int) -> SubQuestion:
        """Generate a single sub-question."""
        # Determine category based on index
        categories = self.template_library.get_all_categories(method)
        if categories:
            category = categories[index % len(categories)]
        else:
            category = None
        
        # Determine topic — always anchor first question on the full hypothesis
        if index == 0:
            topic = parsed.original
        elif index < len(parsed.core_claims) and len(parsed.core_claims[index]) > 15:
            topic = parsed.core_claims[index]
        elif parsed.entities:
            # Use entity + original hypothesis context so questions aren't orphaned
            topic = f"{parsed.entities[0]} ({parsed.original[:60]}...)" if len(parsed.original) > 60 else parsed.original
        else:
            topic = parsed.original
        
        # Generate question
        question_text = self.template_library.get_template(method, category, topic)
        
        # Generate rationale
        rationale_templates = {
            ResearchMethod.WEB_SEARCH: [
                f"To gather empirical evidence about {topic}",
                f"To find current research and expert opinions on {topic}",
                f"To collect data and statistics related to {topic}",
            ],
            ResearchMethod.CODE_EXECUTION: [
                f"To validate quantitative aspects of {topic} through analysis",
                f"To calculate or simulate relationships in {topic}",
                f"To identify patterns in data related to {topic}",
            ],
            ResearchMethod.LOGICAL_REASONING: [
                f"To analyze logical consistency of claims about {topic}",
                f"To examine underlying assumptions in {topic}",
                f"To evaluate implications and consequences of {topic}",
            ]
        }
        
        rationale = rationale_templates[method][index % 3]
        
        # Determine priority
        priority = 1 if index == 0 else (2 if index < 3 else 3)
        
        return SubQuestion(
            id=f"SQ{question_id:02d}",
            question=question_text,
            method=method,
            rationale=rationale,
            priority=priority
        )


# Convenience function
def build_research_plan(parsed_hypothesis: Dict, num_questions: int = 6) -> Dict:
    """Build a research plan from a parsed hypothesis."""
    from parse import ParsedHypothesis, ResearchDomain
    
    domain = ResearchDomain(parsed_hypothesis.get('domain', 'general'))
    
    parsed = ParsedHypothesis(
        original=parsed_hypothesis['original'],
        domain=domain,
        domain_confidence=parsed_hypothesis['domain_confidence'],
        core_claims=parsed_hypothesis['core_claims'],
        variables=parsed_hypothesis['variables'],
        entities=parsed_hypothesis['entities'],
        relationships=parsed_hypothesis['relationships']
    )
    
    builder = ResearchPlanBuilder()
    sub_questions = builder.build(parsed, num_questions)
    
    return {
        "hypothesis": parsed.original,
        "domain": parsed.domain.value,
        "core_claims": parsed.core_claims,
        "variables": parsed.variables,
        "sub_questions": [sq.to_dict() for sq in sub_questions],
        "num_questions": len(sub_questions)
    }


if __name__ == "__main__":
    # Test the plan builder
    from parse import HypothesisParser
    
    test_hypotheses = [
        "Regular exercise improves cognitive function in older adults",
        "Higher minimum wages lead to increased unemployment among low-skilled workers",
        "Artificial intelligence will replace more jobs than it creates by 2030",
    ]
    
    parser = HypothesisParser()
    
    for hypothesis in test_hypotheses:
        print("\n" + "=" * 70)
        print(f"Hypothesis: {hypothesis}")
        print("=" * 70)
        
        parsed = parser.parse(hypothesis)
        
        builder = ResearchPlanBuilder()
        sub_questions = builder.build(parsed, num_questions=5)
        
        print(f"\nResearch Plan ({len(sub_questions)} sub-questions):")
        print("-" * 70)
        
        for sq in sub_questions:
            print(f"\n{sq.id} [{sq.method.value}]")
            print(f"  Q: {sq.question}")
            print(f"  Rationale: {sq.rationale}")
            print(f"  Priority: {sq.priority}")