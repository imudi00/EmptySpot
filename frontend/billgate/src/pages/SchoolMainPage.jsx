// src/pages/SchoolMainPage.jsx

<<<<<<< HEAD
import React, { useState } from 'react';
import { useParams,useNavigate } from 'react-router-dom';
=======
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
>>>>>>> 9596587 (feat: 새로운 기능 추가 및 줄바꿈 형식 통일)
import Header from '../components/common/Header';
import CustomDropdown from '../components/common/CustomDropdown';
import './SchoolMainPage.css';

function SchoolMainPage() {
<<<<<<< HEAD
  const { schoolName } = useParams();
  const [personnel, setPersonnel] = useState('');
  const navigate = useNavigate(); // useNavigate 훅 사용

=======
    const { schoolName } = useParams();
    const [personnel, setPersonnel] = useState('');
    const [sortCriteria, setSortCriteria] = useState('congestion');
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [userLocation, setUserLocation] = useState(null);
    const [personnelError, setPersonnelError] = useState(false);
    const navigate = useNavigate();

    // 입력 필드에 직접 입력할 때 유효성 검사
    const handlePersonnelInput = (e) => {
        const value = e.target.value;
        const numValue = Number(value);

        if (value === '' || (Number.isInteger(numValue) && numValue >= 1 && numValue <= 100)) {
            setPersonnel(value);
            setPersonnelError(false);
        } else {
            setPersonnelError(true);
        }
    };
>>>>>>> 9596587 (feat: 새로운 기능 추가 및 줄바꿈 형식 통일)

    // 버튼으로 인원수를 조절하는 함수
    const handlePersonnelButtonClick = (type) => {
        const numPersonnel = Number(personnel);

        if (type === 'increase') {
            if (numPersonnel < 100) {
                setPersonnel(String(numPersonnel + 1));
                setPersonnelError(false);
            } else {
                setPersonnelError(true);
            }
        } else if (type === 'decrease') {
            if (numPersonnel > 1) {
                setPersonnel(String(numPersonnel - 1));
                setPersonnelError(false);
            } else {
                setPersonnelError(true);
            }
        }
    };
    
    // 마우스 휠로 값 변경 방지
    const handleWheel = (e) => {
        e.preventDefault();
    };

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

    const handleRecommendClick = () => {
        const numPersonnel = Number(personnel);

        if (personnel === '' || !(Number.isInteger(numPersonnel) && numPersonnel >= 1 && numPersonnel <= 100)) {
            setPersonnelError(true);
            return;
        }
        navigate(`/school/${schoolName}/recommendations`, { state: { personnel } });
    };

    const handleCurrentLocationClick = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    setUserLocation({ latitude, longitude });
                    console.log("사용자 위치:", { latitude, longitude });
                },
                (err) => {
                    console.error("위치 정보를 가져오는 데 실패했습니다.", err);
                    alert("위치 정보를 가져오는 데 실패했습니다. 위치 권한을 허용했는지 확인해 주세요.");
                    setUserLocation(null);
                }
            );
        } else {
            alert("이 브라우저에서는 위치 정보를 지원하지 않습니다.");
        }
    };

    const handleSortChange = (selectedOption) => {
        const newSortCriteria = selectedOption.value;
        setSortCriteria(newSortCriteria);

        if (newSortCriteria === 'distance') {
            handleCurrentLocationClick();
        }
    };

    useEffect(() => {
        const fetchDataAndSetPlaces = async () => {
            setLoading(true);
            setError(null);

            try {
                const congestionResponse = await fetch(`/api/recommendation/congestion`);
                if (!congestionResponse.ok) throw new Error('혼잡도 정보를 불러오지 못했습니다.');
                const congestionData = await congestionResponse.json();
                const congestionMap = new Map(congestionData.items.map(item => [item.location_id, item]));

                let fetchedPlaces = [];

                if (sortCriteria === 'distance' && userLocation) {
                    const locationResponse = await fetch(`/api/recommendation/location?lat=${userLocation.latitude}&lng=${userLocation.longitude}`);
                    if (!locationResponse.ok) throw new Error('거리순 장소 정보를 불러오지 못했습니다.');
                    const locationData = await locationResponse.json();
                    
                    if (locationData.sorted_locations) {
                        fetchedPlaces = locationData.sorted_locations.map(item => {
                            const congestionInfo = congestionMap.get(item.id);
                            return { ...item, ...congestionInfo };
                        });
                    }
                } else {
                    fetchedPlaces = congestionData.items || [];
                }
                
                setPlaces(fetchedPlaces);

            } catch (err) {
                setError("장소 정보를 불러오는 중 오류가 발생했습니다.");
                console.error("API 호출 오류:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchDataAndSetPlaces();
    }, [sortCriteria, userLocation]);
    
    const getCongestionColorClass = (congestion) => {
        if (congestion === null) return '';
        if (congestion <= 0.3) return 'low';
        if (congestion <= 0.7) return 'medium';
        return 'high';
    };

    const schoolData = getSchoolData(schoolName);

    if (loading) {
        return <div><Header /><main className="school-main-container"><h2>장소 목록을 불러오는 중...</h2></main></div>;
    }

<<<<<<< HEAD
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
=======
    if (error) {
        return <div><Header /><main className="school-main-container"><h2>오류 발생: {error}</h2></main></div>;
    }

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
                    <div className="feature-card find-classroom">
                        <h2>몇 명이서 사용하시나요?</h2>
                        <div className="input-container custom-number-input">
                            <button className="decrease-button" onClick={() => handlePersonnelButtonClick('decrease')}>-</button>
                            <input 
                                type="text"
                                placeholder="인원수 입력"
                                value={personnel}
                                onChange={handlePersonnelInput}
                                onWheel={handleWheel}
                                className={`personnel-input ${personnelError ? 'input-error' : ''}`}
                            />
                            <button className="increase-button" onClick={() => handlePersonnelButtonClick('increase')}>+</button>

                            {personnelError && (
                                <p className="error-message floating">
                                    1명부터 100명까지의 숫자를 입력해주세요.
                                </p>
                            )}
                        </div>
                        <button className="search-button" onClick={handleRecommendClick}>장소 추천받기</button>
                    </div>

                    <div className="feature-card reserve-room">
                        <div className="chart-header">
                            <h2>회의실 예약</h2>
                            
                            <CustomDropdown
                                options={[
                                    { value: 'congestion', label: '혼잡도' },
                                    { value: 'distance', label: '가까운 순' },
                                ]}
                                onSelect={handleSortChange}
                                selectedValue={sortCriteria}
                            />
                            
                            {userLocation && (
                                <p className="user-location-display">
                                    현재 위치: {userLocation.latitude.toFixed(4)}, {userLocation.longitude.toFixed(4)}
                                </p>
                            )}
                        </div>

                        <div className="realtime-chart-list">
                            {places.length > 0 ? (
                                places.map((item, index) => (
                                    <div key={item.id || item.location_id} className="chart-item">
                                        <span className="rank-number">{index + 1}</span>
                                        <div className="item-details">
                                            <div className="item-details-left">
                                                <p className="item-name">{item.name}</p>
                                                {(item.building || item.details) && (
                                                    <p className="item-location">{item.building || item.details}</p>
                                                )}
                                            </div>
                                            <div className="item-details-right">
                                                <div className="congestion-squares-container">
                                                    {Array.from({ length: 10 }, (_, i) => (
                                                        <div
                                                            key={i}
                                                            className={`square ${getCongestionColorClass(item.congestion)} ${Math.round(item.congestion * 10) > i ? 'filled' : ''}`}
                                                        ></div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p>장소 목록을 불러올 수 없습니다.</p>
                            )}
                        </div>
                        <p className="hardcoded-label">※ 이 부분은 이제 백엔드에서 데이터를 가져옵니다.</p>
                    </div>
                </div>
            </main>
>>>>>>> 9596587 (feat: 새로운 기능 추가 및 줄바꿈 형식 통일)
        </div>
    );
}

export default SchoolMainPage;