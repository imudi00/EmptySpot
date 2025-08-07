// src/pages/SchoolMainPage.jsx

import React, { useState } from 'react';
import { useParams,useNavigate } from 'react-router-dom';
import Header from '../components/common/Header';
import './SchoolMainPage.css';

function SchoolMainPage() {
  const { schoolName } = useParams();
  const [personnel, setPersonnel] = useState('');
  const navigate = useNavigate(); // useNavigate 훅 사용


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
  // '장소 추천받기' 버튼 클릭 시 실행될 함수
  const handleRecommendClick = () => {
    // 인원수(personnel) 상태를 새로운 페이지로 전달하며 이동
    navigate(`/school/${schoolName}/recommendations`, { state: { personnel } });
  };

  return (
    <div>
      <Header />
      <main className="school-main-container">
        <div className="school-info">
          <img src={schoolData.logo} alt={`${schoolData.name} 로고`} className="school-logo" />
          <h1>{schoolData.name}</h1>
          <p>환영합니다! {schoolData.name}의 빈 강의실 찾기 서비스입니다.</p>
        </div>
        
        <div className="features-wrapper">
          {/* 빈 강의실 찾기 UI */}
          <div className="feature-card find-classroom">
            <h2>몇 명이서 사용하시나요?</h2>
            <div className="input-container">
              <input 
                type="number"
                placeholder="인원수 입력"
                value={personnel}
                onChange={(e) => setPersonnel(e.target.value)}
                className="personnel-input"
              />
            </div>
            {/* 버튼에 onClick 이벤트 핸들러 추가 */}
            <button className="search-button" onClick={handleRecommendClick}>장소 추천받기</button>
          </div>

          {/* 회의실 예약 UI - 실시간 차트 형식 */}
          <div className="feature-card reserve-room">
            <h2>회의실 예약</h2>
            {/* 하드코딩된 실시간 차트 UI */}
            <div className="realtime-chart-list">
              <div className="chart-item">
                <span className="rank-number">1</span>
                <div className="item-details">
                  <p className="item-name">
                    oo관 1층 라운지<br />
                    같이 회의하기 좋은 장소
                  </p>
                  <div className="chart-bar-wrapper">
                    <div className="chart-bar" style={{ width: '80%' }}></div>
                  </div>
                </div>
              </div>
              <div className="chart-item">
                <span className="rank-number">2</span>
                <div className="item-details">
                  <p className="item-name">
                    ㅁㅁ관 2층 세미나실<br />
                    조용히 집중하기 좋은 장소
                  </p>
                  <div className="chart-bar-wrapper">
                    <div className="chart-bar" style={{ width: '50%' }}></div>
                  </div>
                </div>
              </div>
              <div className="chart-item">
                <span className="rank-number">3</span>
                <div className="item-details">
                  <p className="item-name">
                    ㅁ관 3층 스터디룸<br />
                    소규모 팀플에 적합한 장소
                  </p>
                  <div className="chart-bar-wrapper">
                    <div className="chart-bar" style={{ width: '65%' }}></div>
                  </div>
                </div>
              </div>
              <div className="chart-item">
                <span className="rank-number">4</span>
                <div className="item-details">
                  <p className="item-name">
                    xx관 5층 열람실<br />
                    개인 공부에 좋은 장소
                  </p>
                  <div className="chart-bar-wrapper">
                    <div className="chart-bar" style={{ width: '40%' }}></div>
                  </div>
                </div>
              </div>
              <div className="chart-item">
                <span className="rank-number">5</span>
                <div className="item-details">
                  <p className="item-name">
                    △△관 지하 휴게실<br />
                    간단한 대화하기 좋은 장소
                  </p>
                  <div className="chart-bar-wrapper">
                    <div className="chart-bar" style={{ width: '30%' }}></div>
                  </div>
                </div>
              </div>
            </div>
            <p className="hardcoded-label">※ 이 부분은 하드코딩된 UI입니다.</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default SchoolMainPage;