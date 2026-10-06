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
    Line 3: Smart Rule-Based Egyptian Fallback.
    Analyzes keywords (حظر، CPM، استهداف، بكسل، عطل، إلخ) and formulates Egyptian summary + practical impact.
    Works 100% offline without any API keys.
    """
    text_corpus = f"{title} {content}".lower()
    platform_name = platform.replace("_", " ").title()

    # Detection logic
    is_outage = any(
        kw in text_corpus
        for kw in [
            "outage", "disruption", "incident", "downtime", "maintenance",
            "degraded", "issue with delivery", "latency", "failure",
            "عطل", "توقف", "خلل", "مشكلة تقنية", "تعطل", "سقوط"
        ]
    )

    is_pixel_tracking = any(
        kw in text_corpus
        for kw in [
            "pixel", "capi", "conversion api", "attribution", "cookie",
            "skadnetwork", "tracking", "tag manager", "event quality",
            "بيكسل", "تتبع", "إحالة", "تحويلات", "أحداث"
        ]
    )

    is_policy_ban = any(
        kw in text_corpus
        for kw in [
            "policy", "violation", "restricted", "ban", "compliance",
            "prohibited", "disapproved", "rejection", "disabled account",
            "سياسة", "حظر", "مخالفة", "رفض", "تقييد", "إغلاق الحساب"
        ]
    )

    is_budget_bidding = any(
        kw in text_corpus
        for kw in [
            "cpm", "cpc", "roas", "bidding", "budget", "cost",
            "auction", "pricing", "spend", "تكلفة", "ميزانية", "عطاء", "مزاد"
        ]
    )

    is_targeting_audience = any(
        kw in text_corpus
        for kw in [
            "audience", "targeting", "lookalike", "custom audience",
            "demographic", "interest", "broad", "advantaget", "pmax",
            "استهداف", "جمهور", "مشابه", "اهتمامات"
        ]
    )

    is_api_update = any(
        kw in text_corpus
        for kw in [
            "api", "endpoint", "version", "deprecated", "deprecation",
            "v21.0", "v22.0", "v20.0", "sdk", "developer", "واجهة برمجة"
        ]
    )

    # 1. Outage Handling
    if is_outage:
        category = "أعطال وسيستم"
        egyptian_summary = (
            f"في عطل أو خلل تقني مؤقت تم رصده في خدمات {platform_name}. "
            f"العنوان: {title.strip()}. النظام سجل بطء أو توقف جزئي في تسليم الإعلانات أو تسجيل التحويلات."
        )
        media_buyer_impact = (
            "🚨 متعدلش في حملاتك دلوقتي خالص ولا تقفلها! راقب الصرف ومستوى الـ Delivery، "
            "ولما المنصة تعلن إن العطل اتحل، راجع النتائج عشان تتأكد إن الميزانية متحرقتش ع الفاضي."
        )

    # 2. Policy & Bans
    elif is_policy_ban:
        category = "سياسات وحظر"
        egyptian_summary = (
            f"منصة {platform_name} نزلت تحديث أو تشديد في معايير وسياسات الإعلانات: {title.strip()}. "
            "التحديث بيركز على مراجعة المحتوى والامتثال لشروط الحسابات الإعلانية."
        )
        media_buyer_impact = (
            "⚠️ راجع نصوص إعلاناتك وصفحات الهبوط (Landing Pages) فوراً قبل ما السيستم الآلي يعمل رفض مفاجئ "
            "أو يقيد الحساب الإعلاني، وخلّي عندك صفحات احتياطية وحسابات طوارئ جاهزة."
        )

    # 3. Pixel & Tracking
    elif is_pixel_tracking:
        category = "تتبع وبيكسل"
        egyptian_summary = (
            f"تحديث في آلية التتبع والـ Conversions في {platform_name}: {title.strip()}. "
            "المنصة بتحدث طريقة احتساب الأحداث وربط الـ Conversions API أو بروتوكولات الخصوصية."
        )
        media_buyer_impact = (
            "🎯 ادخل فوراً على Events Manager وراجع Event Match Quality وسرعة وصول البيانات. "
            "لو مش مفعل الـ CAPI (الربط من السيرفر)، دي إشارة واضحة إنك لازم تفعله عشان متخسرش داتا التحويلات."
        )

    # 4. Budget & Bidding (CPM)
    elif is_budget_bidding:
        category = "مزادات وCPM"
        egyptian_summary = (
            f"تغييرات في نظام المزاد واستراتيجيات التسعير في {platform_name}: {title.strip()}. "
            "التحديث بيأثر على طريقة احتساب التكلفة وتوزيع ميزانية الحملات."
        )
        media_buyer_impact = (
            "💰 راقب الـ CPM وتكلفة النتيجة خلال الـ 48 ساعة الجاية. لو لاحظت ارتفاع غير مبرر، "
            "جرب تغير استراتيجية الـ Bidding أو وسّع الشريحة المستهدفة لتقليل ضغط المزاد."
        )

    # 5. Targeting & Audiences
    elif is_targeting_audience:
        category = "استهداف وجمهور"
        egyptian_summary = (
            f"منصة {platform_name} أطلقت تعديل في خيارات الاستهداف وتوزيع الجماهير: {title.strip()}. "
            "التركيز رايح أكتر لخوارزميات الذكاء الاصطناعي والاستهداف التلقائي الموسع."
        )
        media_buyer_impact = (
            "👥 جرب اختبار A/B Test بين جماهيرك القديمة وبين الـ Broad / Advantage+ Targeting. "
            "المنصات بتقلل الاعتماد على الاهتمامات الضيقة وبتعتمد أكتر على قوة الكرييتيف نفسه."
        )

    # 6. API & Tech Changes
    elif is_api_update:
        category = "تحديثات تقنية"
        egyptian_summary = (
            f"تحديث رسمي في Marketing API لمنصة {platform_name}: {title.strip()}. "
            "تم تعديل بعض الـ Endpoints أو إيقاف ميزات قديمة والانتقال لإصدار أحدث."
        )
        media_buyer_impact = (
            "🔧 لو شغال بأدوات تتبع خارجية (زي Triple Whale أو AppsFlyer أو بوتات أوتوميشن)، "
            "تأكد إن التولز متحدثة على أحدث API Version عشان ميحصلش توقف في تدفق البيانات."
        )

    # 7. General Business / Feature Announcement
    else:
        category = "ميزات جديدة"
        clean_title = title.strip()
        egyptian_summary = (
            f"منصة {platform_name} أعلنت عن ميزة جديدة وتحديث رسمي: {clean_title}. "
            "التحديث هدفه تحسين تجربة المعلنين ورفع كفاءة النتائج."
        )
        media_buyer_impact = (
            "🚀 اقرأ تفاصيل التحديث وجربه في حملة تجريبية صغيرة بميزانية محدودة قبل ما تعممه على باقي الحملات الرئيسية."
        )

    return {
        "egyptian_summary": egyptian_summary,
        "media_buyer_impact": media_buyer_impact,
        "is_outage": is_outage,
        "category": category,
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
