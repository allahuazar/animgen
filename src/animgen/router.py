import json
import re

from .groq_clients import get_router_client

SYSTEM_PROMPT = """You classify the user request and plan a Manim docs search.
Return JSON only. No markdown. No explanation.

Schema:
{
  "intent": "manim_animation" | "unsupported",
  "topic": "",
  "search_queries": [],
  "scene_plan": [],
  "reason": ""
}

Rules:
- Classify as manim_animation if the user asks for animation, educational visual explanation, graph animation, geometry animation, science/math concept animation, or Manim code.
- Generate 5-12 search queries.
- Search queries should prefer Manim class/function names:
  Text, MathTex, VGroup, Arrow, Line, Circle, Rectangle, Square, Dot, NumberLine, Axes, FadeIn, FadeOut, Write, Create, Transform, ReplacementTransform, Scene, self.play.
- Include a short clear scene_plan.
- If unsupported, still include reason.

Example:
{
  "intent": "manim_animation",
  "topic": "solving x + 5 = 12",
  "search_queries": ["Text", "Transform", "NumberLine", "Dot", "VGroup", "Write", "FadeIn"],
  "scene_plan": [
    "Show the equation x + 5 = 12",
    "Show subtracting 5 from both sides",
    "Transform it into x = 7",
    "Show number line and mark 7"
  ],
  "reason": "The user wants an educational math animation."
}"""


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start == -1 or brace_end <= brace_start:
        return None
    candidate = text[brace_start : brace_end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    result = {}
    for key in ("intent", "topic", "search_queries", "scene_plan", "reason"):
        m = re.search(rf'"{key}"\s*:\s*("(?:[^"\\]|\\.)*"|\[.*?\])', candidate, re.DOTALL)
        if m:
            val = m.group(1)
            try:
                result[key] = json.loads(val)
            except json.JSONDecodeError:
                result[key] = val.strip('"')
    return result if result else None


def route_prompt(prompt: str) -> dict:
    client, model = get_router_client()
    try:
        completion = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
    except Exception:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
    raw = completion.choices[0].message.content or ""
    data = _extract_json(raw) or {}
    return {
        "intent": data.get("intent", "unsupported"),
        "topic": data.get("topic", prompt),
        "search_queries": data.get("search_queries", [prompt]),
        "scene_plan": data.get("scene_plan", []),
        "reason": data.get("reason", ""),
    }
