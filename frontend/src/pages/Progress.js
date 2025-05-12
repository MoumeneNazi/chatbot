import React, { useEffect, useState } from 'react';
import { get } from '../api';

function Progress() {
  const [mood, setMood] = useState('');

  useEffect(() => {
    get('/progress').then(res => setMood(res.mood || 'Not available'));
  }, []);

  return (
    <div className="form-box">
      <h2>Today’s Mood Summary</h2>
      <p>{mood}</p>
    </div>
  );
}

export default Progress;
