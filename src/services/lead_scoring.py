
import json
import google.generativeai as genai
from datetime import date
from dataclasses import dataclass

# @dataclass
# class ScoreResult:
#     lead_id: str
#     score: str # "Cold" | "Warm" | "Hot"
#     reasoning: str
#     confidence: float # 0.0 - 1.0


class LeadScoringService:

    CRITERIA = """
    Hot:  decision-maker contact present, potential value > 50000,
          interaction notes suggest positive engagement, contacted within 7 days.
    Warm: has a contact but no recent interaction, or value is moderate.
    Cold: no decision-maker, no recent contact, or disengaged notes.
    """

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def _build_prompt(self, lead_data: dict) -> str:

        prompt = f"""
        You are a B2B sales analyst. Score this lead as Cold, Warm, or Hot. Scoring criteria: {self.CRITERIA} 
        Lead profile: {json.dumps(lead_data, indent=2)} Respond ONLY with valid JSON, 
        no markdown: {{"score": "Hot|Warm|Cold", "reasoning": "one sentence", "confidence": 0.85}}
                """

        return prompt

    def score_lead(self,  lead_id: str , lead_data: dict) -> dict:
        score_date = date.today()
        date_string = score_date.strftime("%Y-m-%d")


        prompt = self._build_prompt(lead_data)
        response = self.model.generate_content(prompt)
        parsed = json.loads(response.text.strip().removeprefix("```json").removesuffix("```").strip())
        # result = ScoreResult(lead_id=lead_id, score=parsed["score"], reasoning=parsed["reasoning"], confidence=parsed["confidence"])
        result = {"ID" : lead_id , "Score" : parsed["score"] , "Reasoning" : parsed["reasoning"] , "Confidence" : parsed["confidence"] , "Date Scored" : date_string}
        return result

