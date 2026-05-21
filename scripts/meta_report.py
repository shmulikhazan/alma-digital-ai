"""
meta_report.py
--------------
שולף נתוני ביצועים של 7 ימים אחרונים מ-Meta Marketing API
עבור חשבון פרסום: act_2432270937227537

נתונים: campaign_name, spend, impressions, clicks, ctr
"""

import requests
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# 🔑 הגדרות - מלא את ה-Access Token שלך כאן
# ─────────────────────────────────────────────
ACCESS_TOKEN = "PASTE_YOUR_ACCESS_TOKEN_HERE"  # אל תשמור כאן טוקן אמיתי!
AD_ACCOUNT_ID = "act_2432270937227537"
API_VERSION = "v20.0"
# ─────────────────────────────────────────────


def get_date_range(days: int = 7) -> dict:
    """מחזיר טווח תאריכים של X ימים אחרונים בפורמט YYYY-MM-DD."""
    today = datetime.now()
    since = today - timedelta(days=days)
    return {
        "since": since.strftime("%Y-%m-%d"),
        "until": today.strftime("%Y-%m-%d"),
    }


def fetch_campaign_insights(access_token: str, ad_account_id: str) -> list[dict]:
    """
    שולף נתוני ביצועים ברמת קמפיין מ-Meta Insights API.

    Returns:
        רשימה של קמפיינים עם הנתונים המבוקשים.
    """
    url = f"https://graph.facebook.com/{API_VERSION}/{ad_account_id}/insights"
    date_range = get_date_range(days=7)

    params = {
        "access_token": access_token,
        "level": "campaign",
        "fields": "campaign_name,spend,impressions,clicks,ctr",
        "time_range": f'{{"since":"{date_range["since"]}","until":"{date_range["until"]}"}}',
        "limit": 500,
    }

    all_results = []

    while url:
        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            raise RuntimeError(
                f"שגיאה מה-API: {data['error'].get('message', data['error'])}"
            )

        all_results.extend(data.get("data", []))

        # Pagination
        paging = data.get("paging", {})
        next_url = paging.get("next")
        if next_url:
            url = next_url
            params = {}  # הפרמטרים כבר מקודדים ב-URL הבא
        else:
            url = None

    return all_results


def format_report(campaigns: list[dict]) -> None:
    """מדפיס דוח מעוצב לטרמינל."""
    date_range = get_date_range(days=7)
    print("\n" + "=" * 75)
    print(f"  📊 Meta Ads Report — {date_range['since']} עד {date_range['until']}")
    print(f"  🏦 Ad Account: {AD_ACCOUNT_ID}")
    print("=" * 75)

    if not campaigns:
        print("  ⚠️  לא נמצאו נתונים עבור הטווח הנבחר.")
        print("=" * 75)
        return

    # כותרות עמודות
    print(f"\n{'קמפיין':<35} {'Spend ($)':>10} {'Impressions':>13} {'Clicks':>9} {'CTR (%)':>9}")
    print("-" * 80)

    total_spend = 0.0
    total_impressions = 0
    total_clicks = 0

    for camp in campaigns:
        name = camp.get("campaign_name", "—")[:34]
        spend = float(camp.get("spend", 0))
        impressions = int(camp.get("impressions", 0))
        clicks = int(camp.get("clicks", 0))
        ctr = float(camp.get("ctr", 0))

        total_spend += spend
        total_impressions += impressions
        total_clicks += clicks

        print(f"{name:<35} {spend:>10.2f} {impressions:>13,} {clicks:>9,} {ctr:>9.2f}%")

    # סיכום
    total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    print("-" * 80)
    print(f"{'TOTAL':<35} {total_spend:>10.2f} {total_impressions:>13,} {total_clicks:>9,} {total_ctr:>9.2f}%")
    print("=" * 75)
    print(f"\n  סה\"כ {len(campaigns)} קמפיינים נמצאו.\n")


def main():
    if ACCESS_TOKEN == "PASTE_YOUR_ACCESS_TOKEN_HERE":
        print("❌ שגיאה: לא הוזן ACCESS_TOKEN. ערוך את הקובץ והזן את הטוקן שלך.")
        return

    print("⏳ שולף נתונים מ-Meta Marketing API...")

    try:
        campaigns = fetch_campaign_insights(ACCESS_TOKEN, AD_ACCOUNT_ID)
        format_report(campaigns)
    except RuntimeError as e:
        print(f"\n❌ {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ שגיאת חיבור: בדוק את החיבור לאינטרנט שלך.")
    except Exception as e:
        print(f"\n❌ שגיאה בלתי צפויה: {e}")


if __name__ == "__main__":
    main()
