import tensorflow as tf
from PIL import Image
import numpy as np
import io
from app.core.config import settings

print("Loading EfficientNet CV Model (This may take a moment)...")
cv_model = tf.keras.models.load_model(settings.MODEL_PATH, compile=False)

CLASS_MAPPING = {
    0: "Eczema",
    1: "Warts / Molluscum (Viral Infection)",
    2: "Melanoma",
    3: "Atopic Dermatitis",
    4: "Basal Cell Carcinoma",
    5: "Melanocytic Nevus",
    6: "Benign Keratosis",
    7: "Psoriasis / Lichen Planus",
    8: "Seborrheic Keratosis",
    9: "Tinea / Ringworm (Fungal Infection)"
}


def analyze_image(image_bytes: bytes) -> tuple[str, float]:
    """Processes the image bytes and returns the predicted disease and confidence."""
    # 1. Prepare image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))

    img_array = tf.keras.utils.img_to_array(image)
    img_array = tf.expand_dims(img_array, 0)

    # 2. Predict
    predictions = cv_model.predict(img_array)
    confidence = float(np.max(predictions[0]))
    class_index = int(np.argmax(predictions[0]))

    predicted_disease = CLASS_MAPPING[class_index]

    return predicted_disease, confidence
