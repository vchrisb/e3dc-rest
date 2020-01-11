from flask import Flask, request

from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from e3dc import E3DC
from json_serialize import to_serializable
import json
import os

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.config['RESTFUL_JSON'] = {"sort_keys":True, 'default':to_serializable}

try:
    IP_ADDRESS = os.environ['E3DC_IP_ADDRESS']
    USERNAME = os.environ['E3DC_USERNAME']
    PASSWORD = os.environ['E3DC_PASSWORD']
    KEY = os.environ['E3DC_KEY']
    ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
except:
    raise Exception("Environmental Variables E3DC_IP_ADDRESS, E3DC_USERNAME, E3DC_PASSWORD E3DC_KEY and ADMIN_PASSWORD need to be present!")

e3dc = E3DC(E3DC.CONNECT_LOCAL, username=USERNAME, password=PASSWORD, ipAddress = IP_ADDRESS, key = KEY)

users = {
    "admin": generate_password_hash(ADMIN_PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

class Resource(Resource):
    method_decorators = [auth.login_required]

class poll(Resource):
    def get(self):
        return e3dc.poll(keepAlive = True)

class system_info(Resource):
    def get(self):
        return e3dc.get_system_info(keepAlive = True)

class battery_data(Resource):
    def get(self):
        return e3dc.get_battery_data(keepAlive = True)

class pvi_data(Resource):
    def get(self):
        return e3dc.get_pvi_data(keepAlive = True)

class power_settings(Resource):
    def get(self):
        return e3dc.get_power_settings(keepAlive = True)

    def post(self):
        if not request.is_json:
            return {'message': 'not an application/json content type'}, 400
        content = request.json
        if "powerLimitsUsed" in content:
            battery_data = e3dc.get_power_settings(keepAlive = True)

            if "maxChargePower" in content:
                battery_data["maxChargePower"] = content["maxChargePower"]

            if "maxDischargePower" in content:
                battery_data["maxDischargePower"] = content["maxDischargePower"]
            
            if "dischargeStartPower" in content:
                battery_data["dischargeStartPower"] = content["dischargeStartPower"]

            if isinstance(content["powerLimitsUsed"], bool):
                req = e3dc.set_power_limits(enable = content["powerLimitsUsed"], max_charge = battery_data["maxChargePower"],  max_discharge = battery_data["maxDischargePower"],  discharge_start = battery_data["dischargeStartPower"], keepAlive = True)
            else:
                return {'message': 'powerLimitsUsed is not a boolean'}, 501 
            
            if req == -1:
                return {'message': 'error updating power limits'}, 501 
    
        if "powerSaveEnabled" in content:
            if isinstance(content["powerSaveEnabled"], bool):
                req = e3dc.set_powersave(enable = content["powerSaveEnabled"], keepAlive = True)
            else:
                return {'message': 'powerSaveEnabled is not a boolean'}, 501 

            if req == -1:
                return {'message': 'error updating Power Save'}, 501

        if "weatherRegulatedChargeEnabled" in content:
            if isinstance(content["weatherRegulatedChargeEnabled"], bool):
                req = e3dc.set_weather_regulated_charge(enable = content["weatherRegulatedChargeEnabled"], keepAlive = True)
            else:
                return {'message': 'weatherRegulatedChargeEnabled is not a boolean'}, 501 

            if req == -1:
                return {'message': 'error updating Weather Regulated Charge'}, 501

        return {'message': 'success'}, 200 

class idle_periods(Resource):
    def get(self):
        return e3dc.get_idle_periods(keepAlive = True)

    def post(self):
        if not request.is_json:
            return {'message': 'not an application/json content type'}, 400
        
        content = request.json
        
        try:        
            if e3dc.set_idle_periods(content, keepAlive = True):
                return {'message': 'success'}, 200
            else:
                return {'message': 'error updating Idle Times'}, 501
        except Exception as e:
            return {'message': e}, 400

api.add_resource(poll, '/api/poll')
api.add_resource(system_info, '/api/system_info')
api.add_resource(battery_data, '/api/battery_data')
api.add_resource(pvi_data, '/api/pvi_data')
api.add_resource(power_settings, '/api/power_settings')
api.add_resource(idle_periods, '/api/idle_periods')

if __name__ == '__main__':
    app.run(debug=True)