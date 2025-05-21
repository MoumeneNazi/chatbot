import React from 'react';
import ReportProblem from './ReportProblem';
import '../styles/components.css';

function ReportProblemModal({ isOpen, onClose }) {
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-btn" onClick={onClose}>×</button>
        <ReportProblem onClose={onClose} />
      </div>
    </div>
  );
}

export default ReportProblemModal; 