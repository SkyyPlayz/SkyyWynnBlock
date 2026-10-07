"""Blockbench MCP over stdio - lets Claude use the Blockbench MCP plugin on a PC whose antivirus breaks localhost HTTP.

Why: on Skyy's PC Avast's web shield (aswMonFltProxy) rewrites every localhost HTTP reply: it drops Content-Length and adds
`transfer-encoding: chunked` without chunking the body, so HTTP clients (Claude's MCP connect included) wait forever. This
script is a stdio MCP server for Claude: it reads JSON-RPC lines on stdin, POSTs each one to the Blockbench plugin
(127.0.0.1:3000/bb-mcp) over a raw socket with `Connection: close`, reads the reply to EOF (so the bogus header doesn't
matter) and writes the JSON back on stdout. It keeps the plugin's GET event stream open to answer its pings, and
re-initializes transparently if the plugin dropped the session (or Blockbench was restarted).

Claude config (~/.claude.json user mcpServers): "blockbench": {"type": "stdio", "command": "python",
"args": ["<repo>/tools/bb_mcp_stdio.py"]}. Blockbench must be open for tools to work. Local only; touches no files.
"""
import json
import socket
import sys
import threading
import time

HOST, PORT, PATH = "127.0.0.1", 3000, "/bb-mcp"
out_lock = threading.Lock()
state = {"sid": None, "proto": "2025-06-18", "init": None, "gen": 0}
state_lock = threading.Lock()


def log(msg):
    sys.stderr.write(f"[bb-stdio] {msg}\n")
    sys.stderr.flush()


def emit(obj):
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8") + b"\n"
    with out_lock:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()


def raw_request(method, body=b"", sid=None, timeout=600):
    """One HTTP request to the plugin, read to EOF. Returns (status, headers dict, body bytes)."""
    head = (f"{method} {PATH} HTTP/1.1\r\nHost: localhost:{PORT}\r\nConnection: close\r\n"
            f"Accept: application/json, text/event-stream\r\nmcp-protocol-version: {state['proto']}\r\n")
    if sid:
        head += f"mcp-session-id: {sid}\r\n"
    if method == "POST":
        head += f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n"
    s = socket.create_connection((HOST, PORT), timeout=10)
    try:
        s.settimeout(timeout)
        s.sendall(head.encode("latin-1") + b"\r\n" + body)
        data = b""
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            data += chunk
    finally:
        s.close()
    h, _, payload = data.partition(b"\r\n\r\n")
    lines = h.decode("latin-1").split("\r\n")
    parts = lines[0].split(" ", 2)
    status = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return status, headers, payload


def parse_payload(payload, ctype):
    """JSON body, or the data: lines of an SSE body. Returns a list of JSON-RPC messages."""
    text = payload.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    if "text/event-stream" in ctype or text.startswith(("data:", "event:", "id:", ":")):
        msgs = []
        for block in text.replace("\r\n", "\n").split("\n\n"):
            data = "\n".join(l[5:].lstrip() for l in block.split("\n") if l.startswith("data:"))
            if data:
                try:
                    msgs.append(json.loads(data))
                except ValueError:
                    pass
        return msgs
    obj = json.loads(text)
    return obj if isinstance(obj, list) else [obj]


def post(msg, sid):
    status, headers, payload = raw_request("POST", json.dumps(msg).encode("utf-8"), sid)
    return status, headers, parse_payload(payload, headers.get("content-type", ""))


def initialize(init_msg):
    status, headers, msgs = post(init_msg, None)
    sid = headers.get("mcp-session-id")
    if status != 200 or not sid:
        raise RuntimeError(f"initialize failed: HTTP {status}")
    for m in msgs:
        proto = (m.get("result") or {}).get("protocolVersion")
        if proto:
            state["proto"] = proto
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    with state_lock:
        state["sid"] = sid
        state["gen"] += 1
        gen = state["gen"]
    threading.Thread(target=event_stream, args=(sid, gen), daemon=True).start()
    log(f"session {sid[:8]}... ready")
    return msgs


def reinit():
    init = dict(state["init"])
    init["id"] = "bb-stdio-reinit"
    initialize(init)


def event_stream(sid, gen):
    """Hold the plugin's GET stream open; answer its pings, pass other server messages to Claude."""
    while state["gen"] == gen:
        try:
            s = socket.create_connection((HOST, PORT), timeout=10)
            s.settimeout(None)
            s.sendall((f"GET {PATH} HTTP/1.1\r\nHost: localhost:{PORT}\r\nAccept: text/event-stream\r\n"
                       f"mcp-session-id: {sid}\r\nmcp-protocol-version: {state['proto']}\r\n\r\n").encode("latin-1"))
            buf = b""
            head_done = False
            while state["gen"] == gen:
                chunk = s.recv(65536)
                if not chunk:
                    break
                buf += chunk
                if not head_done:
                    if b"\r\n\r\n" not in buf:
                        continue
                    h, _, buf = buf.partition(b"\r\n\r\n")
                    code = h.split(b" ", 2)[1] if b" " in h else b"0"
                    if code != b"200":
                        log(f"event stream refused (HTTP {code.decode()})")
                        s.close()
                        return
                    head_done = True
                buf = buf.replace(b"\r\n", b"\n")
                while b"\n\n" in buf:
                    block, _, buf = buf.partition(b"\n\n")
                    for m in parse_payload(block + b"\n\n", "text/event-stream"):
                        if m.get("method") == "ping" and "id" in m:
                            threading.Thread(target=lambda i=m["id"]: safe_post(
                                {"jsonrpc": "2.0", "id": i, "result": {}}, sid), daemon=True).start()
                        else:
                            emit(m)
            s.close()
        except OSError:
            pass
        time.sleep(2)


def safe_post(msg, sid):
    try:
        post(msg, sid)
    except OSError:
        pass


def handle(msg):
    method = msg.get("method")
    is_request = method is not None and "id" in msg
    try:
        if method == "initialize":
            state["init"] = msg
            state["proto"] = (msg.get("params") or {}).get("protocolVersion") or state["proto"]
            for m in initialize(msg):
                emit(m)
            return
        if method == "notifications/initialized":
            return  # already sent during initialize
        sid = state["sid"]
        if sid is None and state["init"]:
            reinit()
            sid = state["sid"]
        status, _, msgs = post(msg, sid)
        if status in (400, 404) and state["init"]:
            log(f"session lost (HTTP {status}); re-initializing")
            reinit()
            status, _, msgs = post(msg, state["sid"])
        if is_request:
            if msgs:
                for m in msgs:
                    emit(m)
            else:
                emit({"jsonrpc": "2.0", "id": msg["id"],
                      "error": {"code": -32603, "message": f"Blockbench MCP returned HTTP {status} with no body"}})
    except (OSError, RuntimeError, ValueError) as e:
        with state_lock:
            state["sid"] = None
        log(f"error: {e}")
        if is_request:
            emit({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32603, "message":
                  f"Blockbench MCP not reachable on {HOST}:{PORT} - is Blockbench open with the MCP plugin? ({e})"}})


def main():
    log(f"stdio bridge -> http://{HOST}:{PORT}{PATH}")
    for line in iter(sys.stdin.buffer.readline, b""):
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        for m in (msg if isinstance(msg, list) else [msg]):
            if m.get("method") == "initialize":
                handle(m)  # in order: everything else waits for the session
            else:
                threading.Thread(target=handle, args=(m,), daemon=True).start()


if __name__ == "__main__":
    main()
