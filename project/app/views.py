from django.shortcuts import render, redirect
from PyPDF2 import PdfReader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
import google.generativeai as genai

from .models import ResearchHistory
from .services.gemini_service import (analyze_research_paper_chunked,ask_question_from_paper_chunked,)
from .services.gemini_service import compare_research_papers_chunked
from .services.paper_search_service import search_research_papers
limit=3
import re


@login_required
def paper_search(request):
    papers = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("query")
        if query:
            papers = search_research_papers(query)

    return render(request, "paper_search.html", {
        "papers": papers,
        "query": query
    })

@login_required
def compare_pdfs(request):
    comparison = None
    comparison_html = None

    if request.method == 'POST' and request.FILES.get('pdf1') and request.FILES.get('pdf2'):
        
        pdf1 = request.FILES['pdf1']
        pdf2 = request.FILES['pdf2']

        # ── STEP 1: Extract text ──
        reader1 = PdfReader(pdf1)
        reader2 = PdfReader(pdf2)

        text1 = ""
        for page in reader1.pages:
            if page.extract_text():
                text1 += page.extract_text()

        text2 = ""
        for page in reader2.pages:
            if page.extract_text():
                text2 += page.extract_text()

        # ── STEP 2: Compare using filenames as paper names ──
        comparison = compare_research_papers_chunked(
            text1, text2,
            name1=pdf1.name,   # e.g. "paper1.pdf"
            name2=pdf2.name    # e.g. "paper2.pdf"
        )

        # ── STEP 3: Format for display ──
        comparison_html = format_comparison_html(comparison)

    return render(request, 'compare_pdfs.html', {
        'comparison': comparison,
        'comparison_html': comparison_html,
    })




#Formet of compare 
def format_comparison_html(text):
    SECTIONS = [
        ('OVERVIEW',    'blue',   '📊'),
        ('METHODOLOGY', 'purple', '🔬'),
        ('STRENGTHS',   'green',  '✅'),
        ('WEAKNESSES',  'red',    '⚠️'),
        ('VERDICT',     'cyan',   '🏆'),
    ]

    pattern = r'(?:^\d+\.\s*)?(OVERVIEW|METHODOLOGY|STRENGTHS|WEAKNESSES|VERDICT)'
    parts = re.split(pattern, text, flags=re.IGNORECASE | re.MULTILINE)

    html_blocks = []
    i = 1
    while i < len(parts):
        heading_raw = parts[i].strip().upper()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ''
        i += 2

        style, icon = 'blue', '📄'
        for kw, st, ic in SECTIONS:
            if kw in heading_raw:
                style, icon = st, ic
                break

        heading_html = f'<div class="sum-heading {style}">{icon} {heading_raw.title()}</div>'
        safe_body = body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        block = f'<div class="sum-block">{heading_html}<div class="sum-prose">{safe_body}</div></div>'
        html_blocks.append(block)

    if not html_blocks:
        safe = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<div class="sum-block"><div class="sum-prose" style="white-space:pre-wrap">{safe}</div></div>'

    return '\n'.join(html_blocks)



#-----------------------------------------------------------------------------------------------#
#------ Upload & chat section ------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------#
# @login_required(login_url="login")
# def upload_pdf(request):
#     analysis = None
#     analysis_html =None 
#     chat = []

#     if request.method == 'POST' and request.FILES.get('pdf'):
#         analysis = """SHORT SUMMARY



        

# 1. This paper is a review of artificial intelligence and robotics, examining their intersection and impact on economic and organizational dynamics across multiple industries.

# 2. The paper covers applications of AI-powered robotics in healthcare, agriculture, storage/warehousing, and the automotive industry, demonstrating the breadth of real-world deployment.

# 3. Six key algorithms used in robotics are analyzed: Reinforcement Learning, Supervised Learning, Computer Vision, SLAM, Evolutionary Algorithms, and Deep Learning, each with noted strengths and limitations.

# 4. The paper addresses significant ethical challenges surrounding AI and robotics including safety, transparency, accountability, bias, and the philosophical problem of automating moral decision-making.

# 5. Distributional economic impacts are reviewed, including effects on employment across industries, with evidence that AI-driven productivity gains can both displace and create jobs depending on the sector.

# 2. KEY CONTRIBUTIONS

# The paper consolidates a wide body of literature on AI in robotics into a single accessible review. It connects technical progress with economic and organizational implications, which is relatively rare in pure engineering reviews. The paper highlights human-robot interaction and social robotics as emerging research areas deserving greater organizational and strategy research attention. It also surfaces the ethical dimension as a first-class concern rather than an afterthought, citing the Moral Machines framework by Wallach and Allen.

# 3. METHODOLOGY

# This is a literature review paper. The author draws from a diverse set of published studies, academic working papers, and industry reports. Specific studies cited include Autor and Salomon (2018) on industry-level employment effects, Choudhury et al. (2018) on skill composition and AI productivity, and Felten et al. (2018) on occupational impact of AI. The review is structured thematically rather than systematically, covering applications, algorithms, ethics, and distributional effects in sequence.

# 4. STRENGTHS

# The paper covers a genuinely broad scope, connecting machine learning algorithms to their real-world robotics applications clearly. The inclusion of economic distributional analysis alongside technical content is a differentiating strength. Ethical challenges are treated with appropriate seriousness and linked to concrete examples such as autonomous vehicle moral dilemmas. The algorithm section provides a useful comparative overview with honest acknowledgment of limitations for each approach.

# 5. WEAKNESSES

# The paper lacks original empirical data or experiments, being entirely a secondary literature review. Several sections, particularly the Storage and Motor Cars applications, contain informal and imprecise language that reduces academic rigor. The literature cited is relatively sparse with only ten references, and several key recent advances in large language models and embodied AI are not addressed. The distributional goods section (Section VI) contains translation artifacts suggesting portions may have been processed through automated tools, reducing readability and credibility."""

#         chat = [
#             {
#                 "sender": "user",
#                 "text": "What are the main algorithms discussed in this paper?"
#             },
#             {
#                 "sender": "kai",
#                 "text": "The paper discusses six algorithms: Reinforcement Learning for adaptive trial-and-error decision making, Supervised Learning for labeled data tasks like object recognition, Computer Vision for visual perception, SLAM for navigation and mapping, Evolutionary Algorithms for optimization problems, and Deep Learning (CNNs) for perception and control tasks. Each is evaluated for its strengths and computational trade-offs."
#             },
#             {
#                 "sender": "user",
#                 "text": "What does the paper say about healthcare applications?"
#             },
#             {
#                 "sender": "kai",
#                 "text": "In healthcare, the paper highlights three key contributions of AI-robotics integration. First, AI enables more personalized patient monitoring and feedback through IoMT integration. Second, AI-powered mammogram analysis can work 30 times faster with 99% accuracy, significantly reducing false positives. Third, surgical robots have been used in medicine for over three decades, improving precision, efficiency, and patient outcomes across hospitals, rehabilitation, and physical therapy."
#             },
#         ]


#         analysis_html = format_analysis_html(analysis)

#     return render(request, 'index.html', {'analysis': analysis,'analysis_html': analysis_html, 'chat': chat})
@login_requird
def upload_pdf(request):
    analysis = None

    if "chat" not in request.session:# if there is no chat history for user create one empty list
        request.session["chat"] = []

    chat = request.session["chat"] # storing the chat in smarter way
    history = ResearchHistory.objects.filter(user=request.user).last()
    # go to db and find most recent uploaded pdf ans stores it

    if request.method == "POST": # when form submitted

        #----- CHAT QUESTION----#
        if "question" in request.POST:# check for question submitted by user
            question = request.POST.get("question")# store the question

            if history and question:
                #--chunked section
                answer = ask_question_from_paper_chunked(
                    history.extracted_text,# gets the answer for user question then store it
                    question
                )

                chat.append({"sender": "user", "text": question}) # to display the question with user and add to chat
                chat.append({"sender": "ai", "text": answer})

                request.session["chat"] = chat # after the conversation all the chats add to chat
                request.session.modified = True

                analysis = history.summary

        #-----PDF UPLOAD-------#
        elif "pdf" in request.FILES:
            pdf_file = request.FILES.get("pdf") #get pdf and store it in pdf_file
            reader = PdfReader(pdf_file) # read the pdf and store in in reader


           #---text extraction---#
            text = "" #string
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text()

            analysis = analyze_research_paper_chunked(text)#summary after sending text and storing in analysis
            

            #---Record in history---#
            ResearchHistory.objects.create(
                user=request.user,
                pdf_name=pdf_file.name,
                summary=analysis,
                extracted_text=text
            )

            request.session["chat"] = [] # when new  paper uploaded reset the chat means empty

    return render(request, "index.html", {
        "analysis": analysis,
        "chat": request.session.get("chat", [])
    })



@login_required
def history_view(request):
    history = ResearchHistory.objects.filter(
        user=request.user
    ).order_by("-id")   # safer than created_at

    return render(request, "history.html", {
        "history": history
    })


@login_required
def paper_detail(request, paper_id):
    paper = ResearchHistory.objects.get(
        id=paper_id,
        user=request.user
    )

    answer = None

    if request.method == "POST":
        question = request.POST.get("question")
        if question:
            answer = ask_question_from_paper_chunked(
                paper.extracted_text,
                question
            )

    return render(request, "paper_detail.html", {
        "paper": paper,
        "answer": answer
    })

#--------------------------------------------------------------#
# ---------- AUTH ---------------------------------------------#
#--------------------------------------------------------------#

# For new user Register
def register_view(request):
    if request.method == "POST": # checks if the user submitted the form
        form = UserCreationForm(request.POST) # create django default form and take input as data
        if form.is_valid():
            login(request, form.save()) # save a new user and pass to login with a session
            return redirect("upload")
    else:
        form = UserCreationForm() # blank page for ger request
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("upload")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
