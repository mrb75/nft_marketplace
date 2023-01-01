from brownie import NftMarketplace, config, network, BasicNft
from .deploy_nft_marketplace import main as deploy_nft_marketplace
from .deploy_basic_nft import main as deploy_basic_nft
import json
from .helpers import update_frontend_abi


def update_nft_marketplace():
    if not (NftMarketplace):
        deploy_nft_marketplace()

    update_frontend_abi(NftMarketplace[-1],
                        config['frontend_nft_marketplace_path'])

    # with open(config['frontend_nft_marketplace_path'], "w") as nft_marketplace_file:
    #     # breakpoint()
    #     print('NftMarketplace frontend updating...')
    #     try:
    #         nft_marketplace_abi = NftMarketplace[-1].abi
    #         nft_marketplace_file.write(json.dumps(nft_marketplace_abi))
    #         print('NftMarketplace frontend updated successfuly')
    #     except:
    #         print('Error in frontend update process')


def update_basic_nft():
    if not (BasicNft):
        deploy_basic_nft()
    update_frontend_abi(BasicNft[-1],
                        config['frontend_basic_nft_path'])


def update_contract_addresses():
    if not (BasicNft):
        deploy_basic_nft()
    if not (NftMarketplace):
        deploy_nft_marketplace()

    with open(config['frontend_contract_addresses'], "r") as addresses_file:
        file_content = addresses_file.read()

    with open(config['frontend_contract_addresses'], "w+") as addresses_file:
        # breakpoint()
        chain_id = network.chain.id
        print('Nft Marketplace contract addresses updating...')
        contracts = [NftMarketplace[-1]]

        for contract in contracts:
            try:
                contract_address = contract.address

                if file_content:

                    addresses = json.loads(file_content)
                else:
                    addresses = json.loads('{}')
                # breakpoint()
                if str(chain_id) in addresses:
                    if contract_address not in addresses[str(chain_id)]:
                        addresses[str(chain_id)].append(contract_address)
                else:
                    addresses[str(chain_id)] = [contract_address]
                # breakpoint()
                addresses_file.write(json.dumps(addresses))
                print('contract addresses updated successfuly')
            except:
                print('Error in contract addresses update process')


def copy_map():
    with open("build/deployments/map.json", "r") as map_file:
        map_content = map_file.read()

    with open(config['frontend_contract_addresses'], "w+") as addresses_file:
        addresses_file.write(map_content)


def main():
    # update_contract_addresses()
    copy_map()
    update_nft_marketplace()
