import cv2, numpy as np, sys

def order(pts):
    s = pts.sum(1); d = np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], dtype="float32")

def find_page(img):
    h, w = img.shape[:2]
    sc = 800 / max(h, w)
    small = cv2.resize(img, None, fx=sc, fy=sc)
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (9, 9), 0)
    _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    cs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs: return None
    c = max(cs, key=cv2.contourArea)
    if cv2.contourArea(c) < 0.4 * small.shape[0] * small.shape[1]: return None
    peri = cv2.arcLength(c, True)
    ap = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(ap) != 4:
        ap = cv2.boxPoints(cv2.minAreaRect(c)).reshape(-1, 1, 2)
    return order(ap.reshape(4, 2) / sc)

def warp(img, q):
    tl, tr, br, bl = q
    W = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    H = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    M = cv2.getPerspectiveTransform(q, np.array([[0, 0], [W, 0], [W, H], [0, H]], dtype="float32"))
    return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_CUBIC)

def enhance(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = g.shape
    f = 6
    sm = cv2.resize(g, (w // f, h // f), interpolation=cv2.INTER_AREA)
    sm = cv2.morphologyEx(sm, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))  # efface le texte
    sm = cv2.GaussianBlur(sm, (0, 0), 6)
    bg = cv2.resize(sm, (w, h), interpolation=cv2.INTER_CUBIC)
    norm = cv2.divide(g, bg, scale=255)
    norm = np.clip((norm.astype(np.float32) - 130) * (255 / (240 - 130)), 0, 255).astype(np.uint8)
    blur = cv2.GaussianBlur(norm, (0, 0), 2)
    return cv2.addWeighted(norm, 1.5, blur, -0.5, 0)

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    img = cv2.imread(src)
    q = find_page(img)
    print("page détectée:", q is not None)
    if q is not None:
        m = 25
        img = warp(img, q)[m:-m, m + 60:-m]
    out = enhance(img)
    cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(out.shape)
