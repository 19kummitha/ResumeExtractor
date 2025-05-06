import React, { useState } from "react";
import {
  Button,
  Container,
  Typography,
  Box,
  CircularProgress,
  Chip,
  Stack,
  Card,
  CardContent,
} from "@mui/material";
import axios from "../api/axios";
import { getToken } from "../utils/token"; // Import getToken from token.js

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const res = await axios.post("/resume/upload", formData);
      setResult(res.data);
    } catch (err) {
      alert("Upload failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    const token = getToken();
    const fileId = result.id;

    try {
      const res = await axios.get(`/resume/generate-pdf/${fileId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "resume.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Download failed");
      console.error(err);
    }
  };

  const handlePreview = async () => {
    const token = getToken();
    const fileId = result.id;

    try {
      const res = await axios.get(`/resume/generate-pdf/${fileId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        responseType: "blob",
      });

      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setPdfPreviewUrl(url);
    } catch (err) {
      alert("Preview failed");
      console.error(err);
    }
  };

  return (
    <Container>
      <Box mt={5} display="flex" flexDirection="column" alignItems="center">
        <Typography variant="h4" gutterBottom>
          Upload Resume
        </Typography>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          accept=".pdf,.doc,.docx"
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          sx={{ mt: 2 }}
        >
          Upload
        </Button>
        {loading && <CircularProgress sx={{ mt: 2 }} />}

        {result && (
          <Box mt={4} width="100%">
            <Typography variant="h5" gutterBottom>
              Extracted Details:
            </Typography>

            {Object.entries(result).map(([key, value]) => {
              if (key === "download_url" || key === "id" || key === "message")
                return null;
              return (
                <Box key={key} mb={3}>
                  <Typography variant="h6" color="primary">
                    {key
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (l) => l.toUpperCase())}
                  </Typography>

                  {Array.isArray(value) && typeof value[0] === "string" && (
                    <Stack direction="row" spacing={1} flexWrap="wrap" mt={1}>
                      {value.map((item, index) => (
                        <Chip key={index} label={item} sx={{ mb: 1 }} />
                      ))}
                    </Stack>
                  )}

                  {Array.isArray(value) && typeof value[0] === "object" && (
                    <Box mt={1}>
                      {value.map((item, idx) => (
                        <Card key={idx} variant="outlined" sx={{ mb: 2 }}>
                          <CardContent>
                            {Object.entries(item).map(([subKey, subVal]) => (
                              <Typography key={subKey} variant="body2">
                                <strong>{subKey}:</strong> {subVal}
                              </Typography>
                            ))}
                          </CardContent>
                        </Card>
                      ))}
                    </Box>
                  )}

                  {!Array.isArray(value) && typeof value !== "object" && (
                    <Typography variant="body1" mt={1}>
                      {value}
                    </Typography>
                  )}
                </Box>
              );
            })}

            {result.id && (
              <Box mt={3}>
                <Stack direction="row" spacing={2}>
                  <Button
                    variant="outlined"
                    color="info"
                    onClick={handlePreview}
                  >
                    Preview Resume
                  </Button>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handleDownload}
                  >
                    Download Styled PDF
                  </Button>
                </Stack>
              </Box>
            )}

            {pdfPreviewUrl && (
              <Box mt={4}>
                <Typography variant="h6" gutterBottom>
                  Resume Preview:
                </Typography>
                <iframe
                  src={pdfPreviewUrl}
                  width="100%"
                  height="600px"
                  title="PDF Preview"
                  style={{ border: "1px solid #ccc", borderRadius: "8px" }}
                />
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Container>
  );
}
