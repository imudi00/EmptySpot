// src/pages/PlaceDetailPage.jsx

 import React from 'react';
 import { useParams } from 'react-router-dom';
 import Header from '../components/common/Header';
 import './PlaceDetailPage.css';

 function PlaceDetailPage() {
   const { schoolName, placeId } = useParams();

   // 임시 장소 데이터 (나중에 API 연동으로 대체)
   const placeDetails = {
     'lobby-1': {
       name: '대양AI센터 1층 로비',
       location: '세종대학교 대양AI센터 1층',
       description: '넓고 개방적인 공간으로, 다양한 활동이 가능합니다.',
       rating: 4.5,
       image: '/images/lobby-example.jpg', // 예시 이미지 경로
       congestion: {
         Monday: 60,
         Tuesday: 75,
         Wednesday: 70,
         Thursday: 80,
         Friday: 55,
         Saturday: 30,
         Sunday: 20,
       },
     },
     'lounge-15': {
       name: '광개토관 15층 라운지',
       location: '세종대학교 광개토관 15층',
       description: '멋진 전망을 자랑하는 쾌적한 라운지입니다.',
       rating: 4.8,
       image: '/images/lounge-example.jpg', // 예시 이미지 경로
       congestion: {
         Monday: 40,
         Tuesday: 50,
         Wednesday: 45,
         Thursday: 55,
         Friday: 35,
         Saturday: 15,
         Sunday: 10,
       },
     },
     // 다른 장소 데이터 추가
   };

   const details = placeDetails?.[placeId];

   if (!details) {
     return (
       <div>
         <Header />
         <main className="place-detail-container">
           <h2>장소 정보를 찾을 수 없습니다.</h2>
         </main>
       </div>
     );
   }

   const congestionData = Object.entries(details.congestion);

   return (
     <div>
       <Header />
       <main className="place-detail-container">
         <div className="place-image">
           <img src={details.image} alt={details.name} />
         </div>
         <div className="place-info">
           <h1 className="place-name">{details.name}</h1>
           <p className="place-location">위치: {details.location}</p>
           <p className="place-description">{details.description}</p>
           <div className="place-rating">별점: {details.rating}</div>
         </div>
         <div className="congestion-graph">
           <h2>요일별 혼잡도</h2>
           <div className="graph-container">
             {congestionData.map(([day, level]) => (
               <div key={day} className="graph-bar">
                 <div className="day">{day.substring(0, 3)}</div>
                 <div className="bar" style={{ height: `${level}%` }} data-level={level}></div>
               </div>
             ))}
           </div>
         </div>
       </main>
     </div>
   );
 }

 export default PlaceDetailPage;