import React, { useState } from 'react';
import './ContactPage.css';

const ContactPage = () => {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <div className="contact-page">
      <h1>Contact Us</h1>
      <form onSubmit={handleSubmit}>
        <label>Name:</label>
        <input type="text" name="name" value={formData.name} onChange={handleChange} />
        <label>Email:</label>
        <input type="email" name="email" value={formData.email} onChange={handleChange} />
        <label>Message:</label>
        <textarea name="message" value={formData.message} onChange={handleChange}></textarea>
        <button type="submit">Send</button>
      </form>
      <div className="contact-info">
        <h2>Follow Us</h2>
        <p>Email: support@mentalhealth.com</p>
        <p>Phone: +1-800-123-4567</p>
      </div>
    </div>
  );
};

export default ContactPage;