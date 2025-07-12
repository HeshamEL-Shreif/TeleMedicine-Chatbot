from utils.utils import llm, search_tool
from langdetect import detect
from langchain_core.tools import tool
from db.vector_db import load_vector_store

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """
    Given a user query, retrieve Arabic documents likely to contain the answer
    by generating a synthetic paragraph in Modern Standard Arabic and performing similarity search.
    Returns a serialized result and top relevant documents.
    """
    search_snippets = search_tool.run(query)
    language = detect(query)
    
    if language == 'en':
        prompt = f'''
            You are an expert assistant that helps retrieve information from Arabic documents.
            When given a user question, generate a synthetic Arabic paragraph (like one that might appear in an Arabic PDF) that would likely contain the answer to the question.

            Use the following information, retrieved from the web, to help you build a realistic paragraph:

            {search_snippets}

            • Write in Modern Standard Arabic, in a formal and informative tone, as if it came from an educational or government report.
            • Use natural sentence structure and include keywords from the question.
            • Your output should be a single realistic paragraph, not a question, and should resemble how content would appear in the original documents.
            • Do not answer the question directly — just simulate a paragraph where such an answer would be found.

            User Question:
            {query}
            '''
    else:
        prompt = f'''
            أنت مساعد ذكي وخبير في استرجاع المعلومات من مستندات مكتوبة باللغة العربية.

            فيما يلي بعض المعلومات التي تم استرجاعها من الإنترنت لتساعدك في إنشاء فقرة واقعية:

            {search_snippets}

            ▪︎ أنشئ فقرة اصطناعية باللغة العربية تشبه تلك الموجودة في تقارير رسمية أو ملفات PDF.
            ▪︎ اكتب بلغة عربية فصحى رسمية.
            ▪︎ لا تكرر السؤال، بل أنشئ فقرة تحتوي على كلمات رئيسية من السؤال وكأنها تقدم المعلومة داخل نص أصلي.
            ▪︎ لا تجب عن السؤال بشكل مباشر، بل حاكي الفقرة التي قد تحتوي على الإجابة.

            سؤال المستخدم:
            {query}
'''
    synthetic_paragraph = llm.invoke(prompt).content
    retrieved_docs = load_vector_store().similarity_search(synthetic_paragraph, k=5)
    
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    
    return serialized, retrieved_docs