import React from 'react';
import './ProjectsPage.css';

const ProjectsPage = () => {
  const projects = [
    { title: 'AI Chatbot', description: 'An intelligent chatbot for mental health support.' },
    { title: 'Therapist Dashboard', description: 'A platform for therapists to monitor chats.' },
    { title: 'Wellness Tracker', description: 'Track your daily mental health activities.' },
  ];

  return (
    <div className="projects-page">
      <h1>Our Projects</h1>
      <div className="project-cards">
        {projects.map((project, index) => (
          <div key={index} className="project-card">
            <h3>{project.title}</h3>
            <p>{project.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectsPage;