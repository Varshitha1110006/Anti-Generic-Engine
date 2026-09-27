import os, sys, json, urllib.request

API = "http://localhost:8001/api"

def call(method, path, body=None, token=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None)
    req.add_header("Content-Type", "application/json")
    if token: req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=280) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())

s, auth = call("POST", "/auth/login", {"email": "demo@antigeneric.app", "password": "Demo1234!"})
token = auth["token"]; print("login", s)
s, wf = call("POST", "/workflow", {"idea": "A pocket notebook brand for chefs who think in flavours, not recipes.", "audience": "Working line cooks and chefs", "constraints": "Must feel like a tool, never a lifestyle product."}, token)
print("workflow", s, wf.get("title"), len(wf.get("stages", [])))
wid = wf["id"]
s, c = call("POST", f"/workflows/{wid}/chat", {"message": "Give me three name options that respect the constraint."}, token)
print("chat1", s, len(c["messages"]), c["messages"][-1]["content"][:160])
s, c = call("POST", f"/workflows/{wid}/chat", {"message": "Which of those three did you like most and why?"}, token)
print("chat2 (memory)", s, len(c["messages"]), c["messages"][-1]["content"][:200])
s, lst = call("GET", "/workflows", None, token); print("list", s, [(x["title"], x["message_count"]) for x in lst])
s, r = call("PATCH", f"/workflows/{wid}", {"title": "Chef Notebook"}, token); print("rename", s, r["title"])
s, g = call("GET", f"/workflows/{wid}", None, token); print("get", s, g["title"], len(g["messages"]))
