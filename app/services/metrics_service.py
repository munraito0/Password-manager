from prometheus_client import Counter

login_attempts_total = Counter(
    'security_login_attempts_total',
    'Total login attempts by result',
    ['result'],
)

rate_limit_hits_total = Counter(
    'security_rate_limit_hits_total',
    'Total rate limit hits',
)
