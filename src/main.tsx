import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { initGA } from "./lib/analytics";

// Initialize GA4 immediately (Vite strips inline scripts from index.html)
initGA();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
