import { BrowserRouter, Routes, Route } from "react-router-dom";
import Subscribe from "./pages/Subscribe";
import MapPage from "./pages/MapPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Subscribe />} />
        <Route path="/map" element={<MapPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
