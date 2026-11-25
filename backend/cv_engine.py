"""
Siddha AI - Computer Vision Engine (Neerkuri & Neikuri)
------------------------------------------------------
Provides OpenCV-based image quality assessment, segmentation, and feature extraction
for traditional Siddha urine (Neerkuri) and oil-drop pattern (Neikuri) photographs.

NOTE:
Features extracted by this module are quantitative image-processing proxies for
digitization and demonstration. They do not constitute certified clinical diagnostics.
"""

import io
import base64
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import cv2
from PIL import Image

# Quality Thresholds
MIN_RESOLUTION = (120, 120)
MAX_RESOLUTION = (4500, 4500)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
BLUR_THRESHOLD = 75.0  # Laplacian variance threshold
UNDEREXPOSURE_THRESHOLD = 45.0  # Mean brightness minimum
OVEREXPOSURE_THRESHOLD = 220.0  # Mean brightness maximum


def validate_and_decode_image(img_bytes: bytes) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Validates file payload size, decodes bytes into OpenCV BGR numpy array,
    and checks image resolution.
    """
    if len(img_bytes) == 0:
        raise ValueError("Uploaded file is empty (0 bytes).")
    if len(img_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size exceeds 10 MB limit ({len(img_bytes) / 1024 / 1024:.2f} MB).")

    # Decode using OpenCV
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        # Fallback to Pillow in case of unusual formats (e.g. RGBA/WebP)
        try:
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"Unsupported or corrupted image format: {e}")

    h, w, c = img_bgr.shape
    if h < MIN_RESOLUTION[0] or w < MIN_RESOLUTION[1]:
        raise ValueError(f"Image resolution too low ({w}x{h}). Minimum required is 120x120.")
    if h > MAX_RESOLUTION[0] or w > MAX_RESOLUTION[1]:
        # Resize safely to keep memory within limits
        scale = min(1600 / w, 1600 / h)
        img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        h, w, c = img_bgr.shape

    info = {
        "width": int(w),
        "height": int(h),
        "channels": int(c),
        "byte_size": len(img_bytes),
    }
    return img_bgr, info


def assess_image_quality(img_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Evaluates image blurriness, illumination/exposure, and contrast.
    Returns quantitative quality metrics, warnings, and overall suitability score.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Blur evaluation via variance of Laplacian
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = laplacian_var < BLUR_THRESHOLD

    # 2. Exposure evaluation
    mean_brightness = float(np.mean(gray))
    is_underexposed = mean_brightness < UNDEREXPOSURE_THRESHOLD
    is_overexposed = mean_brightness > OVEREXPOSURE_THRESHOLD

    # 3. Contrast evaluation (RMS contrast)
    rms_contrast = float(np.std(gray))
    is_low_contrast = rms_contrast < 25.0

    # Quality warnings
    warnings: List[str] = []
    if is_blurry:
        warnings.append(f"Image may be blurry (sharpness score: {laplacian_var:.1f}). Recommend capturing a stable, focused shot.")
    if is_underexposed:
        warnings.append("Sample appears underexposed / dark. Ensure uniform diffuse lighting.")
    if is_overexposed:
        warnings.append("Sample appears overexposed / washed out. Avoid direct camera flash glare.")
    if is_low_contrast:
        warnings.append("Low contrast detected between sample and background.")

    # Composite Quality Score (0 to 100)
    score = 100.0
    if is_blurry:
        score -= min(40.0, 40.0 * (1.0 - laplacian_var / BLUR_THRESHOLD))
    if is_underexposed:
        score -= 25.0
    if is_overexposed:
        score -= 25.0
    if is_low_contrast:
        score -= 15.0

    quality_score = max(10.0, min(100.0, round(score, 1)))

    return {
        "quality_score": quality_score,
        "sharpness_laplacian": round(laplacian_var, 2),
        "mean_brightness": round(mean_brightness, 2),
        "contrast_rms": round(rms_contrast, 2),
        "is_blurry": is_blurry,
        "is_underexposed": is_underexposed,
        "is_overexposed": is_overexposed,
        "is_acceptable": quality_score >= 50.0,
        "warnings": warnings,
    }


def classify_siddha_urine_color(hue_norm: float, sat_norm: float, val_norm: float) -> str:
    """
    Maps normalized HSV values (H: 0-60, S: 0-100, V: 0-100) to Siddha color classifications:
    Pale Yellow, Yellow, Amber, Dark Amber, Reddish, Brownish.
    """
    if val_norm < 35.0:
        return "Brownish"
    if hue_norm < 18.0:
        return "Reddish"
    if hue_norm < 34.0:
        return "Dark Amber" if sat_norm > 50.0 or val_norm < 65.0 else "Amber"
    if hue_norm < 46.0:
        return "Amber" if sat_norm > 65.0 else "Yellow"
    return "Pale Yellow" if sat_norm < 45.0 else "Yellow"


def analyze_neerkuri_image(img_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Analyzes urine photograph (Neerkuri examination):
    - HSV color calibration and color category assignment
    - Transparency & turbidity assessment
    - Meniscus foam detection & bubble coverage estimation
    - Annotated preview with segmented foam/sample region
    """
    quality = assess_image_quality(img_bgr)
    h, w, _ = img_bgr.shape

    # Focus on central liquid region (crop margins to exclude beaker/container borders)
    margin_y = int(h * 0.15)
    margin_x = int(w * 0.15)
    crop = img_bgr[margin_y : h - margin_y, margin_x : w - margin_x]
    if crop.size == 0:
        crop = img_bgr

    # Color extraction in HSV space
    hsv_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mean_h = float(np.median(hsv_crop[..., 0]))  # OpenCV H is 0-179
    mean_s = float(np.mean(hsv_crop[..., 1]))    # OpenCV S is 0-255
    mean_v = float(np.mean(hsv_crop[..., 2]))    # OpenCV V is 0-255

    # Normalize to project scale: H: 0-60 (yellow-amber range), S: 0-100, V: 0-100
    norm_h = round(float(np.clip((mean_h / 179.0) * 60.0, 0, 60)), 1)
    norm_s = round(float(np.clip((mean_s / 255.0) * 100.0, 0, 100)), 1)
    norm_v = round(float(np.clip((mean_v / 255.0) * 100.0, 0, 100)), 1)

    predicted_color = classify_siddha_urine_color(norm_h, norm_s, norm_v)

    # Transparency Score (1-10): based on contrast uniformity and edge gradients
    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    sobel_edges = cv2.Sobel(gray_crop, cv2.CV_64F, 1, 1, ksize=3)
    edge_energy = float(np.mean(np.abs(sobel_edges)))
    # High edge energy/turbidity inside the liquid indicates low transparency
    transparency_score = float(np.clip(10.0 - (edge_energy / 8.0), 1.0, 10.0))

    # Foam Detection (upper 35% of sample where foam typically sits)
    upper_h = int(crop.shape[0] * 0.35)
    upper_region = crop[:upper_h, :]
    upper_gray = cv2.cvtColor(upper_region, cv2.COLOR_BGR2GRAY)

    # Foam appears as high-frequency bright/textured bubble clusters
    blurred_upper = cv2.GaussianBlur(upper_gray, (5, 5), 0)
    _, foam_thresh = cv2.threshold(
        blurred_upper, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Morphological clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    foam_mask = cv2.morphologyEx(foam_thresh, cv2.MORPH_OPEN, kernel)

    foam_pixels = int(cv2.countNonZero(foam_mask))
    total_upper_pixels = upper_gray.shape[0] * upper_gray.shape[1]
    raw_foam_pct = (foam_pixels / max(1, total_upper_pixels)) * 100.0
    foam_percentage = round(float(np.clip(raw_foam_pct * 0.8, 0.0, 100.0)), 1)

    # Bubble count via connected components with size filtering
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(foam_mask)
    bubble_count = 0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if 8 < area < 400:  # Bubble size range
            bubble_count += 1
    bubble_count = min(250, bubble_count * 2)

    # Estimate sediment percentage (lower 20% opacity check)
    lower_h = int(crop.shape[0] * 0.8)
    lower_region = crop[lower_h:, :]
    lower_gray = cv2.cvtColor(lower_region, cv2.COLOR_BGR2GRAY)
    sediment_var = float(np.std(lower_gray))
    sediment_pct = round(float(np.clip((sediment_var / 35.0) * 30.0, 2.0, 65.0)), 1)

    # Generate annotated visualization
    vis = crop.copy()
    cv2.rectangle(vis, (0, 0), (vis.shape[1], upper_h), (0, 200, 255), 2)
    cv2.putText(vis, f"Foam Zone: {foam_percentage}%", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
    cv2.rectangle(vis, (0, lower_h), (vis.shape[1], vis.shape[0]), (255, 100, 0), 2)
    cv2.putText(vis, f"Sediment Zone: {sediment_pct}%", (10, vis.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)

    preview_b64 = encode_cv_image_base64(vis)

    return {
        "modality": "neerkuri",
        "quality": quality,
        "extracted_features": {
            "urine_color": predicted_color,
            "HSV_H": norm_h,
            "HSV_S": norm_s,
            "HSV_V": norm_v,
            "transparency_score": round(transparency_score, 1),
            "foam_percentage": foam_percentage,
            "foam_bubble_count": bubble_count,
            "sediment_percentage": sediment_pct,
        },
        "annotated_preview_base64": preview_b64,
        "disclaimer": "Computer vision estimates are algorithmic proxies for demonstration.",
    }


def analyze_neikuri_image(img_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Analyzes sesame oil drop pattern on urine surface (Neikuri examination):
    - Segments the oil drop boundary from surface reflection
    - Extracts geometric morphology: circularity, aspect ratio, solidity, roughness, branching
    - Classifies shape profile (Circular, Ring, Spiral, Lotus, Snake, Branched, Irregular)
    - Returns annotated segmentation mask and contour overlay
    """
    quality = assess_image_quality(img_bgr)
    h, w, _ = img_bgr.shape

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Adaptive / Otsu Thresholding to isolate oil droplet
    _, thresh_inv = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, thresh_norm = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphological filtering to clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    clean_mask = cv2.morphologyEx(thresh_inv, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, hierarchy = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Fallback to normal threshold if inverted threshold captured border
    if not contours or cv2.contourArea(max(contours, key=cv2.contourArea)) < 150:
        clean_mask = cv2.morphologyEx(thresh_norm, cv2.MORPH_OPEN, kernel)
        contours, hierarchy = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = img_bgr.copy()
    defaults = {
        "circularity": 0.70,
        "symmetry_score": 6.5,
        "branch_count": 2,
        "edge_roughness": 3.0,
        "oil_spread_diameter_mm": 18.0,
        "fractal_dimension": 1.20,
        "oil_shape": "Ring",
    }

    if not contours:
        preview_b64 = encode_cv_image_base64(vis)
        return {
            "modality": "neikuri",
            "quality": quality,
            "extracted_features": defaults,
            "annotated_preview_base64": preview_b64,
            "segmentation_detected": False,
            "message": "No distinct oil drop contour segmented; using default prototype features.",
        }

    # Extract dominant contour (largest non-border area)
    total_img_area = float(h * w)
    valid_contours = [c for c in contours if 100 < cv2.contourArea(c) < 0.95 * total_img_area]

    if not valid_contours:
        c = max(contours, key=cv2.contourArea)
    else:
        c = max(valid_contours, key=cv2.contourArea)

    area = float(cv2.contourArea(c))
    perimeter = float(cv2.arcLength(c, True))

    # 1. Circularity: 4 * pi * Area / Perimeter^2
    circularity = 0.5
    if perimeter > 0:
        circularity = float(np.clip(4.0 * np.pi * area / (perimeter ** 2), 0.05, 1.0))

    # 2. Convex Hull & Solidity
    hull = cv2.convexHull(c)
    hull_area = float(cv2.contourArea(hull))
    solidity = float(area / max(1.0, hull_area))

    # 3. Bounding box & Aspect Ratio
    x, y, bw, bh = cv2.boundingRect(c)
    aspect_ratio = float(bw) / float(max(1, bh))

    # 4. Roughness / Edge Jaggedness (perimeter ratio to hull perimeter)
    hull_perimeter = float(cv2.arcLength(hull, True))
    edge_roughness = float(np.clip(((perimeter / max(1.0, hull_perimeter)) - 1.0) * 15.0 + 1.0, 1.0, 10.0))

    # 5. Branch count via Convexity Defects
    branch_count = 0
    try:
        hull_indices = cv2.convexHull(c, returnPoints=False)
        if len(hull_indices) > 3 and len(c) > 3:
            defects = cv2.convexityDefects(c, hull_indices)
            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    # d is distance in 1/256th pixels
                    depth_px = d / 256.0
                    if depth_px > 10.0:  # significant protrusion / branch defect
                        branch_count += 1
    except Exception:
        branch_count = max(0, int((1.0 - circularity) * 10))

    branch_count = min(12, branch_count)

    # 6. Radial Symmetry (variance of radial distance from centroid)
    M = cv2.moments(c)
    if M["m00"] > 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        cx, cy = x + bw // 2, y + bh // 2

    # Measure distances from centroid to contour points
    pts = c.reshape(-1, 2)
    dists = np.sqrt((pts[:, 0] - cx) ** 2 + (pts[:, 1] - cy) ** 2)
    dist_std = float(np.std(dists))
    dist_mean = float(np.mean(dists)) if len(dists) > 0 else 1.0
    symmetry_score = float(np.clip(10.0 - (dist_std / max(1.0, dist_mean) * 12.0), 1.0, 10.0))

    # 7. Spread Diameter Proxy (mm, scaled relative to typical Petri dish diameter ~60mm)
    spread_diameter_px = 2.0 * np.sqrt(area / np.pi)
    # Estimate mm assuming standard frame width ~ 100mm
    spread_diameter_mm = float(np.clip((spread_diameter_px / max(1, w)) * 80.0, 4.0, 32.0))

    # 8. Fractal Dimension Proxy (box-counting approximation)
    fractal_dim = round(float(np.clip(1.0 + (edge_roughness / 12.0) + (1.0 - circularity) * 0.4, 1.02, 1.95)), 2)

    # 9. Neikuri Shape Classification rule
    if circularity > 0.82 and solidity > 0.90:
        shape_class = "Circular"
    elif circularity > 0.65 and 0.80 <= aspect_ratio <= 1.25:
        shape_class = "Ring"
    elif branch_count >= 5 or (circularity < 0.45 and edge_roughness > 5.5):
        shape_class = "Branched"
    elif circularity < 0.40 and solidity < 0.65:
        shape_class = "Irregular"
    elif 0.35 <= aspect_ratio <= 0.65 or 1.55 <= aspect_ratio <= 2.8:
        shape_class = "Snake"
    elif branch_count in [3, 4] and circularity > 0.50:
        shape_class = "Lotus"
    elif circularity > 0.70:
        shape_class = "Pearl"
    else:
        shape_class = "Spiral"

    # Annotate visual preview with contour, hull, and centroid
    cv2.drawContours(vis, [hull], -1, (0, 215, 255), 2)  # Gold convex hull
    cv2.drawContours(vis, [c], -1, (63, 110, 82), 3)     # Herbal green contour
    cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)        # Centroid
    cv2.putText(vis, f"Shape: {shape_class} (Circ: {circularity:.2f})", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    preview_b64 = encode_cv_image_base64(vis)

    return {
        "modality": "neikuri",
        "quality": quality,
        "extracted_features": {
            "oil_shape": shape_class,
            "circularity": round(circularity, 2),
            "solidity": round(solidity, 2),
            "symmetry_score": round(symmetry_score, 1),
            "branch_count": int(branch_count),
            "edge_roughness": round(edge_roughness, 1),
            "oil_spread_diameter_mm": round(spread_diameter_mm, 1),
            "fractal_dimension": fractal_dim,
        },
        "annotated_preview_base64": preview_b64,
        "segmentation_detected": True,
        "disclaimer": "Neikuri geometric features are derived via OpenCV contour segmentation for academic analysis.",
    }


def encode_cv_image_base64(img_bgr: np.ndarray, max_dim: int = 500) -> str:
    """Resizes and encodes an OpenCV image to base64 JPEG data URL."""
    h, w = img_bgr.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    success, buffer = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not success:
        return ""
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"
