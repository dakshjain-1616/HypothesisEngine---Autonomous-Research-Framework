"""
Synthesis Engine Module
Synthesizes findings from research execution to determine whether
the hypothesis is supported, refuted, or nuanced.
"""

import json
import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class EvidenceStatus(Enum):
    """Status of evidence evaluation."""
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    PARTIAL = "partial"


class ConfidenceLevel(Enum):
    """Confidence levels for verdicts."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class SynthesisResult:
    """Result of synthesizing evidence."""
    verdict: str
    verdict_summary: str
    status: EvidenceStatus
    confidence_level: ConfidenceLevel
    confidence_score: float
    supporting_evidence: List[Dict]
    refuting_evidence: List[Dict]
    inconclusive_evidence: List[Dict]
    reasoning: str
    limitations: List[str]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "verdict": self.verdict,
            "verdict_summary": self.verdict_summary,
            "status": self.status.value,
            "confidence_level": self.confidence_level.value,
            "confidence_score": self.confidence_score,
            "supporting_evidence": self.supporting_evidence,
            "refuting_evidence": self.refuting_evidence,
            "inconclusive_evidence": self.inconclusive_evidence,
            "reasoning": self.reasoning,
            "limitations": self.limitations,
            "generated_at": self.generated_at
        }


class EvidenceWeighter:
    """Weights evidence based on source quality and relevance."""
    
    # Source reliability scores (0-1)
    SOURCE_RELIABILITY = {
        "peer_reviewed": 0.95,
        "academic": 0.90,
        "government": 0.85,
        "established_media": 0.75,
        "industry": 0.70,
        "blog": 0.50,
        "unknown": 0.40
    }
    
    def calculate_weight(self, evidence: Dict) -> float:
        """Calculate weight for a piece of evidence."""
        # Base weight from status
        status_weights = {
            "supported": 1.0,
            "refuted": 1.0,
            "partial": 0.7,
            "inconclusive": 0.3
        }
        
        base_weight = status_weights.get(evidence.get('status', 'inconclusive'), 0.3)
        
        # Source reliability
        source_type = evidence.get('source_type', 'unknown')
        reliability = self.SOURCE_RELIABILITY.get(source_type, 0.4)
        
        # Evidence strength indicator
        strength = evidence.get('strength', 0.5)
        
        # Calculate final weight
        weight = base_weight * reliability * (0.5 + 0.5 * strength)
        
        return min(weight, 1.0)


class SynthesisEngine:
    """Synthesizes evidence to reach a verdict on the hypothesis."""
    
    def __init__(self):
        self.weighter = EvidenceWeighter()
    
    def synthesize(self, sub_questions: List[Dict]) -> SynthesisResult:
        """
        Synthesize all evidence to reach a final verdict.
        
        Args:
            sub_questions: List of sub-question dictionaries with findings
            
        Returns:
            SynthesisResult with verdict and confidence
        """
        if not sub_questions:
            return SynthesisResult(
                verdict="No evidence gathered",
                verdict_summary="No sub-questions were investigated.",
                status=EvidenceStatus.INCONCLUSIVE,
                confidence_level=ConfidenceLevel.LOW,
                confidence_score=0.0,
                supporting_evidence=[],
                refuting_evidence=[],
                inconclusive_evidence=[],
                reasoning="No evidence was available for synthesis.",
                limitations=["No sub-questions were executed"]
            )
        
        # Categorize evidence
        supporting = []
        refuting = []
        inconclusive = []
        partial = []
        
        # Track sources for evidence threshold enforcement
        all_sources = []
        
        for sq in sub_questions:
            status = sq.get('status', 'inconclusive')
            sources = sq.get('sources', [])
            
            # Collect all valid sources (with URLs or titles)
            for src in sources:
                if isinstance(src, dict) and (src.get('url') or src.get('title')):
                    all_sources.append(src)
            
            evidence_entry = {
                'id': sq.get('id', 'unknown'),
                'question': sq.get('question', ''),
                'findings': sq.get('findings', ''),
                'status': status,
                'sources': sources
            }
            
            if status == 'supported':
                supporting.append(evidence_entry)
            elif status == 'refuted':
                refuting.append(evidence_entry)
            elif status == 'partial':
                partial.append(evidence_entry)
            else:
                inconclusive.append(evidence_entry)
        
        # ENFORCE SOURCE-BASED EVIDENCE THRESHOLD
        # Transitioning from INCONCLUSIVE requires at least one valid cited source
        has_valid_sources = len(all_sources) > 0
        unique_source_urls = set(src.get('url', '') for src in all_sources if src.get('url'))
        unique_source_count = len([s for s in unique_source_urls if s])
        
        # Calculate weighted scores
        total_questions = len(sub_questions)
        
        # Count weighted evidence
        supporting_weight = len(supporting)
        refuting_weight = len(refuting)
        partial_weight = len(partial) * 0.5
        
        # SOURCE-BASED EVIDENCE THRESHOLD ENFORCEMENT
        # Transitioning from INCONCLUSIVE requires at least one valid cited source
        has_valid_sources = unique_source_count > 0
        
        # Determine status with source threshold enforcement
        if supporting_weight >= total_questions * 0.6:
            # Check source threshold - need at least 1 source to be SUPPORTED
            if has_valid_sources:
                status = EvidenceStatus.SUPPORTED
                verdict = "SUPPORTED"
                verdict_summary = (
                    f"The hypothesis is SUPPORTED by the evidence. "
                    f"{len(supporting)} out of {total_questions} sub-questions show "
                    f"supporting evidence, with {len(partial)} showing partial support. "
                    f"Evidence is backed by {unique_source_count} unique external source(s)."
                )
                confidence_base = 0.7 + (supporting_weight / total_questions) * 0.3
            else:
                # Has supporting evidence but no sources - downgrade to PARTIAL
                status = EvidenceStatus.PARTIAL
                verdict = "PARTIALLY SUPPORTED"
                verdict_summary = (
                    f"The hypothesis shows PARTIAL SUPPORT. While {len(supporting)} sub-questions "
                    f"indicate supporting evidence, no external sources were cited to validate "
                    f"these findings. Additional verification is needed."
                )
                confidence_base = 0.4
            
        elif refuting_weight >= total_questions * 0.6:
            # Check source threshold - need at least 1 source to be REFUTED
            if has_valid_sources:
                status = EvidenceStatus.REFUTED
                verdict = "REFUTED"
                verdict_summary = (
                    f"The hypothesis is REFUTED by the evidence. "
                    f"{len(refuting)} out of {total_questions} sub-questions show "
                    f"refuting evidence, backed by {unique_source_count} unique external source(s)."
                )
                confidence_base = 0.7 + (refuting_weight / total_questions) * 0.3
            else:
                # Has refuting evidence but no sources - downgrade to PARTIAL
                status = EvidenceStatus.PARTIAL
                verdict = "PARTIALLY REFUTED"
                verdict_summary = (
                    f"The hypothesis shows PARTIAL REFUTATION. While {len(refuting)} sub-questions "
                    f"indicate refuting evidence, no external sources were cited to validate "
                    f"these findings. Additional verification is needed."
                )
                confidence_base = 0.4
            
        elif supporting_weight > refuting_weight and supporting_weight > 0:
            # Check source threshold for PARTIAL
            if has_valid_sources:
                status = EvidenceStatus.PARTIAL
                verdict = "PARTIALLY SUPPORTED"
                verdict_summary = (
                    f"The hypothesis is PARTIALLY SUPPORTED. Evidence is mixed with "
                    f"{len(supporting)} supporting, {len(refuting)} refuting, and "
                    f"{len(partial)} partial findings. "
                    f"Backed by {unique_source_count} unique external source(s)."
                )
                confidence_base = 0.5 + (supporting_weight / total_questions) * 0.3
            else:
                # No sources - remain INCONCLUSIVE
                status = EvidenceStatus.INCONCLUSIVE
                verdict = "INCONCLUSIVE"
                verdict_summary = (
                    f"The evidence is INCONCLUSIVE. While {len(supporting)} sub-questions "
                    f"show some supporting evidence, no external sources were cited to "
                    f"validate these findings. Additional research with proper citations is needed."
                )
                confidence_base = 0.3
            
        elif refuting_weight > supporting_weight and refuting_weight > 0:
            # Check source threshold for PARTIAL
            if has_valid_sources:
                status = EvidenceStatus.PARTIAL
                verdict = "PARTIALLY REFUTED"
                verdict_summary = (
                    f"The hypothesis is PARTIALLY REFUTED. Evidence leans against with "
                    f"{len(refuting)} refuting, {len(supporting)} supporting, and "
                    f"{len(partial)} partial findings. "
                    f"Backed by {unique_source_count} unique external source(s)."
                )
                confidence_base = 0.5 + (refuting_weight / total_questions) * 0.3
            else:
                # No sources - remain INCONCLUSIVE
                status = EvidenceStatus.INCONCLUSIVE
                verdict = "INCONCLUSIVE"
                verdict_summary = (
                    f"The evidence is INCONCLUSIVE. While {len(refuting)} sub-questions "
                    f"show some refuting evidence, no external sources were cited to "
                    f"validate these findings. Additional research with proper citations is needed."
                )
                confidence_base = 0.3
            
        else:
            status = EvidenceStatus.INCONCLUSIVE
            verdict = "INCONCLUSIVE"
            verdict_summary = (
                f"The evidence is INCONCLUSIVE. {len(inconclusive)} out of "
                f"{total_questions} sub-questions lack sufficient evidence. "
                f"No external sources were found to support any claims."
            )
            confidence_base = 0.3
        
        # Penalise confidence when real external sources are scarce
        # A high ratio of simulated/computed sources (no real URLs) signals lower certainty
        real_url_sources = [s for s in all_sources if s.get("url", "").startswith("http")]
        simulated_source_count = len(all_sources) - len(real_url_sources)
        if simulated_source_count >= len(all_sources) and len(all_sources) > 0:
            confidence_base *= 0.75  # All sources are simulated — downgrade substantially
        elif unique_source_count < 2:
            confidence_base *= 0.85  # Very few real sources — slight downgrade

        # Calculate final confidence
        confidence_score = min(confidence_base, 1.0)
        
        # Determine confidence level
        if confidence_score >= 0.8:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
        
        # Build narrative reasoning grouped by method
        web_sqs    = [sq for sq in sub_questions if sq.get('method') == 'web_search']
        code_sqs   = [sq for sq in sub_questions if sq.get('method') == 'code_execution']
        logic_sqs  = [sq for sq in sub_questions if sq.get('method') == 'logical_reasoning']

        reasoning_parts = [
            f"**Overview:** {total_questions} sub-questions were investigated across "
            f"{len([m for m in [web_sqs, code_sqs, logic_sqs] if m])} research methods "
            f"(web search, quantitative analysis, logical reasoning).",
            "",
        ]

        if web_sqs:
            web_supported = sum(1 for sq in web_sqs if sq.get('status') == 'supported')
            web_partial   = sum(1 for sq in web_sqs if sq.get('status') == 'partial')
            reasoning_parts.append(
                f"**Web Search ({len(web_sqs)} queries):** "
                f"{web_supported} returned supporting evidence, {web_partial} partial. "
                + (web_sqs[0].get('findings', '')[:220].rstrip() + "…" if web_sqs[0].get('findings') else "")
            )

        if code_sqs:
            code_status = code_sqs[0].get('status', 'partial')
            reasoning_parts.append(
                f"**Quantitative Analysis ({len(code_sqs)} task(s)):** Status: {code_status.upper()}. "
                + (code_sqs[0].get('findings', '')[:180].rstrip() + "…" if code_sqs[0].get('findings') else "")
                + " Note: analyses were run on simulated data and are illustrative only."
            )

        if logic_sqs:
            logic_partial = sum(1 for sq in logic_sqs if sq.get('status') in ('partial', 'supported'))
            reasoning_parts.append(
                f"**Logical Reasoning ({len(logic_sqs)} analyses):** "
                f"{logic_partial} analyses produced substantive logical assessments. "
                + (logic_sqs[0].get('findings', '')[:200].rstrip() + "…" if logic_sqs[0].get('findings') else "")
            )

        reasoning_parts += [
            "",
            f"**Evidence tally:** {len(supporting)} supporting · {len(refuting)} refuting · "
            f"{len(partial)} partial · {len(inconclusive)} inconclusive.",
        ]
        if supporting:
            reasoning_parts.append(f"Strongest supporting evidence: {supporting[0]['id']} — {supporting[0].get('question','')[:80]}…")
        if refuting:
            reasoning_parts.append(f"Key refuting evidence: {refuting[0]['id']} — {refuting[0].get('question','')[:80]}…")

        reasoning = "\n".join(reasoning_parts)

        # Build specific limitations (4-5 bullets)
        limitations = []
        if simulated_source_count > 0:
            limitations.append(
                "Some sources are simulated/illustrative — findings should be verified against real primary literature."
            )
        if len(partial) > 0:
            limitations.append(
                "Partial evidence across multiple sub-questions indicates the relationship is context-dependent "
                "rather than universal."
            )
        if len(web_sqs) > 1:
            limitations.append(
                "Multiple web-search sub-questions drew from the same domain source pool, "
                "which may understate source diversity."
            )
        if code_sqs:
            limitations.append(
                "Quantitative analyses used randomly generated data as proxies; real empirical datasets "
                "are required for statistically valid conclusions."
            )
        if len(supporting) > 0 and len(refuting) == 0:
            limitations.append(
                "No refuting evidence was surfaced — this reflects the simulated search design, not necessarily "
                "an absence of counter-evidence in the real literature."
            )
        if not limitations:
            limitations.append("Standard limitations of secondary research and simulated evidence synthesis apply.")
        
        return SynthesisResult(
            verdict=verdict,
            verdict_summary=verdict_summary,
            status=status,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            supporting_evidence=supporting,
            refuting_evidence=refuting,
            inconclusive_evidence=inconclusive + partial,
            reasoning=reasoning,
            limitations=limitations
        )


# Convenience function
def synthesize_evidence(sub_questions: List[Dict]) -> Dict:
    """
    Synthesize evidence from sub-questions.
    
    Args:
        sub_questions: List of sub-question dictionaries with findings
        
    Returns:
        Synthesis result dictionary
    """
    engine = SynthesisEngine()
    result = engine.synthesize(sub_questions)
    return result.to_dict()


if __name__ == "__main__":
    # Test the synthesis engine
    print("Testing Synthesis Engine")
    print("=" * 70)
    
    # Test case 1: Strong support
    test_questions_1 = [
        {"id": "SQ01", "question": "Q1", "findings": "Evidence supports", "status": "supported", "sources": []},
        {"id": "SQ02", "question": "Q2", "findings": "Evidence supports", "status": "supported", "sources": []},
        {"id": "SQ03", "question": "Q3", "findings": "Evidence supports", "status": "supported", "sources": []},
        {"id": "SQ04", "question": "Q4", "findings": "Partial evidence", "status": "partial", "sources": []},
    ]
    
    result_1 = synthesize_evidence(test_questions_1)
    print(f"\nTest 1 - Strong Support:")
    print(f"  Verdict: {result_1['verdict']}")
    print(f"  Confidence: {result_1['confidence_level']} ({result_1['confidence_score']:.2f})")
    
    # Test case 2: Mixed evidence
    test_questions_2 = [
        {"id": "SQ01", "question": "Q1", "findings": "Evidence supports", "status": "supported", "sources": []},
        {"id": "SQ02", "question": "Q2", "findings": "Evidence refutes", "status": "refuted", "sources": []},
        {"id": "SQ03", "question": "Q3", "findings": "Partial evidence", "status": "partial", "sources": []},
    ]
    
    result_2 = synthesize_evidence(test_questions_2)
    print(f"\nTest 2 - Mixed Evidence:")
    print(f"  Verdict: {result_2['verdict']}")
    print(f"  Confidence: {result_2['confidence_level']} ({result_2['confidence_score']:.2f})")