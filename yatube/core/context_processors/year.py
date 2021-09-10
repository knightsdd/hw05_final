from typing import Dict

from django.utils import timezone


def year(request) -> Dict:
    """Return current year."""

    now = timezone.now()
    return {
        'year': str(now.year)
    }
