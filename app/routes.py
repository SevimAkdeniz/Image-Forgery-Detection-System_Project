from pathlib import Path
from flask import Blueprint, render_template, request, current_app, url_for
from werkzeug.utils import secure_filename
from .utils import allowed_file, unique_name, read_image, save_result_image
from .detectors import (
    detect_copy_move,
    compare_images,
    ai_cnn_patch_detector,
    ai_lstm_sequence_detector,
    final_decision,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    error = None
    payload = None
    if request.method == "POST":
        original_file = request.files.get("original_image")
        suspect_file = request.files.get("suspect_image")

        if not suspect_file or suspect_file.filename == "":
            error = "Lütfen en az bir şüpheli görüntü yükleyin."
            return render_template("index.html", error=error)

        files_to_save = [suspect_file]
        if original_file and original_file.filename:
            files_to_save.append(original_file)

        for f in files_to_save:
            if not allowed_file(f.filename):
                error = "Desteklenmeyen dosya formatı. jpg, png, webp, gif, bmp, tif kullanılabilir."
                return render_template("index.html", error=error)

        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        result_dir = Path(current_app.config["RESULT_FOLDER"])

        suspect_name = unique_name(secure_filename(suspect_file.filename))
        suspect_path = upload_dir / suspect_name
        suspect_file.save(suspect_path)
        suspect_img = read_image(str(suspect_path))

        original_img = None
        original_url = None
        if original_file and original_file.filename:
            original_name = unique_name(secure_filename(original_file.filename))
            original_path = upload_dir / original_name
            original_file.save(original_path)
            original_img = read_image(str(original_path))
            original_url = url_for("static", filename=f"uploads/{original_name}")

        results = []
        visual_urls = []
        algorithms = ["SIFT", "SURF", "AKAZE", "ORB"]

        for alg in algorithms:
            if original_img is not None:
                result, visual = compare_images(original_img, suspect_img, alg)
            else:
                result, visual = detect_copy_move(suspect_img, alg)
            out_name = f"{Path(suspect_name).stem}_{alg.lower()}_result.jpg"
            save_result_image(str(result_dir / out_name), visual)
            results.append(result)
            visual_urls.append({"algorithm": result["algorithm"], "url": url_for("static", filename=f"results/{out_name}")})

        ai1 = ai_cnn_patch_detector(suspect_img)
        ai2 = ai_lstm_sequence_detector(suspect_img)
        results.extend([ai1, ai2])

        decision = final_decision(results)
        payload = {
            "suspect_url": url_for("static", filename=f"uploads/{suspect_name}"),
            "original_url": original_url,
            "mode": "Orijinal + Şüpheli Karşılaştırma" if original_img is not None else "Tek Görsel Copy-Move Analizi",
            "results": results,
            "visuals": visual_urls,
            "decision": decision,
        }

    return render_template("index.html", error=error, payload=payload)
