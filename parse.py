import sys, json, argparse
parser = argparse.ArgumentParser()
parser.add_argument('--mode', default='m1')
args = parser.parse_args()
try:
    d = json.load(sys.stdin)
except:
    print("  ERROR: could not parse response")
    sys.exit(0)
if args.mode == 'm1':
    v = d.get('estimated_consumption_kwh_monthly', d.get('error', 'ERR'))
    print(f"  M1: {v} kWh/mo")
elif args.mode == 'm4':
    v = d.get('estimated_consumption_kwh', d.get('error', 'ERR'))
    s = d.get('status', '?')
    print(f"  M4: {v} kWh/mo  [{s}]")
elif args.mode == 'blend':
    c = d.get('estimated_consumption_kwh', 'ERR')
    r = d.get('roi_percentage', '?')
    s = d.get('status', '?')
    cost = d.get('system_cost', '?')
    print(f"  consumption: {c} kWh/mo | ROI: {r}% | cost: ${cost} | {s}")