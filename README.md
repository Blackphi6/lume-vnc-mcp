# lume-vnc-mcp

A tiny [MCP](https://modelcontextprotocol.io) server that lets an AI agent (Claude Code,
Claude Desktop, or any other MCP client) **see and control the screen of a
[lume](https://github.com/trycua/cua) macOS virtual machine** over VNC —
without ever touching your real desktop.

This is useful when you want an agent to click through a real app's UI (for a
demo, a test, or a screen recording) in a disposable, isolated environment
instead of your actual machine.

It exposes exactly 4 tools, nothing more:

| Tool | What it does |
| --- | --- |
| `screenshot(vm_name)` | Returns a PNG screenshot of the VM's current screen |
| `click(vm_name, x, y, button=1)` | Moves the mouse and clicks at `(x, y)` |
| `type_text(vm_name, text)` | Types a string, one key event per character |
| `key_press(vm_name, key)` | Sends a key or key combo, e.g. `ctrl-c`, `super-shift-g`, `Return` |

## Prerequisites

- **macOS** on Apple Silicon
- [**lume**](https://github.com/trycua/cua) installed and a VM created and running
  (`lume create`, `lume run`) — this server does not manage VM lifecycle, it
  only talks to a VM that is already running. For that, pair it with lume's
  own built-in MCP server (`lume serve --mcp`), which handles create/start/stop.

## Install

With [`uv`](https://docs.astral.sh/uv/) (recommended — no manual venv needed):

```bash
claude mcp add --scope user lume-vnc -- uvx lume-vnc-mcp
```

Or with `pip`:

```bash
pip install lume-vnc-mcp
claude mcp add --scope user lume-vnc -- lume-vnc-mcp
```

If your `lume` binary isn't on `PATH`, set `LUME_BIN` to its full path via
`-e LUME_BIN=/path/to/lume` on the `claude mcp add` command (or the
equivalent `env` entry in your MCP client's config).

## Usage

Once registered, ask your agent things like:

- "Take a screenshot of the `my-vm` VM"
- "Click the button at 500, 300 in `my-vm`"
- "Type 'hello world' into `my-vm`"

Pair it with lume's own MCP mode (`lume serve --mcp`, see
[trycua/cua](https://github.com/trycua/cua)) so the same agent can also
create, start and stop the VM itself.

## Why not just use the full cua agent stack?

[trycua/cua](https://github.com/trycua/cua) also ships `cua-mcp-server`,
which is a higher-level tool: you hand it a natural-language task and it
runs its *own* internal agent loop (with its own, separately billed, model
API key) to complete it autonomously.

`lume-vnc-mcp` is the opposite: it exposes only the raw primitives
(screenshot / click / type / key) and lets *your* existing agent — the one
you're already talking to — drive the VM directly, call by call, with no
extra model, no extra API key, and no extra cost.

## Security note

These tools give an agent full mouse/keyboard control of whatever is
running inside the target VM. Only point this at a VM you trust the agent
to operate, and never at a VM that has your real accounts or private data
signed in — the whole point is that it's disposable.

## License

MIT
