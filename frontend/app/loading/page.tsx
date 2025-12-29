"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MessageCircle, Users, Brain, BarChart3 } from "lucide-react";
import { MainLayout } from "@/components/layout/main-layout";
import { demoPersonas } from "@/lib/demo-personas";

export default function LoadingPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [user, setUser] = useState<any>(null);

  const loadingSteps = [
    { text: "Initializing AI personas...", icon: Users },
    { text: "Distributing your prompt across the network...", icon: MessageCircle },
    { text: "Processing individual responses...", icon: Brain },
    { text: "Analyzing conversation patterns...", icon: MessageCircle },
    { text: "Generating insights and analytics...", icon: BarChart3 }
  ];

  useEffect(() => {
    // Check if user is authenticated
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Redirect to auth if not logged in
      window.location.href = "/auth";
    }
  }, []);

  useEffect(() => {
    // Progress through loading steps (7 seconds / 5 steps = 1.4 seconds per step)
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < loadingSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 1400);

    // Navigate to results after 7 seconds
    const navigationTimeout = setTimeout(() => {
      window.location.href = "/results";
    }, 7000);

    return () => {
      clearInterval(stepInterval);
      clearTimeout(navigationTimeout);
    };
  }, []);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <MainLayout navigationDelay={0}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 px-4 py-8 pb-32 relative overflow-hidden">
        {/* Subtle Background Pattern */}
        <div className="absolute inset-0 overflow-hidden opacity-30">
          <div 
            className="absolute inset-0"
            style={{
              backgroundImage: `url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none'%3E%3Ccircle fill='%23e5e7eb' opacity='0.4' cx='16' cy='16' r='1.5'%3E%3C/circle%3E%3C/svg%3E")`,
            }}
          />
        </div>

        <div className="w-full max-w-6xl mx-auto relative z-40">
          {/* Header */}
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <Users className="text-gray-700" size={28} />
              <span className="text-gray-600 text-xl">Processing Simulation</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 leading-tight">
              Your Personas Are Thinking...
            </h1>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              AI personas are analyzing your prompt and formulating their responses
            </p>
          </motion.div>

          {/* Main Content - 70/30 Layout */}
          <div className="flex items-start justify-center gap-12 w-full">
            {/* Personas Network - 70% */}
            <motion.div
              className="flex-shrink-0"
              style={{ width: "70%" }}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              {/* Personas Network - EXACT COPY from simulation page */}
              <div className="relative">
                {/* Connection Lines - Full Interconnection */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 10 }}>
                  {/* Center to all corners */}
                  <line x1="50%" y1="50%" x2="16.67%" y2="16.67%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="50%" y1="50%" x2="83.33%" y2="16.67%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="50%" y1="50%" x2="16.67%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="50%" y1="50%" x2="83.33%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  
                  {/* Corner to corner connections */}
                  <line x1="16.67%" y1="16.67%" x2="83.33%" y2="16.67%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="16.67%" y1="16.67%" x2="16.67%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="16.67%" y1="16.67%" x2="83.33%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="83.33%" y1="16.67%" x2="16.67%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="83.33%" y1="16.67%" x2="83.33%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                  <line x1="16.67%" y1="83.33%" x2="83.33%" y2="83.33%" stroke="#e5e7eb" strokeWidth="2" strokeDasharray="5,5" />
                </svg>

                {/* Animated Message Icons - Above lines, below nodes */}
                <div className="absolute inset-0" style={{ zIndex: 20 }}>
                  <AnimatedMessage from="50%" to="16.67%" fromY="50%" toY="16.67%" delay={0} />
                  <AnimatedMessage from="50%" to="83.33%" fromY="50%" toY="16.67%" delay={1} />
                  <AnimatedMessage from="50%" to="16.67%" fromY="50%" toY="83.33%" delay={2} />
                  <AnimatedMessage from="50%" to="83.33%" fromY="50%" toY="83.33%" delay={3} />
                  <AnimatedMessage from="16.67%" to="83.33%" fromY="16.67%" toY="16.67%" delay={4} />
                  <AnimatedMessage from="16.67%" to="83.33%" fromY="16.67%" toY="83.33%" delay={5} />
                </div>

                {/* Personas Grid - EXACT COPY from simulation page */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-8 relative" style={{ zIndex: 30 }}>
                  {/* Center persona */}
                  <div className="md:col-start-2 md:row-start-2 flex justify-center">
                    <LoadingPersonaNode persona={demoPersonas[0]} isCenter={true} />
                  </div>
                  
                  {/* Surrounding personas */}
                  <div className="flex justify-center">
                    <LoadingPersonaNode persona={demoPersonas[1]} />
                  </div>
                  <div className="flex justify-center md:col-start-3 md:row-start-1">
                    <LoadingPersonaNode persona={demoPersonas[2]} />
                  </div>
                  <div className="flex justify-center md:col-start-1 md:row-start-3">
                    <LoadingPersonaNode persona={demoPersonas[3]} />
                  </div>
                  <div className="flex justify-center md:col-start-3 md:row-start-3">
                    <LoadingPersonaNode persona={demoPersonas[4]} />
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Loading Steps - 30% */}
            <motion.div
              className="flex-shrink-0"
              style={{ width: "30%" }}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="space-y-3">
                {loadingSteps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index <= currentStep;
                  const isCurrent = index === currentStep;
                  
                  return (
                    <motion.div
                      key={index}
                      className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                        isActive ? "bg-gray-100 shadow-sm" : "bg-transparent"
                      }`}
                      initial={{ opacity: 0.5 }}
                      animate={{ 
                        opacity: isActive ? 1 : 0.5,
                        scale: isCurrent ? 1.02 : 1
                      }}
                      transition={{ duration: 0.3 }}
                    >
                      <div className={`p-2 rounded-full ${
                        isActive ? "bg-black text-white" : "bg-gray-200 text-gray-400"
                      }`}>
                        <Icon size={16} />
                      </div>
                      <span className={`text-sm font-medium flex-1 ${
                        isActive ? "text-gray-900" : "text-gray-500"
                      }`}>
                        {step.text}
                      </span>
                      {isCurrent && (
                        <motion.div
                          className="ml-auto"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                          <div className="w-3 h-3 border-2 border-gray-300 border-t-black rounded-full"></div>
                        </motion.div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

function AnimatedMessage({ from, to, fromY, toY, delay }: {
  from: string;
  to: string;
  fromY: string;
  toY: string;
  delay: number;
}) {
  return (
    <motion.div
      className="absolute w-5 h-5 bg-black rounded-full flex items-center justify-center shadow-lg"
      style={{ zIndex: 20 }}
      initial={{ 
        left: from, 
        top: fromY,
        x: "-50%",
        y: "-50%"
      }}
      animate={{
        left: [from, to, from],
        top: [fromY, toY, fromY],
      }}
      transition={{
        duration: 5,
        repeat: Infinity,
        delay: delay,
        ease: "easeInOut"
      }}
    >
      <MessageCircle size={10} className="text-white" />
    </motion.div>
  );
}

function LoadingPersonaNode({ persona, isCenter = false }: {
  persona: any;
  isCenter?: boolean;
}) {
  return (
    <motion.div
      className={`relative bg-white rounded-xl shadow-lg border border-gray-200 p-4 ${
        isCenter ? "w-32 h-24" : "w-28 h-20"
      }`}
      animate={{ 
        scale: [1, 1.05, 1],
        boxShadow: [
          "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
          "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
          "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
        ]
      }}
      transition={{ 
        duration: 2, 
        repeat: Infinity, 
        delay: Math.random() * 2,
        ease: "easeInOut"
      }}
    >
      {/* Profile Image */}
      <div className="relative mb-2 flex justify-center">
        <img
          src={persona.image}
          alt={persona.name}
          className={`rounded-full object-cover ${
            isCenter ? "w-10 h-10" : "w-8 h-8"
          }`}
        />
        <motion.div 
          className="absolute -top-1 -right-2 w-3 h-3 bg-green-400 rounded-full border-2 border-white"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      </div>

      {/* Name */}
      <h3 className={`font-semibold text-gray-900 text-center leading-tight truncate px-1 ${
        isCenter ? "text-xs" : "text-xs"
      }`}>
        {persona.name.split(' ')[0]}
      </h3>
    </motion.div>
  );
}