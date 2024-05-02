
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import json
import pytz
import api.main as main
from api.task_on import *
from api.meter_api import *
from api.config import * 

app = Flask(__name__)
CORS(app)

def updatePerpetuals():
    try:
        main.updateAllParams()
    except:
        pass 

def fetch_data():
    with open("json/data.json", "r") as jsonFile:
        data = json.load(jsonFile)
    return data

def fetch_borrowers():
    with open("json/borrowers.json", "r") as jsonFile:
        borrowers = json.load(jsonFile)
    return borrowers

def fetch_lending_yields():
    with open("json/lend_yields.json", "r") as jsonFile:
        lend_yields = json.load(jsonFile)
    return lend_yields

timezone = pytz.timezone('Europe/London')
triggerLending = IntervalTrigger(seconds=1800, timezone=timezone)
triggerPerpetuals = IntervalTrigger(seconds=180, timezone=timezone)

scheduler = BackgroundScheduler()
scheduler.add_job(func=updatePerpetuals, trigger=triggerPerpetuals)
scheduler.start()

@app.route('/')
def index():
    return "Meridian API"

@app.route("/mst_supply",methods=['GET'])
def mstSupply():
    supply = fetch_data()["mst_supply"]
    return jsonify(supply)

@app.route("/daily_volume",methods=['GET'])
def dailyVolume():
    volume = fetch_data()["volume_data"]["daily_volume"]
    return jsonify(int(int(volume)*10**-12))

@app.route("/total_volume",methods=['GET'])
def totalVolume():
    volume = fetch_data()["volume_data"]["total_volume"]
    return jsonify(int(int(volume)*10**-12))

@app.route("/mst_price_30",methods=['GET'])
def mstPrice30():
    mst_price_30 = fetch_data()["mst_price_30"]
    return jsonify(mst_price_30)

@app.route("/total_tvl",methods=['GET'])
def totalTVL():
    total_tvl = fetch_data()["total_tvl"]
    return jsonify(total_tvl)

@app.route("/mst_price",methods=['GET'])
def mstPrice():
    mst_price = fetch_data()["mst_price"]
    return jsonify(mst_price)

@app.route("/mst_mcap",methods=['GET'])
def mstMcap():
    mst_mcap = fetch_data()["mst_mcap"]
    return jsonify(mst_mcap)

@app.route("/volume_data",methods=['GET'])
def volumeData():
    volume = fetch_data()["volume_data"]
    return jsonify(volume)

@app.route("/position_stats",methods=['GET'])
def positionStats():
    stats = fetch_data()["position_stats"]
    return jsonify(stats)

@app.route("/fees_summary",methods=['GET'])
def feeSummary():
    fees = fetch_data()["fees_summary"]
    return jsonify(fees)

@app.route("/weekly_fees",methods=['GET'])
def weeklyFees():
    weeklyFees = fetch_data()["fees_summary"]["weeklyFees"]
    return jsonify(weeklyFees*10**18)

@app.route("/user_data",methods=['GET'])
def userData():
    userData = fetch_data()["user_data"]
    return jsonify(userData)

@app.route("/charm_price",methods=['GET'])
def charmPrice():
    charm_price = fetch_data()["charm_price"]
    return jsonify(charm_price)

@app.route("/charm_supply",methods=['GET'])
def charmSupply():
    supply = fetch_data()["charm_supply"]
    return jsonify(supply)

@app.route("/stability_pool_yield",methods=['GET'])
def telosStabilityPoolYield():
    stability_pool_yield = fetch_data()["stability_pool_yield"]
    return jsonify(stability_pool_yield)

@app.route("/fuse_stability_pool_yield",methods=['GET'])
def fuseStabilityPoolYield():
    stability_pool_yield = fetch_data()["fuse_stability_pool_yield"]
    return jsonify(stability_pool_yield)

@app.route("/trove_count",methods=['GET'])
def troveCount():
    troves = fetch_data()["number_of_troves"]
    return jsonify(troves)

@app.route("/voltage_fuse_usdm_liquidity",methods=['GET'])
def fuseUSDMLiquidity():
    liquidity = fetch_data()["voltage_fuse_usdm_liquidity"]
    return jsonify(liquidity)

@app.route("/incentives",methods=['GET'])
def incentivesData():
    rewards = fetch_data()["incentives"]
    return jsonify(rewards)

@app.route("/keepers",methods=['GET'])
def keeperData():
    data = fetch_data()["keepers"]
    return jsonify(data)

@app.route("/health_factors",methods=['GET'])
def healthFactors():
    hfs = fetch_borrowers()
    return jsonify(hfs)

@app.route("/lending_yields",methods=['GET'])
def LendingYields():
    yields = fetch_lending_yields()
    return jsonify(yields)

@app.route("/stability_pool",methods=['GET'])
def StabilityPoolYields():
    yields = fetch_data()["stability_pool"]
    return jsonify(yields)

@app.route("/warnings",methods=['GET'])
def warnings():
    warnings = fetch_data()["warnings"]
    return jsonify(warnings)

@app.route('/data/debt', methods=['GET'])
def get_user_debt():
    address = request.args.get('address')
    network = request.args.get('network')
    position_info = get_position_info(address,network)
    try:
        return jsonify({"debt": position_info}), 200
    except Exception as e:
        print(f"Error checking balance: {str(e)}")
        return jsonify({"result": {"isValid": False}}), 200


####################### FUSE TASK ON CAMPAIGN ########################

@app.route('/api/trove_status/verification', methods=['GET'])
def get_trove_status():
    address = request.args.get('address')
    try:
        isValid = fetch_trove_status(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200


@app.route('/api/stability_pool_150/verification', methods=['GET'])
def get_stability_pool_status_150():
    address = request.args.get('address')
    try:
        isValid = fetchStabilityPool_150(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200


@app.route('/api/stability_pool_500/verification', methods=['GET'])
def get_stability_pool_status_500():
    address = request.args.get('address')
    try:
        isValid = fetchStabilityPool_500(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200
    

@app.route('/api/stability_pool_1000/verification', methods=['GET'])
def get_stability_pool_status_1000():
    address = request.args.get('address')
    try:
        isValid = fetchStabilityPool_1000(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200
 
 
@app.route('/api/staking_pool_1000/verification', methods=['GET'])
def get_staking_pool_status_1000():
    address = request.args.get('address')
    try:
        isValid = fetchStakingPool_1000(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200   
  
  
@app.route('/api/staking_pool_2500/verification', methods=['GET'])
def get_staking_pool_status_2500():
    address = request.args.get('address')
    try:
        isValid = fetchStakingPool_2500(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200   


@app.route('/api/staking_pool_5000/verification', methods=['GET'])
def get_staking_pool_status_5000():
    address = request.args.get('address')
    try:
        isValid = fetchStakingPool_5000(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200 
    
    
    
################## Meter API #####################


@app.route('/api/meter_staking_pool_1000/verification', methods=['GET'])
def meter_staking_pool_status_1000():
    address = request.args.get('address')
    try:
        isValid = meter_staking_pool_1000(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200   
  
  
@app.route('/api/meter_staking_pool_2500/verification', methods=['GET'])
def meter_staking_pool_status_2500():
    address = request.args.get('address')
    try:
        isValid = meter_staking_pool_2500(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200   


@app.route('/api/meter_staking_pool_5000/verification', methods=['GET'])
def meter_staking_pool_status_5000():
    address = request.args.get('address')
    try:
        isValid = meter_staking_pool_5000(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200 
    


@app.route('/api/meter_lending_pool_100/verification', methods=['GET'])
def meter_lending_pool_status_100():
    address = request.args.get('address')
    try:
        isValid = meter_lending_mtrg_100(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200   
  
  
@app.route('/api/meter_lending_pool_250/verification', methods=['GET'])
def meter_lending_pool_status_250():
    address = request.args.get('address')
    try:
        isValid = meter_lending_mtrg_250(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200   


@app.route('/api/meter_lending_pool_500/verification', methods=['GET'])
def meter_lending_pool_status_500():
    address = request.args.get('address')
    try:
        isValid = meter_lending_mtrg_500(address)
        return jsonify({"result": {"isValid": isValid}}), 200
    except Exception as e:
        # Log the error for server-side debugging.
        print(f"Error checking balance: {str(e)}")
        # Return isValid as false in case of any error.
        return jsonify({"result": {"isValid": False}}), 200 
    
if __name__ == "__main__":
    app.run(debug=True)
    
