import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Subscribe.css";

export default function Subscribe() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      name: name,
      mail: email,
      ip: "192.168.37.68", 
    };

    try {

      const res = await axios.post("http://localhost:8007/subscribe", payload);
      
      navigate("/map", {
        state: {
          user: res.data.data, 
        },
      });
    } catch (err) {
      alert("Subscription failed");
    }
  };

  return (
    <div className="subscribe-container">
      <form className="subscribe-card" onSubmit={handleSubmit}>
        <h1>🌊 Flood Alert </h1>
        <p>Subscribe to receive flood alerts</p>

        <input
          type="text"
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <input
          type="email"
          placeholder="Your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <button type="submit">Subscribe</button>
      </form>
    </div>
  );
}
