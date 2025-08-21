// src/App.js

import React from 'react';
import SchoolMainPage from './pages/SchoolMainPage';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import StartPage from './pages/StartPage';
import SchoolSelectPage from './pages/SchoolSelectPage';
import RecommendationsPage from './pages/RecommendationsPage';
import PlaceDetailPage from './pages/PlaceDetailPage';
import ServiceIntroPage from './pages/ServiceIntroPage'; // 🚀 ServiceIntroPage 컴포넌트를 불러옵니다.
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
          <Route path="/school/:schoolName/places/:placeId" element={<PlaceDetailPage />} />
          {/* 🚀 서비스 소개 페이지로 이동하는 새로운 경로를 추가합니다. */}
          <Route path="/service-intro" element={<ServiceIntroPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
