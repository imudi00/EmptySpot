// src/pages/RecommendationsPage.jsx

import React from 'react';
import { useParams, useLocation } from 'react-router-dom';
import Header from '../components/common/Header';
import './RecommendationsPage.css';

function RecommendationsPage() {
  const { schoolName } = useParams();
  const location = useLocation();
  const personnel = location.state?.personnel || '정보 없음';

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

  // 하드코딩된 추천 장소 데이터
  // 이 데이터는 실제 백엔드 연동 시 API 응답으로 대체됩니다.
  const recommendations = [
    { name: '대양AI센터 1층 로비', description: '많은 인원이 모일 수 있는 넓은 공간', score: 95 },
    { name: '광개토관 15층 라운지', description: '창밖 뷰가 좋은, 쾌적한 공간', score: 85 },
    { name: '학생회관 2층 세미나실', description: '소음이 적고 집중하기 좋은 공간', score: 70 },
    { name: '군자관 지하 휴게실', description: '편하게 앉아 쉴 수 있는 공간', score: 60 },
  ];

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
          <p className="hardcoded-label">※ 이 장소들은 하드코딩된 데이터입니다.</p>
          {recommendations.map((item, index) => (
            <div key={index} className="recommendation-item">
              <span className="rank-number">{index + 1}</span>
              <div className="item-details">
                <div className="item-name">{item.name}</div>
                <div className="item-description">{item.description}</div>
                <div className="chart-bar-wrapper">
                  <div className="chart-bar" style={{ width: `${item.score}%` }}></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default RecommendationsPage;