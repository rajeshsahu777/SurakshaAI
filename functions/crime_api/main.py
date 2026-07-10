import os
import csv
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# =============================================================================
# SURAKSHAAI - COMPLETE UNIFIED DATA PROCESSOR
# Handles ALL 20+ crime datasets, computes multi-dimensional composite scores
# =============================================================================

class SurakshaAIDataProcessor:
    """
    Unified processor for all SurakshaAI datasets
    Loads 20+ CSV files, cleans, normalizes, and computes composite risk
    """
    
    def __init__(self, base_paths=None):
        # Multiple paths to search for datasets
        self.base_paths = base_paths or [
            "datasets",
            os.path.join("..", "..", "datasets"),
            r"D:\SurakshaAI\datasets",
            r"D:\SurakshaAI\datasets\rajanand\crime-in-india\versions\4",
            os.path.dirname(os.path.abspath(__file__)),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "datasets")
        ]
        self.datasets = {}
        self.state_year_index = {}  # Fast lookup: state -> year -> data
        
    # =========================================================================
    # DATA LOADING & CLEANING
    # =========================================================================
    
    def load_all_datasets(self):
        """Load ALL available CSV files from all paths"""
        dataset_configs = {
            # File 1: Police Complaints (base risk)
            'complaints': {
                'pattern': '25_Complaints_against_police',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'complaints_received': 'CPA_-_Complaints_Received/Alleged',
                    'cases_registered': 'CPA_-_Cases_Registered',
                    'disciplinary_actions': 'CPC_-_Police_Personnel_Disciplinary_Action_Initiated',
                    'dismissals': 'CPC_-_Police_Personnel_Dismissal/Removal_from_Service',
                    'convictions': 'CPB_-_Police_Personnel_Convicted',
                    'trials_completed': 'CPB_-_Police_Personnel_Trial_Completed',
                    'false_cases': 'CPA_-_Complaints/Cases_Declared_False/Unsubstantiated',
                    'dept_enquiries': 'CPA_-_No_of_Departmental_Enquiries',
                    'mag_enquiries': 'CPA_-_No_of_Magisterial_Enquiries'
                }
            },
            # File 2: Rape Victims
            'rape_victims': {
                'pattern': '20_Victims_of_rape',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'rape_victims_total': 'Victims_of_Rape_Total',
                    'rape_victims_below_18': 'Victims_of_Rape_Below_18_Years',
                    'rape_victims_above_18': 'Victims_of_Rape_Above_18_Years'
                }
            },
            # File 3: Property Stolen
            'property_stolen': {
                'pattern': '10_Property_stolen_and_recovered',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'property_stolen_value': 'Value_of_Property_Stolen',
                    'property_recovered_value': 'Value_of_Property_Recovered',
                    'recovery_rate': 'Recovery_Rate'
                }
            },
            # File 4: Murder Victims
            'murder': {
                'pattern': '32_Murder_victim_age_sex',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'murder_victims_total': 'Murder_victims_Total',
                    'murder_victims_male': 'Murder_victims_Male',
                    'murder_victims_female': 'Murder_victims_Female'
                }
            },
            # File 5: Auto Theft
            'auto_theft': {
                'pattern': '30_Auto_theft',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'auto_theft_cases': 'Auto_Theft_Stolen',
                    'auto_theft_stolen': 'Auto_Theft_Stolen',
                    'auto_theft_recovered': 'Auto_Theft_Recovered'
                }
            },
            # File 6: Serious Fraud
            'fraud': {
                'pattern': '31_Serious_fraud',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'fraud_cases': 'Fraud_Cases',
                    'fraud_amount': 'Fraud_Amount'
                }
            },
            # File 7: Violent Crime Trials
            'trials': {
                'pattern': '28_Trial_of_violent_crimes_by_courts',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'trials_violent_crimes': 'Trials_of_Violent_Crimes',
                    'convictions_violent': 'Convictions_in_Violent_Crimes',
                    'acquittals_violent': 'Acquittals_in_Violent_Crimes'
                }
            },
            # File 8: Trial Periods
            'trial_periods': {
                'pattern': '29_Period_of_trials_by_courts',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'avg_trial_period_months': 'Average_Period_of_Trial_Months',
                    'pending_trial_cases': 'Pending_Trial_Cases'
                }
            },
            # File 9: Human Rights Violations
            'hr_violations': {
                'pattern': '35_Human_rights_violation_by_police',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'hr_violations_total': 'Human_Rights_Violations_Total',
                    'hr_violations_police': 'Human_Rights_Violations_by_Police'
                }
            },
            # File 10: Police Housing
           'police_housing': {
                'pattern': '36_Police_housing',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'housing_available': 'PH_Hous',
                    'housing_occupied': 'PH_Hous_PH',
                    'sanctioned_strength': 'PH_Sanctioned_Strength'
                }
            },
            # File 11: Kidnapping
            'kidnapping': {
                'pattern': '39_Specific_purpose_of_kidnapping',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'kidnapping_cases': 'Kidnapping_Cases',
                    'kidnapping_ransom': 'Kidnapping_for_Ransom',
                    'kidnapping_marriage': 'Kidnapping_for_Marriage'
                }
            },
            # File 12: Custodial Deaths
            'custodial_deaths': {
                'pattern': '40_01_Custodial_death_person_remanded',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'custodial_deaths_remanded': 'Custodial_Deaths_Remanded',
                    'custodial_deaths_not_remanded': 'Custodial_Deaths_Not_Remanded'
                }
            },
            # File 13: Crimes Against Women
            'crimes_women': {
                'pattern': '42_Cases_under_crime_against_women',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'cases_reported': 'Cases_Reported',
                    'cases_charge_sheeted': 'Cases_Chargesheeted',
                    'cases_convicted': 'Cases_Convicted',
                    'cases_acquitted': 'Cases_Acquitted_or_Discharged',
                    'cases_pending_investigation': 'Cases_Pending_Investigation_at_Year_End',
                    'cases_pending_trial': 'Cases_Pending_Trial_at_Year_End',
                    'cases_false': 'Cases_Declared_False_on_Account_of_Mistake_of_Fact_or_of_Law',
                    'cases_sent_for_trial': 'Cases_Sent_for_Trial',
                    'cases_trials_completed': 'Cases_Trials_Completed'
                }
            },
            # File 14: Arrests Women
            'arrests_women': {
                'pattern': '43_Arrests_under_crime_against_women',
                'key_cols': ['Area_Name', 'Year'],
                'metrics': {
                    'persons_arrested': 'Persons_Arrested',
                    'persons_chargesheeted': 'Persons_Chargesheeted',
                    'persons_convicted': 'Persons_Convicted',
                    'persons_acquitted': 'Persons_Acquitted',
                    'persons_trial_completed': 'Persons_Trial_Completed',
                    'persons_under_trial': 'Total_Persons_under_Trial',
                    'persons_under_trial_beginning': 'Persons_under_Trial_at_Year_beginning',
                    'persons_in_custody_beginning': 'Persons_in_Custody_or_on_Bail_during_Investigation_at_Year_beginning',
                    'persons_in_custody_end': 'Persons_in_Custody_or_on_Bail_during_Investigation_at_Year_end',
                    'persons_in_trial_custody_end': 'Persons_in_Custody_or_on_Bail_during_Trial_at_Year_End',
                    'persons_released_before_trial': 'Persons_Released_or_Freed_by_Police_or_Magistrate_before_Trial_for_want_of_evidence_or_any_other_reason',
                    'persons_compounded_or_withdrawn': 'Persons_against_whom_cases_Compounded_or_Withdrawn'
                }
            }
        }
        
        loaded_count = 0
        for name, config in dataset_configs.items():
            data = self._find_and_load(config['pattern'], config['key_cols'], config['metrics'])
            if data:
                self.datasets[name] = data
                loaded_count += 1
                print(f"[OK] Loaded {name}: {len(data)} rows")
        
        # Build fast lookup index
        self._build_index()
        return loaded_count
    
    def _find_and_load(self, filename_pattern, key_cols, metrics):
        """Find CSV file by partial name match and load it"""
        for base in self.base_paths:
            if not os.path.exists(base):
                continue
            
            # Search for files matching pattern
            for fname in os.listdir(base):
                if filename_pattern.lower() in fname.lower() and fname.endswith('.csv'):
                    filepath = os.path.join(base, fname)
                    try:
                        return self._clean_csv(filepath, key_cols, metrics)
                    except Exception as e:
                        print(f"[WARN] Failed to load {fname}: {e}")
                        continue
            
            # Also check subdirectories
            for root, dirs, files in os.walk(base):
                for fname in files:
                    if filename_pattern.lower() in fname.lower() and fname.endswith('.csv'):
                        filepath = os.path.join(root, fname)
                        try:
                            return self._clean_csv(filepath, key_cols, metrics)
                        except Exception as e:
                            print(f"[WARN] Failed to load {fname}: {e}")
                            continue
        
        print(f"[MISSING] Could not find file matching '{filename_pattern}'")
        return None
    
    def _clean_csv(self, filepath, key_cols, metrics):
        """Clean a single CSV file"""
        rows = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean column names
                clean_row = {}
                for k, v in row.items():
                    if k is None:
                        continue

                    clean_key = str(k).strip().replace('\ufeff', '').replace('\xef\xbb\xbf', '')                    
                    clean_row[clean_key] = v
                                    
                # Ensure key columns exist
                if not all(k in clean_row for k in key_cols):
                    continue
                
                # Convert numeric columns
                for col in list(clean_row.keys()):
                    if col not in ('Area_Name', 'Sub_group', 'Group_Name'):
                        try:
                            clean_row[col] = int(clean_row[col]) if clean_row[col] else 0
                        except (ValueError, TypeError):
                            try:
                                clean_row[col] = float(clean_row[col]) if clean_row[col] else 0.0
                            except (ValueError, TypeError):
                                pass
                
                # Standardize state name
                clean_row['Area_Name'] = str(clean_row.get('Area_Name', '')).strip()
                clean_row['state_key'] = clean_row['Area_Name'].lower().replace('-', ' ').replace('_', ' ')
                clean_row['Year'] = int(clean_row.get('Year', 0))
                
                rows.append(clean_row)
        
        return rows
    
    def _build_index(self):
        """Build fast lookup index: state -> year -> dataset -> metrics"""
        for dataset_name, rows in self.datasets.items():
            for row in rows:
                state = row.get('state_key', '')
                year = row.get('Year', 0)
                
                if not state or not year:
                    continue
                
                if state not in self.state_year_index:
                    self.state_year_index[state] = {}
                if year not in self.state_year_index[state]:
                    self.state_year_index[state][year] = {}
                
                self.state_year_index[state][year][dataset_name] = row
    
    # =========================================================================
    # STATE LOOKUP
    # =========================================================================
    
    def _find_state_data(self, state_name, year=None):
        """Find all data for a state (optionally filtered by year)"""
        search_key = state_name.lower().replace('-', ' ').replace('_', ' ')
        
        # Try exact match
        if search_key in self.state_year_index:
            data = self.state_year_index[search_key]
            if year:
                return data.get(year, None)
            return data
        
        # Try partial match
        for state_key in self.state_year_index:
            if search_key in state_key or state_key in search_key:
                data = self.state_year_index[state_key]
                if year:
                    return data.get(year, None)
                return data
        
        return None
    
    def get_state_name(self, search_key):
        """Get canonical state name from search key"""
        for state_key in self.state_year_index:
            if search_key in state_key or state_key in search_key:
                # Return the first year entry's Area_Name
                first_year = list(self.state_year_index[state_key].keys())[0]
                return self.state_year_index[state_key][first_year].get('complaints', {}).get('Area_Name', search_key)
        return search_key.title()
    
    # =========================================================================
    # COMPOSITE RISK SCORE (6 DIMENSIONS)
    # =========================================================================
    
    def compute_composite_risk(self, state_name, year=None):
        """
        Compute 6-Dimension Composite Risk Score
        Combines ALL available datasets into a unified 0-100 score
        """
        data = self._find_state_data(state_name, year)
        if not data:
            return None
        
        # Get most recent year if not specified
        if not year:
            year = max(data.keys())
        
        year_data = data.get(year, {})
        if not year_data:
            return None
        
        # Extract metrics from all available datasets
        m = {}  # unified metrics dict
        
        # From complaints dataset
        if 'complaints' in year_data:
            c = year_data['complaints']
            m['complaints_received'] = c.get('CPA_-_Complaints_Received/Alleged', 0) or 0
            m['cases_registered'] = c.get('CPA_-_Cases_Registered', 0) or 0
            m['disciplinary'] = c.get('CPC_-_Police_Personnel_Disciplinary_Action_Initiated', 0) or 0
            m['dismissals'] = c.get('CPC_-_Police_Personnel_Dismissal/Removal_from_Service', 0) or 0
            m['convictions'] = c.get('CPB_-_Police_Personnel_Convicted', 0) or 0
            m['trials'] = c.get('CPB_-_Police_Personnel_Trial_Completed', 0) or 0
            m['false_cases'] = c.get('CPA_-_Complaints/Cases_Declared_False/Unsubstantiated', 0) or 0
            m['dept_enquiries'] = c.get('CPA_-_No_of_Departmental_Enquiries', 0) or 0
            m['mag_enquiries'] = c.get('CPA_-_No_of_Magisterial_Enquiries', 0) or 0
        else:
            m.update({k: 0 for k in ['complaints_received', 'cases_registered', 'disciplinary', 
                                      'dismissals', 'convictions', 'trials', 'false_cases', 
                                      'dept_enquiries', 'mag_enquiries']})
        
        # From rape victims
        if 'rape_victims' in year_data:
            r = year_data['rape_victims']
            m['rape_victims'] = r.get('Victims_of_Rape_Total', 0) or 0
        else:
            m['rape_victims'] = 0

        if 'police_housing' in year_data:
            ph = year_data['police_housing']
            m['housing_available'] = ph.get('PH_Hous', 0) or 0
            m['housing_occupied'] = ph.get('PH_Hous_PH', 0) or 0
            m['sanctioned_strength'] = ph.get('PH_Sanctioned_Strength', 0) or 0
        else:
            m['housing_available'] = 0
            m['housing_occupied'] = 0
            m['sanctioned_strength'] = 0
        
        # From murder
        if 'murder' in year_data:
            mu = year_data['murder']
            m['murder_victims'] = mu.get('Murder_victims_Total', 0) or 0
        else:
            m['murder_victims'] = 0
        
        # From auto theft
        if 'auto_theft' in year_data:
            at = year_data['auto_theft']
            # FIXED: Your CSV column is Auto_Theft_Stolen, not Auto_Theft_Cases
            m['auto_theft_cases'] = at.get('Auto_Theft_Stolen', 0) or 0
        else:
            m['auto_theft_cases'] = 0
        
        # From fraud
        if 'fraud' in year_data:
            f = year_data['fraud']
            m['fraud_cases'] = f.get('Fraud_Cases', 0) or 0
        else:
            m['fraud_cases'] = 0
        
        # From kidnapping
        if 'kidnapping' in year_data:
            k = year_data['kidnapping']
            m['kidnapping_cases'] = k.get('Kidnapping_Cases', 0) or 0
        else:
            m['kidnapping_cases'] = 0
        
        # From crimes against women
        if 'crimes_women' in year_data:
            cw = year_data['crimes_women']
            m['crimes_women_total'] = cw.get('Cases_Reported', 0) or 0
            m['women_convicted'] = cw.get('Cases_Convicted', 0) or 0
            m['women_pending'] = cw.get('Cases_Pending_Trial_at_Year_End', 0) or 0
        else:
            m['crimes_women_total'] = 0
            m['women_convicted'] = 0
            m['women_pending'] = 0

        if 'arrests_women' in year_data:
            aw = year_data['arrests_women']

            m['women_arrested'] = aw.get('Persons_Arrested', 0) or 0
            m['women_convicted_persons'] = aw.get('Persons_Convicted', 0) or 0
            m['women_chargesheeted'] = aw.get('Persons_Chargesheeted', 0) or 0
        else:
            m['women_arrested'] = 0
            m['women_convicted_persons'] = 0
            m['women_chargesheeted'] = 0

        # From HR violations
        if 'hr_violations' in year_data:
            hr = year_data['hr_violations']
            m['hr_violations'] = hr.get('Human_Rights_Violations_Total', 0) or 0
        else:
            m['hr_violations'] = 0
        
        # From custodial deaths
        if 'custodial_deaths' in year_data:
            cd = year_data['custodial_deaths']
            m['custodial_deaths'] = cd.get('Custodial_Deaths_Remanded', 0) or 0
        else:
            m['custodial_deaths'] = 0
        
        # From trial periods
        if 'trial_periods' in year_data:
            tp = year_data['trial_periods']
            m['avg_trial_months'] = tp.get('Average_Period_of_Trial_Months', 0) or 0
            m['pending_trials'] = tp.get('Pending_Trial_Cases', 0) or 0
        else:
            m['avg_trial_months'] = 0
            m['pending_trials'] = 0
        
        # === COMPOSITE RISK FORMULA (6 Dimensions) ===
        # Each dimension has max score, total max = 100
        
        # D1: Police Complaint Volume (20%)
        d1 = min(20, (m['complaints_received'] + m['cases_registered'] * 2) / 500)
        
        # D2: Violent Crime Severity (20%)
        # Murder + Rape + Kidnapping + Dowry deaths
        ##d2 = min(20, (m['murder_victims'] + m['rape_victims'] + m['kidnapping_cases'] + m['dowry_deaths']) / 200)
        d2=0
        # D3: Property & Economic Crime (15%)
        # Auto theft + Fraud
        d3 = min(15, (m['auto_theft_cases'] + m['fraud_cases']) / 300)
        
        # D4: Police Accountability (15%)
        # Disciplinary + HR violations + Custodial deaths
        housing_gap = max(
            0,
            m['sanctioned_strength'] - m['housing_available']
        )

        d4 = min(
            15,
            (
                m['disciplinary']
                + m['dismissals'] * 3
                + m['hr_violations']
                + m['custodial_deaths'] * 5
                + housing_gap / 100
            ) / 300
        )        
        # D5: Judicial Efficiency (15%)
        # Convictions - but also penalize long trial periods
        trial_penalty = min(10, m['avg_trial_months'] / 12) if m['avg_trial_months'] > 24 else 0
        d5 = min(15, (m['convictions'] * 2 + m['trials']) / 100) - trial_penalty
        d5 = max(0, d5)
        
        # D6: System Backlog & Women's Safety (15%)
        # Pending trials + Crimes against women
        d6 = min(15,(m['pending_trials']+ m['crimes_women_total']+ m['women_arrested']- m['women_convicted_persons']) / 500)        
        total_score = round(d1 + d2 + d3 + d4 + d5 + d6, 2)
        
        # Risk level
        if total_score >= 70: risk_level = "CRITICAL"
        elif total_score >= 50: risk_level = "HIGH"
        elif total_score >= 30: risk_level = "MEDIUM"
        else: risk_level = "LOW"
        
        # Trend direction
        all_years = sorted(data.keys())
        if len(all_years) >= 2:
            mid = len(all_years) // 2
            first_risks = []
            second_risks = []
            for i, yr in enumerate(all_years):
                # Compute simplified risk for trend
                yd = data[yr]
                yc = yd.get('complaints', {})
                y_complaints = yc.get('CPA_-_Complaints_Received/Alleged', 0) or 0
                y_cases = yc.get('CPA_-_Cases_Registered', 0) or 0
                y_disc = yc.get('CPC_-_Police_Personnel_Disciplinary_Action_Initiated', 0) or 0
                yr_score = min(100, (y_complaints + y_cases * 2 + y_disc * 1.5) / 250)
                
                if i < mid:
                    first_risks.append(yr_score)
                else:
                    second_risks.append(yr_score)
            
            avg_first = sum(first_risks) / len(first_risks) if first_risks else 0
            avg_second = sum(second_risks) / len(second_risks) if second_risks else 0
            diff = avg_second - avg_first
            
            if diff > 5: trend = "INCREASING"
            elif diff < -5: trend = "DECREASING"
            else: trend = "STABLE"
        else:
            trend = "STABLE"
        
        return {
            'state': self.get_state_name(state_name.lower()),
            'year': int(year),
            'composite_risk_score': total_score,
            'risk_level': risk_level,
            'trend_direction': trend,
            'datasets_available': len(year_data),
            'dimensions': {
                'complaint_volume': round(d1, 2),
                'violent_crime_severity': round(d2, 2),
                'property_economic_crime': round(d3, 2),
                'police_accountability': round(d4, 2),
                'judicial_efficiency': round(d5, 2),
                'system_backlog_women_safety': round(d6, 2)
            },
            'raw_metrics': {k: int(v) if isinstance(v, (int, float)) else v for k, v in m.items()}
        }
    
    # =========================================================================
    # TREND DATA
    # =========================================================================
    
    def get_trend_data(self, state_name):
        """Get year-by-year trend for all dimensions"""
        data = self._find_state_data(state_name)
        if not data:
            return None
        
        trends = []
        for year in sorted(data.keys()):
            result = self.compute_composite_risk(state_name, year)
            if result:
                trends.append({
                    'year': result['year'],
                    'risk_score': result['composite_risk_score'],
                    'risk_level': result['risk_level'],
                    'complaint_volume': result['dimensions']['complaint_volume'],
                    'violent_crime': result['dimensions']['violent_crime_severity'],
                    'property_crime': result['dimensions']['property_economic_crime'],
                    'accountability': result['dimensions']['police_accountability'],
                    'judicial': result['dimensions']['judicial_efficiency'],
                    'backlog': result['dimensions']['system_backlog_women_safety']
                })
        
        return trends
    
    # =========================================================================
    # CRIME TYPE BREAKDOWN
    # =========================================================================
    
    def get_crime_breakdown(self, state_name, year=None):
        """Get breakdown of crime types for a state"""
        data = self._find_state_data(state_name, year)
        if not data:
            return None
        
        if not year:
            year = max(data.keys())
        
        year_data = data.get(year, {})
        
        breakdown = {
            'state': self.get_state_name(state_name.lower()),
            'year': int(year),
            'categories': []
        }
        
        # Violent crimes
        violent_total = 0
        if 'murder' in year_data:
            violent_total += year_data['murder'].get('Murder_victims_Total', 0) or 0
        if 'rape_victims' in year_data:
            violent_total += year_data['rape_victims'].get('Victims_of_Rape_Total', 0) or 0
        if 'kidnapping' in year_data:
            violent_total += year_data['kidnapping'].get('Kidnapping_Cases', 0) or 0
        
        breakdown['categories'].append({
            'name': 'Violent Crimes',
            'count': int(violent_total),
            'subtypes': ['Murder', 'Rape', 'Kidnapping']
        })
        
        # Property crimes - FIXED for your actual CSV columns
        property_total = 0
        if 'auto_theft' in year_data:
            # Your CSV has: Auto_Theft_Coordinated/Traced, Auto_Theft_Recovered, Auto_Theft_Stolen
            # No "Auto_Theft_Cases" column exists, so use Auto_Theft_Stolen as the case count
            property_total += year_data['auto_theft'].get('Auto_Theft_Stolen', 0) or 0
        if 'fraud' in year_data:
            property_total += year_data['fraud'].get('Fraud_Cases', 0) or 0
        
        breakdown['categories'].append({
            'name': 'Property & Economic',
            'count': int(property_total),
            'subtypes': ['Auto Theft', 'Fraud']
        })
        
        # Crimes against women
        women_total =0
        if 'crimes_women' in year_data:
            women_total += year_data['crimes_women'].get('Cases_Crime_Against_Women_Total', 0) or 0
        
        breakdown['categories'].append({
            'name': 'Crimes Against Women',
            'count': int(women_total),
            'subtypes': ['Rape', 'Dowry Death', 'Cruelty by Husband']
        })
        
        # Police misconduct
        police_total = 0
        if 'complaints' in year_data:
            police_total += year_data['complaints'].get('CPA_-_Complaints_Received/Alleged', 0) or 0
        if 'hr_violations' in year_data:
            police_total += year_data['hr_violations'].get('Human_Rights_Violations_Total', 0) or 0
        
        breakdown['categories'].append({
            'name': 'Police & System',
            'count': int(police_total),
            'subtypes': ['Complaints', 'HR Violations', 'Custodial Deaths']
        })
        
        return breakdown
    
    # =========================================================================
    # STATE LISTS & RANKINGS
    # =========================================================================
    
    def get_all_states(self):
        """Get all unique states"""
        states = set()
        for dataset in self.datasets.values():
            for row in dataset:
                if row.get('Area_Name'):
                    states.add(row['Area_Name'])
        return sorted(list(states))
    
    def get_top_risky(self, limit=10):
        """Get top N most risky states"""
        states = self.get_all_states()
        results = []
        
        for state in states:
            # Get latest year risk
            data = self._find_state_data(state)
            if not data:
                continue
            
            latest_year = max(data.keys())
            risk = self.compute_composite_risk(state, latest_year)
            if not risk:
                continue
            
            # Get average across all years
            all_risks = []
            for year in data.keys():
                yr_risk = self.compute_composite_risk(state, year)
                if yr_risk:
                    all_risks.append(yr_risk['composite_risk_score'])
            
            avg_risk = round(sum(all_risks) / len(all_risks), 2) if all_risks else 0
            
            results.append({
                'state': state,
                'latest_risk': risk['composite_risk_score'],
                'latest_year': risk['year'],
                'average_risk': avg_risk,
                'risk_level': risk['risk_level'],
                'trend_direction': risk['trend_direction'],
                'datasets_available': risk['datasets_available']
            })
        
        results.sort(key=lambda x: x['average_risk'], reverse=True)
        return results[:limit]


# =============================================================================
# FLASK API ROUTES
# =============================================================================

processor = SurakshaAIDataProcessor()
loaded = processor.load_all_datasets()
print(f"\n[INIT] Loaded {loaded} datasets")

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({
        'message': 'SurakshaAI Complete Unified Processor is live!',
        'version': '3.0-multi-dataset',
        'datasets_loaded': loaded,
        'total_states': len(processor.get_all_states()),
        'endpoints': [
            '/risk/<state>',
            '/trends/<state>',
            '/breakdown/<state>',
            '/states',
            '/top-risky?limit=N',
            '/compare?states=A,B'
        ]
    }), 200

@app.route('/risk/<state_name>', methods=['GET'])
def get_risk(state_name):
    year = request.args.get('year', type=int)
    result = processor.compute_composite_risk(state_name, year)
    if not result:
        return jsonify({'error': f'State "{state_name}" not found or no data'}), 404
    return jsonify(result), 200

@app.route('/trends/<state_name>', methods=['GET'])
def get_trends(state_name):
    trends = processor.get_trend_data(state_name)
    if not trends:
        return jsonify({'error': f'State "{state_name}" not found'}), 404
    return jsonify({
        'state': processor.get_state_name(state_name.lower()),
        'trends': trends
    }), 200

@app.route('/breakdown/<state_name>', methods=['GET'])
def get_breakdown(state_name):
    year = request.args.get('year', type=int)
    result = processor.get_crime_breakdown(state_name, year)
    if not result:
        return jsonify({'error': f'State "{state_name}" not found'}), 404
    return jsonify(result), 200

@app.route('/states', methods=['GET'])
def get_states():
    states = processor.get_all_states()
    return jsonify({'count': len(states), 'states': states}), 200

@app.route('/top-risky', methods=['GET'])
def top_risky():
    limit = request.args.get('limit', 10, type=int)
    top = processor.get_top_risky(limit)
    return jsonify({'top_risky_states': top}), 200

@app.route('/compare', methods=['GET'])
def compare_states():
    states_param = request.args.get('states', '')
    if not states_param:
        return jsonify({'error': 'Use ?states=Delhi,Maharashtra'}), 400
    
    results = []
    for name in [s.strip() for s in states_param.split(',')]:
        risk = processor.compute_composite_risk(name)
        if risk:
            results.append({
                'state': risk['state'],
                'risk_score': risk['composite_risk_score'],
                'risk_level': risk['risk_level'],
                'year': risk['year'],
                'trend': risk['trend_direction']
            })
    
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return jsonify({'ranking': results}), 200

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True)