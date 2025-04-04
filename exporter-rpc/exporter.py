
from flask import Flask, Response
import requests
import time
import os

app = Flask(__name__)

NODE_URL = os.getenv("NODE_URL", "http://127.0.0.1:8545")
BLOCK_HISTORY = 25

previous_block = None

def rpc_call(method, params=[]):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(NODE_URL, json=payload, timeout=5)
        response.raise_for_status()
        return response.json().get("result")
    except Exception as e:
        print(f"RPC Error in {method}: {e}")
        return None

@app.route("/metrics")
def metrics():
    global previous_block
    lines = []

    # eth_blockNumber
    current_block_hex = rpc_call("eth_blockNumber")
    if current_block_hex:
        current_block = int(current_block_hex, 16)
        lines.append(f"besu_rpc_block_number {current_block}")
    else:
        current_block = None

    # Detectar se a rede está travada
    if previous_block is not None and current_block is not None:
        if current_block <= previous_block:
            lines.append("besu_rpc_stalled_blocks 1")
        else:
            lines.append("besu_rpc_stalled_blocks 0")
    previous_block = current_block

    # net_peerCount
    peer_count_hex = rpc_call("net_peerCount")
    if peer_count_hex:
        lines.append(f"besu_rpc_peer_count {int(peer_count_hex, 16)}")

    # admin_peers
    peers = rpc_call("admin_peers")
    if peers:
        for p in peers:
            pid = p.get("id", "unknown")
            ip = p.get("network", {}).get("remoteAddress", "unknown")
            lines.append(f'besu_rpc_peer_info{{peer_id="{pid}",ip="{ip}"}} 1')

    # txpool_besuStatistics
    txpool_stats = rpc_call("txpool_besuStatistics")
    if txpool_stats:
        local = txpool_stats.get("localCount", 0)
        remote = txpool_stats.get("remoteCount", 0)
        maxsize = txpool_stats.get("maxSize", 0)
        lines.append(f"besu_rpc_txpool_local_count {local}")
        lines.append(f"besu_rpc_txpool_remote_count {remote}")
        lines.append(f"besu_rpc_txpool_max_size {maxsize}")

    # txpool_besuTransactions
    txs = rpc_call("txpool_besuTransactions")
    if txs is not None:
        lines.append(f"besu_rpc_txpool_total_transactions {len(txs)}")

    # eth_gasPrice
    gas_price = rpc_call("eth_gasPrice")
    if gas_price:
        lines.append(f"besu_rpc_gas_price {int(gas_price, 16)}")

    # Blocos anteriores
    if current_block:
        for i in range(BLOCK_HISTORY):
            bnum = current_block - i
            block = rpc_call("eth_getBlockByNumber", [hex(bnum), True])
            if block:
                tx_count = len(block.get("transactions", []))
                gas_used = int(block.get("gasUsed", "0x0"), 16)
                difficulty = int(block.get("difficulty", "0x0"), 16)
                proposer = block.get("miner", "unknown")
                lines.append(f'besu_rpc_block_txcount{{block="{bnum}"}} {tx_count}')
                lines.append(f'besu_rpc_block_gasused{{block="{bnum}"}} {gas_used}')
                lines.append(f'besu_rpc_block_difficulty{{block="{bnum}"}} {difficulty}')
                lines.append(f'besu_rpc_block_proposer{{block="{bnum}",proposer="{proposer}"}} 1')

    return Response("\n".join(lines) + "\n", mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)