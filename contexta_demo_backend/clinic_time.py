"""The clinic's clock. Shared by every feature -- do not read the wall clock
anywhere else.

The clinic is in Hyderabad, so every date, opening hour, booking and printed
timestamp is India Standard Time. Deployed on Vercel the server's own clock is
UTC, so a bare datetime.now() reads 5h30m behind: it stamps the wrong time on a
clinical note and silently breaks "is it open right now", "today", "tomorrow"
and the past-date guard. Always take the clock from clinic_now().

Kept in its own module (rather than in ortho_clinic_data.py, which is ChatBot-
only) so Visit Notes can share it without importing ChatBot data.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

CLINIC_TZ = ZoneInfo("Asia/Kolkata")


def clinic_now() -> datetime:
    """Current date/time at the clinic (IST), independent of the server's tz."""
    return datetime.now(CLINIC_TZ)
