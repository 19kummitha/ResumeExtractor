import { Routes, Route } from "react-router-dom";
import Login from "./auth/Login";
import Register from "./auth/Register";
import UploadResume from "./pages/UploadResume";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <UploadResume />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}
