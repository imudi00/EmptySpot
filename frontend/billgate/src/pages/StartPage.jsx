import React from 'react';
import { Link } from 'react-router-dom'; // Link 컴포넌트 불러오기
import Header from '../components/common/Header'; // Header 컴포넌트 사용
import './StartPage.css'; // StartPage 스타일 파일
import mainIllustration from '../assets/main-illustration.png'; // 메인 일러스트 이미지 경로 (예시)

function StartPage() {
  return (
    <div>
      <Header />
      
      <main className="startpage-main-container">
        <section className="startpage-content-wrapper">
          <div className="startpage-text-section">
            <h1 className="startpage-title">
              <span className="title-highlight animated-text">공간시간 장소?</span><br/>
              이젠 한눈에 보세요!(서비스 메인 기능)
            </h1>
            <h2 className="startpage-service-name animated-service-name">
  {"장소 빌게이츠".split("").map((char, index) => (
    <span key={index} className="wave-char" style={{ animationDelay: `${index * 0.1}s` }}>
      {char === " " ? "\u00A0" : char}
    </span>
  ))}
</h2>
            <p className="startpage-subtitle">
              학교 내 빈 공간 정보를  실시간으로.어플에대한 추가설명 ...
            </p>
            <div className="startpage-cta-buttons">
                <Link to="/select-school" className="cta-button primary-button">
                내 학교 선택하기 →
                </Link>
              <button className="cta-button secondary-button">
                내 학교 바로가기 →
              </button>
            </div>
          </div>
          
          <div className="startpage-image-section">
            <img src={mainIllustration} alt="Meeting room illustration" className="main-illustration" />
          </div>
        </section>
      </main>
    </div>
  );
}

export default StartPage;