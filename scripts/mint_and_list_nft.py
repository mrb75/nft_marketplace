from brownie import NftMarketplace, config, network, BasicNft
from .deploy_basic_nft import deploy as deploy_basic_nft
from .deploy_nft_marketplace import deploy as deploy_nft_marketplace
from .helpers import call_contract_method, get_account


def mint_nft():
    if not (BasicNft):
        deploy_basic_nft()

    mint_nft_tx = call_contract_method(
        BasicNft[-1], 'mintNft', {'from': get_account()})
    mint_nft_tx.wait(1)


def list_nft():
    basic_nft = BasicNft[-1]
    if not (NftMarketplace):
        deploy_nft_marketplace()
    nft_marketplace = NftMarketplace[-1]
    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': get_account()})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': get_account()})
    list_item_tx.wait(1)


def main():
    mint_nft()
    list_nft()
