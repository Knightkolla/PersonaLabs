export interface Persona {
  id: string;
  name: string;
  age: number;
  occupation: string;
  location: string;
  image: string;
  bio: string;
  personality: {
    traits: string[];
    values: string[];
    communication_style: string;
  };
  background: {
    education: string;
    experience: string;
    interests: string[];
  };
  social: {
    network_size: string;
    influence_level: string;
    preferred_platforms: string[];
  };
}

export const demoPersonas: Persona[] = [
  {
    id: "1",
    name: "Sarah Chen",
    age: 28,
    occupation: "Product Manager at Tech Startup",
    location: "San Francisco, CA",
    image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop&crop=face",
    bio: "Passionate about building products that solve real-world problems. Former consultant turned tech PM with a focus on user experience and data-driven decisions.",
    personality: {
      traits: ["Analytical", "Empathetic", "Goal-oriented", "Collaborative"],
      values: ["Innovation", "User-centricity", "Transparency", "Growth"],
      communication_style: "Direct but diplomatic, prefers structured discussions with clear action items"
    },
    background: {
      education: "MBA from Stanford, BS in Computer Science from UC Berkeley",
      experience: "5 years in product management, 3 years in consulting at McKinsey",
      interests: ["Design thinking", "Behavioral psychology", "Rock climbing", "Sustainable technology"]
    },
    social: {
      network_size: "Large professional network (500+ LinkedIn connections)",
      influence_level: "Medium - respected voice in product management circles",
      preferred_platforms: ["LinkedIn", "Twitter", "Product Hunt"]
    }
  },
  {
    id: "2",
    name: "Marcus Johnson",
    age: 35,
    occupation: "Senior Software Engineer",
    location: "Austin, TX",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
    bio: "Full-stack developer with 12+ years of experience. Open source contributor and tech mentor. Believes in writing clean, maintainable code and fostering inclusive tech communities.",
    personality: {
      traits: ["Methodical", "Patient", "Curious", "Mentoring-oriented"],
      values: ["Code quality", "Knowledge sharing", "Diversity & inclusion", "Continuous learning"],
      communication_style: "Thoughtful and detailed, enjoys technical deep-dives and teaching moments"
    },
    background: {
      education: "MS in Computer Science from UT Austin, BS from Howard University",
      experience: "12 years in software development, 3 years as tech lead, active open source contributor",
      interests: ["Machine learning", "Jazz music", "Basketball", "Cooking", "Mentoring junior developers"]
    },
    social: {
      network_size: "Moderate but engaged network (300+ connections)",
      influence_level: "High in developer communities, known for thoughtful technical content",
      preferred_platforms: ["GitHub", "Stack Overflow", "Twitter", "Dev.to"]
    }
  },
  {
    id: "3",
    name: "Elena Rodriguez",
    age: 31,
    occupation: "UX Designer & Researcher",
    location: "Barcelona, Spain",
    image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face",
    bio: "Human-centered designer passionate about creating inclusive digital experiences. Specializes in user research and accessibility design for global products.",
    personality: {
      traits: ["Creative", "Empathetic", "Detail-oriented", "Culturally aware"],
      values: ["Accessibility", "Human dignity", "Cultural sensitivity", "Beautiful functionality"],
      communication_style: "Visual storyteller, uses empathy and data to advocate for user needs"
    },
    background: {
      education: "MA in Interaction Design from ELISAVA, BA in Psychology from University of Barcelona",
      experience: "8 years in UX design, worked with startups and Fortune 500 companies across 3 continents",
      interests: ["Accessibility advocacy", "Photography", "Flamenco dancing", "Sustainable design", "Travel"]
    },
    social: {
      network_size: "Global network of designers and researchers (400+ connections)",
      influence_level: "Medium-high in design communities, speaks at international conferences",
      preferred_platforms: ["Dribbble", "Behance", "LinkedIn", "Instagram"]
    }
  },
  {
    id: "4",
    name: "David Kim",
    age: 26,
    occupation: "Data Scientist & AI Researcher",
    location: "Seoul, South Korea",
    image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
    bio: "PhD candidate researching ethical AI and machine learning fairness. Works on developing algorithms that reduce bias in automated decision-making systems.",
    personality: {
      traits: ["Intellectual", "Ethical", "Systematic", "Future-focused"],
      values: ["Scientific rigor", "Ethical technology", "Social justice", "Knowledge advancement"],
      communication_style: "Precise and evidence-based, enjoys complex theoretical discussions"
    },
    background: {
      education: "PhD in Computer Science (in progress) from KAIST, MS from Seoul National University",
      experience: "4 years in data science, 2 years in AI research, published 8 peer-reviewed papers",
      interests: ["Ethics in AI", "Classical music", "Go (board game)", "Philosophy", "Quantum computing"]
    },
    social: {
      network_size: "Academic and research-focused network (250+ connections)",
      influence_level: "High in academic circles, emerging voice in AI ethics",
      preferred_platforms: ["ResearchGate", "LinkedIn", "Twitter", "arXiv"]
    }
  },
  {
    id: "5",
    name: "Amara Okafor",
    age: 29,
    occupation: "Marketing Director & Brand Strategist",
    location: "Lagos, Nigeria",
    image: "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=400&h=400&fit=crop&crop=face",
    bio: "Creative marketing leader building authentic brand connections across African markets. Expert in digital marketing, influencer partnerships, and cross-cultural brand positioning.",
    personality: {
      traits: ["Charismatic", "Strategic", "Culturally intelligent", "Trend-aware"],
      values: ["Authentic storytelling", "Cultural representation", "Economic empowerment", "Creative excellence"],
      communication_style: "Engaging storyteller, adapts communication style to audience and cultural context"
    },
    background: {
      education: "MBA in Marketing from Lagos Business School, BA in Communications from University of Lagos",
      experience: "7 years in marketing, launched 15+ successful campaigns, built marketing teams from scratch",
      interests: ["Afrobeats music", "Contemporary African art", "Fashion", "Social entrepreneurship", "Travel"]
    },
    social: {
      network_size: "Extensive network across Africa and globally (800+ connections)",
      influence_level: "High in African marketing and business communities",
      preferred_platforms: ["LinkedIn", "Instagram", "Twitter", "TikTok"]
    }
  }
];