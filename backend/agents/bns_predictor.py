"""Agent 1: BNS Section Predictor

Analyzes crime descriptions and predicts applicable BNS sections using:
1. Vector search for candidate sections
2. LLM analysis for final selection
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_MODEL, OPENAI_TEMPERATURE
from tools.vector_search import BNSVectorSearch


class BNSPredictorAgent:
    """Predicts applicable BNS sections for crime descriptions"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE
        )
        self.vector_search = BNSVectorSearch()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Indian police legal advisor and criminal law analyst specializing in BNS (Bharatiya Nyaya Sanhita).

Your task: Deeply analyze crime descriptions to identify ALL applicable BNS sections, going beyond surface-level matches.

═══════════════════════════════════════════════════════════════════════════

STEP 1: EXTRACT LEGAL FACTS
Break down the crime into specific legal elements:
- WHO: Accused person(s), victim(s), witnesses
- WHAT: Specific acts performed (physical actions)
- WHERE: Location, property type, jurisdiction
- WHEN: Timing, duration, sequence of events
- WHY: Intent, motive, mental state (mens rea)
- HOW: Method, tools, planning involved

STEP 2: IDENTIFY ALL POSSIBLE OFFENSES
Look for MULTIPLE layers of criminality:

A. PRIMARY OFFENSE (Core criminal act)
   - What law was directly violated?
   - Examples: theft, assault, murder, fraud, trespass

B. PROCEDURAL/REGULATORY VIOLATIONS
   - Failure to comply with government orders
   - Disobedience to public servant directions
   - Violation of statutory requirements
   - Administrative non-compliance

C. AGGRAVATING CIRCUMSTANCES
   - Use of weapons, violence
   - Targeting vulnerable persons
   - Breach of trust, position abuse
   - Planning, premeditation

D. CONSEQUENTIAL OFFENSES
   - What happened as a result?
   - Secondary harms, risks created

═══════════════════════════════════════════════════════════════════════════

CRITICAL ANALYSIS RULES:

1. READ BETWEEN THE LINES
   - "Police verification not done" → Disobedience to public servant order (223)
   - "Living without documentation" → Possible regulatory violation
   - "Landlord failed to inform" → Omission to give information (218)

2. CONSIDER OMISSIONS AS CRIMES
   - Not just what was DONE, but what was NOT DONE
   - Failure to report, failure to verify, failure to comply

3. THINK ABOUT DUTY & RESPONSIBILITY
   - What legal duties existed?
   - Who had responsibility to act?
   - Was there a public servant involved?

4. ANALYZE ADMINISTRATIVE CONTEXT
   - Was there a government regulation/order violated?
   - Did someone ignore a lawful directive?
   - Was required documentation missing?

═══════════════════════════════════════════════════════════════════════════

CONFIDENCE SCORING:

- 0.90-0.95: Crystal clear, all elements present
- 0.80-0.89: Strong evidence, highly probable
- 0.70-0.79: Good match, likely applicable
- 0.60-0.69: Possible, needs investigation
- Below 0.60: Weak connection, mention only if relevant

═══════════════════════════════════════════════════════════════════════════

SPECIAL INSTRUCTIONS FOR ADMINISTRATIVE CASES:

If description mentions:
- "Verification not done" → Check Section 223 (Disobedience to order)
- "Failed to inform police" → Check Section 218 (Public servant concealing design)
- "No permission taken" → Check regulatory compliance sections
- "Landlord negligence" → Check duty-based offenses

═══════════════════════════════════════════════════════════════════════════

OUTPUT FORMAT (JSON):

[
  {{
    "section_number": "223",
    "confidence": 0.85,
    "reasoning": "Disobedience to public servant order - Landlord failed to conduct mandatory police verification for tenant as required by law"
  }},
  {{
    "section_number": "303",
    "confidence": 0.90,
    "reasoning": "Primary offense: Theft - dishonest taking of movable property"
  }}
]

Return 3-7 sections. Think deeply. Consider ALL angles."""),
            ("human", """Crime Description:
{crime_description}

Candidate Sections (from vector search):
{candidates}

Perform DEEP legal analysis. Consider:
1. What acts were committed?
2. What duties were violated?
3. What orders/regulations were disobeyed?
4. What information was concealed or not provided?

Return ALL applicable sections as JSON.""")
        ])

        self.chain = self.prompt | self.llm

    def predict(self, crime_description: str, top_k: int = 50) -> List[Dict]:
        """
        Predict applicable BNS sections.

        Args:
            crime_description: Refined crime description
            top_k: Number of candidate sections to retrieve

        Returns:
            List of predictions with confidence scores
        """
        # Step 1: Vector search for candidates
        candidates = self.vector_search.search(
            crime_description,
            top_k=top_k,
            similarity_threshold=0.25
        )

        if not candidates:
            return []

        # Format candidates for LLM
        candidates_text = self._format_candidates(candidates)

        # Step 2: LLM analysis
        try:
            response = self.chain.invoke({
                "crime_description": crime_description,
                "candidates": candidates_text
            })

            # Parse JSON response
            import json
            import re

            # Extract JSON from response (handle markdown code blocks)
            content = response.content.strip()

            # Remove markdown code blocks if present
            if '```json' in content:
                content = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL).group(1)
            elif '```' in content:
                content = re.search(r'```\s*(\[.*?\])\s*```', content, re.DOTALL).group(1)

            predictions = json.loads(content)

            # Enrich with full section details
            enriched = []
            for pred in predictions:
                section_details = self.vector_search.get_section_details(
                    pred['section_number']
                )
                if section_details:
                    enriched.append({
                        **pred,
                        'section_title': section_details['title'],
                        'section_text': section_details['full_text'][:200] + '...',
                        'metadata': section_details['metadata']
                    })

            return enriched

        except Exception as e:
            print(f"Error in prediction: {e}")
            print(f"LLM Response: {response.content[:500] if 'response' in locals() else 'No response'}")
            # Fallback: return top vector search results
            return self._fallback_predictions(candidates)

    def _format_candidates(self, candidates: List[Dict]) -> str:
        """Format candidate sections for LLM prompt"""
        formatted = []
        for i, c in enumerate(candidates, 1):
            formatted.append(
                f"{i}. Section {c['section_number']} - "
                f"{c['chunk_text'][:150]}... "
                f"(similarity: {c.get('similarity', 0):.2f})"
            )
        return "\n".join(formatted)

    def _fallback_predictions(self, candidates: List[Dict]) -> List[Dict]:
        """Fallback: Return top candidates with basic confidence"""
        predictions = []
        for c in candidates[:3]:  # Top 3
            predictions.append({
                'section_number': c['section_number'],
                'confidence': c.get('similarity', 0.5),
                'reasoning': 'Based on semantic similarity (fallback mode)'
            })
        return predictions


# Convenience function
def predict_bns_sections(description: str) -> List[Dict]:
    """Quick predict function"""
    agent = BNSPredictorAgent()
    return agent.predict(description)
