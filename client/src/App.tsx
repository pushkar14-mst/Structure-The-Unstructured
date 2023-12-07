import { useState } from "react";
import "./App.css";
import {
  ArrowBackIos,
  AudioFile,
  DownloadForOffline,
  PermMedia,
  SettingsEthernet,
} from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import axios from "axios";

const formatsMap: any = {
  Audio: ".wav",
  Image: ".png",
  Logs: ".txt",
};
function App() {
  const [formatSelected, setFormatSelected] = useState<string>("");
  const [files, setFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [downloadReady, setDownloadReady] = useState<boolean>(false);
  const uploadFiles = async () => {
    setIsProcessing(true);
    let formData = new FormData();
    files.forEach((file) => {
      formData.append("Files[]", file);
      formData.append("Formats[]", String(formatSelected));
    });
    console.log(formData.getAll("Files[]"));
    await axios.post("http://127.0.0.1:5000/process", formData).then((res) => {
      setIsProcessing(false);
      setDownloadReady(true);
      console.log(res.data);
      let downloadLink: any = document.querySelector(".downloadLink");
      downloadLink.href =
        "http://127.0.0.1:5000/download/" + res.data.output_filename;
      downloadLink.setAttribute("download", res.data.output_filename);
    });
  };
  return (
    <>
      <h1 id="logo">StructureTheUnstructured</h1>
      <div className="main-app-container">
        {formatSelected === "" ? (
          <div className="get-started-container">
            <h1>Get Started</h1>
            <h2>Select Your Format</h2>
            <div className="formats-row">
              <div
                className="format-container"
                onClick={() => {
                  setFormatSelected("Audio");
                }}
              >
                <AudioFile />
                <p>.wav files</p>
              </div>
              <div
                className="format-container"
                onClick={() => {
                  setFormatSelected("Image");
                }}
              >
                <PermMedia />
                <p>.png files</p>
              </div>
              <div
                className="format-container"
                onClick={() => {
                  setFormatSelected("Logs");
                }}
              >
                <SettingsEthernet />
                <p>Log files</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="upload-container">
            <ArrowBackIos
              id="go-back-btn"
              onClick={() => {
                setFormatSelected("");
                setDownloadReady(false);
                setFiles([]);
                setIsProcessing(false);
              }}
            />
            <h1>Upload your {formatSelected} files</h1>
            <div className="upload-box">
              <p style={{ fontSize: "1.2rem" }}>Upload your files here</p>
              <div className="upload-form">
                <input
                  type="file"
                  multiple
                  accept={formatsMap[formatSelected]}
                  id="files-upload-input"
                  onChange={(e) => {
                    if (e.target.files) {
                      setFiles(Array.from(e.target.files));
                    }
                  }}
                />
              </div>
              <Button
                style={{
                  marginTop: "1rem",
                  backgroundColor: "#06768d",
                  color: "#03002e",
                  fontWeight: "bold",
                  fontFamily: "Montserrat",
                }}
                onClick={uploadFiles}
              >
                Upload
              </Button>
              {isProcessing && (
                <CircularProgress
                  style={{
                    marginTop: "1rem",
                  }}
                />
              )}
              {downloadReady && (
                <div className="download-box">
                  <p style={{ fontSize: "1.2rem", marginTop: "1rem" }}>
                    Download your files here
                  </p>
                  <a className="downloadLink">
                    <DownloadForOffline
                      style={{
                        width: "50px",
                        height: "50px",
                      }}
                    />
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
