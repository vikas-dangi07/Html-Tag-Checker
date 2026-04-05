from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

HTML_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}

TAG_PATTERN = re.compile(r"<(/?\s*[a-zA-Z0-9\-]+)([^>]*)>")
TAG_NAME_RE = re.compile(r"^/?\s*([a-zA-Z0-9\-]+)")

def pos_to_line_col(text, pos):
    line = text.count("\n", 0, pos) + 1
    col = pos - text.rfind("\n", 0, pos)
    return line, col

def check_html_tags(text):
    stack = []
    errors = []

    for match in TAG_PATTERN.finditer(text):
        tag_text = match.group(0)
        tag_name_part = match.group(1)
        start_pos = match.start()
        line, col = pos_to_line_col(text, start_pos)

        name_match = TAG_NAME_RE.match(tag_name_part)
        if not name_match:
            errors.append({"line": line, "col": col, "message": f"Invalid tag: {tag_text}"})
            continue

        tag_name = name_match.group(1).lower()
        is_closing = tag_text.startswith("</")
        is_self_closing = tag_text.endswith("/>") or tag_name in HTML_VOID_TAGS

        if is_closing:
            if not stack:
                errors.append({"line": line, "col": col, "message": f"Unexpected closing tag </{tag_name}>."})
            else:
                last_tag = stack[-1]
                if last_tag == tag_name:
                    stack.pop()
                else:
                    errors.append({"line": line, "col": col,
                                   "message": f"Mismatched closing tag </{tag_name}> (expected </{last_tag}>)."})
                    stack.pop()
        elif not is_self_closing:
            stack.append(tag_name)

    for tag in reversed(stack):
        errors.append({"line": 0, "col": 0, "message": f"Unclosed tag <{tag}>."})

    return {"ok": not errors, "errors": errors}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.json
    text = data.get("text", "")
    result = check_html_tags(text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
