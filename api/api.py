import datetime
import json
import os
from typing import Any, TypeAlias

from e3dc import E3DC
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource
from json_serialize import to_serializable
from webargs import fields, validate
from webargs.flaskparser import abort, parser, use_args
from werkzeug.security import check_password_hash, generate_password_hash

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.config["RESTFUL_JSON"] = {"sort_keys": True, "default": to_serializable}

try:
    IP_ADDRESS = os.environ["E3DC_IP_ADDRESS"]
    USERNAME = os.environ["E3DC_USERNAME"]
    PASSWORD = os.environ["E3DC_PASSWORD"]
    KEY = os.environ["E3DC_KEY"]
    ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
    CONFIG = json.loads(os.getenv("E3DC_CONFIG", "{}"))
except KeyError:
    raise Exception(
        "Environmental Variables E3DC_IP_ADDRESS, E3DC_USERNAME, E3DC_PASSWORD E3DC_KEY and ADMIN_PASSWORD need to be present!"
    )

e3dc = E3DC(
    E3DC.CONNECT_LOCAL,
    username=USERNAME,
    password=PASSWORD,
    ipAddress=IP_ADDRESS,
    key=KEY,
    configuration=CONFIG,
)

users = {"admin": generate_password_hash(ADMIN_PASSWORD)}


@auth.verify_password
def verify_password(username: str, password: str):
    if users.get(username) is not None:
        return check_password_hash(users.get(username), password)
    return False


class Resource(Resource):
    method_decorators = [auth.login_required]


class poll(Resource):
    def get(self):
        return e3dc.poll(keepAlive=True)


class system_info(Resource):
    def get(self):
        return e3dc.get_system_info(keepAlive=True)


class system_status(Resource):
    def get(self):
        return e3dc.get_system_status(keepAlive=True)


class batteries(Resource):
    def get(self):
        return e3dc.get_batteries(keepAlive=True)


class battery_data(Resource):
    def get(self):
        return e3dc.get_battery_data(keepAlive=True)


class batteries_data(Resource):
    def get(self):
        return e3dc.get_batteries_data(keepAlive=True)


class pvis(Resource):
    def get(self):
        return e3dc.get_pvis(keepAlive=True)


class pvi_data(Resource):
    def get(self):
        return e3dc.get_pvi_data(keepAlive=True)


class pvis_data(Resource):
    def get(self):
        return e3dc.get_pvis_data(keepAlive=True)


class powermeters(Resource):
    def get(self):
        return e3dc.get_powermeters(keepAlive=True)


class powermeter_data(Resource):
    def get(self):
        return e3dc.get_powermeter_data(keepAlive=True)


class powermeters_data(Resource):
    def get(self):
        return e3dc.get_powermeters_data(keepAlive=True)


class power_settings(Resource):
    def get(self):
        return e3dc.get_power_settings(keepAlive=True)

    def post(self):
        if not request.is_json:
            return {"message": "not an application/json content type"}, 400
        content: JSON = request.json
        if isinstance(content, dict) and content.keys() & [
            "powerLimitsUsed",
            "powerSaveEnabled",
            "weatherRegulatedChargeEnabled",
        ]:
            if "powerLimitsUsed" in content:
                battery_data = e3dc.get_power_settings(keepAlive=True)

                if "maxChargePower" in content:
                    battery_data["maxChargePower"] = content["maxChargePower"]

                if "maxDischargePower" in content:
                    battery_data["maxDischargePower"] = content["maxDischargePower"]

                if "dischargeStartPower" in content:
                    battery_data["dischargeStartPower"] = content["dischargeStartPower"]

                if isinstance(content["powerLimitsUsed"], bool):
                    req = e3dc.set_power_limits(
                        enable=content["powerLimitsUsed"],
                        max_charge=battery_data["maxChargePower"],
                        max_discharge=battery_data["maxDischargePower"],
                        discharge_start=battery_data["dischargeStartPower"],
                        keepAlive=True,
                    )
                else:
                    return {"message": "powerLimitsUsed is not a boolean"}, 501

                if req == -1:
                    return {"message": "error updating power limits"}, 501

            if "powerSaveEnabled" in content:
                if isinstance(content["powerSaveEnabled"], bool):
                    req = e3dc.set_powersave(
                        enable=content["powerSaveEnabled"], keepAlive=True
                    )
                else:
                    return {"message": "powerSaveEnabled is not a boolean"}, 501

                if req == -1:
                    return {"message": "error updating Power Save"}, 501

            if "weatherRegulatedChargeEnabled" in content:
                if isinstance(content["weatherRegulatedChargeEnabled"], bool):
                    req = e3dc.set_weather_regulated_charge(
                        enable=content["weatherRegulatedChargeEnabled"], keepAlive=True
                    )
                else:
                    return {
                        "message": "weatherRegulatedChargeEnabled is not a boolean"
                    }, 501

                if req == -1:
                    return {"message": "error updating Weather Regulated Charge"}, 501
        else:
            return {
                "message": "any of key powerLimitsUsed, powerSaveEnabled or weatherRegulatedChargeEnabled is required"
            }, 501

        return {"message": "success"}, 200


class idle_periods(Resource):
    def get(self):
        return e3dc.get_idle_periods(keepAlive=True)

    def post(self):
        if not request.is_json:
            return {"message": "not an application/json content type"}, 400

        content: JSON = request.json

        try:
            if e3dc.set_idle_periods(content, keepAlive=True):
                return {"message": "success"}, 200
            else:
                return {"message": "error updating Idle Times"}, 501
        except Exception as e:
            return {"message": e}, 400


class db_data(Resource):
    dateadd_args = {
        "startDate": fields.Date(required=False),
        "timespan": fields.Str(
            missing="DAY", validate=validate.OneOf(["DAY", "MONTH", "YEAR"])
        ),
    }

    @use_args(dateadd_args, location="query")
    def get(self, args: dict[str, Any]):
        if "startDate" not in args:
            startDate = datetime.date.today()
        else:
            startDate = args["startDate"]

        return e3dc.get_db_data(
            startDate=startDate, timespan=args["timespan"], keepAlive=True
        )


# This error handler is necessary for usage with Flask-RESTful
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(error_status_code, errors=err.messages)


api.add_resource(poll, "/api/poll")
api.add_resource(system_info, "/api/system_info")
api.add_resource(system_status, "/api/system_status")
api.add_resource(batteries, "/api/batteries")
api.add_resource(battery_data, "/api/battery_data")
api.add_resource(batteries_data, "/api/batteries_data")
api.add_resource(pvis, "/api/pvis")
api.add_resource(pvi_data, "/api/pvi_data")
api.add_resource(pvis_data, "/api/pvis_data")
api.add_resource(powermeters, "/api/powermeters")
api.add_resource(powermeter_data, "/api/powermeter_data")
api.add_resource(powermeters_data, "/api/powermeters_data")
api.add_resource(power_settings, "/api/power_settings")
api.add_resource(idle_periods, "/api/idle_periods")
api.add_resource(db_data, "/api/db_data")

if __name__ == "__main__":
    app.run(debug=False)
