/**
 * Media Buying Radar — Core Dashboard Engine
 * Vanilla JavaScript (High-Performance, Zero Dependencies)
 */

// Global State
const state = {
  updates: [],
  filteredUpdates: [],
  activePlatform: 'all',
  activeCategory: 'all',
  searchQuery: '',
  sortBy: 'newest',
  lastCheckedTime: new Date(),
  deferredPrompt: null
};

// Embedded Fallback Dataset (Ensures immediate offline / local file:// rendering)
const FALLBACK_UPDATES = [
  {
    "id": "meta-outage-01",
    "platform": "meta",
    "platformName": "Meta Ads",
    "category": "outage",
    "categoryLabel": "🚨 عطل فني",
    "severity": "critical",
    "is_outage": true,
    "timestamp": "2026-10-06T11:30:00Z",
    "relativeTime": "منذ ساعتين",
    "title": "Meta Ads Manager: Intermittent Delay in Conversions Reporting & Event Deduplication",
    "summary_egyptian": "فيه تهنيج خفيف في تقارير مدير الإعلانات.. التحويلات بتسمّع متأخرة ساعتين تلاتة، والـ Deduplication بين البيكسل والـ CAPI ملخبط شوية.",
    "buyer_impact": "أوعى تقفل حملاتك الشغالة أو تفتكر الـ ROAS وقع فجأة! استنى لما السيستم يستقر وماتغيرش الميزانيات بناءً على أرقام الساعات الأخيرة.",
    "source_url": "https://metastatus.com/",
    "source_name": "Meta Status Dashboard"
  },
  {
    "id": "meta-feat-01",
    "platform": "meta",
    "platformName": "Meta Ads",
    "category": "feature",
    "categoryLabel": "🚀 ميزة جديدة",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-06T08:15:00Z",
    "relativeTime": "منذ 5 ساعات",
    "title": "Advantage+ Creative Introduces Real-Time Background Audio & Dialect Tuning",
    "summary_egyptian": "ميتا بتطرح ميزة جديدة في الـ Advantage+ بتغير الموسيقى والنبرة الصوتية في الريلز أوتوماتيك حسب اهتمام كل عميل وبلده.",
    "buyer_impact": "فعّل خيار Audio Enhancements في الـ Ad Level، بس راقب جودة الفيديو للتأكد إن الذكاء الاصطناعي ما غطاش على الفويس أوفر الأساسي.",
    "source_url": "https://www.facebook.com/business/news",
    "source_name": "Meta for Business News"
  },
  {
    "id": "meta-policy-01",
    "platform": "meta",
    "platformName": "Meta Ads",
    "category": "policy",
    "categoryLabel": "⚠️ سياسات وحظر",
    "severity": "warning",
    "is_outage": false,
    "timestamp": "2026-10-05T18:00:00Z",
    "relativeTime": "أمس",
    "title": "Stricter Verification Mandate for Health, Supplements & Financial Lead Gen in MENA",
    "summary_egyptian": "تشديد جامد على إعلانات المكملات والتخسيس والخدمات المالية في الخليج ومصر.. أي فورم ليد لازم ترخيص وتوثيق رسمي للشركة.",
    "buyer_impact": "لو شغال في النيش ده، جهز السجل التجاري ورخصة الصحة فوراً قبل ما الحسابات تاخد Restricted، وحول جزء من الترافيك لصفحات هبوط مؤمنة.",
    "source_url": "https://www.facebook.com/business/help/policies",
    "source_name": "Meta Advertising Standards"
  },
  {
    "id": "google-algo-01",
    "platform": "google",
    "platformName": "Google Ads",
    "category": "algorithm",
    "categoryLabel": "⚡ تعديل خوارزمي",
    "severity": "warning",
    "is_outage": false,
    "timestamp": "2026-10-06T09:45:00Z",
    "relativeTime": "منذ 4 ساعات",
    "title": "Demand Gen Algorithm Update: Heavy Favoring of Vertical 9:16 Shorts Video Formats",
    "summary_egyptian": "جوجل عدلت توزيع ميزانيات حملات الـ Demand Gen وبقت تدي أكتر من 60% من الظهور لـ YouTube Shorts بدل الديسكفري التقليدي.",
    "buyer_impact": "حملتك لو مفهياش فيديوهات عمودية 9:16 احترافية بنظام Hook سريع، تكلفتك هتزيد والريتش هيقل. ارفع كريفات شورتس فوراً في كل Ad Group.",
    "source_url": "https://support.google.com/google-ads/announcements",
    "source_name": "Google Ads Announcements"
  },
  {
    "id": "google-feat-01",
    "platform": "google",
    "platformName": "Google Ads",
    "category": "feature",
    "categoryLabel": "🚀 ميزة جديدة",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-05T14:20:00Z",
    "relativeTime": "أمس",
    "title": "Performance Max Asset Group Level Negative Keywords Now in Open Beta",
    "summary_egyptian": "أخيراً جوجل بتسمح بإضافة كلمات سلبية (Negative Keywords) على مستوى الـ Asset Group الواحد في PMax من غير ما تكلم الدعم الفني!",
    "buyer_impact": "ادخل فوراً على حملات الـ PMax بتاعتك، استبعد الكلمات غير ذات الصلة والبراندات المنافسة اللي كانت بتاكل ميزانيتك عالفاضي.",
    "source_url": "https://blog.google/products/ads-commerce/",
    "source_name": "Google Ads & Commerce Blog"
  },
  {
    "id": "google-outage-01",
    "platform": "google",
    "platformName": "Google Ads",
    "category": "outage",
    "categoryLabel": "🚨 عطل فني",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-04T16:10:00Z",
    "relativeTime": "منذ يومين",
    "title": "Resolved: Google Tag Manager (GTM) Container Publish Latency",
    "summary_egyptian": "كان فيه بطء في نشر حاويات الـ GTM وتحديث إشارات التتبع.. جوجل أعلنت حل المشكلة بالكامل ورجوع السيستم للسرعة الطبيعية.",
    "buyer_impact": "اتأكد من عمل Preview لأحدث Tags رفعتها، وافحص هل كل التريجرات شغالة تمام ولا محتاجة Re-publish سريع.",
    "source_url": "https://ads.google.com/status",
    "source_name": "Google Ads Status Dashboard"
  },
  {
    "id": "tiktok-feat-01",
    "platform": "tiktok",
    "platformName": "TikTok Ads",
    "category": "feature",
    "categoryLabel": "🚀 ميزة جديدة",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-06T10:00:00Z",
    "relativeTime": "منذ 3 ساعات",
    "title": "Smart+ Performance Campaigns Global Rollout: Fully Automated Bidding & Creative Mixing",
    "summary_egyptian": "تيك توك أطلقت نظام Smart+ رسمياً لمنافسة Advantage+ من ميتا.. السيستم بيدمج الكريتيف مع الاستهداف والمزايدة أوتوماتيك بالكامل.",
    "buyer_impact": "جرب تعمل حملة اختبار Smart+ بميزانية 20% بجانب حملاتك العادية، وحط 5-7 فيديوهات متنوعة وسيب الخوارزمية تطلع أفضل توليفة.",
    "source_url": "https://www.tiktok.com/business/en/blog",
    "source_name": "TikTok For Business Insights"
  },
  {
    "id": "tiktok-policy-01",
    "platform": "tiktok",
    "platformName": "TikTok Ads",
    "category": "policy",
    "categoryLabel": "⚠️ سياسات وحظر",
    "severity": "warning",
    "is_outage": false,
    "timestamp": "2026-10-05T11:45:00Z",
    "relativeTime": "أمس",
    "title": "Stricter AI-Generated Content (AIGC) Labeling Rules for Paid Video Ads",
    "summary_egyptian": "أي فيديو إعلاني معمول بالـ AI أو فيه أصوات مولدة لازم تعلم على خيار 'AI-generated' في إعدادات الإعلان وإلا الإعلان هيترفض فوري.",
    "buyer_impact": "لو بتستخدم أدوات زي HeyGen أو Midjourney في إعلاناتك، علم على التاج المخصص عشان تتجنب رفض الإعلانات وتعطيل الـ Learning Phase.",
    "source_url": "https://ads.tiktok.com/help/article/creative-policies",
    "source_name": "TikTok Ads Policy Center"
  },
  {
    "id": "tiktok-algo-01",
    "platform": "tiktok",
    "platformName": "TikTok Ads",
    "category": "algorithm",
    "categoryLabel": "⚡ تعديل خوارزمي",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-04T09:15:00Z",
    "relativeTime": "منذ يومين",
    "title": "First 3-Seconds Hook Weight Increased in Auction Quality Score",
    "summary_egyptian": "تيك توك زودت أهمية أول 3 ثواني من الفيديو في تحديد سعر المزاد.. لو المشاهد مكملش للثانية التالتة الـ CPM بيعلى عليك جداً.",
    "buyer_impact": "ركز 80% من مجهود الإنتاج على الـ Hook البصري والنصي في أول ثانيتين، واختبر 3 بدايات مختلفة لكل فيديو بتصوره.",
    "source_url": "https://ads.tiktok.com/help/article/auction-mechanics",
    "source_name": "TikTok Auction Guide"
  },
  {
    "id": "snap-feat-01",
    "platform": "snapchat",
    "platformName": "Snapchat Ads",
    "category": "feature",
    "categoryLabel": "🚀 ميزة جديدة",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-06T07:30:00Z",
    "relativeTime": "منذ 6 ساعات",
    "title": "Snapchat Conversions API (CAPI) v3 Mandate & Enhanced Value Optimization (VO)",
    "summary_egyptian": "سناب شات أطلقت الإصدار الثالث من CAPI بمطابقة متقدمة للإيميلات وأرقام التليفونات، مع تحسين قوي لخوارزمية الـ Value Optimization.",
    "buyer_impact": "ضروري تطلب من المطور يحدث الـ CAPI للنسخة 3 عشان تحافظ على جودة المطابقة، ولو متجر إلكتروني فعّل الـ VO لمضاعفة متوسط قيمة الطلب.",
    "source_url": "https://forbusiness.snapchat.com/blog",
    "source_name": "Snapchat for Business"
  },
  {
    "id": "snap-outage-01",
    "platform": "snapchat",
    "platformName": "Snapchat Ads",
    "category": "outage",
    "categoryLabel": "🚨 عطل فني",
    "severity": "warning",
    "is_outage": true,
    "timestamp": "2026-10-06T12:00:00Z",
    "relativeTime": "منذ ساعة ونصف",
    "title": "Snap Ads Manager: Campaign Delivery Pacing Fluctuations in KSA & UAE",
    "summary_egyptian": "فيه تذبذب في سرعة صرف الميزانيات على سناب في السعودية والإمارات.. بعض الحملات بتصرف أبطأ من المعتاد بـ 35%.",
    "buyer_impact": "بلاش تزود الـ Daily Budget فجأة عشان تعوض الصرف، لأن السيستم أول ما يرجع طبيعي ممكن يصرف الزيادة دفعة واحدة بدون كفاءة.",
    "source_url": "https://status.snap.com/",
    "source_name": "Snap Engineering Status"
  },
  {
    "id": "snap-policy-01",
    "platform": "snapchat",
    "platformName": "Snapchat Ads",
    "category": "policy",
    "categoryLabel": "⚠️ سياسات وحظر",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-03T15:00:00Z",
    "relativeTime": "منذ 3 أيام",
    "title": "Updated Guidelines for AR Lens Sponsored Campaigns Targeting Under-18s",
    "summary_egyptian": "سناب منعت استخدام عدسات الـ AR الترويجية التي تستهدف فئات تحت 18 سنة بدون موافقة صريحة على شروط حماية الخصوصية الجديدة.",
    "buyer_impact": "عدّل استهداف حملات الـ Lens وخلي الفئة العمرية تبدأ من 18+ لتفادي توقف الحملات في الخليج ومصر.",
    "source_url": "https://forbusiness.snapchat.com/advertising/guidelines",
    "source_name": "Snap Advertising Policies"
  },
  {
    "id": "linkedin-feat-01",
    "platform": "linkedin",
    "platformName": "LinkedIn Ads",
    "category": "feature",
    "categoryLabel": "🚀 ميزة جديدة",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-05T16:40:00Z",
    "relativeTime": "أمس",
    "title": "Thought Leader Ads Now Support Promoting Non-Employee Brand Advocates & Influencers",
    "summary_egyptian": "لينكد إن فتحت الترويج لمنشورات أشخاص من خارج شركتك (Thought Leader Ads) زي العملاء والخبراء المستقلين بموافقتهم.",
    "buyer_impact": "فرصة ذهبية لحملات B2B! اطلب من عملائك الراضين ينشروا Case Study عنك وروّج للبوست بتاعهم مباشرة؛ التحويلات أعلى 3 أضعاف من بوستات الشركات.",
    "source_url": "https://www.linkedin.com/business/marketing/blog",
    "source_name": "LinkedIn Marketing Blog"
  },
  {
    "id": "linkedin-algo-01",
    "platform": "linkedin",
    "platformName": "LinkedIn Ads",
    "category": "algorithm",
    "categoryLabel": "⚡ تعديل خوارزمي",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-04T12:00:00Z",
    "relativeTime": "منذ يومين",
    "title": "Predictive Audiences Expansion Using AI Graph Data",
    "summary_egyptian": "خوارزمية لينكد إن بقت تستخدم بيانات الشبكة المهنية لتوسيع الجماهير (Predictive Audiences) استناداً إلى مسار الترقية والمهارات وليس فقط المسمى.",
    "buyer_impact": "جرب تفعل خيار Audience Expansion لو حجم جمهورك أقل من 50 ألف؛ الخوارزمية بقت أدق كتير في استبعاد غير المؤهلين.",
    "source_url": "https://www.linkedin.com/help/linkedin/answer/a518386",
    "source_name": "LinkedIn Help Center"
  },
  {
    "id": "linkedin-policy-01",
    "platform": "linkedin",
    "platformName": "LinkedIn Ads",
    "category": "policy",
    "categoryLabel": "⚠️ سياسات وحظر",
    "severity": "warning",
    "is_outage": false,
    "timestamp": "2026-10-02T10:15:00Z",
    "relativeTime": "منذ 4 أيام",
    "title": "Ban on Third-Party Cookie Relying Audience Segments Ahead of Privacy Sandbox",
    "summary_egyptian": "إيقاف تدريجي لاستيراد الجماهير المعتمدة على ملفات تعريف الطرف الثالث؛ والاعتماد التام على LinkedIn Insight Tag v2 و Conversions API.",
    "buyer_impact": "راجع مصادر جماهيرك، وثبت الـ Insight Tag عبر سيرفر جانبي أو GTM وتأكد إن إرسال الإيميلات المشفرة مفعل.",
    "source_url": "https://www.linkedin.com/legal/privacy-policy",
    "source_name": "LinkedIn Privacy Center"
  },
  {
    "id": "x-feat-01",
    "platform": "x",
    "platformName": "X (Twitter) Ads",
    "category": "feature",
    "categoryLabel": "🚀 ميزة جديدة",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-06T06:20:00Z",
    "relativeTime": "منذ 7 ساعات",
    "title": "X Ads Unveils AI Smart Bidding & Grok-Powered Keyword Intent Matching",
    "summary_egyptian": "منصة إكس أطلقت محرك مزايدة جديد مدعوم بـ Grok لفهم نية المغرد من سياق التغريدات والردود بدقة أعلى بكتير من الكلمات المفتاحية الحرفية.",
    "buyer_impact": "استهدف الكلمات العريضة وسيب المحرك يفهم السياق، ولاحظ هل انخفض سعر النقرة CPC في حملات الترافيك والمبيعات.",
    "source_url": "https://business.x.com/en/blog",
    "source_name": "X Business Blog"
  },
  {
    "id": "x-algo-01",
    "platform": "x",
    "platformName": "X (Twitter) Ads",
    "category": "algorithm",
    "categoryLabel": "⚡ تعديل خوارزمي",
    "severity": "warning",
    "is_outage": false,
    "timestamp": "2026-10-05T08:50:00Z",
    "relativeTime": "أمس",
    "title": "Premium Verified Accounts Granted 5x Auction Weight in Organic & Paid Engagement",
    "summary_egyptian": "الحسابات الموثقة (العلامة الزرقاء أو الذهبية) واخدة أفضلية قوية جداً في التفاعل على إعلاناتها وظهور الردود الترويجية في التايم لاين.",
    "buyer_impact": "ممنوع تشغل إعلانات من حساب غير موثق على إكس؛ الحسابات غير الموثقة بتدفع ما يقارب الضعف في الـ CPM ونسبة التفاعل بتكون ضعيفة.",
    "source_url": "https://help.x.com/en/rules-and-policies/platform-manipulation",
    "source_name": "X Platform Rules"
  },
  {
    "id": "x-outage-01",
    "platform": "x",
    "platformName": "X (Twitter) Ads",
    "category": "outage",
    "categoryLabel": "🚨 عطل فني",
    "severity": "info",
    "is_outage": false,
    "timestamp": "2026-10-03T19:00:00Z",
    "relativeTime": "منذ 3 أيام",
    "title": "Resolved: Analytics Dashboard Impression Discrepancy",
    "summary_egyptian": "تم إصلاح العطل اللي كان مسبب اختلاف بين عدد الظهور المحسوب في تقرير الحملة والأرقام الموجودة في لوحة تحليلات الحساب.",
    "buyer_impact": "الأرقام دلوقتي دقيقة ومتطابقة، وتقدر تعتمد على تقارير الأيام السابقة بعد ما السيستم عمل إعادة احتساب للبيانات.",
    "source_url": "https://status.twitterstat.us/",
    "source_name": "X Status Page"
  }
];

// Helper: Get Platform Icon HTML
function getPlatformIcon(platform) {
  switch (platform) {
    case 'meta':
      return '<i class="fa-brands fa-meta"></i>';
    case 'google':
      return '<i class="fa-brands fa-google"></i>';
    case 'tiktok':
      return '<i class="fa-brands fa-tiktok"></i>';
    case 'snapchat':
      return '<i class="fa-brands fa-snapchat"></i>';
    case 'linkedin':
      return '<i class="fa-brands fa-linkedin"></i>';
    case 'x':
      return '<i class="fa-brands fa-x-twitter"></i>';
    default:
      return '<i class="fa-solid fa-bullhorn"></i>';
  }
}

// Helper: Category Class & Styling
function getCategoryClass(category) {
  switch (category) {
    case 'feature': return 'cat-feature';
    case 'policy': return 'cat-policy';
    case 'outage': return 'cat-outage';
    case 'algorithm': return 'cat-algorithm';
    default: return 'cat-feature';
  }
}

// Platform Arabic Display Names
const PLATFORM_NAMES_AR = {
  all: 'الكل',
  meta: 'Meta Ads',
  google: 'Google Ads',
  tiktok: 'TikTok Ads',
  snapchat: 'Snapchat Ads',
  linkedin: 'LinkedIn Ads',
  x: 'X Ads'
};

// Application Initialization
document.addEventListener('DOMContentLoaded', () => {
  initUrlParams();
  setupEventListeners();
  loadUpdatesData();
  registerServiceWorker();
  initPwaInstall();
  startRelativeTimeTicker();
});

// Parse initial URL query parameters
function initUrlParams() {
  const urlParams = new URLSearchParams(window.location.search);
  const platformParam = urlParams.get('platform');
  const filterParam = urlParams.get('filter') || urlParams.get('category');
  const searchParam = urlParams.get('search') || urlParams.get('q');

  if (platformParam && ['meta', 'google', 'tiktok', 'snapchat', 'linkedin', 'x'].includes(platformParam.toLowerCase())) {
    state.activePlatform = platformParam.toLowerCase();
  }
  if (filterParam && ['feature', 'policy', 'outage', 'algorithm'].includes(filterParam.toLowerCase())) {
    state.activeCategory = filterParam.toLowerCase();
  }
  if (searchParam) {
    state.searchQuery = searchParam.trim();
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = state.searchQuery;
  }
}

// Setup Event Listeners
function setupEventListeners() {
  // Platform Tabs Click
  const platformTabs = document.getElementById('platformTabs');
  if (platformTabs) {
    platformTabs.addEventListener('click', (e) => {
      const btn = e.target.closest('.tab-btn');
      if (!btn) return;
      const platform = btn.dataset.platform;
      if (!platform) return;

      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      state.activePlatform = platform;
      applyFilters();
    });
  }

  // Category Pills Click
  const categoryFilters = document.getElementById('categoryFilters');
  if (categoryFilters) {
    categoryFilters.addEventListener('click', (e) => {
      const btn = e.target.closest('.cat-pill');
      if (!btn) return;
      const category = btn.dataset.category;
      if (!category) return;

      document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      state.activeCategory = category;
      applyFilters();
    });
  }

  // Search Input with Debounce
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim();
      if (clearSearchBtn) {
        clearSearchBtn.style.display = state.searchQuery.length > 0 ? 'block' : 'none';
      }
      applyFilters();
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      state.searchQuery = '';
      clearSearchBtn.style.display = 'none';
      applyFilters();
      searchInput.focus();
    });
  }

  // Sort Select
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sortBy = e.target.value;
      applyFilters();
    });
  }

  // Manual Refresh Button
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      const icon = refreshBtn.querySelector('i');
      if (icon) icon.classList.add('spinning');
      refreshBtn.disabled = true;

      loadUpdatesData(true).finally(() => {
        setTimeout(() => {
          if (icon) icon.classList.remove('spinning');
          refreshBtn.disabled = false;
          showToast('تم تحديث الرادار بأحدث البيانات 🔄', 'fa-solid fa-check');
        }, 600);
      });
    });
  }

  // Outage Filter Banner Button
  const filterOutageBtn = document.getElementById('filterOutageBtn');
  if (filterOutageBtn) {
    filterOutageBtn.addEventListener('click', () => {
      // Set category to outage
      state.activeCategory = 'outage';
      state.activePlatform = 'all';

      // Update UI active buttons
      document.querySelectorAll('.cat-pill').forEach(b => {
        b.classList.toggle('active', b.dataset.category === 'outage');
      });
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.platform === 'all');
      });

      applyFilters();

      // Scroll smoothly to cards grid
      const grid = document.getElementById('cardsGrid');
      if (grid) {
        grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }
}

// Arabic Relative Time Formatter
function computeArabicRelativeTime(dateStr) {
  if (!dateStr) return 'مؤخراً';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return 'مؤخراً';
    const now = new Date();
    const diffSec = Math.floor((now - date) / 1000);
    if (diffSec < 60) return 'منذ لحظات';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin === 1) return 'منذ دقيقة';
    if (diffMin === 2) return 'منذ دقيقتين';
    if (diffMin < 11) return `منذ ${diffMin} دقائق`;
    if (diffMin < 60) return `منذ ${diffMin} دقيقة`;
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours === 1) return 'منذ ساعة';
    if (diffHours === 2) return 'منذ ساعتين';
    if (diffHours < 11) return `منذ ${diffHours} ساعات`;
    if (diffHours < 24) return `منذ ${diffHours} ساعة`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return 'أمس';
    if (diffDays === 2) return 'منذ يومين';
    if (diffDays < 11) return `منذ ${diffDays} أيام`;
    return `منذ ${diffDays} يوم`;
  } catch (e) {
    return 'مؤخراً';
  }
}

// Normalize item to ensure all dashboard fields are present
function normalizeUpdateItem(item, idx) {
  let plat = (item.platform || 'all').toLowerCase();
  if (plat === 'google_ads') plat = 'google';
  if (plat === 'x_ads') plat = 'x';

  const ts = item.timestamp || item.published_at || item.created_at || new Date().toISOString();
  const relTime = item.relativeTime || computeArabicRelativeTime(ts);
  const isOut = Boolean(item.is_outage === true || item.is_outage === 1);

  return {
    ...item,
    id: item.id || `radar-item-${idx}`,
    platform: plat,
    platformName: item.platformName || PLATFORM_NAMES_AR[plat] || item.platform || 'منصة إعلانية',
    category: isOut ? 'outage' : (item.category || 'feature'),
    categoryLabel: item.categoryLabel || (isOut ? '🚨 عطل فني' : '💡 تحديث منصة'),
    summary_egyptian: item.summary_egyptian || item.egyptian_summary || '',
    buyer_impact: item.buyer_impact || item.media_buyer_impact || '',
    source_url: item.source_url || item.original_url || '#',
    timestamp: ts,
    relativeTime: relTime,
    is_outage: isOut
  };
}

// Load Updates Data (Fetch with Fallback)
async function loadUpdatesData(isManual = false) {
  try {
    const response = await fetch(`data/updates.json?t=${Date.now()}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    let rawList = [];
    if (Array.isArray(data) && data.length > 0) {
      rawList = data;
    } else if (data && Array.isArray(data.updates) && data.updates.length > 0) {
      rawList = data.updates;
    } else {
      rawList = FALLBACK_UPDATES;
    }
    state.updates = rawList.map(normalizeUpdateItem);
  } catch (error) {
    console.warn('Network fetch failed, using built-in fallback dataset:', error);
    state.updates = FALLBACK_UPDATES.map(normalizeUpdateItem);
  }

  state.lastCheckedTime = new Date();
  updateLastCheckedIndicator();
  updateStatsAndBadges();
  syncActivePillsWithState();
  applyFilters();
}

// Synchronize UI pills if state was loaded via URL params
function syncActivePillsWithState() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.platform === state.activePlatform);
  });
  document.querySelectorAll('.cat-pill').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === state.activeCategory);
  });
}

// Compute and update stats bar and tab badges
function updateStatsAndBadges() {
  const total = state.updates.length;
  
  // Today's updates: check ISO timestamp date equals today's UTC or relativeTime contains "اليوم" or "ساع"
  const now = new Date();
  const todayDateStr = now.toISOString().split('T')[0];
  const todayCount = state.updates.filter(u => {
    if (u.timestamp && u.timestamp.startsWith(todayDateStr)) return true;
    if (u.relativeTime && (u.relativeTime.includes('ساع') || u.relativeTime.includes('اليوم'))) return true;
    return false;
  }).length;

  // Active outages
  const activeOutages = state.updates.filter(u => u.is_outage === true);
  const outageCount = activeOutages.length;

  // Most active platform
  const platformCounts = {};
  state.updates.forEach(u => {
    platformCounts[u.platform] = (platformCounts[u.platform] || 0) + 1;
  });

  let topPlatformKey = '-';
  let maxCount = 0;
  for (const [p, c] of Object.entries(platformCounts)) {
    if (c > maxCount) {
      maxCount = c;
      topPlatformKey = p;
    }
  }

  // Update DOM stats
  const totalEl = document.getElementById('statTotalUpdates');
  const todayEl = document.getElementById('statTodayUpdates');
  const outagesEl = document.getElementById('statActiveOutages');
  const topPlatformEl = document.getElementById('statTopPlatform');

  if (totalEl) totalEl.textContent = total;
  if (todayEl) todayEl.textContent = todayCount;
  if (outagesEl) outagesEl.textContent = outageCount;
  if (topPlatformEl) topPlatformEl.textContent = PLATFORM_NAMES_AR[topPlatformKey] || topPlatformKey;

  // Update Outage Banner
  const outageBanner = document.getElementById('outageBanner');
  const outageTitle = document.getElementById('outageBannerTitle');
  const outageDesc = document.getElementById('outageBannerDesc');

  if (outageBanner) {
    if (outageCount > 0) {
      outageBanner.classList.remove('hidden');
      if (outageTitle) {
        outageTitle.textContent = `تنبيه طارئ: تم رصد ${outageCount} عطل نشط في منصات الإعلانات`;
      }
      if (outageDesc) {
        const platformsWithOutage = [...new Set(activeOutages.map(o => o.platformName))].join('، ');
        outageDesc.textContent = `هناك تذبذب أو تأخير في تقارير (${platformsWithOutage}). لا تتسرع بتعديل الميزانيات أو الاعتماد على أرقام الساعات الأخيرة!`;
      }
    } else {
      outageBanner.classList.add('hidden');
    }
  }

  // Update Tab Counts
  const countAll = document.getElementById('count-all');
  if (countAll) countAll.textContent = total;

  ['meta', 'google', 'tiktok', 'snapchat', 'linkedin', 'x'].forEach(plat => {
    const countEl = document.getElementById(`count-${plat}`);
    if (countEl) countEl.textContent = platformCounts[plat] || 0;
  });
}

// Filter and Sort Updates
function applyFilters() {
  let list = [...state.updates];

  // 1. Platform Filter
  if (state.activePlatform !== 'all') {
    list = list.filter(u => u.platform === state.activePlatform);
  }

  // 2. Category Filter
  if (state.activeCategory !== 'all') {
    list = list.filter(u => u.category === state.activeCategory);
  }

  // 3. Search Query Filter
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(u => {
      const matchTitle = (u.title || '').toLowerCase().includes(q);
      const matchEg = (u.summary_egyptian || '').toLowerCase().includes(q);
      const matchImpact = (u.buyer_impact || '').toLowerCase().includes(q);
      const matchPlatform = (u.platformName || '').toLowerCase().includes(q);
      const matchCategory = (u.categoryLabel || '').toLowerCase().includes(q);
      return matchTitle || matchEg || matchImpact || matchPlatform || matchCategory;
    });
  }

  // 4. Sort
  if (state.sortBy === 'newest') {
    list.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  } else if (state.sortBy === 'oldest') {
    list.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  } else if (state.sortBy === 'outages-first') {
    list.sort((a, b) => {
      if (a.is_outage && !b.is_outage) return -1;
      if (!a.is_outage && b.is_outage) return 1;
      return new Date(b.timestamp) - new Date(a.timestamp);
    });
  }

  state.filteredUpdates = list;
  renderCards(list);
}

// Render Update Cards
function renderCards(items) {
  const container = document.getElementById('cardsGrid');
  if (!container) return;

  if (items.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon"><i class="fa-solid fa-radar fa-spin" style="animation-duration: 6s;"></i></div>
        <h3>لا توجد تحديثات مطابقة لبحثك</h3>
        <p>جرب تغيير المنصة، أو مسح شريط البحث، أو اختيار فئة تحديث أخرى لعرض نتائج الرادار.</p>
        <button class="btn-reset-filters" id="btnResetFilters">
          <i class="fa-solid fa-rotate-left"></i> إعادة تعيين الفلاتر
        </button>
      </div>
    `;

    const resetBtn = document.getElementById('btnResetFilters');
    if (resetBtn) {
      resetBtn.addEventListener('click', resetAllFilters);
    }
    return;
  }

  container.innerHTML = items.map(item => {
    const platformIcon = getPlatformIcon(item.platform);
    const catClass = getCategoryClass(item.category);

    return `
      <article class="radar-card platform-${escapeHtml(item.platform)}" id="${escapeHtml(item.id)}" data-platform="${escapeHtml(item.platform)}">
        
        <!-- Card Top Meta -->
        <div class="card-top-meta">
          <span class="platform-badge">
            ${platformIcon}
            <span>${escapeHtml(item.platformName)}</span>
          </span>

          <div class="card-tags">
            <span class="category-tag ${catClass}">${escapeHtml(item.categoryLabel)}</span>
            <span class="time-tag">
              <i class="fa-regular fa-clock"></i>
              <span>${escapeHtml(item.relativeTime || 'مؤخراً')}</span>
            </span>
          </div>
        </div>

        <!-- Original Title -->
        <h2 class="card-title">${escapeHtml(item.title)}</h2>

        <!-- Box 1: Egyptian Summary -->
        <div class="box-summary-eg">
          <div class="box-header-title">
            <i class="fa-solid fa-lightbulb"></i>
            <span>الزبدة بالمصري:</span>
          </div>
          <p>${escapeHtml(item.summary_egyptian)}</p>
        </div>

        <!-- Box 2: Buyer Impact -->
        <div class="box-buyer-impact">
          <div class="box-header-title">
            <i class="fa-solid fa-crosshairs"></i>
            <span>الأثر على الميديا باير:</span>
          </div>
          <p>${escapeHtml(item.buyer_impact)}</p>
        </div>

        <!-- Card Actions Footer -->
        <div class="card-actions-footer">
          <a href="${escapeHtml(item.source_url)}" target="_blank" rel="noopener noreferrer" class="btn-open-source" title="فتح المقال أو الإعلان الرسمي">
            <i class="fa-solid fa-arrow-up-right-from-square"></i>
            <span>المصدر الأصلي</span>
          </a>

          <div class="card-action-icons">
            <button class="btn-icon-action btn-copy-summary" data-id="${escapeHtml(item.id)}" title="نسخ ملخص الزبدة">
              <i class="fa-regular fa-copy"></i>
            </button>
            <button class="btn-icon-action btn-share-item" data-id="${escapeHtml(item.id)}" title="مشاركة التحديث">
              <i class="fa-solid fa-share-nodes"></i>
            </button>
          </div>
        </div>

      </article>
    `;
  }).join('');

  // Attach card action buttons listeners
  container.querySelectorAll('.btn-copy-summary').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      const item = state.updates.find(u => u.id === id);
      if (item) copyEgyptianSummary(item);
    });
  });

  container.querySelectorAll('.btn-share-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      const item = state.updates.find(u => u.id === id);
      if (item) shareUpdateItem(item);
    });
  });
}

// Copy Summary Action
function copyEgyptianSummary(item) {
  const textToCopy = `🚨 [رادار الميديا باير | ${item.platformName}]\n📌 ${item.title}\n\n💡 الزبدة بالمصري:\n${item.summary_egyptian}\n\n🎯 الأثر على الميديا باير:\n${item.buyer_impact}\n\n🔗 المصدر: ${item.source_url}`;

  copyTextToClipboard(textToCopy).then(() => {
    showToast('تم نسخ ملخص الزبدة بنجاح! جاهز للإرسال 🚀', 'fa-solid fa-clipboard-check');
  }).catch(() => {
    showToast('فشل النسخ التلقائي، يرجى النسخ يدوياً', 'fa-solid fa-triangle-exclamation');
  });
}

// Share Update Action
function shareUpdateItem(item) {
  const shareData = {
    title: `[رادار الميديا باير] ${item.platformName}`,
    text: `💡 ${item.summary_egyptian}\n🎯 ${item.buyer_impact}`,
    url: item.source_url || window.location.href
  };

  if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
    navigator.share(shareData).catch((err) => {
      console.log('Share dismissed:', err);
    });
  } else {
    // Fallback to copying
    copyEgyptianSummary(item);
  }
}

// Robust Clipboard Copy Function
function copyTextToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text).catch(() => {
      return fallbackCopyText(text);
    });
  } else {
    return fallbackCopyText(text);
  }
}

function fallbackCopyText(text) {
  return new Promise((resolve, reject) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '0';
    textArea.setAttribute('readonly', '');
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      if (successful) resolve();
      else reject(new Error('execCommand failed'));
    } catch (err) {
      document.body.removeChild(textArea);
      reject(err);
    }
  });
}

// Toast Notification Manager
function showToast(message, iconClass = 'fa-solid fa-check') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<i class="${iconClass}"></i><span>${escapeHtml(message)}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-leave');
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, 3200);
}

// Reset all filters to default
function resetAllFilters() {
  state.activePlatform = 'all';
  state.activeCategory = 'all';
  state.searchQuery = '';
  state.sortBy = 'newest';

  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const sortSelect = document.getElementById('sortSelect');

  if (searchInput) searchInput.value = '';
  if (clearSearchBtn) clearSearchBtn.style.display = 'none';
  if (sortSelect) sortSelect.value = 'newest';

  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.platform === 'all');
  });
  document.querySelectorAll('.cat-pill').forEach(b => {
    b.classList.toggle('active', b.dataset.category === 'all');
  });

  applyFilters();
}

// Relative Time Indicator in Header
function updateLastCheckedIndicator() {
  const el = document.getElementById('lastCheckIndicator');
  if (!el) return;
  const now = new Date();
  const diffMinutes = Math.floor((now - state.lastCheckedTime) / 60000);
  
  let label = 'منذ لحظات';
  if (diffMinutes === 1) label = 'منذ دقيقة';
  else if (diffMinutes > 1 && diffMinutes < 10) label = `منذ ${diffMinutes} دقائق`;
  else if (diffMinutes >= 10) label = `منذ ${diffMinutes} دقيقة`;

  el.innerHTML = `<i class="fa-regular fa-clock"></i> <span>آخر فحص: ${label}</span>`;
}

function startRelativeTimeTicker() {
  setInterval(updateLastCheckedIndicator, 60000);
}

// Service Worker Registration
function registerServiceWorker() {
  if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {
    navigator.serviceWorker.register('sw.js')
      .then(reg => {
        console.log('[PWA] Service Worker registered successfully:', reg.scope);
      })
      .catch(err => {
        console.warn('[PWA] Service Worker registration failed:', err);
      });
  }
}

// PWA Install Prompt Support
function initPwaInstall() {
  const installBtn = document.getElementById('installAppBtn');
  if (!installBtn) return;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    state.deferredPrompt = e;
    installBtn.style.display = 'inline-flex';
  });

  installBtn.addEventListener('click', async () => {
    if (!state.deferredPrompt) return;
    state.deferredPrompt.prompt();
    const { outcome } = await state.deferredPrompt.userChoice;
    console.log(`[PWA] Install prompt outcome: ${outcome}`);
    state.deferredPrompt = null;
    installBtn.style.display = 'none';
  });

  window.addEventListener('appinstalled', () => {
    installBtn.style.display = 'none';
    showToast('تم تثبيت تطبيق رادار الميديا باير بنجاح! 📱', 'fa-solid fa-circle-check');
  });
}

// Simple HTML escaping helper for security
function escapeHtml(str) {
  if (typeof str !== 'string') return str || '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
