


import sys
import os
import argparse
from urllib.parse import urlparse, parse_qs

# =============================================================================
# AUTO-FIND main.py in parent directories
# =============================================================================
def find_main_py():
    """Search for main.py in current and parent directories"""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        main_path = os.path.join(current, 'main.py')
        if os.path.exists(main_path):
            if current not in sys.path:
                sys.path.insert(0, current)
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None

main_dir = find_main_py()
if not main_dir:
    print("[ERROR] Cannot find main.py. Searched up 5 parent directories.")
    print("[INFO] Ensure main.py is in the project root or same folder.")
    sys.exit(1)

try:
    from main import SurakshaAIDataProcessor
except ImportError as e:
    print(f"[ERROR] Cannot import SurakshaAIDataProcessor from {main_dir}/main.py: {e}")
    sys.exit(1)


class SurakshaCLIReport:
    """Generates formatted CLI reports from SurakshaAI data processor"""

    REPORT_WIDTH = 61
    DATASET_YEAR_RANGE = (2001, 2014)

    # Column name variants to try for each metric
    # Order matters: first match wins
    COLUMN_VARIANTS = {
        # 1. Police Complaints
        'complaints_received': ['CPA_-_Complaints_Received/Alleged', 'CPA - Complaints Received/Alleged',
                                 'Complaints_Received', 'Complaints Received', 'CPA_-_Complaints_Received'],
        'cases_registered': ['CPA_-_Cases_Registered', 'CPA - Cases Registered', 'Cases_Registered', 'Cases Registered'],

        # 2. Rape Victims
        'rape_victims_total': ['Victims_of_Rape_Total'],
        'rape_victims_below_18': ['Victims_Upto_10_Yrs','Victims_Between_10-14_Yrs','Victims_Between_14-18_Yrs'],

        # 3. Property Stolen
        'property_stolen_value': ['Property_Stolen_Value', 'Property Stolen Value', 'Value_of_Property_Stolen',
                                  'Stolen_Value', 'Stolen Value', 'Property_Stolen'],
        'property_recovered_value': ['Property_Recovered_Value', 'Property Recovered Value', 'Value_of_Property_Recovered',
                                     'Recovered_Value', 'Recovered Value', 'Property_Recovered'],

        # 4. Murder
        'murder_victims_total': [
            'Victims_Total'
        ],

        'victims_above50': [
            'Victims_Above_50_Yrs'
        ],

        'victims_upto10': [
            'Victims_Upto_10_Yrs'
        ],

        'victims_10_15': [
            'Victims_Upto_10_15_Yrs'
        ],

        'victims_15_18': [
            'Victims_Upto_15_18_Yrs'
        ],

        'victims_18_30': [
            'Victims_Upto_18_30_Yrs'
        ],

        'victims_30_50': [
            'Victims_Upto_30_50_Yrs'
        ],

        # 5. Auto Theft
        'auto_theft_cases': ['Auto_Theft_Stolen', 'Auto Theft Stolen', 'Auto_Theft_Cases', 'Auto Theft Cases',
                             'Stolen', 'Cases', 'Auto_Theft_Coordinated/Traced', 'Auto Theft Coordinated/Traced'],
        'auto_theft_recovered': ['Auto_Theft_Recovered', 'Auto Theft Recovered', 'Recovered'],

        # 6. Serious Fraud
        'fraud_cases': [
            'Loss_of_Property_1_10_Crores',
            'Loss_of_Property_10_25_Crores',
            'Loss_of_Property_25_50_Crores',
            'Loss_of_Property_50_100_Crores',
            'Loss_of_Property_Above_100_Crores'
        ],
        # 7. Violent Crime Trials
        'convictions_violent': ['Convictions_in_Violent_Crimes', 'Convictions in Violent Crimes', 'Convictions',
                                'Violent_Crime_Convictions', 'Violent Crime Convictions'],
        'acquittals_violent': ['Acquittals_in_Violent_Crimes', 'Acquittals in Violent Crimes', 'Acquittals',
                               'Violent_Crime_Acquittals', 'Violent Crime Acquittals'],

        # 8. Trial Periods
        'trial_confession': [
            'Trial_of_Violent_Crimes_by_Courts_By_Confession'
        ],

        'trial_regular': [
            'Trial_of_Violent_Crimes_by_Courts_By_trial'
        ],

        'trial_total': [
            'Trial_of_Violent_Crimes_by_Courts_Total'
        ],

        # 9. Human Rights
        'hr_violations_total': ['Human_Rights_Violations_Total', 'Human Rights Violations Total',
                                'HR_Violations_Total', 'HR Violations Total', 'Total_Violations', 'Total Violations'],
        'hr_violations_police': ['Human_Rights_Violations_by_Police', 'Human Rights Violations by Police',
                                 'HR_Violations_by_Police', 'HR Violations by Police', 'Police_Violations', 'Police Violations'],

        # 10. Police Housing
        'housing_available': ['PH_Hous', 'Housing_Available', 'Housing Available', 'Available',
                              'PH_Housing', 'PH Housing', 'Housing'],
        'sanctioned_strength': ['PH_Sanctioned_Strength', 'Sanctioned_Strength', 'Sanctioned Strength',
                                'Sanctioned', 'Total_Strength', 'Total Strength'],

        # 11. Kidnapping
        'kidnapping_cases': ['Kidnapping_Cases', 'Kidnapping Cases', 'Cases', 'Kidnapping_Total', 'Kidnapping Total'],
        'kidnapping_ransom': ['Kidnapping_for_Ransom', 'Kidnapping for Ransom', 'For_Ransom', 'For Ransom', 'Ransom'],

        # 12. Custodial Deaths
        'custodial_deaths_remanded': ['Custodial_Deaths_Remanded', 'Custodial Deaths Remanded', 'Remanded',
                                      'Deaths_Remanded', 'Deaths Remanded'],
        'custodial_deaths_not_remanded': ['Custodial_Deaths_Not_Remanded', 'Custodial Deaths Not Remanded',
                                          'Not_Remanded', 'Not Remanded'],

        # 13. Crimes Against Women
        'women_reported': ['Cases_Reported', 'Cases Reported', 'Reported', 'Total_Cases', 'Total Cases'],
        'women_convicted': ['Cases_Convicted', 'Cases Convicted', 'Convicted'],

        # 14. Arrests Against Women
        'women_arrested': ['Persons_Arrested', 'Persons Arrested', 'Arrested', 'Total_Arrested', 'Total Arrested'],
        'women_convicted_persons': ['Persons_Convicted', 'Persons Convicted', 'Convicted'],
    }

    def __init__(self):
        self.processor = SurakshaAIDataProcessor()
        print("[INIT] Loading datasets...")
        loaded = self.processor.load_all_datasets()
        print(f"[INIT] Loaded {loaded} datasets")
        print(f"[INIT] Total states available: {len(self.processor.get_all_states())}")
        print()

    def _line(self, char="="):
        return char * self.REPORT_WIDTH

    def _separator(self):
        return "-" * self.REPORT_WIDTH

    def _format_kv(self, key, value, width=25):
        key_str = f"{key:<{width}}"
        return f"{key_str}: {value}"

    def _format_rupee(self, amount):
        if amount == 0:
            return "₹0"
        s = str(int(amount))
        if len(s) > 3:
            last3 = s[-3:]
            rest = s[:-3]
            groups = []
            while rest:
                groups.append(rest[-2:])
                rest = rest[:-2]
            formatted = ",".join(reversed(groups)) + "," + last3 if groups else last3
        else:
            formatted = s
        return f"₹{formatted}"

    def _get_col(self, row, variants):
        """Try multiple column name variants, return first match value or 0"""
        if not row:
            return 0
        for col in variants:
            if col in row:
                val = row[col]
                if val is not None and val != '':
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return 0
        return 0

    def _get_dataset_rows(self, dataset_name, state_name, year):
        """Get all rows from a dataset matching state and year"""
        if dataset_name not in self.processor.datasets:
            return []
        rows = []
        search_key = state_name.lower().replace('-', ' ').replace('_', ' ')
        for row in self.processor.datasets[dataset_name]:
            row_state = str(row.get('Area_Name', '')).strip().lower().replace('-', ' ').replace('_', ' ')
            row_year = row.get('Year', 0)
            if (search_key == row_state or search_key in row_state or row_state in search_key) and row_year == year:
                rows.append(row)
        return rows

    def _sum_metric(self, dataset_name, state_name, year, metric_key):
        """Sum a metric across all matching rows in a dataset"""
        rows = self._get_dataset_rows(dataset_name, state_name, year)
        variants = self.COLUMN_VARIANTS.get(metric_key, [metric_key])
        total = 0
        for row in rows:
            total += self._get_col(row, variants)
        return int(total)

    def _get_single_metric(self, dataset_name, state_name, year, metric_key):
        """Get first non-zero metric from matching rows"""
        rows = self._get_dataset_rows(dataset_name, state_name, year)
        variants = self.COLUMN_VARIANTS.get(metric_key, [metric_key])
        for row in rows:
            val = self._get_col(row, variants)
            if val != 0:
                return val
        return 0

    def _validate_year(self, year, available_years):
        if year is not None and year not in available_years:
            lo, hi = min(available_years), max(available_years)
            print(f"[WARN] Year {year} not found. Dataset range: {lo}-{hi}.")
            print(f"[INFO] Auto-selecting latest year: {hi}")
            return hi
        return year if year is not None else max(available_years)

    def _get_available_years(self, state_name):
        """Get all years available for a state across all datasets"""
        years = set()
        search_key = state_name.lower().replace('-', ' ').replace('_', ' ')
        for dataset_name, rows in self.processor.datasets.items():
            for row in rows:
                row_state = str(row.get('Area_Name', '')).strip().lower().replace('-', ' ').replace('_', ' ')
                if search_key == row_state or search_key in row_state or row_state in search_key:
                    years.add(row.get('Year', 0))
        return sorted(years)

    def generate_report(self, state_name, year=None):
        # Get available years
        available_years = self._get_available_years(state_name)
        if not available_years:
            print(f"[ERROR] State '{state_name}' not found in any dataset.")
            print(f"[INFO] Use --list-states to see available states.")
            return None

        year = self._validate_year(year, available_years)

        # Compute composite risk (don't pass year to avoid main.py bug)
        try:
            risk_data = self.processor.compute_composite_risk(state_name)
        except Exception as e:
            print(f"[WARN] Composite risk error: {e}")
            risk_data = None

        lines = []
        lines.append(self._line("="))
        lines.append("SURAKSHA AI REPORT")
        lines.append(self._line("="))
        lines.append("")

        # State name resolution
        canonical_state = state_name.title()
        if risk_data:
            canonical_state = risk_data.get('state', canonical_state)

        lines.append(self._format_kv("State", canonical_state))
        lines.append(self._format_kv("Year", year))
        lines.append("")

        if risk_data:
            lines.append(self._format_kv("Composite Risk", f"{risk_data['composite_risk_score']} /100"))
            lines.append(self._format_kv("Risk Level", risk_data['risk_level']))
            lines.append(self._format_kv("Trend", risk_data['trend_direction']))
        else:
            lines.append(self._format_kv("Composite Risk", "N/A"))
            lines.append(self._format_kv("Risk Level", "N/A"))
            lines.append(self._format_kv("Trend", "N/A"))
        lines.append("")

        # 1. Police Complaints
        lines.append(self._separator())
        lines.append("1. Police Complaints")
        lines.append(self._separator())
        comp_received = self._sum_metric('complaints', state_name, year, 'complaints_received')
        cases_reg = self._sum_metric('complaints', state_name, year, 'cases_registered')
        lines.append(self._format_kv("Complaints Received", f"{comp_received:,}"))
        lines.append(self._format_kv("Cases Registered", f"{cases_reg:,}"))
        lines.append("")

        # 2. Rape Victims
        lines.append(self._separator())
        lines.append("2. Rape Victims")
        lines.append(self._separator())
        rape_total = self._sum_metric('rape_victims', state_name, year, 'rape_victims_total')
        rows = self._get_dataset_rows('rape_victims', state_name, year)
        rape_below18 = 0
        for row in rows:
            rape_below18 += (
                row.get('Victims_Upto_10_Yrs',0)
                + row.get('Victims_Between_10-14_Yrs',0)
                + row.get('Victims_Between_14-18_Yrs',0)
    )
        lines.append(self._format_kv("Total Victims", f"{rape_total:,}"))
        lines.append(self._format_kv("Victims Below 18", f"{rape_below18:,}"))
        lines.append("")

        # 3. Property Crime
        lines.append(self._separator())
        lines.append("3. Property Crime")
        lines.append(self._separator())
        stolen = self._sum_metric('property_stolen', state_name, year, 'property_stolen_value')
        recovered = self._sum_metric('property_stolen', state_name, year, 'property_recovered_value')
        lines.append(self._format_kv("Property Stolen", self._format_rupee(stolen)))
        lines.append(self._format_kv("Recovered", self._format_rupee(recovered)))
        lines.append("")

        # 4. Murder
        lines.append(self._separator())
        lines.append("4. Murder")
        lines.append(self._separator())
        murder_total = self._sum_metric('murder', state_name, year, 'murder_victims_total')
        murder_above50 = self._sum_metric('murder',state_name,year,'victims_above50')
        lines.append(self._format_kv("Total Victims", f"{murder_total:,}"))
        lines.append(self._format_kv("Victims Above 50", f"{murder_above50:,}"))
        lines.append("")

        # 5. Auto Theft
        lines.append(self._separator())
        lines.append("5. Auto Theft")
        lines.append(self._separator())
        auto_cases = self._sum_metric('auto_theft', state_name, year, 'auto_theft_cases')
        auto_recovered = self._sum_metric('auto_theft', state_name, year, 'auto_theft_recovered')
        lines.append(self._format_kv("Cases", f"{auto_cases:,}"))
        lines.append(self._format_kv("Recovered", f"{auto_recovered:,}"))
        lines.append("")

        # 6. Serious Fraud
        lines.append(self._separator())
        lines.append("6. Serious Fraud")
        lines.append(self._separator())
        fraud_cases = self._sum_metric('fraud', state_name, year, 'fraud_cases')
        fraud_amt = self._sum_metric('fraud', state_name, year, 'fraud_amount')
        lines.append(self._format_kv("Fraud Cases", f"{fraud_cases:,}"))
        lines.append(self._format_kv("Fraud Amount", self._format_rupee(fraud_amt)))
        lines.append("")

        # 7. Violent Crime Trials
        lines.append(self._separator())
        lines.append("7. Violent Crime Trials")
        lines.append(self._separator())

        by_confession = self._sum_metric('trials', state_name, year, 'trial_confession')

        by_trial = self._sum_metric(
            'trials',
            state_name,
            year,
            'trial_regular'
        )

        total_trials = self._sum_metric(
            'trials',
            state_name,
            year,
            'trial_total'
        )

        lines.append(self._format_kv("By Confession", f"{by_confession:,}"))
        lines.append(self._format_kv("By Trial", f"{by_trial:,}"))
        lines.append(self._format_kv("Total Trials", f"{total_trials:,}"))
        lines.append("")

        # 8. Trial Period
        lines.append(self._separator())
        lines.append("8. Trial Period")
        lines.append(self._separator())
        pending = self._sum_metric('trial_periods', state_name, year, 'pending_trials')
        avg_months = self._get_single_metric('trial_periods', state_name, year, 'avg_trial_months')
        lines.append(self._format_kv("Pending Trials", f"{pending:,}"))
        lines.append(self._format_kv("Average Trial", f"{avg_months} Months"))
        lines.append("")

        # 9. Human Rights
        lines.append(self._separator())
        lines.append("9. Human Rights")
        lines.append(self._separator())
        hr_total = self._sum_metric('hr_violations', state_name, year, 'hr_violations_total')
        hr_police = self._sum_metric('hr_violations', state_name, year, 'hr_violations_police')
        lines.append(self._format_kv("Violations", f"{hr_total:,}"))
        lines.append(self._format_kv("Police Violations", f"{hr_police:,}"))
        lines.append("")

        # 10. Police Housing
        lines.append(self._separator())
        lines.append("10. Police Housing")
        lines.append(self._separator())
        housing_avail = self._sum_metric('police_housing', state_name, year, 'housing_available')
        sanctioned = self._sum_metric('police_housing', state_name, year, 'sanctioned_strength')
        lines.append(self._format_kv("Housing Available", f"{housing_avail:,}"))
        lines.append(self._format_kv("Sanctioned Strength", f"{sanctioned:,}"))
        lines.append("")

        # 11. Kidnapping
        lines.append(self._separator())
        lines.append("11. Kidnapping")
        lines.append(self._separator())
        kidnap_cases = self._sum_metric('kidnapping', state_name, year, 'kidnapping_cases')
        kidnap_ransom = self._sum_metric('kidnapping', state_name, year, 'kidnapping_ransom')
        lines.append(self._format_kv("Cases", f"{kidnap_cases:,}"))
        lines.append(self._format_kv("For Ransom", f"{kidnap_ransom:,}"))
        lines.append("")

        # 12. Custodial Deaths
        lines.append(self._separator())
        lines.append("12. Custodial Deaths")
        lines.append(self._separator())
        remand_deaths = self._sum_metric('custodial_deaths', state_name, year, 'custodial_deaths_remanded')
        not_remand = self._sum_metric('custodial_deaths', state_name, year, 'custodial_deaths_not_remanded')
        total_deaths = remand_deaths + not_remand
        lines.append(self._format_kv("Deaths", f"{total_deaths:,}"))
        lines.append(self._format_kv("Remand Deaths", f"{remand_deaths:,}"))
        lines.append("")

        # 13. Crimes Against Women
        lines.append(self._separator())
        lines.append("13. Crimes Against Women")
        lines.append(self._separator())
        women_reported = self._sum_metric('crimes_women', state_name, year, 'women_reported')
        women_convicted = self._sum_metric('crimes_women', state_name, year, 'women_convicted')
        lines.append(self._format_kv("Reported", f"{women_reported:,}"))
        lines.append(self._format_kv("Convicted", f"{women_convicted:,}"))
        lines.append("")

        # 14. Arrests Against Women
        lines.append(self._separator())
        lines.append("14. Arrests Against Women")
        lines.append(self._separator())
        persons_arrested = self._sum_metric('arrests_women', state_name, year, 'women_arrested')
        persons_convicted = self._sum_metric('arrests_women', state_name, year, 'women_convicted_persons')
        lines.append(self._format_kv("Persons Arrested", f"{persons_arrested:,}"))
        lines.append(self._format_kv("Persons Convicted", f"{persons_convicted:,}"))
        lines.append("")

        lines.append(self._line("="))
        return "\n".join(lines)

    def print_dimensions(self, state_name):
        try:
            risk_data = self.processor.compute_composite_risk(state_name)
        except Exception as e:
            print(f"[WARN] Cannot compute dimension breakdown: {e}")
            return
        if not risk_data:
            return
        print("\n--- DIMENSION BREAKDOWN ---")
        for dim, score in risk_data['dimensions'].items():
            print(f"  {dim:<30}: {score}")
        print("---------------------------\n")


def parse_url_style(url_string):
    if url_string.startswith('/'):
        url_string = url_string[1:]
    parts = url_string.split('?')
    path = parts[0]
    query = parts[1] if len(parts) > 1 else ""
    path_parts = path.split('/')
    state = path_parts[1] if len(path_parts) >= 2 else None
    year = None
    if query:
        params = parse_qs(query)
        year_list = params.get('year', [None])
        if year_list and year_list[0]:
            try:
                year = int(year_list[0])
            except ValueError:
                pass
    return state, year


def main():
    parser = argparse.ArgumentParser(
        description='SurakshaAI CLI Report Generator (Dataset: 2001-2014)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py --state Maharashtra
  python test.py --state Maharashtra --year 2014
  python test.py Maharashtra 2014
  python test.py --url "/risk/Maharashtra?year=2014"
  python test.py --list-states
  python test.py --state Maharashtra --dimensions
        """
    )
    parser.add_argument('positional', nargs='*', help='State name and optionally year')
    parser.add_argument('--state', '-s', help='State name (e.g., Maharashtra, Delhi)')
    parser.add_argument('--year', '-y', type=int, help='Year (dataset range: 2001-2014)')
    parser.add_argument('--url', '-u', help='URL-style path (e.g., /risk/Maharashtra?year=2014)')
    parser.add_argument('--dimensions', '-d', action='store_true', help='Show 6-D risk breakdown')
    parser.add_argument('--list-states', '-l', action='store_true', help='List all available states')
    parser.add_argument('--output', '-o', help='Save report to file')
    args = parser.parse_args()

    cli = SurakshaCLIReport()

    if args.list_states:
        states = cli.processor.get_all_states()
        print(f"\nAvailable States ({len(states)}):")
        for i, state in enumerate(states, 1):
            print(f"  {i:2}. {state}")
        return

    state_name = None
    year = args.year

    if args.url:
        state_name, url_year = parse_url_style(args.url)
        if url_year and not year:
            year = url_year
    elif args.state:
        state_name = args.state
    elif len(args.positional) >= 1:
        state_name = args.positional[0]
        if len(args.positional) >= 2:
            try:
                year = int(args.positional[1])
            except ValueError:
                year = None

    if not state_name:
        print("[ERROR] No state specified.")
        print("Usage: python test.py --state Maharashtra --year 2014")
        print("       python test.py --url '/risk/Maharashtra?year=2014'")
        print("       python test.py --list-states")
        sys.exit(1)

    print(f"[QUERY] State: {state_name}, Year: {year if year else 'auto'}\n")
    report = cli.generate_report(state_name, year)

    if report:
        print(report)
        if args.dimensions:
            cli.print_dimensions(state_name)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n[SAVED] Report written to: {args.output}")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()