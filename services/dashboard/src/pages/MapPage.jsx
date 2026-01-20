import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { useEffect, useState, useRef } from "react";
import { useLocation, Navigate } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import "./MapPage.css";

const OCCITANIE_CENTER = [43.8927, 3.2828];
const ZOOM = 7;


const fakeData = [
  // Toulouse centre
  { lat: 43.6047, lng: 1.4442, severity: 0.85, date: "2026-01-12" },

  // Première couronne
  { lat: 43.6111, lng: 1.4991, severity: 0.65, date: "2026-01-12" }, // Balma
  { lat: 43.5906, lng: 1.3895, severity: 0.92, date: "2026-01-12" }, // Blagnac
  { lat: 43.5696, lng: 1.4026, severity: 0.55, date: "2026-01-12" }, // Tournefeuille
  { lat: 43.6577, lng: 1.5026, severity: 0.78, date: "2026-01-12" }, // L'Union
  { lat: 43.6675, lng: 1.4292, severity: 0.60, date: "2026-01-12" }, // Aucamville
  { lat: 43.6333, lng: 1.4667, severity: 0.88, date: "2026-01-12" }, // Ramonville-Saint-Agne

  // Deuxième couronne
  { lat: 43.5178, lng: 1.4986, severity: 0.70, date: "2026-01-12" }, // Muret
  { lat: 43.7383, lng: 1.3707, severity: 0.58, date: "2026-01-12" }, // Grenade
  { lat: 43.4599, lng: 1.3254, severity: 0.82, date: "2026-01-12" }, // Fonsorbes
  { lat: 43.6486, lng: 1.5416, severity: 0.66, date: "2026-01-12" }, // Saint-Orens-de-Gameville
  { lat: 43.7286, lng: 1.3458, severity: 0.73, date: "2026-01-12" }, // Seilh
  { lat: 43.6947, lng: 1.4028, severity: 0.59, date: "2026-01-12" }, // Castelginest
];


export default function MapPage() {
  const location = useLocation();
  const user = location.state?.user;


  if (!user) return <Navigate to="/" replace />;
  console.log("USER FROM LOCATION.STATE =", user);

  const [points, setPoints] = useState([]);
  const [open, setOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const mapRef = useRef(null);

  useEffect(() => {
    setPoints(fakeData);
  }, []);

  useEffect(() => {
    if (mapRef.current) {
      setTimeout(() => mapRef.current.invalidateSize(), 300);
    }
  }, [open]);

  const alertUsers = async () => {
    setLoading(true); // début chargement

    try {
      const res = await fetch("http://localhost:8007/alertUsers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
        },
        body: JSON.stringify({
          id: 0,
          segment_id: 0,
          severity: 1,
          probability: 0.9,
          start_date: new Date().toISOString(),
          end_date: new Date().toISOString(),
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }

      alert(" Users alerted successfully");
    } catch (err) {
      console.error(err);
      alert(" Error while alerting users");
    } finally {
      setLoading(false); // fin chargement
    }
  };



  return (
    <div className="map-layout">
      {/* Map */}
      <MapContainer
        center={OCCITANIE_CENTER}
        zoom={ZOOM}
        className="map-container"
        whenCreated={(map) => (mapRef.current = map)}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {points.map((p, i) => (
          <CircleMarker
            key={i}
            center={[p.lat, p.lng]}
            radius={10}
            pathOptions={{
              color: p.severity > 0.8 ? "#ef4444" : "#f59e0b",
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
      <div className={`sidebar ${open ? "open" : "closed"}`}>
        {/* Arrow always visible */}
        <button
          className="arrow arrow-fixed"
          onClick={() => setOpen(!open)}
        >
          {open ? "❮" : "❯"}
        </button>

        {open && (
          <>
            <div className="sidebar-header">
              <span className="date">
                {new Date().toLocaleDateString()}
              </span>

              <span className="user-name">
                👤 {user.mail}
              </span>
            </div>
              <button
                className="alert-btn"
                onClick={alertUsers}
                disabled={loading}
              >
                {loading ? "⏳ Sending alerts..." : "🚨 Alert Users"}
              </button>
            <div className="alerts">
              {points.map((p, i) => (
                <div
                  key={i}
                  className={`alert-card ${
                    p.severity > 0.8 ? "high" : "medium"
                  }`}
                >
                  <b>{p.severity > 0.8 ? "High risk" : "Medium risk"}</b>
                  <div className="small">📍 {p.lat}, {p.lng}</div>
                  <div className="small">🗓 {p.date}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Sending alerts…</p>
        </div>
      )}
    </div>
  );
}
