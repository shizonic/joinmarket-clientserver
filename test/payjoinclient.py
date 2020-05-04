#!/usr/bin/env python
import sys
from twisted.internet import reactor
from jmclient.cli_options import check_regtest
from jmclient import get_wallet_path, WalletService, open_test_wallet_maybe, jm_single, load_test_config
from jmclient.payjoin import send_payjoin, parse_payjoin_setup

if __name__ == "__main__":
    wallet_name = sys.argv[1]
    mixdepth = int(sys.argv[2])
    load_test_config()
    jm_single().datadir = "."
    check_regtest()    
    bip21uri = "bitcoin:2N7CAdEUjJW9tUHiPhDkmL9ukPtcukJMoxK?amount=0.3&pj=http://127.0.0.1:8080"
    wallet_path = get_wallet_path(wallet_name, None)
    wallet = open_test_wallet_maybe(
        wallet_path, wallet_name, 4,
        wallet_password_stdin=False,
        gap_limit=6)
    wallet_service = WalletService(wallet)
    # in this script, we need the wallet synced before
    # logic processing for some paths, so do it now:
    while not wallet_service.synced:
        wallet_service.sync_wallet(fast=True)
    # the sync call here will now be a no-op:
    wallet_service.startService()
    manager = parse_payjoin_setup(bip21uri, wallet_service, mixdepth)
    reactor.callWhenRunning(send_payjoin, manager)
    reactor.run()