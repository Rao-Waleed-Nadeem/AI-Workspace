STRUCTURED_ANALYSIS_PROMPT = """
Analyze the following text.

Return a JSON object with exactly these fields:

- title
- summary
- keywords

Rules:

- title must be a short title
- summary must be a concise explanation
- keywords must contain relevant keywords
- return valid JSON only
- do not include Markdown
- do not include explanations outside the JSON

Text:

{content}
"""
