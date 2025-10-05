"""Agent 0: Crime Description Refiner

Cleans and standardizes crime descriptions before processing.
- Translates Hindi to English
- Expands abbreviations
- Clarifies ambiguous terms
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_MODEL, OPENAI_TEMPERATURE


class CrimeRefinerAgent:
    """Refines and standardizes crime descriptions"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a language translator and text clarifier for Indian police officers.

STRICT RULES:
1. If text is in Hindi/Hinglish/other language → Translate to English
2. If text is already in English → Return it AS-IS without changes
3. DO NOT add legal terminology
4. DO NOT interpret or add words like "unlawfully", "committed", etc.
5. Keep it simple and direct
6. Only expand well-known abbreviations if needed

Examples:
- Hindi: "एक व्यक्ति ने घर में घुसकर सोना चुरा लिया" → "A person entered a house and stole gold jewelry"
- English: "A person entered a house and stole gold jewelry" → "A person entered a house and stole gold jewelry"
- English: "Someone took my phone" → "Someone took my phone"

Output ONLY the translated/clarified description, nothing else."""),
            ("human", "{crime_description}")
        ])

        self.chain = self.prompt | self.llm

    def refine(self, crime_description: str) -> str:
        """
        Refine crime description for processing.

        Args:
            crime_description: Raw crime description (may contain Hindi, slang)

        Returns:
            Refined English description
        """
        try:
            response = self.chain.invoke({"crime_description": crime_description})
            return response.content.strip()
        except Exception as e:
            print(f"Error refining description: {e}")
            # Fallback: return original
            return crime_description


# Convenience function
def refine_crime_description(description: str) -> str:
    """Quick refine function"""
    agent = CrimeRefinerAgent()
    return agent.refine(description)
