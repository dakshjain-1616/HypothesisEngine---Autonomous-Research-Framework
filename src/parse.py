"""
Hypothesis Parsing Module
Parses user-provided hypotheses or research questions into core claims,
identifies variables, and extracts the research domain.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class ResearchDomain(Enum):
    """Research domains for classification."""
    HEALTH = "health"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    POLITICAL = "political"
    EDUCATION = "education"
    PSYCHOLOGY = "psychology"
    GENERAL = "general"


@dataclass
class ParsedHypothesis:
    """Result of parsing a hypothesis."""
    original: str
    domain: ResearchDomain
    domain_confidence: float
    core_claims: List[str]
    variables: Dict[str, str]
    entities: List[str]
    relationships: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "original": self.original,
            "domain": self.domain.value,
            "domain_confidence": self.domain_confidence,
            "core_claims": self.core_claims,
            "variables": self.variables,
            "entities": self.entities,
            "relationships": self.relationships
        }


class DomainClassifier:
    """Classifies hypotheses into research domains."""
    
    DOMAIN_KEYWORDS = {
        ResearchDomain.HEALTH: [
            "health", "medical", "disease", "treatment", "patient", "clinical",
            "medicine", "therapy", "diagnosis", "symptom", "hospital", "doctor",
            "nurse", "healthcare", "wellness", "fitness", "nutrition", "diet",
            "exercise", "mental health", "depression", "anxiety", "cancer",
            "diabetes", "heart", "blood pressure", "cholesterol", "vaccine",
            "medication", "drug", "pharmaceutical", "epidemic", "pandemic"
        ],
        ResearchDomain.ECONOMICS: [
            "economy", "market", "price", "inflation", "gdp", "trade", "financial",
            "economic", "revenue", "profit", "loss", "investment", "stock", "bond",
            "interest rate", "unemployment", "employment", "wage", "salary",
            "consumer", "demand", "supply", "monopoly", "competition", "tax",
            "fiscal", "monetary", "bank", "currency", "exchange rate", "import",
            "export", "tariff", "subsidy", "recession", "growth", "wealth", "income"
        ],
        ResearchDomain.TECHNOLOGY: [
            "technology", "software", "ai", "machine learning", "algorithm", "computing",
            "artificial intelligence", "deep learning", "neural network", "data science",
            "programming", "code", "application", "app", "system", "hardware",
            "computer", "internet", "network", "cybersecurity", "encryption",
            "blockchain", "cloud", "database", "automation", "robotics", "robot",
            "virtual reality", "augmented reality", "quantum", "chip", "processor",
            "semiconductor", "digital", "electronic", "device", "gadget", "innovation"
        ],
        ResearchDomain.ENVIRONMENT: [
            "climate", "environment", "pollution", "carbon", "renewable", "temperature",
            "global warming", "greenhouse", "emission", "sustainability", "ecology",
            "ecosystem", "biodiversity", "species", "habitat", "conservation",
            "deforestation", "forest", "ocean", "water", "air quality", "waste",
            "recycling", "solar", "wind", "energy", "fossil fuel", "oil", "gas",
            "coal", "nuclear", "weather", "natural disaster", "flood", "drought",
            "hurricane", "earthquake", "sea level", "ozone", "acid rain"
        ],
        ResearchDomain.SOCIAL: [
            "society", "social", "behavior", "psychology", "demographic", "culture",
            "community", "relationship", "family", "marriage", "divorce", "parenting",
            "education", "school", "university", "student", "teacher", "learning",
            "crime", "law", "justice", "police", "court", "prison", "violence",
            "poverty", "inequality", "discrimination", "racism", "sexism",
            "gender", "identity", "sexuality", "religion", "belief", "value",
            "norm", "tradition", "custom", "language", "communication", "media"
        ],
        ResearchDomain.POLITICAL: [
            "political", "politics", "government", "policy", "election", "vote",
            "democracy", "republic", "monarchy", "dictatorship", "authoritarian",
            "legislation", "law", "regulation", "congress", "parliament", "senate",
            "president", "prime minister", "minister", "official", "bureaucracy",
            "party", "ideology", "liberal", "conservative", "socialist", "nationalist",
            "diplomacy", "foreign policy", "international relations", "war", "peace",
            "treaty", "alliance", "sanction", "constitution", "rights", "freedom"
        ],
        ResearchDomain.EDUCATION: [
            "education", "learning", "teaching", "school", "university", "college",
            "student", "teacher", "professor", "academic", "curriculum", "course",
            "degree", "diploma", "certificate", "graduation", "enrollment", "admission",
            "classroom", "online learning", "e-learning", "distance education",
            "homework", "assignment", "exam", "test", "quiz", "grade", "score",
            "literacy", "numeracy", "skill", "competency", "knowledge", "understanding",
            "pedagogy", "andragogy", "cognitive development", "critical thinking"
        ],
        ResearchDomain.PSYCHOLOGY: [
            "psychology", "psychological", "mental", "mind", "brain", "cognitive",
            "behavior", "behavioral", "emotion", "feeling", "mood", "attitude",
            "personality", "trait", "character", "temperament", "consciousness",
            "perception", "sensation", "memory", "learning", "intelligence",
            "motivation", "desire", "need", "drive", "goal", "achievement",
            "stress", "anxiety", "depression", "trauma", "disorder", "therapy",
            "development", "child", "adolescent", "aging", "lifespan", "social psychology"
        ]
    }
    
    def classify(self, hypothesis: str) -> Tuple[ResearchDomain, float]:
        """
        Classify hypothesis into a research domain.
        
        Returns:
            Tuple of (domain, confidence_score)
        """
        hypothesis_lower = hypothesis.lower()
        words = set(re.findall(r'\b\w+\b', hypothesis_lower))
        
        domain_scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            # Multi-word phrase matches are more discriminating — weight them higher
            multi_word_matches = sum(1 for kw in keywords if ' ' in kw and kw in hypothesis_lower)
            single_word_matches = sum(1 for kw in keywords if ' ' not in kw and kw in hypothesis_lower)
            # Count word overlap (single-word keywords present in hypothesis word set)
            keyword_words = set(kw for kw in keywords if ' ' not in kw)
            word_overlap = len(words & keyword_words)

            # Multi-word matches score highest (more specific), then single-word matches, then overlap
            domain_scores[domain] = (multi_word_matches * 4) + (single_word_matches * 2) + word_overlap
        
        # Get best matching domain
        if not domain_scores or max(domain_scores.values()) == 0:
            return ResearchDomain.GENERAL, 0.5
        
        best_domain = max(domain_scores, key=domain_scores.get)
        best_score = domain_scores[best_domain]
        
        # Calculate confidence based on score margin
        total_score = sum(domain_scores.values())
        if total_score > 0:
            confidence = min(0.5 + (best_score / total_score), 1.0)
        else:
            confidence = 0.5
        
        return best_domain, confidence


class ClaimExtractor:
    """Extracts core claims from a hypothesis."""
    
    CAUSAL_CONNECTIVES = [
        " because ", " therefore ", " thus ", " hence ", " consequently ",
        " leads to ", " causes ", " results in ", " implies ", " suggests ",
        " is associated with ", " correlates with ", " relates to ",
        " affects ", " influences ", " impacts ", " determines ", " drives ",
        " produces ", " generates ", " creates ", " enables ", " prevents ",
        " reduces ", " increases ", " improves ", " enhances ", " decreases "
    ]
    
    CONDITIONAL_MARKERS = [
        " if ", " when ", " while ", " during ", " given ", " assuming ",
        " provided that ", " in cases where ", " under conditions of ",
        " for ", " among ", " in ", " within ", " across ", " throughout "
    ]
    
    def extract(self, hypothesis: str) -> List[str]:
        """
        Extract core claims from a hypothesis.
        
        Returns:
            List of core claims
        """
        claims = []
        hypothesis_clean = hypothesis.strip()
        
        # Strategy 1: Split by causal connectives
        causal_claims = self._split_by_connectives(
            hypothesis_clean, self.CAUSAL_CONNECTIVES
        )
        claims.extend(causal_claims)
        
        # Strategy 2: Extract conditional claims
        conditional_claims = self._extract_conditional_claims(hypothesis_clean)
        claims.extend(conditional_claims)
        
        # Strategy 3: Extract main assertion
        main_claim = self._extract_main_assertion(hypothesis_clean)
        if main_claim and main_claim not in claims:
            claims.insert(0, main_claim)
        
        # Clean and deduplicate
        claims = self._clean_claims(claims)
        
        return claims[:5]  # Return max 5 claims
    
    def _split_by_connectives(self, text: str, connectives: List[str]) -> List[str]:
        """Split text by causal or conditional connectives."""
        claims = [text]
        text_lower = text.lower()
        
        for conn in connectives:
            if conn in text_lower:
                new_claims = []
                for claim in claims:
                    # Split while preserving case
                    parts = re.split(re.escape(conn), claim, flags=re.IGNORECASE)
                    new_claims.extend([p.strip() for p in parts if p.strip()])
                claims = new_claims
        
        return claims
    
    def _extract_conditional_claims(self, hypothesis: str) -> List[str]:
        """Extract claims based on conditional markers."""
        claims = []
        
        for marker in self.CONDITIONAL_MARKERS:
            pattern = marker.strip() + r'\s+([^,;]+)'
            matches = re.findall(pattern, hypothesis, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    claims.append(f"Condition: {match.strip()}")
        
        return claims
    
    def _extract_main_assertion(self, hypothesis: str) -> Optional[str]:
        """Extract the main assertion from the hypothesis."""
        # Remove common prefixes
        prefixes = [
            r'^\s*hypothesis:\s*',
            r'^\s*research question:\s*',
            r'^\s*does\s+',
            r'^\s*is\s+',
            r'^\s*are\s+',
            r'^\s*can\s+',
            r'^\s*will\s+',
            r'^\s*should\s+',
        ]
        
        cleaned = hypothesis
        for prefix in prefixes:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
        
        cleaned = cleaned.strip()
        
        # Extract main clause (before first comma or conjunction if complex)
        main_clause = re.split(r'[,;]|\s+and\s+|\s+but\s+', cleaned)[0].strip()
        
        if len(main_clause) > 10:
            return main_clause.capitalize()
        
        return cleaned.capitalize() if len(cleaned) > 10 else None
    
    def _clean_claims(self, claims: List[str]) -> List[str]:
        """Clean and deduplicate claims."""
        cleaned = []
        seen = set()
        
        for claim in claims:
            # Clean the claim
            clean = claim.strip()
            clean = re.sub(r'\s+', ' ', clean)  # Normalize whitespace
            clean = clean.capitalize()
            
            # Skip if too short or already seen
            if len(clean) < 10:
                continue
            
            # Check for duplicates (case-insensitive)
            clean_lower = clean.lower()
            if clean_lower not in seen:
                seen.add(clean_lower)
                cleaned.append(clean)
        
        return cleaned


class VariableExtractor:
    """Extracts variables from hypotheses."""
    
    VARIABLE_PATTERNS = {
        "trend": [
            r"(\w+)\s+(?:increases?|decreases?|rises?|falls?|grows?|declines?|improves?|worsens?)",
            r"(?:increase|decrease|rise|fall|growth|decline)\s+(?:in|of)\s+(\w+)",
        ],
        "level": [
            r"(high|low|higher|lower|more|less|greater|fewer)\s+(?:levels?\s+of\s+)?(\w+)",
            r"(\w+)\s+(?:levels?|amounts?|concentrations?)",
        ],
        "comparison": [
            r"(\w+)\s+(?:vs\.?|versus|compared\s+to|relative\s+to)\s+(\w+)",
            r"(?:difference|gap)\s+(?:between|in)\s+(\w+)\s+and\s+(\w+)",
        ],
        "condition": [
            r"(?:when|if|while|during)\s+([^,;]+?)(?:,|then|the)",
            r"under\s+(?:conditions?\s+of\s+)?([^,;]+)",
        ],
        "outcome": [
            r"(?:leads?\s+to|results?\s+in|causes?|produces?|generates?)\s+([^,;.]+)",
            r"(?:effect|impact|influence|consequence)\s+(?:of|on)\s+([^,;.]+)",
        ]
    }
    
    def extract(self, hypothesis: str) -> Dict[str, str]:
        """
        Extract variables from hypothesis.
        
        Returns:
            Dictionary mapping variable names to their types
        """
        variables = {}
        hypothesis_lower = hypothesis.lower()
        
        for var_type, patterns in self.VARIABLE_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, hypothesis_lower)
                for match in matches:
                    if isinstance(match, tuple):
                        # Multi-group match - combine groups
                        var_name = "_".join(m.strip() for m in match if m.strip())
                    else:
                        var_name = match.strip()
                    
                    # Clean and validate
                    var_name = re.sub(r'\s+', '_', var_name)
                    var_name = re.sub(r'[^\w_]', '', var_name)
                    
                    if len(var_name) > 2 and var_name not in variables:
                        variables[var_name] = var_type
        
        return variables
    
    def extract_entities(self, hypothesis: str) -> List[str]:
        """Extract named entities from hypothesis."""
        entities = []
        
        # Look for capitalized phrases (potential proper nouns)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, hypothesis)
        
        # Filter out common words
        common_words = {'The', 'A', 'An', 'This', 'That', 'These', 'Those',
                       'What', 'When', 'Where', 'Why', 'How', 'Who', 'Which',
                       'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being',
                       'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will',
                       'Would', 'Could', 'Should', 'May', 'Might', 'Must',
                       'Can', 'Shall', 'If', 'Then', 'Than', 'As', 'Like',
                       'Such', 'Very', 'More', 'Most', 'Less', 'Least',
                       'Many', 'Much', 'Few', 'Little', 'Several', 'Both',
                       'All', 'Each', 'Every', 'Some', 'Any', 'No', 'Not',
                       'Only', 'Own', 'Same', 'So', 'Just', 'Also', 'Well',
                       'Back', 'Still', 'Even', "It's", "Don't", "Won't"}
        
        for match in matches:
            if match not in common_words and len(match) > 2:
                entities.append(match)
        
        return list(dict.fromkeys(entities))  # Remove duplicates while preserving order
    
    def extract_relationships(self, hypothesis: str) -> List[str]:
        """Extract relationship indicators from hypothesis."""
        relationships = []
        
        # Causal relationships
        causal = [
            "causes", "caused by", "leads to", "results in", "produces",
            "generates", "creates", "triggers", "induces", "promotes",
            "drives", "determines", "influences", "affects", "impacts"
        ]
        
        # Correlational relationships
        correlational = [
            "correlates with", "associated with", "linked to", "related to",
            "connected to", "tied to", "coupled with", "accompanied by"
        ]
        
        # Comparative relationships
        comparative = [
            "greater than", "less than", "higher than", "lower than",
            "more than", "fewer than", "better than", "worse than",
            "superior to", "inferior to", "equal to", "similar to",
            "different from", "versus", "compared to"
        ]
        
        hypothesis_lower = hypothesis.lower()
        
        for rel in causal:
            if rel in hypothesis_lower:
                relationships.append(f"causal: {rel}")
        
        for rel in correlational:
            if rel in hypothesis_lower:
                relationships.append(f"correlational: {rel}")
        
        for rel in comparative:
            if rel in hypothesis_lower:
                relationships.append(f"comparative: {rel}")
        
        return relationships


class HypothesisParser:
    """Main parser class that orchestrates hypothesis analysis."""
    
    def __init__(self):
        self.domain_classifier = DomainClassifier()
        self.claim_extractor = ClaimExtractor()
        self.variable_extractor = VariableExtractor()
    
    def parse(self, hypothesis: str) -> ParsedHypothesis:
        """
        Parse a hypothesis into structured components.
        
        Args:
            hypothesis: The research question or hypothesis to parse
            
        Returns:
            ParsedHypothesis object with extracted components
        """
        if not hypothesis or not isinstance(hypothesis, str):
            raise ValueError("Hypothesis must be a non-empty string")
        
        # Clean the hypothesis
        hypothesis = hypothesis.strip()
        
        # Step 1: Classify domain
        domain, domain_confidence = self.domain_classifier.classify(hypothesis)
        
        # Step 2: Extract core claims
        core_claims = self.claim_extractor.extract(hypothesis)
        
        # Step 3: Extract variables
        variables = self.variable_extractor.extract(hypothesis)
        
        # Step 4: Extract entities
        entities = self.variable_extractor.extract_entities(hypothesis)
        
        # Step 5: Extract relationships
        relationships = self.variable_extractor.extract_relationships(hypothesis)
        
        return ParsedHypothesis(
            original=hypothesis,
            domain=domain,
            domain_confidence=domain_confidence,
            core_claims=core_claims,
            variables=variables,
            entities=entities,
            relationships=relationships
        )


# Convenience function
def parse_hypothesis(hypothesis: str) -> Dict:
    """
    Parse a hypothesis and return as dictionary.
    
    Args:
        hypothesis: The research question or hypothesis
        
    Returns:
        Dictionary with parsed components
    """
    parser = HypothesisParser()
    result = parser.parse(hypothesis)
    return result.to_dict()


if __name__ == "__main__":
    # Test with example hypotheses
    test_hypotheses = [
        "Regular exercise improves cognitive function in older adults",
        "Higher minimum wages lead to increased unemployment among low-skilled workers",
        "Artificial intelligence will replace more jobs than it creates by 2030",
        "Renewable energy sources can fully replace fossil fuels within 20 years",
        "Social media usage is linked to increased rates of depression in teenagers"
    ]
    
    parser = HypothesisParser()
    
    for hypothesis in test_hypotheses:
        print("\n" + "=" * 60)
        print(f"Hypothesis: {hypothesis}")
        print("=" * 60)
        
        result = parser.parse(hypothesis)
        
        print(f"\nDomain: {result.domain.value} (confidence: {result.domain_confidence:.2f})")
        print(f"\nCore Claims:")
        for i, claim in enumerate(result.core_claims, 1):
            print(f"  {i}. {claim}")
        
        if result.variables:
            print(f"\nVariables:")
            for var, var_type in result.variables.items():
                print(f"  - {var}: {var_type}")
        
        if result.entities:
            print(f"\nEntities: {', '.join(result.entities[:5])}")
        
        if result.relationships:
            print(f"\nRelationships: {', '.join(result.relationships[:3])}")