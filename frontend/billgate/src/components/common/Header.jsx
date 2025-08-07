import React from 'react';
import './Header.css';


import { FaUserCircle, FaQuestionCircle } from 'react-icons/fa';

function Header() {
  return (
    <header className="header-container">
      <div className="header-left">
        <div className="header-logo">
          <span className="logo-text">timebillgate</span>
        </div>
        <nav className="header-nav">
          <a href="#" className="nav-item">로그인</a>
          <a href="#" className="nav-item">회원가입</a>
         
        
        </nav>
      </div>
      <div className="header-right-icons">
        <a href="javascript:void(0)" className="icon-link"><FaQuestionCircle /></a>
  <a href="javascript:void(0)" className="icon-link"><FaUserCircle /></a>
      </div>
    </header>
  );
}

export default Header;