"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Users, Info, Eye, EyeOff, MessageSquare, BarChart3, Lightbulb, TrendingUp } from "lucide-react";
import { MainLayout } from "@/components/layout/main-layout";

export default function ResultsPage() {
  const [user, setUser] = useState<any>(null);
  const [simulationInput, setSimulationInput] = useState("");

  useEffect(() => {
    // Check if user is authenticated
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Redirect to auth if not logged in
      window.location.href = "/auth";
    }

    // Get simulation input
    const input = localStorage.getItem("simulationInput");
    if (input) {
      setSimulationInput(input);
    }
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

        <div className="w-full max-w-7xl mx-auto relative z-10">
          {/* Back Button */}
          <motion.a
            href="/simulation"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-8 transition-colors"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ArrowLeft size={20} />
            Back to Simulation
          </motion.a>

          {/* Header */}
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <BarChart3 className="text-gray-700" size={28} />
              <span className="text-gray-600 text-xl">Simulation Results</span>
            </div>
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 leading-tight">
              Analysis Complete
            </h1>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Here's how your personas responded to: <span className="font-semibold">"{simulationInput}"</span>
            </p>
          </motion.div>

          {/* Results Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Analytics Section */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <AnalyticsSection />
            </motion.div>

            {/* Insights Section */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <InsightsSection />
            </motion.div>
          </div>

          {/* Conversations Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <ConversationsSection />
          </motion.div>
        </div>
      </div>
    </MainLayout>
  );
}

function AnalyticsSection() {
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-full">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="text-gray-700" size={24} />
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
      </div>

      {/* Impact Score */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="text-gray-600" size={18} />
          <h3 className="text-lg font-semibold text-gray-900">Impact Score</h3>
          <Info className="text-gray-400" size={16} />
        </div>
        
        <div className="flex items-end gap-4 mb-4">
          <span className="text-4xl font-bold text-gray-900">72</span>
          <span className="text-lg text-gray-500 mb-1">/100</span>
          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium mb-1">
            Moderate
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 h-3 rounded-full" style={{ width: "72%" }}></div>
        </div>
      </div>

      {/* Engagement Breakdown */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Eye className="text-gray-600" size={18} />
          <h3 className="text-lg font-semibold text-gray-900">Engagement</h3>
          <Info className="text-gray-400" size={16} />
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Eye className="text-green-500" size={16} />
              <span className="text-gray-700">High Interest</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: "45%" }}></div>
              </div>
              <span className="text-sm font-medium text-gray-900 w-8">45%</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Eye className="text-blue-500" size={16} />
              <span className="text-gray-700">Moderate Interest</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: "35%" }}></div>
              </div>
              <span className="text-sm font-medium text-gray-900 w-8">35%</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <EyeOff className="text-red-500" size={16} />
              <span className="text-gray-700">Low Interest</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: "20%" }}></div>
              </div>
              <span className="text-sm font-medium text-gray-900 w-8">20%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function InsightsSection() {
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-full">
      <div className="flex items-center gap-2 mb-6">
        <Lightbulb className="text-gray-700" size={24} />
        <h2 className="text-2xl font-bold text-gray-900">Insights</h2>
        <Info className="text-gray-400" size={16} />
      </div>

      <div className="space-y-6">
        <div>
          <p className="text-gray-900 font-medium text-lg leading-relaxed mb-4">
            Your content resonated well with tech-savvy audiences but struggled with broader appeal.
          </p>
        </div>

        <div>
          <p className="text-gray-700 leading-relaxed mb-4">
            Entrepreneurs and developers showed strong engagement, particularly around technical implementation details.
          </p>
        </div>

        <div>
          <p className="text-gray-700 leading-relaxed mb-4">
            Consider simplifying technical jargon to reach a wider audience while maintaining depth for expert users.
          </p>
        </div>

        <div>
          <p className="text-gray-700 leading-relaxed mb-6">
            The timing and platform choice significantly impact reception - LinkedIn performs better than Twitter for this content type.
          </p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <div className="p-1 bg-blue-100 rounded-full">
              <Lightbulb className="text-blue-600" size={16} />
            </div>
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Recommendation</h4>
              <p className="text-blue-800 text-sm">
                Lead with the business value proposition before diving into technical details to maximize engagement across all persona types.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConversationsSection() {
  const conversations = [
    {
      title: "Technical Complexity",
      description: "About 34% of personas found the technical aspects overwhelming, suggesting a need for clearer explanations.",
      quotes: [
        "This seems too complex for everyday users",
        "Need more context about implementation",
        "Great concept but needs simplification"
      ]
    },
    {
      title: "Market Timing",
      description: "Mixed reactions on market readiness, with 28% expressing concerns about adoption timeline.",
      quotes: [
        "Market might not be ready for this yet",
        "Perfect timing with current trends",
        "Early adopters will love this"
      ]
    },
    {
      title: "Value Proposition",
      description: "Strong positive response to core value, with 67% seeing clear benefits for their use cases.",
      quotes: [
        "This solves a real problem I have",
        "Could save significant time and effort",
        "Exactly what the market needs right now"
      ]
    }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <MessageSquare className="text-gray-700" size={24} />
        <h2 className="text-2xl font-bold text-gray-900">Conversations</h2>
        <Info className="text-gray-400" size={16} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {conversations.map((conversation, index) => (
          <motion.div
            key={index}
            className="bg-gray-50 rounded-xl p-5 border border-gray-100"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <h3 className="font-semibold text-gray-900 mb-3">{conversation.title}</h3>
            <p className="text-gray-600 text-sm mb-4 leading-relaxed">
              {conversation.description}
            </p>
            
            <div className="space-y-2">
              {conversation.quotes.map((quote, quoteIndex) => (
                <div key={quoteIndex} className="border-l-3 border-gray-300 pl-3">
                  <p className="text-gray-700 text-sm italic">"{quote}"</p>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}