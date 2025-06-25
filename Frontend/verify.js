// === Signup & Login Logic ===
document.querySelector('.signup-form')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const [username, email, password] = [this[0].value, this[1].value, this[2].value];
    if (username && email && password) {
        window.location.href = 'upload.html';
    } else {
        alert('Please fill in all fields.');
    }
});

document.querySelector('.login-form')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const [email, password] = [this[0].value, this[1].value];
    if (email && password) {
        window.location.href = 'upload.html';
    } else {
        alert('Please fill in all fields.');
    }
});

// === Face Capture and Upload Logic ===
document.addEventListener("DOMContentLoaded", () => {
    const passportUpload = document.getElementById("passportUpload");
    const captureBtn = document.getElementById("captureBtn");
    const submitBtn = document.getElementById("submitBtn");
    const webcam = document.getElementById("webcam");
    const canvas = document.getElementById("capturedImage");
    const resultDiv = document.getElementById("result");
    let capturedImageData = null;

    // Webcam Initialization
    function initWebcam() {
        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => webcam.srcObject = stream)
                .catch(err => console.error("Webcam not accessible", err));
        } else {
            console.error("getUserMedia not supported in this browser.");
        }
    }

    // Capture Image from Webcam
    function captureImage() {
        const context = canvas.getContext("2d");
        canvas.width = webcam.videoWidth;
        canvas.height = webcam.videoHeight;
        context.drawImage(webcam, 0, 0, canvas.width, canvas.height);
        capturedImageData = canvas.toDataURL("image/png");
    }

    // Convert Base64 to Blob
    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(",")[1]);
        const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
        const buffer = new ArrayBuffer(byteString.length);
        const array = new Uint8Array(buffer);
        for (let i = 0; i < byteString.length; i++) {
            array[i] = byteString.charCodeAt(i);
        }
        return new Blob([buffer], { type: mimeString });
    }

    // Submit to Backend for Verification
    async function submitVerification() {
        if (!passportUpload?.files[0]) {
            resultDiv.innerHTML = "❌ Please upload a passport document.";
            return;
        }

        if (!capturedImageData) {
            resultDiv.innerHTML = "❌ Please capture a real-time face.";
            return;
        }

        const formData = new FormData();
        formData.append("file", passportUpload.files[0]);
        formData.append("captured_image", dataURItoBlob(capturedImageData));
        resultDiv.innerHTML = "⏳ Verifying...";

        try {
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                resultDiv.innerHTML = `❌ Error: ${data.error}`;
                return;
            }

            resultDiv.innerHTML = `
                <strong>Verification Result:</strong> ${data.verification_result === "Match" ? "✅ Face Matched" : "❌ No Match"}<br>
                <strong>Passport Number:</strong> ${data.passport_number || "Not Found"}<br>
                <strong>Document Hash:</strong> ${data.hash}<br>
                <p><strong>QR Code:</strong><br><img src="${data.qr_code}" alt="QR Code"></p>
                <p><strong>Extracted Face:</strong><br><img src="${data.face_image}" alt="Extracted Face"></p>
                <p><strong>Real-time Captured Face:</strong><br><img src="${data.real_time_face}" alt="Captured Face"></p>
            `;
        } catch (error) {
            console.error("Error:", error);
            resultDiv.innerHTML = "❌ Error during verification.";
        }
    }

    // Attach Event Listeners (if DOM elements exist)
    if (captureBtn && submitBtn && webcam && canvas && resultDiv && passportUpload) {
        initWebcam();
        captureBtn.addEventListener("click", captureImage);
        submitBtn.addEventListener("click", submitVerification);
    }
});
