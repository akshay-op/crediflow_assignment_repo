import React, { useState } from 'react';
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Upload } from "lucide-react";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Extracting...');
  const [intervalId, setIntervalId] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0); // Track elapsed time in seconds

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    console.log('File selected:', selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    setFile(droppedFile);
    console.log('File dropped:', droppedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('https://amazingly-allowing-stag.ngrok-free.app/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('File uploaded successfully:', response.data);
      alert('File uploaded successfully!');
      setUploadSuccess(true);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file');
    }
  };

  const handleExtract = async () => {
    try {
      setLoading(true);
      setStatusMessage('Extracting');
      setElapsedTime(0);
  
      let baseMessage = 'Extracting';
      const dotInterval = setInterval(() => {
        setStatusMessage(prev => {
          const dots = prev.match(/\./g)?.length || 0;
          return baseMessage + '.'.repeat((dots + 1) % 4);
        });
      }, 500);
      setIntervalId(dotInterval);
  
      // Track elapsed time and change base message after 30 and 60 seconds
      const timeInterval = setInterval(() => {
        setElapsedTime(prev => {
          const newElapsed = prev + 1;
          if (newElapsed === 30) {
            baseMessage = 'Processing';
          } else if (newElapsed === 60) {
            baseMessage = 'Almost Done';
          }
          return newElapsed;
        });
      }, 1000);
  
      await new Promise(resolve => setTimeout(resolve, 50));
  
      const response = await fetch('https://amazingly-allowing-stag.ngrok-free.app/start-process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fileName: file.name }),
      });
  
      clearInterval(dotInterval);
      clearInterval(timeInterval);
      setLoading(false);
  
      if (response.ok) {
        const data = await response.json();
        navigate('/report', { state: { myData: data['message'] } });
      } else {
        const errorData = await response.json();
        alert(errorData.message || 'Something went wrong. Please try again.');
      }
    } catch (error) {
      console.error('Error during extraction:', error);
      clearInterval(intervalId);
      alert('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  

  // Update status message based on elapsed time
  React.useEffect(() => {
    if (elapsedTime === 30) {
      setStatusMessage('Processing...');
    } else if (elapsedTime === 60) {
      setStatusMessage('Almost Done...');
    }
  }, [elapsedTime]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 md:p-8 bg-gradient-to-br from-emerald-600 to-teal-700">
      <div className="w-full max-w-3xl text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Crediflow report</h1>
      </div>

      <Card className="w-full max-w-xl p-6 md:p-8 shadow-2xl bg-white/95 rounded-3xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-semibold text-emerald-700">Upload File</h2>
        </div>

        <div
          className="border-2 border-dashed border-emerald-600/30 rounded-xl p-8 md:p-12 text-center cursor-pointer hover:border-emerald-600/50 transition-colors"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <input
            type="file"
            id="fileInput"
            className="hidden"
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt"
          />
          <Upload className="mx-auto h-12 w-12 text-emerald-600 mb-4" />
          <p className="text-sm md:text-base text-gray-600 mb-2">
            Drag and drop your file here or click to browse
          </p>
          <p className="text-xs text-gray-500">
            {file ? file.name : 'Supported formats: PDF, DOC, DOCX, TXT'}
          </p>
        </div>

        {file && (
          <div className="mt-6 text-center">
            <Button
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-10 py-2 text-lg rounded-md"
              onClick={handleUpload}  // Trigger the file upload when clicked
            >
              Upload File
            </Button>
          </div>
        )}

        {uploadSuccess && (
          <div className="mt-6 text-center">
            <Button
              className="bg-teal-600 hover:bg-teal-700 text-white px-10 py-2 text-lg rounded-md"
              onClick={handleExtract} disabled={loading}
            >
              {loading ? statusMessage : 'Extract'}
            </Button>
          </div>
        )}

      </Card>
    </div>
  );
};

export default UploadPage;
