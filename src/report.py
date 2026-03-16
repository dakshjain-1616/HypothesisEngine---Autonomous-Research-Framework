"""
Reporting Module
Generates 'research_brief.md' with hypothesis, plan, findings, verdict, and sources.
"""

import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class ReportGenerator:
    """Generates the final research brief markdown report."""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, hypothesis: str, domain: str, core_claims: List[str],
                 variables: Dict[str, str], sub_questions: List[Dict],
                 verdict: str, verdict_summary: str, status: str,
                 confidence_level: str, confidence_score: float,
                 reasoning: str, limitations: List[str],
                 output_filename: str = "research_brief.md") -> str:
        """
        Generate the research brief markdown report.
        
        Returns:
            Path to the generated report
        """
        output_path = os.path.join(self.output_dir, output_filename)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Collect all sources
        all_sources = []
        for sq in sub_questions:
            sources = sq.get('sources', [])
            all_sources.extend(sources)
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_ups(status, domain, sub_questions)
        
        # Build the report
        report = self._build_report(
            timestamp=timestamp,
            hypothesis=hypothesis,
            domain=domain,
            core_claims=core_claims,
            variables=variables,
            sub_questions=sub_questions,
            verdict=verdict,
            verdict_summary=verdict_summary,
            status=status,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            reasoning=reasoning,
            limitations=limitations,
            follow_up_questions=follow_up_questions,
            all_sources=all_sources
        )
        
        # Write the report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path
    
    def _build_report(self, **kwargs) -> str:
        """Build the markdown report content."""
        sections = []
        
        # Header
        sections.append(self._build_header(kwargs['timestamp']))
        
        # Original Hypothesis
        sections.append(self._build_hypothesis_section(kwargs['hypothesis']))

        # Executive Summary (new)
        sections.append(self._build_executive_summary(
            kwargs['hypothesis'],
            kwargs['status'],
            kwargs['verdict_summary'],
            kwargs['confidence_level'],
            kwargs['confidence_score'],
            kwargs['domain'],
            kwargs['sub_questions'],
            kwargs['limitations']
        ))

        # Research Plan
        sections.append(self._build_research_plan_section(
            kwargs['domain'],
            kwargs['core_claims'],
            kwargs['variables'],
            kwargs['sub_questions']
        ))
        
        # Key Findings
        sections.append(self._build_findings_section(kwargs['sub_questions']))
        
        # Synthesis & Verdict
        sections.append(self._build_verdict_section(
            kwargs['verdict'],
            kwargs['verdict_summary'],
            kwargs['status'],
            kwargs['confidence_level'],
            kwargs['confidence_score'],
            kwargs['reasoning'],
            kwargs['limitations']
        ))
        
        # Follow-up Questions
        sections.append(self._build_followups_section(kwargs['follow_up_questions']))
        
        # Sources
        sections.append(self._build_sources_section(kwargs['all_sources']))
        
        # Footer
        sections.append(self._build_footer())
        
        return "\n".join(sections)
    
    def _build_header(self, timestamp: str) -> str:
        return f"""# Research Brief: Hypothesis Investigation

**Generated:** {timestamp}  
**HypothesisEngine v1.0**

---

"""
    
    def _build_hypothesis_section(self, hypothesis: str) -> str:
        return f"""## Original Hypothesis

> {hypothesis}

---

"""
    
    def _build_executive_summary(self, hypothesis: str, status: str, verdict_summary: str,
                                  confidence_level: str, confidence_score: float,
                                  domain: str, sub_questions: List[Dict],
                                  limitations: List[str]) -> str:
        """Build an executive summary at the top of the report."""
        status_label = {
            'supported': 'SUPPORTED',
            'refuted': 'REFUTED',
            'partial': 'PARTIALLY SUPPORTED',
            'inconclusive': 'INCONCLUSIVE',
        }.get(status.lower(), status.upper())

        n_supported  = sum(1 for sq in sub_questions if sq.get('status') == 'supported')
        n_partial    = sum(1 for sq in sub_questions if sq.get('status') == 'partial')
        n_refuted    = sum(1 for sq in sub_questions if sq.get('status') == 'refuted')
        n_total      = len(sub_questions)
        methods_used = sorted(set(sq.get('method', '').replace('_', ' ') for sq in sub_questions))

        # Pull the first real web-search finding snippet as key evidence
        key_evidence = ""
        for sq in sub_questions:
            if sq.get('method') == 'web_search' and sq.get('findings'):
                raw = sq['findings']
                key_evidence = raw[:250].rsplit(' ', 1)[0] + "…"
                break

        first_limitation = limitations[0] if limitations else "Standard research limitations apply."

        return f"""## Executive Summary

| | |
|---|---|
| **Hypothesis** | {hypothesis} |
| **Domain** | {domain.capitalize()} |
| **Verdict** | {status_label} |
| **Confidence** | {confidence_level} ({confidence_score:.2f} / 1.00) |
| **Methods used** | {', '.join(m.title() for m in methods_used)} |
| **Sub-questions** | {n_total} total — {n_supported} supporting, {n_partial} partial, {n_refuted} refuting |

**Key finding:** {key_evidence}

**Primary limitation:** {first_limitation}

---

"""

    def _build_research_plan_section(self, domain: str, core_claims: List[str],
                                     variables: Dict[str, str],
                                     sub_questions: List[Dict]) -> str:
        section = f"""## Research Plan

### Domain Analysis
- **Domain:** {domain.capitalize()}
- **Core Claims:**
"""
        for i, claim in enumerate(core_claims, 1):
            section += f"  {i}. {claim}\n"
        
        if variables:
            section += "\n### Key Variables\n"
            for var, var_type in variables.items():
                section += f"- **{var}:** {var_type}\n"
        
        section += f"\n### Sub-Questions ({len(sub_questions)} total)\n\n"
        
        for sq in sub_questions:
            section += f"#### {sq.get('id', 'SQ00')}: {sq.get('question', '')}\n"
            section += f"- **Method:** {sq.get('method', 'unknown').replace('_', ' ').title()}\n"
            section += f"- **Rationale:** {sq.get('rationale', '')}\n\n"
        
        section += "---\n\n"
        return section
    
    def _build_findings_section(self, sub_questions: List[Dict]) -> str:
        section = "## Detailed Findings\n\n"

        METHOD_BADGE = {
            'web_search':        '🔍 Web Search',
            'code_execution':    '📊 Quantitative Analysis',
            'logical_reasoning': '🧠 Logical Reasoning',
        }
        STATUS_LABEL = {
            'supported':    '✅ SUPPORTED',
            'refuted':      '❌ REFUTED',
            'partial':      '⚠️  PARTIALLY SUPPORTED',
            'inconclusive': '❓ INCONCLUSIVE',
        }

        for sq in sub_questions:
            sq_id    = sq.get('id', 'SQ00')
            question = sq.get('question', '')
            findings = sq.get('findings', 'No findings recorded')
            status   = sq.get('status', 'inconclusive')
            method   = sq.get('method', '')
            sources  = sq.get('sources', [])
            rationale = sq.get('rationale', '')

            badge  = METHOD_BADGE.get(method, method.replace('_', ' ').title())
            slabel = STATUS_LABEL.get(status, status.upper())

            section += f"### {sq_id}: {question}\n\n"
            section += f"**Method:** {badge}  \n"
            section += f"**Status:** {slabel}  \n"
            section += f"**Rationale:** {rationale}\n\n"
            section += f"**Analysis:**\n\n{findings}\n\n"

            if sources:
                real_sources = [s for s in sources if s.get('url')]
                if real_sources:
                    section += "**Supporting sources:**\n"
                    for src in real_sources[:3]:
                        section += f"- [{src.get('title','Source')}]({src.get('url','')})\n"
                    section += "\n"

            section += "---\n\n"

        return section
    
    def _build_verdict_section(self, verdict: str, verdict_summary: str,
                                status: str, confidence_level: str,
                                confidence_score: float, reasoning: str,
                                limitations: List[str]) -> str:
        # Confidence bar (ASCII)
        filled = int(confidence_score * 20)
        bar = '█' * filled + '░' * (20 - filled)

        return f"""## Synthesis & Verdict

### Final Verdict: {verdict}

{verdict_summary}

### Confidence Assessment

| Metric | Value |
|--------|-------|
| **Verdict** | {verdict} |
| **Confidence Level** | {confidence_level} |
| **Confidence Score** | {confidence_score:.2f} / 1.00 |
| **Confidence Bar** | `{bar}` |

The confidence score reflects source reliability, consistency across research methods, and the ratio of supporting to inconclusive findings. Scores above 0.80 indicate High confidence; 0.50–0.79 Medium; below 0.50 Low.

### Detailed Reasoning

{reasoning}

### Limitations

""" + "\n".join(f"- {lim}" for lim in limitations) + "\n\n---\n\n"
    
    def _build_followups_section(self, follow_up_questions: List[str]) -> str:
        section = """## Follow-up Questions

Based on the investigation, the following questions warrant further exploration:

"""
        for i, q in enumerate(follow_up_questions, 1):
            section += f"{i}. {q}\n"
        
        section += "\n---\n\n"
        return section
    
    def _build_sources_section(self, all_sources: List[Dict]) -> str:
        section = """## Sources

"""
        if all_sources:
            # Deduplicate sources by URL
            seen_urls = set()
            unique_sources = []
            for src in all_sources:
                url = src.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_sources.append(src)
                elif not url:
                    unique_sources.append(src)
            
            for i, src in enumerate(unique_sources, 1):
                title = src.get('title', 'Unknown Source')
                url = src.get('url', '')
                snippet = src.get('snippet', '')
                
                if url:
                    section += f"{i}. **[{title}]({url})**\n"
                else:
                    section += f"{i}. **{title}**\n"
                
                if snippet:
                    section += f"   > {snippet}\n"
                section += "\n"
        else:
            section += "*No external sources were cited in this investigation.*\n"
        
        return section
    
    def _build_footer(self) -> str:
        return """
---

*Report generated by **HypothesisEngine** — Autonomous Research Assistant*
*Built autonomously by [NEO - Your Fully Autonomous AI Agent](https://heyneo.so)*
*Research methodology: Structured evidence synthesis across web search, quantitative analysis, and logical reasoning*
"""
    
    def _generate_follow_ups(self, status: str, domain: str, 
                              sub_questions: List[Dict]) -> List[str]:
        """Generate follow-up questions based on findings."""
        follow_ups = []
        
        # Based on status
        if status == 'inconclusive':
            follow_ups.append("What additional data sources could provide more definitive evidence?")
            follow_ups.append("Are there confounding variables that need to be controlled for?")
        
        if status == 'partial':
            follow_ups.append("Under what specific conditions does the hypothesis hold true?")
            follow_ups.append("What are the boundary conditions or limitations of this relationship?")
        
        # Based on domain
        domain_specific = {
            'health': "What are the potential clinical implications of these findings?",
            'economics': "How might policy interventions affect this relationship?",
            'technology': "What are the implementation challenges for practical applications?",
            'environment': "What mitigation strategies are most effective?",
            'social': "What cultural factors might moderate these effects?",
            'political': "What are the implications for governance and policy?",
            'education': "How can these findings inform teaching practices?",
            'psychology': "What are the therapeutic implications?"
        }
        
        if domain in domain_specific:
            follow_ups.append(domain_specific[domain])
        
        # General follow-ups
        follow_ups.extend([
            "How does this compare to alternative explanations or competing hypotheses?",
            "What longitudinal or causal evidence would strengthen these conclusions?"
        ])
        
        return follow_ups[:5]


# Convenience function
def generate_report(hypothesis: str, domain: str, core_claims: List[str],
                   variables: Dict[str, str], sub_questions: List[Dict],
                   synthesis_result: Dict, output_path: str = None) -> str:
    """
    Generate a research brief report.
    
    Args:
        hypothesis: Original hypothesis
        domain: Research domain
        core_claims: List of core claims
        variables: Dictionary of variables
        sub_questions: List of sub-question dictionaries
        synthesis_result: Synthesis result dictionary
        output_path: Optional output path
        
    Returns:
        Path to generated report
    """
    generator = ReportGenerator()
    
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "research_brief.md")
    
    return generator.generate(
        hypothesis=hypothesis,
        domain=domain,
        core_claims=core_claims,
        variables=variables,
        sub_questions=sub_questions,
        verdict=synthesis_result.get('verdict', 'UNKNOWN'),
        verdict_summary=synthesis_result.get('verdict_summary', ''),
        status=synthesis_result.get('status', 'inconclusive'),
        confidence_level=synthesis_result.get('confidence_level', 'Low'),
        confidence_score=synthesis_result.get('confidence_score', 0.0),
        reasoning=synthesis_result.get('reasoning', ''),
        limitations=synthesis_result.get('limitations', []),
        output_path=output_path
    )


if __name__ == "__main__":
    # Test report generation
    print("Testing Report Generator")
    print("=" * 70)
    
    test_data = {
        "hypothesis": "Regular exercise improves cognitive function in older adults",
        "domain": "health",
        "core_claims": ["Regular exercise improves cognitive function"],
        "variables": {"exercise": "trend", "cognitive_function": "outcome"},
        "sub_questions": [
            {
                "id": "SQ01",
                "question": "What is the current scientific consensus on exercise and cognition?",
                "method": "web_search",
                "rationale": "To gather empirical evidence",
                "findings": "Multiple studies show positive correlation",
                "status": "supported",
                "sources": [{"title": "Study 1", "url": "http://example.com/1"}]
            },
            {
                "id": "SQ02",
                "question": "What are the logical implications?",
                "method": "logical_reasoning",
                "rationale": "To analyze consistency",
                "findings": "Logical framework supports the claim",
                "status": "supported",
                "sources": []
            }
        ],
        "synthesis": {
            "verdict": "SUPPORTED",
            "verdict_summary": "The hypothesis is supported by evidence.",
            "status": "supported",
            "confidence_level": "High",
            "confidence_score": 0.85,
            "reasoning": "Analysis shows consistent support across methods.",
            "limitations": ["Limited sample size in some studies"]
        }
    }
    
    output_path = generate_report(
        test_data["hypothesis"],
        test_data["domain"],
        test_data["core_claims"],
        test_data["variables"],
        test_data["sub_questions"],
        test_data["synthesis"],
        output_filename="test_research_brief.md"
    )
    
    print(f"\nReport generated: {output_path}")
    
    # Show first 50 lines
    with open(output_path, 'r') as f:
        lines = f.readlines()[:50]
        print("\nFirst 50 lines of report:")
        print("-" * 70)
        for line in lines:
            print(line.rstrip())