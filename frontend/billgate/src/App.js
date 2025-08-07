// src/App.js

import React from 'react';
import SchoolMainPage from './pages/SchoolMainPage'; // 새로운 페이지 컴포넌트 불러오기
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import StartPage from './pages/StartPage';
import SchoolSelectPage from './pages/SchoolSelectPage';
import RecommendationsPage from './pages/RecommendationsPage';
import './App.css';


function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={<StartPage />} />
          <Route path="/select-school" element={<SchoolSelectPage />} />
          <Route path="/school/:schoolName" element={<SchoolMainPage />} />
          <Route path="/school/:schoolName/recommendations" element={<RecommendationsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;