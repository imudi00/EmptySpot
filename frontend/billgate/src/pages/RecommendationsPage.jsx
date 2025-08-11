// src/pages/RecommendationsPage.jsx

import React, { useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import Header from '../components/common/Header';
import './RecommendationsPage.css';

function RecommendationsPage() {
  const { schoolName } = useParams();
  const location = useLocation();
  const personnel = location.state?.personnel || '정보 없음';

  const [recommendations, setRecommendations] = useState([]);

  const getSchoolData = (name) => {
    switch (name) {
      case 'sju':
        return { name: '세종대학교', logo: '/sju-logo.png' };
      case 'gcu':
        return { name: '가천대학교', logo: '/gcu-logo.png' };
      default:
        return { name: '알 수 없는 학교', logo: '' };
    }
  };

  const schoolData = getSchoolData(schoolName);

  useEffect(() => {
    // 임의 위치값 (테스트용)
    const lat = 37.550;  
    const lng = 127.073; 

    fetch(`/api/recommendation/location?lat=${lat}&lng=${lng}`)
      .then((res) => res.json())
      .then((data) => {
        console.log("API 응답:", data);

        // 백엔드에서 sorted_locations로 온다고 가정
        if (data.sorted_locations) {
          setRecommendations(data.sorted_locations);
        }
      })
      .catch((err) => {
        console.error("API 호출 오류:", err);
      });
  }, [schoolName]);

  return (
    <div>
      <Header />
      <main className="recommendations-container">
        <div className="recommendations-header">
          <img src={schoolData.logo} alt={`${schoolData.name} 로고`} className="school-logo" />
          <h1>{schoolData.name}</h1>
          <p className="personnel-info">
            입력 인원: **{personnel}명**에 대한 장소 추천 결과입니다.
          </p>
        </div>

        <div className="recommendations-list">
          <h2>추천 장소</h2>
          <p className="hardcoded-label">※ 현재는 DB에서 가져온 원시 데이터입니다.</p>

          {recommendations.length > 0 ? (
            recommendations.map((item, index) => (
              <div key={index} className="recommendation-item">
                <span className="rank-number">{index + 1}</span>
                <div className="item-details">
                  <Link to={`/school/${schoolName}/places/${item.id}`} className="recommendation-link">
                    <div className="item-name">{item.name}</div>
                    <div className="item-description">
                      {item.building || '설명 없음'}
                    </div>
                  </Link>
                  <div className="chart-bar-wrapper">
                    <div
                      className="chart-bar"
                      style={{ width: `${(100 - item.distance_km).toFixed(1)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p>추천 데이터를 불러오는 중...</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default RecommendationsPage;
