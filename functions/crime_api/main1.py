import os
import csv
from flask import Flask, jsonify

app = Flask(__name__)

def load_csv():
    base = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(base, "25_Complaints_against_police.csv"),
        r"D:\SurakshaAI\datasets\rajanand\crime-in-india\versions\4\25_Complaints_against_police.csv",
    ]
    for p in paths:
        p = os.path.normpath(p)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = []
                for row in reader:
                    clean = {k.strip().replace('\ufeff',''): v for k,v in row.items()}
                    for k in clean:
                        if k not in ('Area_Name','Sub_group'):
                            try: clean[k] = int(clean[k]) if clean[k] else 0
                            except: pass
                    rows.append(clean)
                return rows
    return []

DATA = load_csv()

def find_state(name):
    s = name.lower().replace('-',' ').replace('_',' ')
    for row in DATA:
        area = row.get('Area_Name','').lower()
        if s in area or area in s:
            return row
    return None

def risk_score(row):
    c = row.get('CPA_-_Complaints_Received/Alleged',0) or 0
    r = row.get('CPA_-_Cases_Registered',0) or 0
    d = row.get('CPC_-_Police_Personnel_Disciplinary_Action_Initiated',0) or 0
    raw = c + r*2 + d*1.5
    return min(100, round((raw/25000)*100, 2))

@app.route('/risk/<state_name>', methods=['GET'])
def get_risk(state_name):
    row = find_state(state_name)
    if not row:
        return jsonify({'error': 'State not found'}), 404
    
    return jsonify({
        'state': row['Area_Name'],
        'risk_rate': risk_score(row),
        'no_of_cases': row.get('CPA_-_Cases_Registered', 0)
    }), 200

@app.route('/states', methods=['GET'])
def get_states():
    return jsonify({'states': sorted(set(r['Area_Name'] for r in DATA))}), 200

if __name__ == '__main__':
    app.run(debug=True)