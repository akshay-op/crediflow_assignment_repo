

import React, { useState } from 'react';
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Login attempt with:', { username, password });
    // Hardcoded username and password validation
    // Access credentials from environment variables
    const Username = process.env.REACT_APP_USERNAME;
    const Password = process.env.REACT_APP_PASSWORD;

    if (username === Username && password === Password) {
      // Navigate to the upload page upon successful login
      navigate('/upload');
    } else {
      // Alert the user if login credentials are incorrect
      alert('Invalid username or password!');
    }
  };

  return (

    <div className="min-h-screen flex flex-col md:flex-row items-center justify-center md:justify-between px-4 md:px-12 bg-gradient-to-br from-emerald-600 to-teal-700">

      {/* Column 1 - Welcome Text */}
      <div className="w-full md:w-1/2 flex items-center justify-center md:justify-start py-12 md:py-0">
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white text-center md:text-left">
          Welcome!
        </h1>
      </div>

      {/* Column 2 - Login Card */}
      <div className="w-full md:w-1/2 flex justify-center">
        <Card className="w-full md:w-[400px] p-4 md:p-6 shadow-2xl bg-white/95 rounded-3xl max-w-[90%] md:max-w-none">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="text"
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="h-12 px-4 rounded-xl border-gray-200"
            />
            <Input
              type="password"
              placeholder="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-12 px-4 rounded-xl border-gray-200"
            />
            <Button
              type="submit"
              className="w-full h-12 text-white bg-blue-600 hover:bg-blue-700 rounded-xl text-lg font-medium"
            >
              login
            </Button>
          </form>
        </Card>
      </div>
    </div>


  );
};

export default LoginPage;
