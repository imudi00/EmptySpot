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
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const getSchoolData = (name) => {
        switch (name) {
            case 'sju':
                return { name: '세종대학교', logo: '/sju-logo.png' };
            case 'gcu':
                return { name: '가천대학교', logo: '/gcu-logo3.png' };
            default:
                return { name: '알 수 없는 학교', logo: '' };
        }
    };

    const getCongestionColorClass = (congestion) => {
        if (congestion === null) return '';
        if (congestion <= 0.3) return 'low';
        if (congestion <= 0.7) return 'medium';
        return 'high';
    };

    const schoolData = getSchoolData(schoolName);

    useEffect(() => {
        setLoading(true);
        setError(null);
        
        if (personnel === '정보 없음') {
            setLoading(false);
            setError("인원수 정보가 없습니다. 메인 페이지에서 인원수를 입력해주세요.");
            return;
        }

        fetch(`/api/congestion_people?group=${personnel}`)
            .then((res) => {
                if (!res.ok) {
                    throw new Error('인원수 기반 추천 정보를 불러오지 못했습니다.');
                }
                return res.json();
            })
            .then((data) => {
                console.log("API 응답:", data);
                
                if (data.recommendations) {
                    setRecommendations(data.recommendations);
                } else if (data.items) {
                    setRecommendations(data.items);
                } else {
                    setRecommendations(data);
                }
            })
            .catch((err) => {
                console.error("API 호출 오류:", err);
                setError(err.message);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [personnel]);

    if (loading) {
        return (
            <div>
                <Header />
                <main className="recommendations-container">
                    <h2>추천 데이터를 불러오는 중...</h2>
                </main>
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <Header />
                <main className="recommendations-container">
                    <h2>오류 발생: {error}</h2>
                </main>
            </div>
        );
    }

    if (recommendations.length === 0) {
        return (
            <div>
                <Header />
                <main className="recommendations-container">
                    <h2>추천 장소를 찾을 수 없습니다.</h2>
                    <p>인원수({personnel}명)에 맞는 장소가 현재 없습니다.</p>
                </main>
            </div>
        );
    }

    return (
        <div>
            <Header />
            <main className="recommendations-container">
                <div className="recommendations-list">
                    <h2>✨ {schoolData.name}에 맞는 장소 추천 순</h2>
                    <div className="recommendations-scroll-container">
                        {recommendations.map((item, index) => (
                            <div key={item.location_id || index} className="recommendation-item">
                                <span className="rank-number">{index + 1}</span>
                                <div className="item-details">
                                    {/* 🚀 이 부분을 수정했습니다! */}
                                    <Link to={`/school/${schoolName}/places/${item.location_id}`} className="recommendation-link">
                                        <div className="item-details-left">
                                            <p className="item-name">{item.name || '이름 없음'}</p>
                                            <p className="item-location">{item.building || item.details || '설명 없음'}</p>
                                        </div>
                                        <div className="item-details-right">
                                            <div className="congestion-squares-container">
                                                {Array.from({ length: 10 }, (_, i) => (
                                                    <div
                                                        key={i}
                                                        className={`square ${getCongestionColorClass(item.congestion)} ${Math.round((item.congestion || 0) * 10) > i ? 'filled' : ''}`}
                                                    ></div>
                                                ))}
                                            </div>
                                            <span className="congestion-percent">
                                                {(item.congestion !== null) ? `${(item.congestion * 100).toFixed(0)}%` : ''}
                                            </span>
                                        </div>
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default RecommendationsPage;