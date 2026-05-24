from . import config
from .codegen import generate_code, repair_code
from .docs_search import search_docs
from .router import route_prompt
from .runner import render_scene
from .validator import validate_code


def generate_manim(prompt: str) -> dict:
    router_result = route_prompt(prompt)
    if router_result.get("intent") == "unsupported":
        return {
            "ok": False,
            "router": router_result,
            "error": f"Unsupported request: {router_result.get('reason', 'unknown')}",
        }

    snippets = search_docs(router_result.get("search_queries", [prompt]))
    code = generate_code(prompt, router_result, snippets)
    validation = validate_code(code)

    config.OUTPUT_DIR.mkdir(exist_ok=True)
    config.GENERATED_SCENE_PATH.write_text(code, encoding="utf-8")

    return {
        "ok": True,
        "router": router_result,
        "snippets": snippets,
        "code": code,
        "validation": validation,
        "warnings": validation["warnings"],
    }


def render_manim() -> dict:
    return render_scene()


def generate_and_render(prompt: str) -> dict:
    gen_result = generate_manim(prompt)
    if not gen_result["ok"]:
        return gen_result

    if not gen_result["validation"]["ok"]:
        return {
            "ok": False,
            "error": "Validation blocking errors",
            "router": gen_result.get("router"),
            "code": gen_result.get("code"),
            "validation": gen_result["validation"],
            "warnings": gen_result["validation"]["warnings"],
        }

    render_result = render_scene()
    code = gen_result["code"]
    repaired = False

    if not render_result["ok"]:
        error_text = render_result.get("stderr", "") or render_result.get("error", "")
        repair_snippets = search_docs(["error", "fix", "common_errors"])
        try:
            repaired_code = repair_code(prompt, code, error_text, repair_snippets)
            config.GENERATED_SCENE_PATH.write_text(repaired_code, encoding="utf-8")
            code = repaired_code
            render_result = render_scene()
            repaired = True
        except Exception as e:
            return {
                "ok": False,
                "router": gen_result.get("router"),
                "code": code,
                "error": "Generation succeeded but render failed and repair failed",
                "details": [str(e)],
                "render": render_result,
                "repaired": repaired,
                "warnings": gen_result["validation"]["warnings"],
            }

    validation = validate_code(code)

    return {
        "ok": render_result["ok"],
        "router": gen_result.get("router"),
        "code": code,
        "validation": validation,
        "warnings": validation["warnings"],
        "video_url": render_result.get("video_url"),
        "render": render_result,
        "repaired": repaired,
    }
