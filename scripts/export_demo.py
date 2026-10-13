"""Export exact served model predictions and parity examples for a static demo."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from solar_scenario.core import calculate, load_evidence

def main():
    evidence=load_evidence()
    vectors=[{}, {"solar_profile":"xgboost"}, {"business_type":"grocery"}, {"consumption_mode":"measured","monthly_consumption_kwh":300,"panel_area_m2":100}, {"panel_area_m2":0}, {"self_consumption_fraction":0}, {"tariff_kes_per_kwh":0}]
    evidence["parity_vectors"]=[{"input":v,"result":calculate(v,evidence)} for v in vectors]
    destination=ROOT/"web-demo/data/scenario-evidence.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(destination)
if __name__=="__main__": main()
