# 🛰️ رادار تحديثات منصات الإعلانات الممولة (Media Buying Updates Radar)

> **المنظومة السحابية المستقلة الأولى لرصد، تلخيص، وتحليل تحديثات وأعطال منصات الإعلانات العالمية على مدار الساعة (24/7) مجاناً 100% وبدون أي سيرفر مدفوع.**

---

## 📌 المشكلة والحل

### المشكلة:
- منصات الإعلانات (Meta, Google, TikTok, Snapchat, LinkedIn, X) تجري مئات التحديثات الدورية على خوارزمياتها، سياسات الحظر، ميزات الاستهداف، ومصطلحات الـ API.
- تتبع 20-50 موقعاً ومدونة يدوياً يهدر ساعات طويلة، ويفوت تحديثات حاسمة (مثل تغييرات الذكاء الاصطناعي في سناب شات أو تعديلات بكسل التتبع في إكس).
- الشروحات والمدونات الرسمية طويلة ومعقدة وباللغة الإنجليزية وتفتقر إلى الربط العملي بشغل الميديا باير.

### الحل في هذا النظام:
1. **رصد آلي شامل وموحد:** مجسات تسحب كل جديد من المدونات الرسمية، وثائق المطورين (Changelogs)، موجزات الـ RSS، وصفحات الأعطال الرسمية (MetaStatus)، ومجتمعات المسوقين (PPC Hero & Search Engine Journal).
2. **منع التكرار الصارم:** قاعدة بيانات SQLite محلية مدمجة مع نظام بصمة رقمية **SHA-256 Hash** تمنع ظهور أي تحديث مرتين.
3. **سلسلة تلخيص ذكية بالذكاء الاصطناعي المجاني:**
   - استخراج **"💡 الزبدة بالمصري"**: ملخص مركز وسريع في سطرين باللهجة المصرية البسيطة.
   - استخراج **"🎯 الأثر على الميديا باير"**: توجيه عملي مباشر (هل ترفع الميزانية؟ هل تحذر من إغلاق الحساب؟ هل تفعل ميزة استهداف جديدة؟).
4. **لوحة تحكم تفاعلية فخمة (Web Dashboard & PWA):**
   - تصميم زجاجي داكن فاخر (**Dark Glassmorphism**).
   - نظام تابات علوي مستقل لكل منصة: `[الكل]`, `[Meta]`, `[Google Ads]`, `[TikTok Ads]`, `[Snapchat Ads]`, `[LinkedIn Ads]`, `[X Ads]`.
   - شريط بحث فوري، فلترة حسب نوع التحديث (ميزة جديدة / سياسات وحظر / عطل فني / تعديل خوارزمي).
   - زر مباشر لفتح المصدر الأصلي وزر نسخ الملخص بنقرة واحدة.
   - دعم التثبيت كتطبيق PWA على الهواتف الذكية والحواسب.
5. **تشغيل سحابي مجاني 100% (Serverless):**
   - مؤتمت بالكامل عبر **GitHub Actions** يعمل كـ Cron Job كل 30 دقيقة.
   - يستضيف الواجهة مجاناً عبر **GitHub Pages** أو **Vercel**.

---

## 🏗️ المعمارية التقنية (Architecture & Tech Stack)

```
media-buying-radar/
├── .github/
│   └── workflows/
│       └── radar.yml                # المشغل السحابي التلقائي (Cron كل 30 دقيقة عبر GitHub Actions)
├── radar/
│   ├── config.py                   # إعدادات روابط الـ RSS والمصادر ومفاتيح الـ APIs
│   ├── database.py                 # قاعدة بيانات SQLite + منع التكرار بـ SHA-256 + تصدير JSON
│   ├── llm_summarizer.py           # سلسلة التلخيص الذكية (Gemini -> Groq -> Local Fallback)
│   ├── scanners/                   # مجسات الرصد المتخصصة لكل منصة
│   │   ├── base.py                 # الفئة الأساسية للمجسات والطلبات المحمية
│   │   ├── meta_scanner.py         # رصد Meta & MetaStatus
│   │   ├── google_scanner.py       # رصد Google Ads Developer & Announcements
│   │   ├── tiktok_scanner.py       # رصد TikTok Newsroom & API
│   │   ├── snapchat_scanner.py     # رصد Snapchat Business & Developers
│   │   ├── linkedin_scanner.py     # رصد LinkedIn Marketing API & Blog
│   │   ├── x_scanner.py            # رصد X Developers & Ads
│   │   └── community_scanner.py    # رصد مجتمعات PPC Hero & Search Engine Journal
│   └── main.py                     # المنسق العام لمحرك الرصد
├── web/                            # لوحة التحكم التفاعلية للويب و PWA
│   ├── index.html                  # هيكل الواجهة الزجاجية باللغة العربية
│   ├── style.css                   # تنسيق Dark Glassmorphism متجاوب
│   ├── app.js                      # المنطق التفاعلي، التابات، البحث، والتصفية
│   ├── manifest.json               # إعدادات تطبيق الويب PWA
│   ├── sw.js                       # Service Worker للعمل أوفلاين
│   └── data/
│       └── updates.json            # قاعدة البيانات الحية المصدرة للواجهة
├── requirements.txt                # متطلبات بايثون
├── test_engine.py                  # حزمة الاختبارات الشاملة (Unit & Integration Tests)
└── main.py                         # نقطة الدخول السريعة لتشغيل الدورة من الجذر
```

---

## 🚀 طريقة التشغيل السريع محلياً (Local Setup)

### 1. تثبيت المتطلبات:
```bash
cd media-buying-radar
pip install -r requirements.txt
```

### 2. تشغيل فحص الرادار الآن:
```bash
python main.py
```
يقوم الأمر بفحص كافة المنصات، حفظ التحديثات الجديدة في `radar.db`، وتصدير النتيجة فوراً إلى `web/data/updates.json`.

### 3. تشغيل لوحة التحكم في المتصفح:
يمكنك فتح ملف `web/index.html` مباشرة في المتصفح، أو تشغيل خادم محلي خفيف:
```bash
cd web
python -m http.server 8080
```
ثم توجه إلى الرابط: `http://localhost:8080`

### 4. تشغيل حزمة الاختبارات الذاتية:
```bash
python test_engine.py
```

---

## ☁️ خطوات النشر السحابي المجاني (100% Free Hosting & Automation)

### الخطوة 1: رفع المشروع على مستودع GitHub
1. أنشئ مستودعاً جديداً (Public أو Private) على حسابك في GitHub باسم `media-buying-radar`.
2. ارفع ملفات المشروع:
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit for media-buying-radar"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/media-buying-radar.git
   git push -u origin main
   ```

### الخطوة 2: تفعيل الأذونات لـ GitHub Actions
1. في صفحة المستودع على GitHub، اذهب إلى: **Settings** $\rightarrow$ **Actions** $\rightarrow$ **General**.
2. تحت قسم **Workflow permissions**، اختر:
   - ✅ **Read and write permissions** (لتمكين السيرفر السحابي من حفظ ملف التحديثات والتعديلات تلقائياً).
3. اضغط **Save**.

### الخطوة 3: (اختياري) إضافة مفاتيح الذكاء الاصطناعي المجانية
النظام مزود بمولد ذكي محلي يعمل بكفاءة تامة بدون أي مفاتيح، ولكن للحصول على صياغات أعمق، يمكنك إضافة مفاتيح مجانية:
1. اذهب إلى: **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
2. أضف الـ Secrets التالية:
   - `GEMINI_API_KEY`: مفتاحك المجاني من [Google AI Studio](https://aistudio.google.com/).
   - `GROQ_API_KEY`: مفتاحك المجاني من [Groq Console](https://console.groq.com/).

### الخطوة 4: النشر السحابي الفوري على Vercel (موصى به ⚡)
بفضل ملف الإعداد الجاهز `vercel.json` الموجود في جذر المشروع، يمكنك نشره بنقرة واحدة:
1. توجه إلى [Vercel](https://vercel.com/) وسجّل الدخول بحساب GitHub الخاص بك.
2. اضغط **Add New...** ثم **Project**.
3. اختر مستودع `media-buying-radar` واضغط **Import**.
4. اترك كافة الإعدادات كما هي (سيتعرف Vercel تلقائياً على مجلد `web/` بفضل `vercel.json`) واضغط **Deploy**.
5. ستحصل فوراً وخلال 15 ثانية على رابط سحابي عالمي سريع وفائق السرعة:
   `https://media-buying-radar.vercel.app`
6. **مزامنة تلقائية 24/7:** في كل مرة يعمل فيها GitHub Actions كل 30 دقيقة ويسحب تحديثات جديدة، ستقوم Vercel تلقائياً بإعادة نشر الموقع بالبيانات الجديدة دون أي تدخل يدوي منك!

---

### خيار بديل: تفعيل لوحة التحكم عبر GitHub Pages
1. اذهب إلى: **Settings** $\rightarrow$ **Pages** داخل مستودع GitHub.
2. تحت **Build and deployment**:
   - **Source**: اختر `Deploy from a branch`.
   - **Branch**: اختر `main` واضغط **Save**. (ملف `index.html` في الجذر سيوجه الزوار تلقائياً لمجلد الويب `web/`).
3. ستحصل على رابط مباشر مجاني 24/7 لموقعك:
   `https://YOUR_USERNAME.github.io/media-buying-radar/`

---

## 🛡️ خط دفاع الذكاء الاصطناعي (Free LLM Fallback Pool)

النظام مصمم بمبدأ **الحماية الثلاثية (Triple Redundancy)** حتى لا يتعطل أبداً:
1. **Google Gemini Flash (Primary):** يقوم بصياغة ملخصات مصرية دقيقة واستخراج الأثر التسويقي في ثوانٍ عبر واجهة مجانية.
2. **Groq Llama 3.3 (Backup 1):** يتحول إليه النظام تلقائياً لو نفدت حصة جيميني أو حدث بطء.
3. **Smart Rule-Based Egyptian Engine (Last Resort):** يحلل الكلمات المفتاحية في متن التحديث ويستنتج نوعه (حظر، تكلفة إعلانات، بكسل تتبع، استهداف، أو عطل)، ويولد كارت "الزبدة بالمصري" و"الأثر على الميديا باير" حتى لو انقطعت كافة خدمات الـ API!

---

## 📱 ميزات لوحة التحكم (Dashboard Features)
- **شريط تنبيه الأعطال الطارئة (Live Outage Banner):** ينبهك فوراً إذا واجهت منصة ميتا أو غيرها عطلاً في السيستم لتتجنب إلقاء اللوم على إعلاناتك.
- **نسخ الملخص بضغطة زر:** لمشاركة التحديث السريع مع فريقك في تليجرام أو واتساب أو سلاك.
- **تطبيق PWA:** يمكنك الضغط على "تثبيت كتطبيق" في المتصفح واستخدامه كتطبيق سطح مكتب أو موبايل مستقل.
- **تحديث يدوي وفوري:** زر مزامنة لإعادة تحميل أحدث البيانات بلمسة واحدة.

---

**تم البناء بنجاح وبأعلى معايير الجودة والحتمية البرمجية بواسطة Antigravity AI.**
