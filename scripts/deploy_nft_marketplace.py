from brownie import NftMarketplace, config, network
from .helpers import deploy_with_gas, get_account


def deploy():
    deploy_with_gas(NftMarketplace, {'from': get_account(
    )}, publish_source=config['networks'][network.show_active()]['publish_source'])


def main():
    deploy()
