from flask import Blueprint, render_template, request, flash
from app.utils.image_handler import process_image
from app.utils.celebrity_detector import CelebrityDetector
from app.utils.qa_engine import QAEngine
import base64

# Define blueprint
main = Blueprint("main", __name__)

# Initialize core engines once (for performance)
celebrity_detector = CelebrityDetector()
qa_engine = QAEngine()


@main.route("/", methods=["GET", "POST"])
def index():
    player_info = ""
    result_img_data = ""
    user_question = ""
    answer = ""

    if request.method == "POST":
        # Case 1: User uploaded a new image
        if "image" in request.files:
            image_file = request.files["image"]

            if image_file and image_file.filename != "":
                try:
                    img_bytes, face_box = process_image(image_file)
                    player_info, player_name = celebrity_detector.identify(img_bytes)

                    if face_box is not None:
                        # Convert processed image to base64 for display
                        result_img_data = base64.b64encode(img_bytes).decode()
                    else:
                        player_info = "No face detected. Please try another image."
                except Exception as e:
                    player_info = f"❌ Error processing image: {str(e)}"
            else:
                player_info = "Please select an image before submitting."

        # Case 2: User asked a question
        elif "question" in request.form:
            user_question = request.form["question"].strip()
            player_name = request.form.get("player_name", "").strip()
            player_info = request.form.get("player_info", "")
            result_img_data = request.form.get("result_img_data", "")

            if user_question and player_name:
                try:
                    answer = qa_engine.ask_about_celebrity(player_name, user_question)
                except Exception as e:
                    answer = f"⚠️ Could not generate an answer: {str(e)}"
            else:
                answer = "Please upload a celebrity image before asking a question."

    return render_template(
        "index.html",
        player_info=player_info,
        result_img_data=result_img_data,
        user_question=user_question,
        answer=answer,
    )
