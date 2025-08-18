import React from 'react';
import Header from '../components/common/Header'; // Header 컴포넌트 불러오기


function ServiceIntroPage() {
    return (
        <div>
            <Header />
            <main className="service-intro-container">
                <div className="service-intro-content">
                    <h1>서비스 소개</h1>
                    <p>
                        ‘장소 빌게이츠’는 여러분이 더 이상 교내에서 빈 강의실이나 스터디 공간을 찾느라 헤매지 않도록 돕는 서비스입니다.
                        <br /><br />
                        실시간으로 각 장소의 혼잡도를 확인하고, 인원수에 맞는 최적의 장소를 추천받을 수 있습니다.
                        <br /><br />
                        - **실시간 혼잡도**: 각 장소의 현재 혼잡도를 한눈에 파악하세요.
                        - **인원수 기반 추천**: 팀플이나 소규모 모임을 위한 장소를 쉽게 찾을 수 있습니다.
                        <br /><br />
                        이제 '장소 빌게이츠'와 함께 효율적인 학교 생활을 시작하세요!
                    </p>
                </div>
            </main>
        </div>
    );
}

export default ServiceIntroPage;