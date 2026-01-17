import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { useEffect, useState } from "react";
import { useLocation, Navigate } from "react-router-dom";
import "leaflet/dist/leaflet.css";

const OCCITANIE_CENTER = [43.8927, 3.2828];
const ZOOM = 7;

const fakeData = [
  { lat: 43.6, lng: 1.44, severity: 0.9, date: "2026-01-12" },
  { lat: 43.3, lng: 3.2, severity: 0.6, date: "2026-01-12" },
];

export default function MapPage() {
  const location = useLocation();
  const user = location.state?.user;

  // 🔒 sécurité : accès uniquement après subscribe
  if (!user) {
    return <Navigate to="/" replace />;
  }

  const [points, setPoints] = useState([]);

  useEffect(() => {
    setPoints(fakeData);
  }, []);

  return (
    <div style={{ display: "flex" }}>
      {/* Bandeau utilisateur */}
      <div
        style={{
          position: "absolute",
          top: 20,
          left: 20,
          background: "white",
          padding: "0.6rem 1rem",
          borderRadius: "8px",
          boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
          zIndex: 1000,
        }}
      >
        ✅ Subscribed as <b>{user.mail}</b>
      </div>

      {/* Carte */}
      <MapContainer
        center={OCCITANIE_CENTER}
        zoom={ZOOM}
        style={{ height: "100vh", width: "75%" }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {points.map((p, i) => (
          <CircleMarker
            key={i}
            center={[p.lat, p.lng]}
            radius={10}
            pathOptions={{
              color: p.severity > 0.8 ? "red" : "orange",
              fillOpacity: 0.8,
            }}
          >
            <Popup>
              <b>Severity:</b> {p.severity}
              <br />
              <b>Date:</b> {p.date}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* Sidebar */}
      <div
        style={{
          width: "25%",
          padding: "1rem",
          background: "#f9fafb",
          borderLeft: "1px solid #e5e7eb",
        }}
      >
        <h3>⚠️ Alert zones</h3>
        {points.map((p, i) => (
          <div key={i} style={{ marginBottom: "0.5rem" }}>
            {p.severity > 0.8 ? "🔴" : "🟡"} {p.lat}, {p.lng}
          </div>
        ))}
      </div>
    </div>
  );
}
