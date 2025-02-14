import streamlit as st
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def compare_images(original, tampered):
    # Convert images to grayscale
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    tampered_gray = cv2.cvtColor(tampered, cv2.COLOR_BGR2GRAY)

    # Resize images to the same size
    original_gray = cv2.resize(original_gray, (tampered_gray.shape[1], tampered_gray.shape[0]))

    # Compute SSIM between the two images
    score, diff = ssim(original_gray, tampered_gray, full=True)
    diff = (diff * 255).astype("uint8")

    # Apply thresholding to highlight differences
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY_INV)

    # Find contours of differences
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes around detected differences
    result = tampered.copy()
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Ignore small contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red bounding box

    return score, diff, thresh, result

# Streamlit App UI
st.set_page_config(page_title="PAN Card Tampering Detection", layout="wide")

st.title("PAN Card Tampering Detection App")
st.write("Upload an **original** and a **tampered** PAN card to check for modifications.")

col1, col2 = st.columns(2)
with col1:
    original_file = st.file_uploader("Upload Original PAN Card", type=["jpg", "png", "jpeg"])
with col2:
    tampered_file = st.file_uploader("Upload Tampered PAN Card", type=["jpg", "png", "jpeg"])

if original_file and tampered_file:
    # Read the uploaded images
    original = cv2.imdecode(np.frombuffer(original_file.read(), np.uint8), cv2.IMREAD_COLOR)
    tampered = cv2.imdecode(np.frombuffer(tampered_file.read(), np.uint8), cv2.IMREAD_COLOR)

    if original is not None and tampered is not None:
        # Compare the images
        score, diff, thresh, result = compare_images(original, tampered)

        # Display results
        st.subheader(f"🔍 Structural Similarity Index (SSIM): {score:.4f}")

        # Status message based on SSIM score
        if score < 0.95:
            st.error("⚠️ **Tampering Detected!** The images show significant differences.")
        else:
            st.success("✅ **No Tampering Detected.** The images are nearly identical.")

        # Display images
        st.subheader("📊 Visual Comparison")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.image(original, caption="Original PAN Card", use_container_width=True)
        with col2:
            st.image(tampered, caption="Tampered PAN Card", use_container_width=True)
        with col3:
            st.image(diff, caption="Difference Map", use_container_width=True)
        with col4:
            st.image(thresh, caption="Thresholded Differences", use_container_width=True)

        # Highlighted tampering result
        st.subheader("🔴 Tampered Regions Highlighted")
        st.image(result, caption="Tampered Image with Marked Differences", use_container_width=True)

st.write("🛡️ This tool helps in **fraud detection** and **document verification** by ensuring fast and accurate authenticity checks.")
