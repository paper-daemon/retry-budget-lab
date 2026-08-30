#!/usr/bin/env python3
import argparse, json, math, html
from pathlib import Path


def _finite(name, value):
    if not math.isfinite(float(value)):
        raise ValueError(f'{name} must be finite')

def validate_schedule(attempts, base, factor, cap, jitter):
    if attempts < 1:
        raise ValueError('attempts must be >= 1')
    for name, value in (('base', base), ('factor', factor), ('cap', cap), ('jitter', jitter)):
        _finite(name, value)
    if base < 0:
        raise ValueError('base must be >= 0')
    if factor <= 0:
        raise ValueError('factor must be > 0')
    if cap < 0:
        raise ValueError('cap must be >= 0')
    if jitter < 0:
        raise ValueError('jitter must be >= 0')

def validate_probability(attempts, success_prob):
    if attempts < 1:
        raise ValueError('attempts must be >= 1')
    _finite('success_prob', success_prob)
    if not 0 <= success_prob <= 1:
        raise ValueError('success_prob must be between 0 and 1')

def schedule(attempts, base, factor, cap, jitter):
    validate_schedule(attempts, base, factor, cap, jitter)
    rows=[]
    for i in range(1, attempts+1):
        if i == 1:
            delay = 0.0
        else:
            raw = min(cap, base * (factor ** (i-2)))
            delay = raw * (1 + jitter)
        rows.append({'attempt':i,'delay_before':round(delay,3)})
    return rows

def metrics(attempts, success_prob):
    validate_probability(attempts, success_prob)
    p=float(success_prob); q=1-p
    expected=sum(q**i for i in range(attempts))
    success_by_n=1-(q**attempts)
    return {
        'expected_requests_per_job':round(expected,4),
        'success_probability':round(success_by_n,6),
        'worst_case_requests_per_job':attempts,
    }

def analyze(attempts, base, factor, cap, jitter, success_prob, concurrency, timeout):
    if concurrency < 1:
        raise ValueError('concurrency must be >= 1')
    _finite('timeout', timeout)
    if timeout < 0:
        raise ValueError('timeout must be >= 0')
    rows=schedule(attempts,base,factor,cap,jitter)
    m=metrics(attempts,success_prob)
    total_delay=sum(x['delay_before'] for x in rows)
    worst_duration=total_delay + attempts*timeout
    m.update({
        'max_concurrent_requests_if_all_retry':concurrency*attempts,
        'worst_case_job_seconds':round(worst_duration,3),
        'delay_schedule':rows,
    })
    return m
def render(r, cfg):
    rows=''.join(f"<tr><td>{x['attempt']}</td><td>{x['delay_before']}s</td></tr>" for x in r['delay_schedule'])
    return (
        '<!doctype html><meta charset="utf-8">'
        '<style>body{font:15px system-ui;max-width:950px;margin:auto;padding:40px;background:#f1eadf}'
        '.hero{font:700 52px serif;color:#a94768}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}'
        '.cards div{background:#fffaf2;padding:18px;border:1px solid #ded2c4}table{width:100%;border-collapse:collapse;background:#fffaf2}'
        'td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}</style>'
        '<h1>Retry Budget Lab</h1>'
        f"<div class='hero'>{r['expected_requests_per_job']}x</div><p>expected request amplification</p>"
        '<div class="cards">'
        f"<div><b>success by final attempt</b><br>{r['success_probability']:.2%}</div>"
        f"<div><b>worst job time</b><br>{r['worst_case_job_seconds']}s</div>"
        f"<div><b>max request pressure</b><br>{r['max_concurrent_requests_if_all_retry']}</div></div>"
        f"<p>policy: {html.escape(str(cfg))}</p>"
        '<table><tr><th>attempt</th><th>delay before</th></tr>'+rows+'</table>'
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--attempts',type=int,default=5)
    ap.add_argument('--base-delay',type=float,default=1.0)
    ap.add_argument('--factor',type=float,default=2.0)
    ap.add_argument('--cap',type=float,default=30.0)
    ap.add_argument('--jitter',type=float,default=.2,help='worst-side jitter fraction')
    ap.add_argument('--success-prob',type=float,default=.65,help='success chance per attempt')
    ap.add_argument('--concurrency',type=int,default=20)
    ap.add_argument('--timeout',type=float,default=10.0)
    ap.add_argument('--json',default='retry-budget.json'); ap.add_argument('--html',default='retry-budget.html')
    a=ap.parse_args(); cfg=vars(a).copy(); cfg.pop('json'); cfg.pop('html')
    r=analyze(a.attempts,a.base_delay,a.factor,a.cap,a.jitter,a.success_prob,a.concurrency,a.timeout)
    Path(a.json).write_text(json.dumps({'config':cfg,'report':r},indent=2),encoding='utf-8')
    Path(a.html).write_text(render(r,cfg),encoding='utf-8')
    print(f"amplification={r['expected_requests_per_job']}x success={r['success_probability']:.2%} worst={r['worst_case_job_seconds']}s")
if __name__=='__main__': main()
