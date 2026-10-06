"""
Smart Egyptian Slang Summarizer & Media Buyer Impact Engine.
3-Tier Cascade:
1. Google Gemini Flash
2. Groq Llama-3.3-70b
3. Smart Rule-Based Egyptian Fallback (Keyword-driven domain heuristic)
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional

from radar.config import GEMINI_API_KEY, GROQ_API_KEY

logger = logging.getLogger("radar.summarizer")


SYSTEM_PROMPT = """
أنت خبير ميديا باينج مخضرم ومدير حملات إعلانية محترف في الشرق الأوسط.
مهمتك قراءة تحديثات منصات الإعلانات (Meta, Google, TikTok, Snapchat, LinkedIn, X, إلخ) وتلخيصها للميديا بايرز.

المطلوب استخراج JSON دقيق بالشكل التالي:
{
  "egyptian_summary": "ملخص سريع وسلس باللهجة المصرية البسيطة والعملية، يوضح إيه اللي حصل بالضبط في سطرين لـ 3 أسطر بدون فذلكة أو مصطلحات معقدة.",
  "media_buyer_impact": "الأثر العملي الصريح على الميديا باير: هل الـ CPM هيزيد؟ هل في خطر حظر أو رفض إعلانات؟ هل لازم يغير إعدادات البيكسل أو الاستهداف؟ إيه الإجراء الفوري اللي لازم يعمله؟",
  "is_outage": false,
  "category": "تصنيف مناسب مثل (أعطال وسيستم, سياسات وحظر, تتبع وبيكسل, استهداف وجمهور, مزادات وCPM, ميزات جديدة, تحديثات تقنية)"
}

ملاحظات هامة:
- إذا كان الخبر عطلاً أو توقفاً أو مشكلة تقنية في المنصة، اجعل is_outage = true.
- اللهجة المصرية يجب أن تكون احترافية وسلسة (كلام ماركتيرز مصريين فاهمين شغلهم: "خد بالك"، "عدّل البيدج"، "راقب الـ CPM"، "البيكسل مش هيقرا").
- أخرج JSON صالح فقط بدون كود ماركداون إضافي إذا أمكن.
"""


def _clean_json_text(text: str) -> str:
    """Extracts raw JSON substring from markdown backticks or surrounding text."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


def _summarize_with_gemini(title: str, content: str, platform: str) -> Optional[Dict[str, Any]]:
    """Line 1: Google Gemini Flash."""
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        # Try latest flash model names
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json", "temperature": 0.3},
        )
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"المنصة: {platform}\n"
            f"العنوان: {title}\n"
            f"المحتوى:\n{content[:3000]}"
        )
        response = model.generate_content(prompt)
        if response and response.text:
            cleaned = _clean_json_text(response.text)
            parsed = json.loads(cleaned)
            if "egyptian_summary" in parsed and "media_buyer_impact" in parsed:
                return parsed
    except Exception as e:
        logger.warning(f"Gemini summarizer failed: {e}. Falling back to Groq...")
    return None


def _summarize_with_groq(title: str, content: str, platform: str) -> Optional[Dict[str, Any]]:
    """Line 2: Groq Llama-3.3-70b."""
    api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"المنصة: {platform}\nالعنوان: {title}\nالمحتوى:\n{content[:3000]}",
            },
        ]
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        output_str = completion.choices[0].message.content
        if output_str:
            cleaned = _clean_json_text(output_str)
            parsed = json.loads(cleaned)
            if "egyptian_summary" in parsed and "media_buyer_impact" in parsed:
                return parsed
    except Exception as e:
        logger.warning(f"Groq summarizer failed: {e}. Falling back to Rule-Based...")
    return None


def _summarize_with_rule_based(title: str, content: str, platform: str) -> Dict[str, Any]:
    """
    Line 3: Smart Domain-Specific Contextual Fallback.
    Extracts deep, specific Egyptian summary and actionable media buyer playbooks.
    Zero generic boilerplates.
    """
    try:
        from radar.enrich_all_updates import enrich_update
        result = enrich_update(0, platform, title, content, "")
        return {
            "egyptian_summary": result["summary"],
            "media_buyer_impact": result["impact"],
            "is_outage": result["is_outage"],
            "category": result["category"]
        }
    except Exception as e:
        logger.error(f"Error in contextual rule-based summarizer: {e}")
        return {
            "egyptian_summary": f"تحديث في {platform}: {title.strip()}",
            "media_buyer_impact": "راجع تفاصيل التحديث وطبقه على إعدادات حسابك الإعلاني.",
            "is_outage": False,
            "category": "ميزات جديدة"
        }


def summarize_update(title: str, raw_content: str, platform: str) -> Dict[str, Any]:
    """
    Main cascading entry point:
    Line 1: Gemini -> Line 2: Groq -> Line 3: Smart Rule-Based Egyptian Fallback
    Guarantees 100% valid dictionary return with Egyptian summary and impact.
    """
    title = (title or "").strip()
    raw_content = (raw_content or "").strip()

    # Step 1: Gemini
    gemini_result = _summarize_with_gemini(title, raw_content, platform)
    if gemini_result:
        gemini_result["source_engine"] = "gemini"
        return gemini_result

    # Step 2: Groq
    groq_result = _summarize_with_groq(title, raw_content, platform)
    if groq_result:
        groq_result["source_engine"] = "groq"
        return groq_result

    # Step 3: Smart Rule-Based Egyptian Fallback
    fallback_result = _summarize_with_rule_based(title, raw_content, platform)
    fallback_result["source_engine"] = "rule_based_egyptian"
    return fallback_result
