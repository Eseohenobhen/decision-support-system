import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./layouts/AppLayout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import DSSRecommendations from "./pages/DSSRecommendations.jsx";
import Funds from "./pages/Funds.jsx";
import Login from "./pages/Login.jsx";
import MaintenanceRequests from "./pages/MaintenanceRequests.jsx";
import Properties from "./pages/Properties.jsx";
import PropertyDetails from "./pages/PropertyDetails.jsx";
import Reports from "./pages/Reports.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="properties" element={<Properties />} />
            <Route path="properties/:propertyId" element={<PropertyDetails />} />
            <Route path="funds" element={<Funds />} />
            <Route path="maintenance-requests" element={<MaintenanceRequests />} />
            <Route path="dss-recommendations" element={<DSSRecommendations />} />
            <Route path="reports" element={<Reports />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
