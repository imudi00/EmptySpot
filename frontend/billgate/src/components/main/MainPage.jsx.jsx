// src/components/main/MainHeroSection.jsx

import React from 'react';

const MainHeroSection = () => {
  const handleGoToSchool = () => {
    alert('내 학교 바로가기 버튼이 눌렸습니다!');
  };

  return (
    <section className="hero-section">
      <div className="hero-content">
        <div className="date-info">
          {/* 달력 아이콘 경로를 assets 폴더에 맞게 수정해주세요 */}
          <img src="/assets/calendar-icon.png" alt="달력" className="icon" />
          <p>계절학기 수강 신청 변경 기간</p>
          <p>6월 12일(목) ~ 6월 13일(금)</p>
        </div>

        <div className="feature-list">
          <p>1. 학교 내</p>
          <p>2. 지금 필요한</p>
          <p>3. 인원별 장소</p>
          <p>4. 실시간 빈 장소를 찾아드림</p>
          <p>→ 4가지 포인트로 웹페이지 주요기능을 설명</p>
        </div>

        <h1>도와드립니다!</h1>
        <p className="description">
          실시간 여석 확인부터 수강신청 연습까지 ALLCLL이 여러분과 함께합니다.
        </p>

        <button className="primary-button" onClick={handleGoToSchool}>
          내 학교 바로가기
        </button>
      </div>
      
      <div className="hero-image-container">
        {/* 우산 아래 사람 이미지 경로를 assets 폴더에 맞게 수정해주세요 */}
        <img src="/assets/hero-image.png" alt="도와드립니다 이미지" />
      </div>
    </section>
  );
};

export default MainHeroSection;