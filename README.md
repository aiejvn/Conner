# **C**ollaborative **O**utput-time **N**eural **N**etworks for **E**nhanced **R**easoning (**CONNER**)

Canadian physicians spend 18.5 million hours annually on unnecessary administrative tasks - that's 55.6 million patient visits lost to paperwork instead of patient care. Physicians also spend 19 unpaid hours per week on administrative tasks, 75% of physicians report dissatisfaction when doing this unnecessary admin work, and 94% of physicians say they're overwhelmed by it. Furthermore, 40% of these administrative tasks don't require physician expertise.

However, current AI agents perform poorly on administrative tasks. A 2024 study at Carnegie Mellon University, researchers found most AI agents struggled to complete over 90% of administrative tasks assigned to them, citing self-deception and shortcuts as a key factor hindering performance. We designed the CONNER framework to resolve this issue.

CONNER is the first plug-and-play deep reasoning AI framework specifically designed for medical administrative workflows.
CONNER leverages the same optimized solution searching strategies as Deepseek Prover v1.5, the state-of-the-art reasoning model for complex multi-step tasks, but purpose-built for healthcare administration.

The CONNER framework solves the biggest problem with AI agents: the black box issue. With CONNER, physicians maintain complete control and can ensure accuracy at every step. 

## Setting Up:

1. Add `GEMINI_API_KEY` and `OPENAI_API_KEY` to a `.env` file.

2. Run `streamlit run app.py`.