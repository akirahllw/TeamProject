import React from "react";
import { Navigate, Route, Routes } from "react-router";

const Login = React.lazy(() => import("../pages/Login/page"));
const SignUp = React.lazy(() => import("../pages/SignUp/page"));

const Welcome = React.lazy(() => import("../pages/WelcomePage/page"));

const Dashboard = React.lazy(() => import("../pages/Dashboard/page"));

const Projects = React.lazy(() => import("../pages/ProjectPage/ProjectsPage"));

const AppRoutes = () => {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/create" element={<SignUp />} />
        <Route path="/welcome" element={<Welcome />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        </Routes>
    </React.Suspense>
  );
};

export default AppRoutes;
