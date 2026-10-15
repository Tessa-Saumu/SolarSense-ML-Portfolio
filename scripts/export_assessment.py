"""Export the actual consumption trees, solar profiles and numerical test cases."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from solar_scenario.assessment import assess, load_assessment_evidence

def main():
    evidence=load_assessment_evidence()
    vectors=[{}, {"business_type":"butchery","floor_area_m2":50,"refrigeration_units":5}, {"power_source":"hybrid"}, {"power_source":"diesel","business_type":"cold_storage","floor_area_m2":500,"refrigeration_units":12}, {"business_type":"bakery","floor_area_m2":250,"operating_hours_weekly":60,"refrigeration_units":0}, {"assumptions":{"grid_tariff_kes_per_kwh":0,"annual_maintenance_fraction":0}}, {"business_type":"restaurant","floor_area_m2":180,"operating_hours_weekly":100,"refrigeration_units":2}]
    evidence["parity_vectors"]=[{"input":v,"result":assess(v,evidence)} for v in vectors]
    destination=ROOT/"web-demo/data/assessment-evidence.json"
    destination.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(destination)
if __name__=="__main__":main()
