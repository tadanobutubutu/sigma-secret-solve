#!/usr/bin/env python3
"""
Daily AlpacaHack - Σecret (sigma-secret) solver

prob.py はフラグを 8 バイトずつのブロックに分け、各ブロックから
  x = 前半 4 バイト (big-endian)          ... 0 <= x < 2^32
  y = 2^32 + 後半 4 バイト (big-endian)   ... 2^32 <= y < 2^33
を作り、べき和 [S1, S2] = [x + y, x^2 + y^2] だけを出力する。

  (y - x)^2 = 2 * (x^2 + y^2) - (x + y)^2 = 2*S2 - S1^2
なので、整数平方根で d = y - x が求まり（x < y なので符号は正で確定）、
  y = (S1 + d) / 2,  x = (S1 - d) / 2
で x, y が復元できる。

使い方:
  python3 solve.py HOST PORT      # サーバーに接続して解く
  python3 prob.py | python3 solve.py   # 標準入力から [S1, S2] の行を読む
"""
import ast
import math
import socket
import sys

HALF_SIZE = 4                     # prob.py と同じ定数
OFFSET = 1 << (8 * HALF_SIZE)     # 2^32


def recv_all(host: str, port: int) -> str:
    """サーバーは出力し終わると接続を閉じるので、EOF まで全部読む。"""
    data = b""
    with socket.create_connection((host, port)) as s:
        while chunk := s.recv(4096):
            data += chunk
    return data.decode()


def solve_block(s1: int, s2: int) -> bytes:
    """1 ブロック分の [S1, S2] から元の 8 バイトを復元する。"""
    # (y - x)^2 = 2*S2 - S1^2  （交差項 2xy が打ち消し合う）
    diff_sq = 2 * s2 - s1 * s1
    d = math.isqrt(diff_sq)
    assert d * d == diff_sq, "完全平方数にならない: 入力が壊れている"

    # x < 2^32 <= y なので y - x > 0、つまり d = y - x で符号が確定する
    y = (s1 + d) // 2
    x = (s1 - d) // 2

    # y にはオフセット 2^32 が足されているので引いて戻す
    return x.to_bytes(HALF_SIZE, "big") + (y - OFFSET).to_bytes(HALF_SIZE, "big")


def main() -> None:
    if len(sys.argv) == 3:
        text = recv_all(sys.argv[1], int(sys.argv[2]))
    else:
        text = sys.stdin.read()

    flag = b""
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("["):
            continue
        s1, s2 = ast.literal_eval(line)
        flag += solve_block(s1, s2)

    # 末尾のゼロパディング（prob.py の bytes(-len % 8)）を除く
    print(flag.rstrip(b"\x00").decode())


if __name__ == "__main__":
    main()
