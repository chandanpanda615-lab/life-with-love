import json

def parse_lighthouse():
    with open('lighthouse-report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cats = data.get('categories', {})
    perf = cats.get('performance', {})
    
    print("--- Lighthouse Audit ---")
    if 'score' in perf:
        print(f"Performance Score: {perf['score'] * 100:.0f} / 100")
        
    audits = data.get('audits', {})
    metrics = [
        ('first-contentful-paint', 'First Contentful Paint (FCP)'),
        ('largest-contentful-paint', 'Largest Contentful Paint (LCP)'),
        ('total-blocking-time', 'Total Blocking Time (TBT)'),
        ('cumulative-layout-shift', 'Cumulative Layout Shift (CLS)'),
        ('speed-index', 'Speed Index')
    ]
    
    print("\\n--- Core Web Vitals & Metrics ---")
    for key, label in metrics:
        if key in audits:
            val = audits[key].get('displayValue', 'N/A')
            print(f"{label}: {val}")
            
    print("\\n--- Opportunities (Speed Improvements) ---")
    for key, audit in audits.items():
        if audit.get('details') and audit['details'].get('type') == 'opportunity':
            savings = audit['details'].get('overallSavingsMs', 0)
            if savings > 100:
                print(f"- {audit['title']}: Potential savings ~{savings:.0f} ms")

if __name__ == '__main__':
    parse_lighthouse()
