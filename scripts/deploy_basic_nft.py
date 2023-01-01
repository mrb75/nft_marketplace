from brownie import BasicNft, network, config
from .helpers import get_account, deploy_with_gas


def deploy():
    print('start deploying basic nft ...')
    deploy_with_gas(BasicNft, {'from': get_account(
    )}, publish_source=config['networks'][network.show_active()]['publish_source'])
    print('basic nft was deployed successfully')


def main():
    deploy()
