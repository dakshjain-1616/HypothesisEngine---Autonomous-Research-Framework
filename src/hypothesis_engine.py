"""
HypothesisEngine - Autonomous Research Assistant
Main orchestrator for hypothesis investigation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from parse import HypothesisParser, parse_hypothesis, ResearchDomain
from plan import ResearchPlanBuilder, ResearchMethod, EvidenceStatus, SubQuestion
from execute import EvidenceGatherer
from synthesize import SynthesisEngine, synthesize_evidence
from report import ReportGenerator, generate_report

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class HypothesisEngine:
    """
    Main orchestrator for hypothesis investigation.
    
    Implements the 5-step workflow:
    1. Parse the question
    2. Build research plan
    3. Execute research
    4. Synthesize findings
    5. Generate report
    """
    
    def __init__(self):
        self.parser = HypothesisParser()
        self.plan_builder = ResearchPlanBuilder()
        self.evidence_gatherer = EvidenceGatherer()
        self.synthesis_engine = SynthesisEngine()
        self.report_generator = ReportGenerator()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def investigate(self, hypothesis: str, output_path: str = None, 
                    num_questions: int = 5) -> str:
        """
        Execute full investigation workflow on a hypothesis.
        
        Args:
            hypothesis: The research question or hypothesis to investigate
            output_path: Optional path for the output report
            num_questions: Number of sub-questions to generate (3-6)
            
        Returns:
            Path to the generated research brief
        """
        self.logger.info("=" * 60)
        self.logger.info("HYPOTHESIS ENGINE - Starting Investigation")
        self.logger.info("=" * 60)
        self.logger.info(f"Hypothesis: {hypothesis}")
        
        # Step 1: Parse the hypothesis
        self.logger.info("\n[Step 1/5] Parsing hypothesis...")
        parsed = self.parser.parse(hypothesis)
        self.logger.info(f"  Domain: {parsed.domain.value}")
        self.logger.info(f"  Core claims: {len(parsed.core_claims)}")
        self.logger.info(f"  Variables: {len(parsed.variables)}")
        
        # Step 2: Build research plan
        self.logger.info("\n[Step 2/5] Building research plan...")
        sub_questions = self.plan_builder.build(parsed, num_questions)
        self.logger.info(f"  Generated {len(sub_questions)} sub-questions")
        
        for sq in sub_questions:
            self.logger.info(f"    {sq.id}: [{sq.method.value}] {sq.question[:50]}...")
        
        # Step 3: Execute research
        self.logger.info("\n[Step 3/5] Executing research...")
        sub_question_dicts = []
        for i, sq in enumerate(sub_questions, 1):
            self.logger.info(f"  [{i}/{len(sub_questions)}] {sq.id}: {sq.method.value}")
            sq_dict = sq.to_dict()
            sq_dict = self.evidence_gatherer.gather(sq_dict)
            sub_question_dicts.append(sq_dict)
        
        # Step 4: Synthesize findings
        self.logger.info("\n[Step 4/5] Synthesizing findings...")
        synthesis_result = self.synthesis_engine.synthesize(sub_question_dicts)
        self.logger.info(f"  Status: {synthesis_result.status.value.upper()}")
        self.logger.info(f"  Confidence: {synthesis_result.confidence_score:.2f}")
        
        # Step 5: Generate report
        self.logger.info("\n[Step 5/5] Generating research brief...")
        output_filename = os.path.basename(output_path) if output_path else "research_brief.md"
        report_path = self.report_generator.generate(
            hypothesis=hypothesis,
            domain=parsed.domain.value,
            core_claims=parsed.core_claims,
            variables=parsed.variables,
            sub_questions=sub_question_dicts,
            verdict=synthesis_result.verdict,
            verdict_summary=synthesis_result.verdict_summary,
            status=synthesis_result.status.value,
            confidence_level=synthesis_result.confidence_level.value,
            confidence_score=synthesis_result.confidence_score,
            reasoning=synthesis_result.reasoning,
            limitations=synthesis_result.limitations,
            output_filename=output_filename
        )
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Investigation Complete!")
        self.logger.info(f"Report saved to: {report_path}")
        self.logger.info("=" * 60)
        
        return report_path


# Convenience function for direct use
def investigate_hypothesis(hypothesis: str, output_path: str = None, 
                           num_questions: int = 5) -> str:
    """
    Convenience function to investigate a hypothesis.
    
    Args:
        hypothesis: The research question or hypothesis
        output_path: Optional path for output report
        num_questions: Number of sub-questions to generate
        
    Returns:
        Path to the generated research brief
    """
    engine = HypothesisEngine()
    return engine.investigate(hypothesis, output_path, num_questions)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HypothesisEngine - Autonomous Research Assistant"
    )
    parser.add_argument(
        "--hypothesis", "-H",
        type=str,
        help="Research question or hypothesis to investigate"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output path for the research brief (default: reports/research_brief.md)"
    )
    parser.add_argument(
        "--questions", "-q",
        type=int,
        default=5,
        help="Number of sub-questions to generate (3-6, default: 5)"
    )
    
    args = parser.parse_args()
    
    # Get hypothesis from CLI argument or interactive prompt
    if args.hypothesis:
        hypothesis = args.hypothesis
    else:
        print("=" * 60)
        print("HYPOTHESIS ENGINE - Interactive Mode")
        print("=" * 60)
        hypothesis = input("\nEnter your research question or hypothesis: ").strip()
        if not hypothesis:
            print("Error: No hypothesis provided. Use --hypothesis or enter interactively.")
            parser.print_help()
            sys.exit(1)
    
    # Run investigation
    report_path = investigate_hypothesis(
        hypothesis=hypothesis,
        output_path=args.output,
        num_questions=args.questions
    )
    print(f"\nReport generated: {report_path}")