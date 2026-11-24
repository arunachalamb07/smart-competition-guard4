"""Visible laptop heartbeat agent. It does not read files, keystrokes, screen or messages."""
import argparse, platform, socket, time, requests

def main():
    p=argparse.ArgumentParser(description="Smart Guard visible laptop connection agent")
    p.add_argument("--server", default="http://127.0.0.1:5000", help="Server base URL, e.g. http://192.168.1.10:5000")
    p.add_argument("--team-code", required=True, help="Team code from judge dashboard")
    p.add_argument("--laptop-name", default=socket.gethostname(), help="Name shown on judge dashboard")
    args=p.parse_args()
    url=args.server.rstrip("/")+"/api/heartbeat"
    print("SMART COMPETITION GUARD - laptop agent")
    print("This visible agent sends only device name and connection heartbeat.")
    print("Press Ctrl+C to stop.")
    while True:
        try:
            res=requests.post(url,json={"team_code":args.team_code,"laptop_name":args.laptop_name},timeout=5)
            if res.ok:
                print(f"[CONNECTED] {args.laptop_name} | {time.strftime('%H:%M:%S')}")
            else:
                print(f"[SERVER] {res.status_code}: {res.text}")
        except requests.RequestException as exc:
            print(f"[CONNECTION LOST] {exc}")
        time.sleep(15)

if __name__=="__main__":
    main()
