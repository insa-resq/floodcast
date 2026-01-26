import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { useEffect, useState, useRef } from "react";
import { useLocation, Navigate } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import "./MapPage.css";

const OCCITANIE_CENTER = [43.8927, 3.2828];
const ZOOM = 7;


const fakeData = [
  //  Nord & Nord-Ouest — Seine, Oise, Somme, Canche
  { lat: 48.8566, lng: 2.3522, severity: 0.90, date: "2026-02-10" }, // Paris (Seine)
  { lat: 49.4179, lng: 2.8261, severity: 0.75, date: "2026-02-10" }, // Compiègne (Oise)
  { lat: 49.8941, lng: 2.2957, severity: 0.70, date: "2026-02-10" }, // Amiens (Somme)
  { lat: 50.7214, lng: 1.6133, severity: 0.65, date: "2026-02-10" }, // Montreuil-sur-Mer (Canche)

  //  Sud-Ouest — Dronne, Isle, Charente, Lot-et-Garonne
  { lat: 45.1857, lng: 0.7216, severity: 0.85, date: "2026-02-12" }, // Périgueux (Isle)
  { lat: 45.0486, lng: -0.7055, severity: 0.78, date: "2026-02-12" }, // Libourne (Dordogne)
  { lat: 45.6484, lng: 0.1569, severity: 0.72, date: "2026-02-12" }, // Angoulême (Charente)
  { lat: 44.2031, lng: 0.6212, severity: 0.80, date: "2026-02-12" }, // Agen (Garonne)

  //  Centre & Vallée de la Loire
  { lat: 47.9029, lng: 1.9093, severity: 0.77, date: "2026-02-14" }, // Orléans (Loire)
  { lat: 47.3941, lng: 0.6848, severity: 0.70, date: "2026-02-14" }, // Tours (Loire)

  //  Sud-Est — Rhône & affluents
  { lat: 45.7640, lng: 4.8357, severity: 0.88, date: "2026-02-16" }, // Lyon (Rhône)
  { lat: 44.9334, lng: 4.8924, severity: 0.74, date: "2026-02-16" }, // Valence (Rhône)

  //  Autres zones — Bretagne, Pays de la Loire, Méditerranée
  { lat: 48.1173, lng: -1.6778, severity: 0.68, date: "2026-02-18" }, // Rennes (Vilaine)
  { lat: 47.2184, lng: -1.5536, severity: 0.73, date: "2026-02-18" }, // Nantes (Loire)
  { lat: 43.6108, lng: 3.8767, severity: 0.82, date: "2026-02-20" }, // Montpellier (Lez)
  { lat: 43.2965, lng: 5.3698, severity: 0.76, date: "2026-02-20" }, // Marseille (Huveaune)
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
