from brownie import accounts, network, config
from functools import wraps
import pytest
from brownie.exceptions import VirtualMachineError
import json
LOCAL_ENVIRONMENTS = ['development', 'ganache-local']
FORKED_LOCAL_ENVIROMENT = ['mainnet-fork', 'mainnet-fork-dev']
AGGREGATOR_DECIMAIL = 8
AGGREGATOR_INITIAL_ANSWER = 2e11
BASE_FEE = "0.25 ether"
GAS_PRICE_LINK = 1e9


def get_account():
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        account = accounts[0]
    else:
        account = accounts.load("mymeta")
    return account


def deploy_with_gas(contract, *args, **kwargs):
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        gas_price = "60 gwei"
        args[-1]['gas_price'] = gas_price
        args[-1]["gas_limit"] = 12000000
    contract.deploy(*args, **kwargs)


def get_vrf_coordinator_address():
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        if not (VRFCoordinatorV2Mock):
            deploy_with_gas(VRFCoordinatorV2Mock, BASE_FEE, GAS_PRICE_LINK, {
                'from': get_account()})
        coordinator = VRFCoordinatorV2Mock[-1]
        address = coordinator.address
    else:
        address = config['networks'][network.show_active()]['vrf_coordinator']
    return address


def get_subscription_id():
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        if not (VRFCoordinatorV2Mock):
            deploy_with_gas(VRFCoordinatorV2Mock, BASE_FEE, GAS_PRICE_LINK, {
                'from': get_account()})
        coordinator = VRFCoordinatorV2Mock[-1]
        transaction_response = call_contract_method(
            coordinator, 'createSubscription', {"from": get_account()})
        transaction_receipt = transaction_response.wait(1)
        subscription_id = transaction_response.events['SubscriptionCreated'][0][0]['subId']
        call_contract_method(coordinator, 'fundSubscription',
                             subscription_id, 1e18, {'from': get_account()})

    else:
        subscription_id = config['networks'][network.show_active(
        )]['subscription_id']
    return subscription_id


def only_local_env_test(func):
    from pytest import skip

    @wraps(func)
    def wrapper(*args, **kwargs):
        if network.show_active() not in LOCAL_ENVIRONMENTS:
            skip("only for local testing")
        result = func(*args, **kwargs)
        return result

    return wrapper


def call_contract_method(contract, method_name: str, *args, **kwargs):
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        args[-1]["gas_price"] = "60 gwei"
        args[-1]["gas_limit"] = 12000000
    # args[-1]["gas_limit"] = 120000000000
    return getattr(contract, method_name)(*args, **kwargs)


def calculate_tx_fee(tx_receipt):
    return tx_receipt.gas_used*tx_receipt.gas_price


def get_price_feed_address():
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        if not (MockV3Aggregator):
            MockV3Aggregator.deploy(AGGREGATOR_DECIMAIL, AGGREGATOR_INITIAL_ANSWER, {
                                    'from': get_account(), 'gas_price': '60 gwei'})
        aggregator = MockV3Aggregator[-1]
        address = aggregator.address
    else:
        address = config['networks'][network.show_active()
                                     ]['eth_usd_price_feed']
    return address


def custom_error(error_type, error_args):

    return "typed error: "+Web3.keccak(text=txt)[:4].hex()


def update_frontend_abi(contract, file_path):

    with open(file_path, "w") as contract_file:

        print('{0} frontend updating...'.format(contract))
        try:
            contract_abi = contract.abi
            contract_file.write(json.dumps(contract_abi))
            print('{0} frontend updated successfuly'.format(
                contract))
        except:
            print('Error in frontend update process')
