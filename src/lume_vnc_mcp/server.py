"""lume VM の画面を VNC 経由で操作する軽量 MCP サーバー。

screenshot / click / type_text / key_press の4ツールのみを提供する。
lume (https://github.com/trycua/cua) で作成した macOS VM を前提とする。
"""

import json
import os
import re
import shutil
import subprocess
import tempfile

from mcp.server.mcpserver import Image, MCPServer
from vncdotool import api

LUME_BIN = os.environ.get("LUME_BIN") or shutil.which("lume") or "lume"

mcp = MCPServer("lume-vnc")


def _vnc_info(vm_name: str) -> tuple[str, int, str]:
    out = subprocess.run(
        [LUME_BIN, "get", vm_name, "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(out.stdout)
    data = parsed[0] if isinstance(parsed, list) else parsed
    vnc_url = data.get("vncUrl") or data.get("vnc")
    if not vnc_url:
        raise RuntimeError(f"VM '{vm_name}' にVNC URLがありません(起動していますか?)")
    # vnc://:password@host:port
    m = re.match(r"vnc://:(?P<password>[^@]*)@(?P<host>[^:]+):(?P<port>\d+)", vnc_url)
    if not m:
        raise RuntimeError(f"VNC URLを解析できません: {vnc_url}")
    return m.group("host"), int(m.group("port")), m.group("password")


def _connect(vm_name: str):
    host, port, password = _vnc_info(vm_name)
    return api.connect(f"{host}::{port}", password=password)


@mcp.tool()
def screenshot(vm_name: str) -> Image:
    """指定した lume VM の現在の画面をスクリーンショットとして取得する。"""
    client = _connect(vm_name)
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = tmp.name
        try:
            client.captureScreen(path)
            with open(path, "rb") as f:
                data = f.read()
        finally:
            os.unlink(path)
        return Image(data=data, format="png")
    finally:
        client.disconnect()


@mcp.tool()
def click(vm_name: str, x: int, y: int, button: int = 1) -> str:
    """指定した lume VM の画面上の座標をクリックする。button: 1=左, 2=中, 3=右。"""
    client = _connect(vm_name)
    try:
        client.mouseMove(x, y)
        client.mousePress(button)
        return f"clicked ({x}, {y}) button={button}"
    finally:
        client.disconnect()


@mcp.tool()
def type_text(vm_name: str, text: str) -> str:
    """指定した lume VM に文字列をキー入力としてタイプする。"""
    client = _connect(vm_name)
    try:
        for ch in text:
            key = "minus" if ch == "-" else ch
            client.keyPress(key)
        return f"typed {len(text)} chars"
    finally:
        client.disconnect()


@mcp.tool()
def key_press(vm_name: str, key: str) -> str:
    """指定した lume VM にキー(組み合わせ)を送信する。例: 'ctrl-c', 'super-shift-g', 'Return'。"""
    client = _connect(vm_name)
    try:
        client.keyPress(key)
        return f"pressed {key}"
    finally:
        client.disconnect()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
