from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
from datetime import datetime, timedelta
import time
import io
import logging

from beem.blockchain import Blockchain
from beem.block import Block
from beem.steem import Steem
from beem.utils import parse_time, formatTimedelta


if __name__ == "__main__":
    # stm = Steem(node="https://api.steemit.com")
    # stm = Steem(node="https://api.steemitstage.com")
    # stm = Steem(node="wss://appbasetest.timcliff.com")
    stm = Steem()
    blockchain = Blockchain(steem_instance=stm)
    last_block_id = 19273700
    last_block = Block(last_block_id, steem_instance=stm)
    startTime = datetime.now()
    how_many_hours = 1
    stopTime = last_block.time() + timedelta(seconds=how_many_hours * 60 * 60)
    ltime = time.time()
    cnt = 0
    total_transaction = 0

    start_time = time.time()
    last_node = blockchain.steem.rpc.url
    print("Current node:", last_node)
    for entry in blockchain.blocks(start=last_block_id, threading=True, thread_num=8):
        block_no = entry.id

        if "block" in entry:
            trxs = entry["block"]["transactions"]
        else:
            trxs = entry["transactions"]

        for tx in trxs:
            for op in tx["operations"]:
                total_transaction += 1
        if "block" in entry:
            block_time = parse_time(entry["block"]["timestamp"])
        else:
            block_time = parse_time(entry["timestamp"])

        if block_time > stopTime:
            total_duration = formatTimedelta(datetime.now() - startTime)
            last_block_id = block_no
            avtran = total_transaction / (last_block_id - 19273700)
            print("* HOUR mark: Processed %d blockchain hours in %s" % (how_many_hours, total_duration))
            print("* Blocks %d, Transactions %d (Avg. per Block %f)" % ((last_block_id - 19273700), total_transaction, avtran))
            break

        if block_no != last_block_id:
            cnt += 1
            last_block_id = block_no
            if last_block_id % 100 == 0:
                now = time.time()
                duration = now - ltime
                total_duration = now - start_time
                speed = int(100000.0 / duration) * 1.0 / 1000
                avspeed = int((last_block_id - 19273700) * 1000 / total_duration) * 1.0 / 1000
                avtran = total_transaction / (last_block_id - 19273700)
                ltime = now
                if last_node != blockchain.steem.rpc.url:
                    last_node = blockchain.steem.rpc.url
                    print("Current node:", last_node)
                print("* 100 blocks processed in %.2f seconds. Speed %.2f. Avg: %.2f. Avg.Trans:"
                      "%.2f Count: %d Block minutes: %d" % (duration, speed, avspeed, avtran, cnt, cnt * 3 / 60))
