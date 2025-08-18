import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/common/Header';
import './StartPage.css';
import mainIllustration from '../assets/main-illustration.png';

function StartPage() {
    return (
        <div>
            <Header />
            
            <main className="startpage-main-container">
                <section className="startpage-content-wrapper">
                    <div className="startpage-text-section">
                        <h1 className="startpage-title">
                            <span className="title-highlight animated-text">우리를 위한 최선의 장소찾기</span><br/> 더이상 장소찾아 헤메지 마세요!
                        </h1>
                        <h2 className="startpage-service-name animated-service-name">
                            {"장소 빌게이츠".split("").map((char, index) => (
                                <span key={index} className="wave-char" style={{ animationDelay: `${index * 0.1}s` }}>
                                    {char === " " ? "\u00A0" : char}
                                </span>
                            ))}
                        </h2>
                        <p className="startpage-subtitle">
                            실시간 혼잡도 확인부터 인원수 맞춤 공간 추천까지, 학교 장소를 모두 확인하세요.
                        </p>
                        <div className="startpage-cta-buttons">
                            <Link to="/select-school" className="cta-button primary-button">
                                내 학교 선택하기 →
                            </Link>
                            {/* 🚀 이 부분을 수정했습니다! */}
                            <Link to="/service-intro" className="cta-button secondary-button">
                                서비스 소개 →
                            </Link>
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