// src/components/CustomDropdown.jsx

import React, { useState } from 'react';
import './CustomDropdown.css'; // 커스텀 CSS 파일

// ⭐️ selectedValue prop을 받도록 수정
const CustomDropdown = ({ options, onSelect, selectedValue }) => {
    const [isOpen, setIsOpen] = useState(false);

    // ⭐️ 부모로부터 전달받은 selectedValue prop을 기반으로 현재 선택된 항목을 찾습니다.
    const selectedOption = options.find(option => option.value === selectedValue);

    const handleSelect = (option) => {
        onSelect(option); // 부모 컴포넌트로 선택된 값 전달
        setIsOpen(false);
    };

    return (
        <div className="custom-dropdown-container">
            <div className="dropdown-selected" onClick={() => setIsOpen(!isOpen)}>
                {/* ⭐️ 찾은 selectedOption의 label을 표시 */}
                {selectedOption ? selectedOption.label : '선택하세요'}
                <span className={`arrow ${isOpen ? 'up' : 'down'}`}>▼</span>
            </div>
            {isOpen && (
                <ul className="dropdown-options">
                    {options.map((option) => (
                        <li
                            key={option.value}
                            // ⭐️ 선택된 값에 따라 active 클래스 추가
                            className={`dropdown-item ${selectedValue === option.value ? 'active' : ''}`}
                            onClick={() => handleSelect(option)}
                        >
                            {option.label}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default CustomDropdown;