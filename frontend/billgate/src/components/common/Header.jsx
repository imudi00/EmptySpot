// src/components/common/Header.jsx

import React from 'react';
import { Link } from 'react-router-dom'; // Link 컴포넌트를 가져옵니다.
import './Header.css';
import { FaUserCircle, FaQuestionCircle } from 'react-icons/fa';

function Header() {
  return (
    <header className="header-container">
      <div className="header-left">
        {/* 로고를 Link 컴포넌트로 감싸서 클릭 시 첫 페이지로 이동하게 합니다. */}
        <Link to="/" className="header-logo-link">
          <div className="header-logo">
            <span className="logo-text">timebillgate</span>
          </div>
        </Link>
        
      </div>
      <div className="header-right-icons">
        <a href="javascript:void(0)" className="icon-link"><FaQuestionCircle /></a>
        <a href="javascript:void(0)" className="icon-link"><FaUserCircle /></a>
      </div>
    </header>
  );
}

export default Header;
