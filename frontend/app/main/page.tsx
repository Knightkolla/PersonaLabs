"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Users } from "lucide-react";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";
import { MainLayout } from "@/components/layout/main-layout";

export default function MainPage() {
  const [societyDescription, setSocietyDescription] = useState("");
  const [numberOfPersonas, setNumberOfPersonas] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if user is authenticated
    const userData = localStorage.getItem("user-data");
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Redirect to auth if not logged in
      window.location.href = "/auth";
    }
  }, []);

  const handleCreateSociety = async () => {
    if (!societyDescription.trim()) return;
    
    setIsLoading(true);
    
    // Simulate API call for now
    setTimeout(() => {
      console.log("Creating society:", societyDescription, "with", numberOfPersonas, "personas");
      setIsLoading(false);
      // Navigate to simulation page
      window.location.href = "/simulation";
    }, 2000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSocietyDescription(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    handleCreateSociety();
  };

  const placeholders = [
    "Entrepreneurs in Bangalore...",
    "Gen Z creators in LA...",
    "Investors at a startup demo day...",
    "Researchers at an AI conference...",
    "Tech enthusiasts on Reddit...",
    "Professionals on LinkedIn discussing career growth..."
  ];

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <MainLayout navigationDelay={0}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 flex items-center justify-center px-4 py-8 pb-32 relative overflow-hidden">
        {/* Subtle Background Pattern */}
        <div className="absolute inset-0 overflow-hidden opacity-30">
          <div 
            className="absolute inset-0"
            style={{
              backgroundImage: `url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none'%3E%3Ccircle fill='%23e5e7eb' opacity='0.4' cx='16' cy='16' r='1.5'%3E%3C/circle%3E%3C/svg%3E")`,
            }}
          />
        </div>

        <div className="w-full max-w-2xl relative z-10">
          {/* Back Button */}
          <motion.a
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-12 transition-colors"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ArrowLeft size={20} />
            Back to Home
          </motion.a>

          {/* Main Content */}
          <div className="text-center">
            {/* Welcome Message */}
            <motion.div
              className="mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="flex items-center justify-center gap-2 mb-4">
                <Users className="text-gray-700" size={24} />
                <span className="text-gray-600 text-lg">Welcome back, {user?.name}</span>
              </div>
            </motion.div>

            {/* Main Heading */}
            <motion.h1
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Who do you want in your society?
            </motion.h1>

            {/* Description */}
            <motion.p
              className="text-gray-600 text-lg md:text-xl mb-12 max-w-3xl mx-auto leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Describe the people you want in your society. We'll match your description with
              AI personas from our database. Every AI persona is based on a real person.
            </motion.p>

            {/* Input Section */}
            <motion.div
              className="mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <PlaceholdersAndVanishInput
                placeholders={placeholders}
                onChange={handleInputChange}
                onSubmit={handleSubmit}
              />
            </motion.div>

            {/* Number of Personas Selection */}
            <motion.div
              className="mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-700 mb-4">
                  How many personas do you want to simulate?
                </h3>
                <div className="flex items-center justify-center gap-4">
                  {[3, 5, 8, 10, 15].map((number) => (
                    <button
                      key={number}
                      onClick={() => setNumberOfPersonas(number)}
                      className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                        numberOfPersonas === number
                          ? "bg-black text-white shadow-lg scale-105"
                          : "bg-white text-gray-600 border border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      {number}
                    </button>
                  ))}
                </div>
                <p className="text-gray-500 text-sm mt-3">
                  Selected: {numberOfPersonas} personas
                </p>
              </div>
            </motion.div>

            {/* Status Message */}
            {isLoading && (
              <motion.div
                className="flex items-center justify-center gap-2 text-gray-600 mb-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                Creating your society with {numberOfPersonas} personas...
              </motion.div>
            )}

            {/* Helper Text */}
            <motion.p
              className="text-gray-500 text-sm mt-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              Type your society description and press Enter to continue
            </motion.p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}