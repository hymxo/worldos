import { createRoot } from "react-dom/client";
import Home from "../app/page";
import AdminPanel from "../app/admin/panel";
import "../app/globals.css";

const path = window.location.pathname.replace(/\/+$/, "") || "/";
const page = path === "/admin" ? <AdminPanel /> : <Home locale={path === "/en" ? "en" : "zh"} />;

createRoot(document.getElementById("root")!).render(page);
