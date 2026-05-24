import cv2
import numpy as np
from collections import Counter
from .utils import resize_for_speed, to_percent


def _gray(img):
    return cv2.cvtColor(resize_for_speed(img), cv2.COLOR_BGR2GRAY)


def _feature_detector(name: str):
    name = name.upper()
    if name == "SIFT" and hasattr(cv2, "SIFT_create"):
        return cv2.SIFT_create(nfeatures=2500), cv2.NORM_L2, "SIFT"
    if name == "SURF":
        try:
            detector = cv2.xfeatures2d.SURF_create(400)
            return detector, cv2.NORM_L2, "SURF"
        except Exception:
            # SURF çoğu OpenCV paketinde nonfree olduğu için kapalı gelir.
            # Programın bozulmaması için SIFT fallback kullanılır.
            if hasattr(cv2, "SIFT_create"):
                return cv2.SIFT_create(nfeatures=2500), cv2.NORM_L2, "SURF (SIFT fallback)"
            return cv2.ORB_create(nfeatures=2500), cv2.NORM_HAMMING, "SURF (ORB fallback)"
    if name == "AKAZE":
        return cv2.AKAZE_create(), cv2.NORM_HAMMING, "AKAZE"
    return cv2.ORB_create(nfeatures=3000), cv2.NORM_HAMMING, "ORB"


def _score_from_metrics(match_count, cluster_count, changed_ratio=0.0, inlier_ratio=0.0):
    score = 0.0
    score += min(match_count / 80.0, 1.0) * 0.25
    score += min(cluster_count / 18.0, 1.0) * 0.35
    score += min(changed_ratio / 0.18, 1.0) * 0.25
    score += max(0.0, 1.0 - inlier_ratio) * 0.15 if inlier_ratio else 0.0
    return float(np.clip(score, 0, 1))


def detect_copy_move(img, algorithm="SIFT"):
    gray = _gray(img)
    detector, norm, label = _feature_detector(algorithm)
    keypoints, descriptors = detector.detectAndCompute(gray, None)

    if descriptors is None or len(keypoints) < 8:
        return {
            "algorithm": label,
            "tampered": False,
            "confidence": 0.0,
            "keypoints": len(keypoints) if keypoints else 0,
            "matches": 0,
            "cluster_matches": 0,
            "message": "Yeterli ayırt edici nokta bulunamadı."
        }, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    matcher = cv2.BFMatcher(norm, crossCheck=False)
    k = min(3, max(2, len(descriptors)))
    raw = matcher.knnMatch(descriptors, descriptors, k=k)

    good = []
    for group in raw:
        for m in group[1:]:
            p1 = np.array(keypoints[m.queryIdx].pt)
            p2 = np.array(keypoints[m.trainIdx].pt)
            dist = np.linalg.norm(p1 - p2)
            if 25 < dist < max(gray.shape) * 0.75:
                good.append((m, p1, p2))
                break

    # Aynı kaydırma vektörüne sahip eşleşme kümeleri copy-move belirtisidir.
    vectors = []
    for _, p1, p2 in good:
        dx, dy = p2 - p1
        vectors.append((round(dx / 12) * 12, round(dy / 12) * 12))
    cluster_count = Counter(vectors).most_common(1)[0][1] if vectors else 0

    confidence = _score_from_metrics(len(good), cluster_count)
    tampered = confidence >= 0.45 and cluster_count >= 8

    vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    draw_matches = sorted(good, key=lambda x: x[0].distance)[:60]
    for _, p1, p2 in draw_matches:
        color = (0, 0, 255) if tampered else (0, 180, 0)
        cv2.circle(vis, tuple(np.int32(p1)), 4, color, 1)
        cv2.circle(vis, tuple(np.int32(p2)), 4, color, 1)
        cv2.line(vis, tuple(np.int32(p1)), tuple(np.int32(p2)), color, 1)

    return {
        "algorithm": label,
        "tampered": bool(tampered),
        "confidence": to_percent(confidence / 1.0),
        "keypoints": len(keypoints),
        "matches": len(good),
        "cluster_matches": int(cluster_count),
        "message": "Kopyala-yapıştır/sahtecilik izi bulundu." if tampered else "Güçlü sahtecilik izi bulunmadı."
    }, vis


def compare_images(original, suspect, algorithm="SIFT"):
    img1 = resize_for_speed(original)
    img2 = resize_for_speed(suspect)
    g1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    detector, norm, label = _feature_detector(algorithm)
    kp1, des1 = detector.detectAndCompute(g1, None)
    kp2, des2 = detector.detectAndCompute(g2, None)

    aligned = img2.copy()
    inlier_ratio = 0.0
    match_count = 0
    if des1 is not None and des2 is not None and len(kp1) >= 8 and len(kp2) >= 8:
        matcher = cv2.BFMatcher(norm)
        pairs = matcher.knnMatch(des1, des2, k=2)
        good = []
        for pair in pairs:
            if len(pair) == 2 and pair[0].distance < 0.75 * pair[1].distance:
                good.append(pair[0])
        match_count = len(good)
        if len(good) >= 8:
            src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            H, mask = cv2.findHomography(dst, src, cv2.RANSAC, 5.0)
            if H is not None:
                aligned = cv2.warpPerspective(img2, H, (img1.shape[1], img1.shape[0]))
                inlier_ratio = float(mask.sum() / len(mask)) if mask is not None else 0.0

    if aligned.shape[:2] != img1.shape[:2]:
        aligned = cv2.resize(aligned, (img1.shape[1], img1.shape[0]))

    diff = cv2.absdiff(img1, aligned)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_diff, (5, 5), 0)
    _, mask = cv2.threshold(blur, 30, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)
    changed_ratio = float(np.count_nonzero(mask) / mask.size)
    confidence = _score_from_metrics(match_count, 0, changed_ratio, inlier_ratio)
    tampered = changed_ratio >= 0.025 or confidence >= 0.42

    heat = img1.copy()
    heat[mask > 0] = (0, 0, 255)
    overlay = cv2.addWeighted(img1, 0.65, heat, 0.35, 0)

    return {
        "algorithm": label,
        "tampered": bool(tampered),
        "confidence": to_percent(confidence),
        "matches": int(match_count),
        "inlier_ratio": to_percent(inlier_ratio),
        "changed_area": to_percent(changed_ratio),
        "message": "İki görüntü arasında değişiklik tespit edildi." if tampered else "Belirgin değişiklik tespit edilmedi."
    }, overlay


def ai_cnn_patch_detector(img):
    """CNN mantığına benzer patch tabanlı anomali skoru: kenar/gürültü/doku bloklarını inceler."""
    small = resize_for_speed(img, 768)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    patch = 32
    scores = []
    for y in range(0, h - patch + 1, patch):
        for x in range(0, w - patch + 1, patch):
            roi = gray[y:y + patch, x:x + patch]
            lap = cv2.Laplacian(roi, cv2.CV_64F).var()
            edges = cv2.Canny(roi, 80, 160).mean()
            scores.append([lap, edges, roi.std()])
    if not scores:
        return {"algorithm": "AI-CNN", "tampered": False, "confidence": 0.0, "message": "Görüntü çok küçük."}
    arr = np.array(scores, dtype=np.float32)
    z = np.abs((arr - arr.mean(axis=0)) / (arr.std(axis=0) + 1e-6))
    anomaly_ratio = float((z.max(axis=1) > 2.6).mean())
    confidence = float(np.clip(anomaly_ratio / 0.18, 0, 1))
    return {
        "algorithm": "AI-CNN",
        "tampered": bool(confidence >= 0.45),
        "confidence": to_percent(confidence),
        "anomaly_ratio": to_percent(anomaly_ratio),
        "message": "Patch tabanlı yapay zeka analizi şüpheli alanlar buldu." if confidence >= 0.45 else "AI-CNN analizinde güçlü şüphe bulunmadı."
    }


def ai_lstm_sequence_detector(img):
    """LSTM mantığına benzer sıralı satır/sütun tutarlılığı analizi yapar."""
    small = resize_for_speed(img, 768)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    stripe = 16
    row_features = []
    for y in range(0, gray.shape[0] - stripe + 1, stripe):
        roi = gray[y:y + stripe, :]
        row_features.append([roi.mean(), roi.std(), cv2.Laplacian(roi, cv2.CV_64F).var()])
    col_features = []
    for x in range(0, gray.shape[1] - stripe + 1, stripe):
        roi = gray[:, x:x + stripe]
        col_features.append([roi.mean(), roi.std(), cv2.Laplacian(roi, cv2.CV_64F).var()])
    seq = np.vstack([row_features, col_features]).astype(np.float32)
    if len(seq) < 4:
        return {"algorithm": "AI-LSTM", "tampered": False, "confidence": 0.0, "message": "Görüntü çok küçük."}
    diffs = np.linalg.norm(np.diff(seq, axis=0), axis=1)
    z = np.abs((diffs - diffs.mean()) / (diffs.std() + 1e-6))
    anomaly_ratio = float((z > 2.4).mean())
    confidence = float(np.clip(anomaly_ratio / 0.16, 0, 1))
    return {
        "algorithm": "AI-LSTM",
        "tampered": bool(confidence >= 0.45),
        "confidence": to_percent(confidence),
        "sequence_anomaly": to_percent(anomaly_ratio),
        "message": "Sıralı tutarlılık analizinde değişiklik şüphesi var." if confidence >= 0.45 else "AI-LSTM analizinde güçlü şüphe bulunmadı."
    }


def final_decision(results):
    numeric = [r.get("confidence", 0) for r in results]
    positives = sum(1 for r in results if r.get("tampered"))
    avg = round(float(np.mean(numeric)) if numeric else 0.0, 2)
    final = positives >= max(2, len(results) // 2)
    return {
        "tampered": bool(final),
        "confidence": avg,
        "positive_algorithms": positives,
        "total_algorithms": len(results),
        "label": "GÖRÜNTÜ DEĞİŞTİRİLMİŞ / ŞÜPHELİ" if final else "GÖRÜNTÜ TEMİZ GÖRÜNÜYOR"
    }
