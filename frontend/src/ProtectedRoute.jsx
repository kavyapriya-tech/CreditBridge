import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  const isLoggedIn = sessionStorage.getItem("cb_logged_in") === "true";
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  return children;
}