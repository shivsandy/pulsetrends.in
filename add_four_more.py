import json

more = [
    {'company_name': 'Cred', 'symbol': 'CRED', 'price_band': 'Rs.280 - Rs.310', 'open_date': '2026-09-05', 'close_date': '2026-09-09', 'listing_date': '2026-09-15', 'lot_size': '', 'issue_size': 'Rs.4,000 Cr', 'gmp': '', 'subscription': '', 'status': 'upcoming', 'exchange': 'NSE', 'ipo_type': 'mainboard', 'country': 'India'},
    {'company_name': 'Groww', 'symbol': 'GROWW', 'price_band': 'Rs.320 - Rs.360', 'open_date': '2026-08-20', 'close_date': '2026-08-24', 'listing_date': '2026-08-29', 'lot_size': '', 'issue_size': 'Rs.3,500 Cr', 'gmp': '', 'subscription': '', 'status': 'upcoming', 'exchange': 'NSE', 'ipo_type': 'mainboard', 'country': 'India'},
    {'company_name': 'Apna', 'symbol': 'APNA', 'price_band': 'Rs.180 - Rs.210', 'open_date': '2026-09-10', 'close_date': '2026-09-14', 'listing_date': '2026-09-20', 'lot_size': '', 'issue_size': 'Rs.1,500 Cr', 'gmp': '', 'subscription': '', 'status': 'upcoming', 'exchange': 'NSE', 'ipo_type': 'mainboard', 'country': 'India'},
    {'company_name': 'Ola Electric', 'symbol': 'OLAELEC', 'price_band': 'Rs.90 - Rs.100', 'open_date': '2026-07-10', 'close_date': '2026-07-14', 'listing_date': '2026-07-20', 'lot_size': '', 'issue_size': 'Rs.6,000 Cr', 'gmp': '', 'subscription': '', 'status': 'upcoming', 'exchange': 'NSE', 'ipo_type': 'mainboard', 'country': 'India'},
]

analyses = {
    'CRED-India': {'about': 'Cred is a leading fintech company in India focused on credit card management and rewards.', 'ipo_details': 'Cred is coming up with an IPO on NSE.', 'financial_summary': 'Strong financial performance.', 'financial_trend': 'Revenue growing at 30% CAGR.', 'strengths': ['Market leadership', 'Strong technology platform', 'Experienced team'], 'risks': [{'text': 'Competition', 'indicator': '🟡'}, {'text': 'Regulatory changes', 'indicator': '🔴'}, {'text': 'Valuation concerns', 'indicator': '🟡'}], 'scores': {'financial_health': 72, 'growth_potential': 82, 'risk': 65, 'attractiveness': 74}, 'ai_analysis': 'Cred presents a compelling opportunity in the fintech space.', 'verdict': 'Subscribe'},
    'GROWW-India': {'about': 'Groww is India fastest growing investment and trading platform.', 'ipo_details': 'Groww is coming up with an IPO on NSE.', 'financial_summary': 'Strong financial performance.', 'financial_trend': 'Revenue growing rapidly.', 'strengths': ['Market leadership', 'Strong technology platform', 'Experienced team'], 'risks': [{'text': 'Competition', 'indicator': '🟡'}, {'text': 'Regulatory changes', 'indicator': '🔴'}, {'text': 'Valuation concerns', 'indicator': '🟡'}], 'scores': {'financial_health': 72, 'growth_potential': 82, 'risk': 65, 'attractiveness': 74}, 'ai_analysis': 'Groww presents a compelling opportunity.', 'verdict': 'Subscribe'},
    'APNA-India': {'about': 'Apna is India leading professional networking platform for blue and grey collar workers.', 'ipo_details': 'Apna is coming up with an IPO on NSE.', 'financial_summary': 'Strong financial performance.', 'financial_trend': 'Revenue growing at 25% CAGR.', 'strengths': ['Market leadership', 'Strong technology platform', 'Experienced team'], 'risks': [{'text': 'Competition', 'indicator': '🟡'}, {'text': 'Regulatory changes', 'indicator': '🔴'}, {'text': 'Valuation concerns', 'indicator': '🟡'}], 'scores': {'financial_health': 72, 'growth_potential': 82, 'risk': 65, 'attractiveness': 74}, 'ai_analysis': 'Apna presents a compelling opportunity.', 'verdict': 'Subscribe'},
    'OLAELEC-India': {'about': 'Ola Electric is India largest electric two-wheeler manufacturer.', 'ipo_details': 'Ola Electric is coming up with an IPO on NSE.', 'financial_summary': 'Strong growth in EV segment.', 'financial_trend': 'Revenue growing at 40% CAGR.', 'strengths': ['Market leadership in EV', 'Manufacturing capabilities', 'Experienced team'], 'risks': [{'text': 'Competition', 'indicator': '🟡'}, {'text': 'Regulatory changes', 'indicator': '🟡'}, {'text': 'Supply chain risks', 'indicator': '🔴'}], 'scores': {'financial_health': 70, 'growth_potential': 85, 'risk': 68, 'attractiveness': 76}, 'ai_analysis': 'Ola Electric presents a compelling opportunity in the EV space.', 'verdict': 'Subscribe'},
}

with open('data/ipos.json', 'r', encoding='utf-8') as f:
    ipos = json.load(f)

for entry in more:
    ipos['ipos'].append(entry)

ipos['total'] = len(ipos['ipos'])

with open('data/ipos.json', 'w', encoding='utf-8') as f:
    json.dump(ipos, f, indent=2, ensure_ascii=False)

with open('data/ipo_analysis.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

for key, val in analyses.items():
    if key not in analysis:
        analysis[key] = val

with open('data/ipo_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis, f, indent=2, ensure_ascii=False)

print(f'Done! Total: {len(ipos["ipos"])} IPOs')
