import json, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

def read_battery():
    result={"available":False,"chargePercent":None,"status":"N/A","designCapacityMWh":None,"fullChargeCapacityMWh":None,"healthPercent":None,"voltageV":None,"currentA":None,"temperatureC":None,"cycleCount":None}
    try:
        ps='$b=Get-CimInstance Win32_Battery; if($b){$b | Select-Object EstimatedChargeRemaining,BatteryStatus,DesignCapacity,FullChargeCapacity | ConvertTo-Json -Compress}'
        p=subprocess.run(["powershell","-NoProfile","-Command",ps],capture_output=True,text=True,timeout=8)
        if p.stdout.strip():
            d=json.loads(p.stdout)
            if isinstance(d,list): d=d[0]
            result["available"]=True
            result["chargePercent"]=d.get("EstimatedChargeRemaining")
            result["designCapacityMWh"]=d.get("DesignCapacity")
            result["fullChargeCapacityMWh"]=d.get("FullChargeCapacity")
            if result["designCapacityMWh"] and result["fullChargeCapacityMWh"]:
                result["healthPercent"]=round(result["fullChargeCapacityMWh"]/result["designCapacityMWh"]*100,1)
            result["status"]="Charging" if d.get("BatteryStatus") in [6,7,8,9] else "On Battery"
    except Exception as e: result["error"]=str(e)
    return result

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!="/api/battery": self.send_response(404);self.end_headers();return
        data=json.dumps(read_battery()).encode()
        self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Access-Control-Allow-Origin","*");self.end_headers();self.wfile.write(data)
    def log_message(self,*a): pass

print("Smart Battery Windows bridge: http://127.0.0.1:5000")
HTTPServer(("127.0.0.1",5000),H).serve_forever()
