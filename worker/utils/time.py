from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def now_kst() -> datetime:
    return datetime.now(KST).replace(microsecond=0)


def now_kst_text() -> str:
    return now_kst().strftime("%Y-%m-%d %H:%M:%S")
