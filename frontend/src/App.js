import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import { useReveal } from './hooks/useReveal';

import Home from './pages/Home';
import About from './pages/About';
import Contact from './pages/Conatct';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import Journal from './pages/Journal';
import Progress from './pages/Progress';
import Therapist from './pages/Therapist';

function App() {
  useReveal(); // enables scroll animation
  return (
    <BrowserRouter>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/therapist" element={<Therapist />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
