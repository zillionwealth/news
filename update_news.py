import json
import os
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

HKT = timezone(timedelta(hours=8))
SHARE_URL = os.environ.get("SHARE_URL", "https://zillionwealth.github.io/news/")

STATIC_I18N = {
    "tc": {
        "motto": '"Enriching the life of the people we touch" — Zillion Wealth 專業財富與保障管理團隊',
        "topBadge": "每日晨間 09:00 AM HKT 準時發送",
        "btnPrint": "🖨️ 列印 / 另存 PDF",
        "btnShare": "🔗 複製分享連結",
        "headerTag": "每日晨訊",
        "headerSubtitle": "保險 · 理財 · 環球市場 · 宏觀資產配置 6 大核心焦點",
        "headerAuthor": "主編：Fasun Wong | Certified Trust Planner (認可信託策劃師)",
        "sec1Title": "環球股票市場指數 及美債息 & 波動率 (Stock Market Index, Yields & VIX)",
        "sec2Title": "大宗商品 · 加密貨幣 · 樓市指數 (Commodities, Crypto & Property Index)",
        "sec3Title": "今日保險、理財與投資 6 大新聞精粹 (Top 6 Intelligence Highlights)",
        "idxHsiName": "香港恒生指數",
        "idxSpName": "標普 500 指數",
        "idxDjiName": "道瓊斯工業指數",
        "idxNasName": "納斯達克綜合指數",
        "idxVixName": "CBOE 恐慌指數",
        "idxUs10Name": "美國 10 年期債息",
        "idxEuName": "歐洲斯托克 50",
        "idxNikName": "日本日經 225",
        "idxKorName": "韓國綜合指數",
        "idxTwnName": "台灣加權指數",
        "idxCsiName": "滬深 300 指數",
        "idxUs2Name": "美國 2 年期債息",
        "idxGoldName": "國際現貨黃金",
        "idxSilName": "國際現貨白銀",
        "idxOilName": "布蘭特原油期貨",
        "idxBtcName": "比特幣加密貨幣",
        "idxCclName": "中原城市領先指數",
        "bannerBadge": "今日智策",
        "footerBrand": "Zillion Wealth · 每日財富與保障管理團隊晨報",
        "footerCredentials": "編輯主理：Fasun Wong | Certified Trust Planner (認可信託策劃師)",
        "footerDisclaimer": "免責聲明：本晨報所載市場數據與新聞摘要均彙整自公開權威財經媒體及官方收市報告，僅供內部團隊及客戶財富管理參考與教育用途，不構成任何投資、保險或稅務要約或建議。",
    },
    "sc": {
        "motto": '"Enriching the life of the people we touch" — Zillion Wealth 专业财富与保障管理团队',
        "topBadge": "每日晨间 09:00 AM HKT 准时发送",
        "btnPrint": "🖨️ 打印 / 另存 PDF",
        "btnShare": "🔗 复制分享链接",
        "headerTag": "每日晨讯",
        "headerSubtitle": "保险 · 理财 · 环球市场 · 宏观资产配置 6 大核心焦点",
        "headerAuthor": "主编：Fasun Wong | Certified Trust Planner (认可信托策划师)",
        "sec1Title": "环球股票市场指数 及美债息 & 波动率 (Stock Market Index, Yields & VIX)",
        "sec2Title": "大宗商品 · 加密货币 · 楼市指数 (Commodities, Crypto & Property Index)",
        "sec3Title": "今日保险、理财与投资 6 大新闻精粹 (Top 6 Intelligence Highlights)",
        "idxHsiName": "香港恒生指数",
        "idxSpName": "标普 500 指数",
        "idxDjiName": "道琼斯工业指数",
        "idxNasName": "纳斯达克综合指数",
        "idxVixName": "CBOE 恐慌指数",
        "idxUs10Name": "美国 10 年期债息",
        "idxEuName": "欧洲斯托克 50",
        "idxNikName": "日本日经 225",
        "idxKorName": "韩国综合指数",
        "idxTwnName": "台湾加权指数",
        "idxCsiName": "沪深 300 指数",
        "idxUs2Name": "美国 2 年期债息",
        "idxGoldName": "国际现货黄金",
        "idxSilName": "国际现货白银",
        "idxOilName": "布伦特原油期货",
        "idxBtcName": "比特币加密货币",
        "idxCclName": "中原城市领先指数",
        "bannerBadge": "今日智策",
        "footerBrand": "Zillion Wealth · 每日财富与保障管理团队晨报",
        "footerCredentials": "编辑主理：Fasun Wong | Certified Trust Planner (认可信托策划师)",
        "footerDisclaimer": "免责声明：本晨报所载市场数据与新闻摘要均汇整自公开权威财经媒体及官方收市报告，仅供内部团队及客户财富管理参考与教育用途，不构成任何投资、保险或税务要约或建议。",
    },
    "en": {
        "motto": '"Enriching the life of the people we touch" — Zillion Wealth Professional Wealth & Protection Team',
        "topBadge": "Dispatched Daily at 09:00 AM HKT",
        "btnPrint": "🖨️ Print / Save PDF",
        "btnShare": "🔗 Copy Share Link",
        "headerTag": "Daily Brief",
        "headerSubtitle": "Insurance · Wealth Management · Global Markets · Macro Asset Allocation",
        "headerAuthor": "Editor: Fasun Wong | Certified Trust Planner",
        "sec1Title": "Stock Market Index, US Treasury Yields & VIX",
        "sec2Title": "Commodities, Crypto & HK Property Index",
        "sec3Title": "Top 6 Insurance, Wealth & Investment Highlights",
        "idxHsiName": "Hang Seng Index",
        "idxSpName": "S&P 500 Index",
        "idxDjiName": "Dow Jones (DJIA)",
        "idxNasName": "Nasdaq Composite",
        "idxVixName": "CBOE Volatility (VIX)",
        "idxUs10Name": "US 10Y Treasury",
        "idxEuName": "Euro Stoxx 50",
        "idxNikName": "Nikkei 225",
        "idxKorName": "KOSPI Composite",
        "idxTwnName": "TAIEX Index",
        "idxCsiName": "CSI 300 Index",
        "idxUs2Name": "US 2Y Treasury",
        "idxGoldName": "Spot Gold",
        "idxSilName": "Spot Silver",
        "idxOilName": "Brent Crude Oil",
        "idxBtcName": "Bitcoin (BTC)",
        "idxCclName": "Centaline CCL (HK)",
        "bannerBadge": "Daily Strategy",
        "footerBrand": "Zillion Wealth · Daily Wealth & Protection Briefing",
        "footerCredentials": "Editor: Fasun Wong | Certified Trust Planner",
        "footerDisclaimer": "Disclaimer: Market data and news summaries are compiled from public financial media and official closing reports for internal team and client wealth planning reference only, and do not constitute investment, insurance, or tax advice.",
    },
}

INDEX_KEYS = [
    ("hsi", "idxHsiNote"),
    ("sp", "idxSpNote"),
    ("dji", "idxDjiNote"),
    ("nas", "idxNasNote"),
    ("vix", "idxVixNote"),
    ("us10", "idxUs10Note"),
    ("eu", "idxEuNote"),
    ("nik", "idxNikNote"),
    ("kor", "idxKorNote"),
    ("twn", "idxTwnNote"),
    ("csi", "idxCsiNote"),
    ("us2", "idxUs2Note"),
    ("gold", "idxGoldNote"),
    ("sil", "idxSilNote"),
    ("oil", "idxOilNote"),
    ("btc", "idxBtcNote"),
    ("ccl", "idxCclNote"),
]


def fetch_daily_briefing(now_hkt: datetime) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    weekday_en = now_hkt.strftime("%A")
    date_str = now_hkt.strftime("%Y-%m-%d")
    is_weekend = now_hkt.weekday() >= 5  # Saturday=5, Sunday=6

    prompt = f"""
You are the chief financial editor for Zillion Wealth (Hong Kong). Today in Hong Kong is {date_str} ({weekday_en}), 08:45 AM HKT.
Use Google Search to retrieve REAL, VERIFIED market data and news. Never invent numbers or URLs.

Rules:
1. If equity/bond markets were closed (weekend or public holiday, e.g. {is_weekend}), use the latest official closing price and change %, and mark sec1Tag as:
   - tc: "最後更新結算價（休市期間維持上日收市）"
   - sc: "最后更新结算价（休市期间维持上日收市）"
   - en: "Last Update (Previous Official Close — Market Closed)"
   Otherwise use:
   - tc: "隔夜官方收市結算價"
   - sc: "隔夜官方收市结算价"
   - en: "Overnight Official Close"
   For sec2Tag: Crypto trades 24/7; if commodities are closed, mark "晨間最新報價 / 最後更新" ("晨间最新报价 / 最后更新" / "Latest Morning Quote / Last Update").
2. Return ONLY valid JSON matching this exact schema (no markdown fences):
{{
  "dates": {{
    "tc": "YYYY 年 M 月 D 日 星期X",
    "sc": "YYYY 年 M 月 D 日 星期X",
    "en": "Weekday, Month D, YYYY"
  }},
  "headerTime": {{
    "tc": "⏰ 09:00 AM HKT 發行 · 隔夜權威結算基準" (or "⏰ 09:00 AM HKT 發行 · 休市最後更新基準" if closed),
    "sc": "...",
    "en": "..."
  }},
  "sec1Tag": {{"tc": "...", "sc": "...", "en": "..."}},
  "sec2Tag": {{"tc": "...", "sc": "...", "en": "..."}},
  "indices": {{
    "hsi": {{"price": "23,264.96", "change": "▼ -1.03%", "direction": "down", "note": {{"tc": "...", "sc": "...", "en": "..."}}}},
    "sp": {{"price": "...", "change": "...", "direction": "up|down|flat", "note": {{"tc": "...", "sc": "...", "en": "..."}}}},
    "dji": {{...}}, "nas": {{...}}, "vix": {{...}}, "us10": {{...}},
    "eu": {{...}}, "nik": {{...}}, "kor": {{...}}, "twn": {{...}}, "csi": {{...}}, "us2": {{...}},
    "gold": {{...}}, "sil": {{...}}, "oil": {{...}}, "btc": {{...}}, "ccl": {{...}}
  }},
  "highlights": [
    {{
      "source_name": "South China Morning Post",
      "source_url": "https://...",
      "cat": {{"tc": "...", "sc": "...", "en": "..."}},
      "title": {{"tc": "1. ...", "sc": "1. ...", "en": "1. ..."}},
      "sum": {{"tc": "...", "sc": "...", "en": "..."}},
      "adv": {{"tc": "...", "sc": "...", "en": "..."}}
    }}
    // exactly 6 highlights covering HK/Greater Bay insurance, wealth/family office, macro rates, commodities/crypto, global equities
  ],
  "banner": {{
    "title": {{"tc": "...", "sc": "...", "en": "..."}},
    "desc": {{"tc": "...", "sc": "...", "en": "..."}}
  }},
  "team_whatsapp_summary": "3 concise Traditional Chinese bullet points + link {SHARE_URL}",
  "client_email": {{
    "subject": "Zillion Wealth 每日晨訊 | {date_str}：...",
    "intro": "2-sentence Traditional Chinese greeting & key takeaway for clients"
  }}
}}
"""
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.2,
        ),
    )
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.S)
    return json.loads(raw)


def update_html(data: dict) -> None:
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # 1. Update header date/time & section tags (TC default)
    for elem_id, val in [
        ("text-header-date", data["dates"]["tc"]),
        ("text-header-time", data["headerTime"]["tc"]),
        ("text-sec1-tag", data["sec1Tag"]["tc"]),
        ("text-sec2-tag", data["sec2Tag"]["tc"]),
        ("text-banner-title", data["banner"]["title"]["tc"]),
        ("text-banner-desc", data["banner"]["desc"]["tc"]),
    ]:
        el = soup.find(id=elem_id)
        if el:
            el.string = val

    # 2. Update 17 metric cards
    for key, _ in INDEX_KEYS:
        idx = data["indices"][key]
        note_el = soup.find(id=f"idx-{key}-note")
        if note_el:
            note_el.string = idx["note"]["tc"]
            card = note_el.find_parent(class_="metric-card")
            if card:
                price_el = card.find(class_="price-value")
                if price_el:
                    price_el.string = idx["price"]
                badge_el = card.find(class_="change-badge")
                if badge_el:
                    badge_el.string = idx["change"]
                    direction = idx.get("direction", "flat")
                    cls = "change-up" if direction == "up" else ("change-down" if direction == "down" else "change-flat")
                    badge_el["class"] = ["change-badge", cls]

    # 3. Update 6 news highlights
    for i, hl in enumerate(data["highlights"][:6], start=1):
        for elem_id, val in [
            (f"hl-cat-{i}", hl["cat"]["tc"]),
            (f"hl-title-{i}", hl["title"]["tc"]),
            (f"hl-sum-{i}", hl["sum"]["tc"]),
            (f"hl-adv-desc-{i}", hl["adv"]["tc"]),
        ]:
            el = soup.find(id=elem_id)
            if el:
                el.string = val
        src_label = soup.find(id=f"hl-src-label-{i}")
        if src_label and src_label.parent:
            link = src_label.parent.find("a")
            if link:
                link["href"] = hl["source_url"]
                link.string = hl["source_name"]

    updated_html = str(soup)

    # 4. Rebuild i18nData cleanly
    i18n_full = {}
    for lang in ("tc", "sc", "en"):
        lang_dict = dict(STATIC_I18N[lang])
        lang_dict["headerDate"] = data["dates"][lang]
        lang_dict["headerTime"] = data["headerTime"][lang]
        lang_dict["sec1Tag"] = data["sec1Tag"][lang]
        lang_dict["sec2Tag"] = data["sec2Tag"][lang]
        for key, i18n_note_key in INDEX_KEYS:
            lang_dict[i18n_note_key] = data["indices"][key]["note"][lang]
        for i, hl in enumerate(data["highlights"][:6], start=1):
            lang_dict[f"hlCat{i}"] = hl["cat"][lang]
            lang_dict[f"hlTitle{i}"] = hl["title"][lang]
            lang_dict[f"hlSum{i}"] = hl["sum"][lang]
            lang_dict[f"hlAdvDesc{i}"] = hl["adv"][lang]
        lang_dict["bannerTitle"] = data["banner"]["title"][lang]
        lang_dict["bannerDesc"] = data["banner"]["desc"][lang]
        i18n_full[lang] = lang_dict

    i18n_js = "const i18nData = " + json.dumps(i18n_full, ensure_ascii=False, indent=6) + ";"
    updated_html = re.sub(
        r"const i18nData\s*=\s*\{.*?\};\s*(?=\n\s*function switchLang)",
        lambda _: i18n_js + "\n",
        updated_html,
        flags=re.S,
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(updated_html)


def write_daily_summary(data: dict, now_hkt: datetime) -> None:
    summary = {
        "date_hkt": now_hkt.strftime("%Y-%m-%d"),
        "display_date_tc": data["dates"]["tc"],
        "share_url": SHARE_URL,
        "whatsapp_message": (
            f"☀️ *Zillion Wealth 每日晨訊* ({data['dates']['tc']})\n\n"
            f"{data['team_whatsapp_summary']}\n\n"
            f"👉 完整互動報告：{SHARE_URL}"
        ),
        "email_subject": data["client_email"]["subject"],
        "email_intro": data["client_email"]["intro"],
        "highlights": [
            {
                "title": hl["title"]["tc"],
                "summary": hl["sum"]["tc"],
                "source_name": hl["source_name"],
                "source_url": hl["source_url"],
            }
            for hl in data["highlights"][:6]
        ],
    }
    with open("daily_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    now_hkt = datetime.now(HKT)
    briefing = fetch_daily_briefing(now_hkt)
    update_html(briefing)
    write_daily_summary(briefing, now_hkt)
    print(f"Successfully updated index.html and daily_summary.json for {now_hkt.strftime('%Y-%m-%d')}")
