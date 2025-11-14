import React from "react";
import { Navigate, Route, Routes } from "react-router";

const Login = React.lazy(() => import("../pages/Login/page"));

const AppRoutes = () => {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        </Routes>
    </React.Suspense>
  );
};

export default AppRoutes;