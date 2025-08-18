// src/pages/SchoolSelectPage.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/common/Header';
import './SchoolSelectPage.css';

function SchoolSelectPage() {
    const navigate = useNavigate();
    const [isComingSoon, setIsComingSoon] = useState(false);

    const schools = [
        { id: 'sju', name: '세종대학교', logo: '/sju-logo.png' },
        { id: 'gcu', name: '가천대학교', logo: '/gcu-logo3.png' }
    ];

    const handleSchoolClick = (schoolId) => {
        if (schoolId === 'sju') {
            setIsComingSoon(true);
            // 일정 시간 후 메시지 숨기기
            setTimeout(() => {
                setIsComingSoon(false);
            }, 3000);
        } else {
            // 다른 학교는 정상적으로 페이지 이동
            navigate(`/school/${schoolId}`);
        }
    };

    return (
        <div>
            <Header />
            <main className="school-select-container">
                <h1>학교 선택</h1>
                <p>서비스를 이용할 학교를 선택해주세요.</p>
                
                <div className="school-list">
                    {schools.map(school => (
                        <div 
                            key={school.id} 
                            onClick={() => handleSchoolClick(school.id)} 
                            className="school-item-link"
                        >
                            <div className="school-item">
                                <img src={school.logo} alt={`${school.name} 로고`} />
                                <p>{school.name}</p>
                            </div>
                        </div>
                    ))}
                </div>
                {isComingSoon && (
                    <div className="coming-soon-message">
                        <p>💡 세종대학교는 현재 서비스 준비 중입니다.</p>
                    </div>
                )}
            </main>
        </div>
    );
}

export default SchoolSelectPage;
