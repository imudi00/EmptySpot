// src/pages/SchoolSelectPage.jsx

import React from 'react';
import { Link } from 'react-router-dom';//Link컴포넌트
import Header from '../components/common/Header'; // Header 컴포넌트를 재사용합니다.
import './SchoolSelectPage.css'; // 페이지 전용 CSS 파일을 불러옵니다.

function SchoolSelectPage() {
    // 실제로는 API를 통해 학교 목록을 가져와야함.지금은하드코딩
  const schools = [
    
    { id: 'sju', name: '세종대학교', logo: '/path/to/school-sju.png' },
    { id: 'gcu', name: '가천대학교', logo: '/path/to/school-gcu.png' }
  ]
  return (
    <div>
      <Header />
      <main className="school-select-container">
        <h1>학교 선택</h1>
        <p>서비스를 이용할 학교를 선택해주세요.</p>
        
        <div className="school-list">
          <div className="school-item">
            {schools.map(school => (
            <Link key={school.id} to={`/school/${school.id}`} className="school-item-link">
              <div className="school-item">
                <img src={school.logo} alt={`${school.name} 로고`} />
                <p>{school.name}</p>
              </div>
            </Link>
          ))}
          </div>
         
        </div>
        
      </main>
    </div>
  );
}

export default SchoolSelectPage;