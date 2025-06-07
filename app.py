import streamlit as st
import openai
from PIL import Image
import io, base64, zipfile, re
import time

st.title("GPT-4o AI Image Renamer & Zipper")

openai.api_key = "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"  # <--- YOUR KEY HERE

uploaded_files = st.file_uploader(
    "Upload images (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

def suggest_filename(image_bytes, file_ext):
    image_base64 = base64.b64encode(image_bytes).decode()
    prompt = (
        "You are an assistant that generates short, SEO-friendly, hyphenated filenames for images, "
        "based strictly on the main objects, concepts, and colors in the image. Do not use generic words. "
        "Avoid numbers, keep it lowercase, no spaces, no extension. Max 5 words, use hyphens."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Suggest a filename:"},
                    {"type": "image_url", "image_url": {"url": "data:image/"+file_ext+";base64,"+image_base64}}
                ]
            }
        ],
        max_tokens=15
    )
    name = response.choices[0].message.content.strip()
    # Remove non-filename-safe characters
    name = re.sub(r'[^a-z0-9\-]+', '', name.lower())
    return name if name else "image"

if uploaded_files:
    if st.button("Generate & Download ZIP"):
        progress = st.progress(0)
        status = st.empty()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
            for idx, file in enumerate(uploaded_files):
                file_bytes = file.read()
                file_ext = file.type.split('/')[-1]
                img = Image.open(io.BytesIO(file_bytes))
                status.text(f"Processing image {idx+1}/{len(uploaded_files)}...")
                suggested = suggest_filename(file_bytes, file_ext)
                out_name = f"{suggested}.{file_ext if file_ext != 'jpeg' else 'jpg'}"
                img_buffer = io.BytesIO()
                if file_ext == "png":
                    img.save(img_buffer, format="PNG")
                else:
                    img = img.convert("RGB")
                    img.save(img_buffer, format="JPEG")
                img_buffer.seek(0)
                zipf.writestr(out_name, img_buffer.read())
                progress.progress((idx+1) / len(uploaded_files))
                # Optionally: add small delay so the bar is visible (for demo)
                # time.sleep(0.1)

        progress.empty()
        status.success("All images processed! Click below to download.")
        zip_buffer.seek(0)
        st.download_button(
            "Download ZIP with Renamed Images",
            data=zip_buffer,
            file_name="renamed_images.zip",
            mime="application/zip"
        )
