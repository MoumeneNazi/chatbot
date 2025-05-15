import React, { useState, useEffect } from "react";

function Progress() {
  const [moodSummary, setMoodSummary] = useState(null);

  useEffect(() => {
    // Fetch mood summary from the backend
    fetch("http://localhost:8000/progress", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Mood Summary:", data); // Log the response structure
        if (data && typeof data === 'object') {
          setMoodSummary(data);
        } else {
          console.error("Invalid data structure:", data);
        }
      })
      .catch((error) => {
        console.error("Error fetching mood summary:", error);
      });
  }, []);

  // Loading message if the moodSummary is still null
  if (!moodSummary) {
    return <div>Loading mood summary...</div>;
  }

  // Render the sentiment data dynamically
  return (
    <div className="progress-page">
      <h1>Mood Summary</h1>
      <div className="summary-grid">
        {Object.entries(moodSummary).map(([key, value]) => (
          <div key={key} className="summary-box">
            <h3>{key.charAt(0).toUpperCase() + key.slice(1)}</h3>
            <p>{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Progress;
