import json
from typing import Optional

from openai import OpenAI
from anthropic import Anthropic
from google import genai

from src.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, LLM_PROVIDER


class LLMClient:
    def __init__(self):
        self.openai_client: Optional[OpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self.gemini_client: Optional[genai.Client] = None

        if OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        if ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        if GOOGLE_API_KEY:
            self.gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

        self._provider = LLM_PROVIDER

    def _pick_provider(self, prefer_claude: bool) -> str:
        if self._provider == "openai" and self.openai_client:
            return "openai"
        if self._provider == "anthropic" and self.anthropic_client:
            return "anthropic"
        if self._provider == "gemini" and self.gemini_client:
            return "gemini"
        if prefer_claude and self.anthropic_client:
            return "anthropic"
        if self.gemini_client:
            return "gemini"
        if self.openai_client:
            return "openai"
        if self.anthropic_client:
            return "anthropic"
        return "none"

    def analyze_match(self, resume_text: str, jd_text: str) -> dict:
        prompt = (
            "You are an ATS resume analyst. Compare the following resume and job description. "
            "Return a JSON object with:\n"
            "- 'score': a float from 0.0 to 1.0 indicating how well the resume matches the JD\n"
            "- 'matching_skills': list of skills from the resume that match the JD\n"
            "- 'missing_skills': list of key skills in the JD missing from the resume\n"
            "- 'reasoning': 2-3 sentence explanation of the score\n\n"
            f"--- RESUME ---\n{resume_text}\n\n--- JOB DESCRIPTION ---\n{jd_text}"
        )
        return self._call_llm(prompt, prefer_claude=True)

    def tailor_resume(self, resume_text: str, jd_text: str, analysis: dict) -> str:
        missing = ", ".join(analysis.get("missing_skills", []))
        matching = ", ".join(analysis.get("matching_skills", []))
        prompt = (
            "You are an ATS resume writer. Rewrite the resume below to better match the job description. "
            f"The resume already matches on: {matching}. "
            f"Prioritize adding these missing keywords naturally: {missing}. "
            "Keep the same overall structure (summary, experience, education, skills). "
            "Output the rewritten resume in plain text markdown format.\n\n"
            f"--- RESUME ---\n{resume_text}\n\n--- JOB DESCRIPTION ---\n{jd_text}"
        )
        return self._call_llm_text(prompt, prefer_claude=False)

    def _call_llm(self, prompt: str, prefer_claude: bool = True) -> dict:
        provider = self._pick_provider(prefer_claude)
        if provider == "anthropic":
            return self._call_claude(prompt)
        elif provider == "gemini":
            return self._call_gemini_json(prompt)
        elif provider == "openai":
            return self._call_openai(prompt)
        return {"score": 0.5, "matching_skills": [], "missing_skills": [], "reasoning": "No LLM configured"}

    def _call_llm_text(self, prompt: str, prefer_claude: bool = True) -> str:
        provider = self._pick_provider(prefer_claude)
        if provider == "anthropic":
            return self._call_claude_raw(prompt)
        elif provider == "gemini":
            return self._call_gemini_raw(prompt)
        elif provider == "openai":
            return self._call_openai_raw(prompt)
        return ""

    def _call_openai(self, prompt: str) -> dict:
        resp = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(resp.choices[0].message.content)

    def _call_openai_raw(self, prompt: str) -> str:
        resp = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content

    def _call_claude(self, prompt: str) -> dict:
        resp = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned.strip())

    def _call_claude_raw(self, prompt: str) -> str:
        resp = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    def _call_gemini_json(self, prompt: str) -> dict:
        resp = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "matching_skills": {"type": "array", "items": {"type": "string"}},
                        "missing_skills": {"type": "array", "items": {"type": "string"}},
                        "reasoning": {"type": "string"},
                    },
                    "required": ["score", "matching_skills", "missing_skills", "reasoning"],
                },
            },
        )
        return json.loads(resp.text)

    def _call_gemini_raw(self, prompt: str) -> str:
        resp = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.3},
        )
        return resp.text