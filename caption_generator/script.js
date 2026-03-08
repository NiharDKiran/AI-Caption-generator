const BACKEND_URL = "http://localhost:5000";

document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const imageInput = document.getElementById("imageInput");
  const captionText = document.getElementById("captionText");
  const previewImg = document.getElementById("previewImg");

  if (!imageInput.files[0]) {
    captionText.innerText = "Please upload an image.";
    return;
  }

  const file = imageInput.files[0];
  const reader = new FileReader();

  reader.onloadend = async function () {
    console.log("Image loaded, showing preview...");
    previewImg.src = reader.result;
    previewImg.style.display = "block";
    captionText.innerText = "Generating caption...";

    try {
      // Upload image to backend
      console.log("Uploading image to backend...");
      const formData = new FormData();
      formData.append("image", file);

      const uploadResponse = await fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        body: formData
      });

      console.log("Upload response status:", uploadResponse.status);

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(`Upload failed (${uploadResponse.status}): ${errorData.error || "Unknown error"}`);
      }

      const uploadData = await uploadResponse.json();
      const filename = uploadData.filename;
      console.log("Image uploaded successfully. Filename:", filename);

      // Generate caption using the uploaded image
      console.log("Generating caption...");
      const captionResponse = await fetch(`${BACKEND_URL}/generate_caption`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          image: filename
        })
      });

      console.log("Caption response status:", captionResponse.status);

      if (!captionResponse.ok) {
        const errorData = await captionResponse.json();
        throw new Error(`Caption generation failed (${captionResponse.status}): ${errorData.error || "Unknown error"}`);
      }

      const captionData = await captionResponse.json();
      console.log("Caption received:", captionData.caption);
      captionText.innerText = captionData.caption;
    } catch (error) {
      console.error("Error:", error);
      captionText.innerText = "Error: " + error.message;
    }
  };

  reader.onerror = function() {
    console.error("Error reading file");
    captionText.innerText = "Error: Could not read file";
  };

  reader.readAsDataURL(file);
});