import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# ── Smart text trimmer — grabs intro + conclusion, skips middle bulk ──
def smart_trim(text, max_chars=6000):
    if len(text) <= max_chars:
        return text
    # Take first 4000 (abstract/intro) + last 2000 (conclusion)
    return text[:4000] + "\n\n[...middle sections trimmed...]\n\n" + text[-2000:]


# ── Single call summary — no chunking needed ──
def analyze_research_paper_chunked(full_text):
    trimmed = smart_trim(full_text, max_chars=6000)

    prompt = f"""
You are an expert research analyst.

Analyze this research paper and return a structured analysis.

Rules:
- Clear academic tone
- No emojis
- No special characters
- Plain text only
- Use section headings exactly as shown below

Sections:
SHORT SUMMARY
(5 numbered points)

KEY CONTRIBUTIONS
(paragraph)

METHODOLOGY
(paragraph)

STRENGTHS
(paragraph)

WEAKNESSES
(paragraph)

Paper Content:
{trimmed}
"""
    response = model.generate_content(prompt)
    return response.text


# ── Compare in 3 calls instead of 11 ──
def compare_research_papers_chunked(text1, text2, name1, name2):
    # Call 1: summarize paper 1
    summary1 = model.generate_content(f"""
Summarize this research paper in 300 words. Focus on objective, method, findings.
Plain text only. No markdown.

{smart_trim(text1, 5000)}
""").text

    # Call 2: summarize paper 2
    summary2 = model.generate_content(f"""
Summarize this research paper in 300 words. Focus on objective, method, findings.
Plain text only. No markdown.

{smart_trim(text2, 5000)}
""").text

    # Call 3: compare both summaries
    prompt = f"""
You are an expert AI research assistant.

Compare these two research papers based on the summaries below.

Rules:
- Plain text only
- No markdown
- No special characters
- Neutral academic tone
- Use section headings exactly as shown

Paper 1: {name1}
{summary1}

Paper 2: {name2}
{summary2}

Sections:
OVERVIEW
METHODOLOGY
STRENGTHS
WEAKNESSES
VERDICT
"""
    response = model.generate_content(prompt)
    return response.text


# ── Q&A unchanged — already efficient (1 call) ──
def ask_question_from_paper_chunked(full_text, question):
    trimmed = smart_trim(full_text, max_chars=6000)

    prompt = f"""
Answer the question ONLY using the research paper content below.
If not found, say: Not mentioned in the paper.

Paper Content:
{trimmed}

Question:
{question}
"""
    response = model.generate_content(prompt)
    return response.text