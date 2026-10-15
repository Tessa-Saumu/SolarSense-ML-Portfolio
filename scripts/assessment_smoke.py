"""Real localhost HTTP smoke check; no external APIs, keys or billing."""
import json
import os
import secrets
import sys
import threading
import urllib.request
from urllib.error import HTTPError
from pathlib import Path
from werkzeug.serving import make_server
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# Legacy gateway components require a key even though the bounded scenario route
# is public. Generate an ephemeral local-only key without storing or printing it.
os.environ.setdefault("API_KEY", secrets.token_hex(24))
os.environ.setdefault("MODELS_API_KEY", os.environ["API_KEY"])
from api.main import app
from solar_scenario.assessment import assess

def main():
    server=make_server("127.0.0.1",0,app)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    checks=[]
    try:
        with urllib.request.urlopen(base+"/api/v1/assessment/evidence") as response:
            e=json.load(response)
        checks.append("GET consumption and solar artifact evidence:200")
        for payload in ({},{"business_type":"butchery","floor_area_m2":120,"refrigeration_units":5},{"power_source":"hybrid","business_type":"cold_storage","floor_area_m2":500}):
            req=urllib.request.Request(base+"/api/v1/assessment",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req) as response:
                result=json.load(response)
            assert result==assess(payload,e)
            checks.append("POST minimal-input assessment parity:200")
        req=urllib.request.Request(base+"/api/v1/assessment",data=b'{"country":"Uganda"}',headers={"Content-Type":"application/json"})
        try: urllib.request.urlopen(req)
        except HTTPError as exc: assert exc.code==400
        else: raise AssertionError("Out-of-scope input accepted")
        checks.append("Out-of-scope geography:400")
        print(json.dumps({"checks":checks,"model_sha256":e["consumption_model_sha256"],"default":assess({},e)},indent=2))
    finally:
        server.shutdown();thread.join(timeout=5);server.server_close()
if __name__=="__main__": main()
