"""Prototype of the symbol detection (state of the specification). Usage: python tools/prototype_detect.py ref/intel-x.png"""
import sys, cv2, numpy as np
from pathlib import Path

T = Path(__file__).resolve().parent.parent / "templates"
TYPES = ["paw", "tent", "axe", "skull"]

def white_mask(im):
    return cv2.inRange(cv2.cvtColor(im, cv2.COLOR_BGR2HSV), (0, 0, 215), (180, 45, 255))

def disc_saturation(im, cx, cy, r=26):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    yy, xx = np.ogrid[:im.shape[0], :im.shape[1]]
    sel = ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r) & ~(cv2.inRange(hsv, (0, 0, 200), (180, 60, 255)) > 0)
    return int(np.median(hsv[..., 1][sel]))

def green_checks(im):
    g = cv2.inRange(cv2.cvtColor(im, cv2.COLOR_BGR2HSV), (45, 120, 120), (75, 255, 255))
    g[:170] = 0; g[1050:] = 0
    n, _, st, cen = cv2.connectedComponentsWithStats(g)
    return [(int(cen[i][0]), int(cen[i][1])) for i in range(1, n) if 40 < st[i][4] < 600]

def detect(path, thr=0.75):
    im = cv2.imread(str(path)); W = white_mask(im); W[:170] = 0; W[1050:] = 0
    checks = green_checks(im); out = im.copy(); hits = []
    for k in TYPES:
        m = cv2.imread(str(T / f"{k}_mask.png"), cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(W, m, cv2.TM_CCOEFF_NORMED); h, w = m.shape
        while True:
            _, mv, _, ml = cv2.minMaxLoc(res)
            if mv < thr: break
            cx, cy = ml[0] + w // 2, ml[1] + h // 2
            res[max(0, ml[1]-20):ml[1]+20, max(0, ml[0]-20):ml[0]+20] = -1
            sat = disc_saturation(im, cx, cy)
            done = any(abs(x - (cx + 24)) < 14 and abs(y - (cy - 24)) < 14 for x, y in checks)
            status = "DONE" if done else ("RUNNING" if sat < 130 else "AVAILABLE")
            hits.append((k, cx, cy, round(mv, 2), sat, status))
            cv2.circle(out, (cx, cy), 27, (0, 0, 255) if status == "AVAILABLE" else (128, 128, 128), 2)
            cv2.putText(out, f"{k} {status}", (cx - 40, cy - 32), 0, 0.45, (0, 0, 255), 2)
    for h in sorted(hits, key=lambda t: t[2]): print(*h)
    cv2.imwrite(str(Path(path).with_suffix(".debug.png")), out)

if __name__ == "__main__":
    for p in sys.argv[1:]: print("==", p); detect(p)
