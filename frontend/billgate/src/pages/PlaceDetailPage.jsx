// src/pages/PlaceDetailPage.jsx

import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../components/common/Header';
import './PlaceDetailPage.css';

function PlaceDetailPage() {
  const { placeId } = useParams();
  const [placeDetails, setPlaceDetails] = useState(null);
  const [distance, setDistance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hourlyCongestion, setHourlyCongestion] = useState({});

  const getCongestionColorClass = (level) => {
    if (level <= 30) return 'low';
    if (level <= 70) return 'medium';
    return 'high';
  };

  const fetchAllData = useCallback(async (userLat, userLng) => {
    try {
      setLoading(true);
      // 장소 정보와 혼잡도 데이터를 먼저 불러옵니다.
      const placeResponse = await fetch(`/api/places/${placeId}`);
      if (!placeResponse.ok) {
        throw new Error('장소 정보를 불러오지 못했습니다. (네트워크 오류)');
      }
      const placeData = await placeResponse.json();
      
      if (!placeData || !placeData.place || !placeData.place.name) {
        setPlaceDetails(null);
        return;
      }
      setPlaceDetails(placeData.place);

      // 시간별 혼잡도 데이터 로드
      const hours = Array.from({ length: 14 }, (_, i) => 9 + i);
      const hourlyData = {};
      for (const hour of hours) {
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/congestion/avg?location_id=${placeId}&hour=${hour}`);
          if (response.ok) {
            const data = await response.json();
            hourlyData[hour] = data.congestion;
          } else {
            hourlyData[hour] = null;
          }
        } catch (err) {
          console.error(`Error fetching congestion for hour ${hour}:`, err);
          hourlyData[hour] = null;
        }
      }
      setHourlyCongestion(hourlyData);

      // 사용자의 실제 위치를 기반으로 거리 정보 API 호출
      const recommendationResponse = await fetch(`/api/recommendation/location?lat=${userLat}&lng=${userLng}`);
      if (!recommendationResponse.ok) {
        throw new Error('거리 정보를 불러오지 못했습니다. (네트워크 오류)');
      }
      const recommendationData = await recommendationResponse.json();
      
      if (recommendationData.sorted_locations) {
        const matchedPlace = recommendationData.sorted_locations.find(
          (loc) => loc.id === Number(placeId)
        );
        
        if (matchedPlace) {
          setDistance(matchedPlace.distance_km);
        }
      }
      
    } catch (err) {
      console.error("Fetch Error:", err);
      setError(`데이터 로딩 중 오류 발생: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [placeId]);

  const refreshLocationAndDistance = useCallback(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userLat = position.coords.latitude;
          const userLng = position.coords.longitude;
          fetchAllData(userLat, userLng);
        },
        (err) => {
          console.error("Geolocation Error:", err);
          console.warn("사용자 위치를 가져오지 못하여 기본 위치로 거리를 계산합니다.");
          fetchAllData(38, 127);
        }
      );
    } else {
      console.warn("Geolocation API가 지원되지 않아 기본 위치로 거리를 계산합니다.");
      fetchAllData(38, 127);
    }
  }, [fetchAllData]);

  useEffect(() => {
    refreshLocationAndDistance();
  }, [refreshLocationAndDistance]);
  
  if (loading) {
    return (
      <div>
        <Header />
        <main className="place-detail-container">
          <h2>장소 정보를 불러오는 중... ⏳</h2>
          <p>잠시만 기다려주세요.</p>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Header />
        <main className="place-detail-container">
          <h2>오류 발생 ❌</h2>
          <p>{error}</p>
        </main>
      </div>
    );
  }
  
  if (!placeDetails) {
    return (
      <div>
        <Header />
        <main className="place-detail-container">
          <h2>장소 정보를 찾을 수 없습니다. 🤔</h2>
        </main>
      </div>
    );
  }
  
  const hours = Object.keys(hourlyCongestion).sort((a, b) => a - b);

  return (
    <div>
      <Header />
      <main className="place-detail-container">
        <div className="place-image">
          {placeDetails.image && (
            <img src={placeDetails.image} alt={placeDetails.name} />
          )}
        </div>
        <div className="place-info-card">
          <h1 className="place-name">{placeDetails.name || '장소 이름'}</h1>
          <p className="place-location">📍 {placeDetails.building || '정보 없음'}</p>
          <p className="place-distance">
            📏 거리: {distance !== null ? `${distance}km` : '정보 없음'}
            <button onClick={refreshLocationAndDistance} className="refresh-button">
              <span role="img" aria-label="refresh-location">📍 현위치 갱신</span>
            </button>
          </p>
          <p className="place-description">{placeDetails.details || '설명 없음'}</p>
        </div>

        <div className="congestion-graph-card">
          <h2>시간대별 혼잡도</h2>
          <div className="graph-container">
            {hours.length > 0 ? (
              hours.map((hour) => {
                const level = hourlyCongestion[hour];
                return (
                  <div key={hour} className="graph-bar-item">
                    <div className="day">{hour}시</div>
                    <div className={`bar-chart ${getCongestionColorClass(level)}`}>
                      <div className="bar" style={{ height: `${level}%` }}></div>
                    </div>
                    <div className="bar-label">{level !== null ? `${level}%` : '-'}</div>
                  </div>
                );
              })
            ) : (
              <p>시간별 혼잡도 데이터가 없습니다.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default PlaceDetailPage;