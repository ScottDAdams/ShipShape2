# app/utils/rate_limit.py
from flask import request
from functools import wraps
from datetime import datetime
from app.models import db, RateLimit


def rate_limit(limit=100, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not request.headers.get('X-API-Key'):
                return {'error': 'No API key provided'}, 401

            key = request.headers['X-API-Key']
            window_start = datetime.utcnow() - timedelta(seconds=window)

            # Check rate limit
            request_count = RateLimit.query.filter(
                RateLimit.api_key == key,
                RateLimit.timestamp > window_start
            ).count()

            if request_count >= limit:
                return {'error': 'Rate limit exceeded'}, 429

            # Log request
            rate_limit = RateLimit(api_key=key)
            db.session.add(rate_limit)
            db.session.commit()

            return f(*args, **kwargs)

        return wrapped

    return decorator