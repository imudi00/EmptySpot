// src/pages/SchoolSelectPage.jsx

import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/common/Header';
import './SchoolSelectPage.css';

function SchoolSelectPage() {
    const schools = [
        { id: 'sju', name: '세종대학교', logo: '/sju-logo.png' },
        { id: 'gcu', name: '가천대학교', logo: '/gcu-logo3.png' }
    ];

    return (
        <div>
            <Header />
            <main className="school-select-container">
                <h1>학교 선택</h1>
                <p>서비스를 이용할 학교를 선택해주세요.</p>
                
                <div className="school-list">
                    {schools.map(school => (
                        <Link key={school.id} to={`/school/${school.id}`} className="school-item-link">
                            <div className="school-item">
                                <img src={school.logo} alt={`${school.name} 로고`} />
                                <p>{school.name}</p>
                            </div>
                        </Link>
                    ))}
                </div>
            </main>
        </div>
    );
}

export default SchoolSelectPage;