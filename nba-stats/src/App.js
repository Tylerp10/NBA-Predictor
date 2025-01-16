import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom"
import Players from "./players";
import Odds from "./odds";
import Home from "./home";
import PredictionModel from "./predictionmodel";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/players" element={<Players />}></Route>
        <Route path="/odds" element={<Odds />}></Route>
        <Route path="/predictor" element={<PredictionModel />}></Route>
      </Routes>
    </BrowserRouter>  
  )
}

export default App;