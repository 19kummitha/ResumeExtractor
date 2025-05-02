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

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

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

            {Object.entries(result).map(([key, value]) => (
              <Box key={key} mb={3}>
                <Typography variant="h6" color="primary">
                  {key
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (l) => l.toUpperCase())}
                </Typography>

                {/* Array of strings */}
                {Array.isArray(value) && typeof value[0] === "string" && (
                  <Stack direction="row" spacing={1} flexWrap="wrap" mt={1}>
                    {value.map((item, index) => (
                      <Chip key={index} label={item} sx={{ mb: 1 }} />
                    ))}
                  </Stack>
                )}

                {/* Array of objects */}
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

                {/* Plain text */}
                {!Array.isArray(value) && typeof value !== "object" && (
                  <Typography variant="body1" mt={1}>
                    {value}
                  </Typography>
                )}
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Container>
  );
}
