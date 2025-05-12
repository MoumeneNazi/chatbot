import React from 'react';
import './AboutPage.css';

const AboutPage = () => {
  return (
    <div className="about-page">
      <h1>About Us</h1>
      <section className="mission">
        <h2>Our Mission</h2>
        <p>To make mental health care accessible and available to everyone.</p>
      </section>
      <section className="vision">
        <h2>Our Vision</h2>
        <p>Empowering individuals with tools to improve their mental well-being.</p>
      </section>
      <section className="team">
        <h2>Meet the Team</h2>
        <p>We are a group of passionate individuals committed to mental health advocacy.</p>
      </section>
    </div>
  );
};

export default AboutPage;