from brownie import NftMarketplace, config, network, BasicNft
from .deploy_nft_marketplace import deploy as deploy_nft_marketplace
from .helpers import call_contract_method, get_account
from .mint_and_list_nft import main as mint_and_list_nft


def cancel_nft():
    mint_and_list_nft()
    basic_nft = BasicNft[-1]
    cancel_tx = call_contract_method(NftMarketplace[-1], 'buyItem', basic_nft.address,
                                     basic_nft.getTokenCounter(), {'from': get_account(), 'value': '0.01 ether'})

    cancel_tx.wait(1)


def main():
    cancel_nft()
