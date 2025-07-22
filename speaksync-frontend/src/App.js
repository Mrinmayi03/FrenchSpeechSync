import React, { useState } from "react";
import axios from "axios";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [downloadLink, setDownloadLink] = useState("");
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setDownloadLink("");
    setMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile); // ⬅️ nothing else is required

    try {
      const res = await axios.post("/process/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setDownloadLink(res.data.file_url);
      setMessage("✅ Processing finished! COPY PASTE THIS LINK INTO A NEW WINDOW TO DOWNLOAD THE TRANSLATED VIDEO:");
    } catch (err) {
      console.error(err);
      setMessage("❌ Upload / processing failed – see browser console.");
    }
  };

  return (
    <div style={{ padding: 40, textAlign: "center" }}>
      <h1>SpeakSync uploader</h1>
      <p>Please wait for some time after clicking upload for the processing to finish.</p>

      <input type="file" accept="video/mp4" onChange={handleFileChange} />
      <br />
      <br />

      <button onClick={handleUpload}>Upload</button>
      <br />
      <br />

      {message && <p>{message}</p>}

      {downloadLink && (
        <p>
          <a
            href={encodeURI(downloadLink)}
            target="_blank"
            rel="noopener noreferrer"
          >
            {downloadLink}
          </a>
        </p>
      )}
    </div>
  );
}

export default App;

