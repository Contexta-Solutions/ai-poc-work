import React, { useState, useEffect } from 'react';
import { X, Clock, Calendar, AlertCircle, Heart, Wind, Stethoscope, Bone, Sparkles, Brain, Ear } from 'lucide-react';

export default function RightSidebar({ onClose }) {
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    setCurrentDate(new Date());
  }, []);

  const getDynamicStatus = (baseStatus, scheduleString) => {
    if (scheduleString.includes("June 13th - June 26th")) {
      const year = currentDate.getFullYear();
      const leaveStart = new Date(year, 5, 13);
      const leaveEnd = new Date(year, 5, 26, 23, 59, 59);

      if (currentDate >= leaveStart && currentDate <= leaveEnd) {
        return { label: "On Leave", badgeBg: "bg-red-100 dark:bg-red-900/30", badgeText: "text-red-600 dark:text-red-400", displaySchedule: "Currently on leave until June 26th" };
      } else if (currentDate < leaveStart) {
        return { label: "Available", badgeBg: "bg-[#d9fdd3] dark:bg-[#005c4b]/40", badgeText: "text-[#008069] dark:text-[#46c2a8]", displaySchedule: "Upcoming Leave: June 13th - June 26th" };
      } else {
        return { label: "Available", badgeBg: "bg-[#d9fdd3] dark:bg-[#005c4b]/40", badgeText: "text-[#008069] dark:text-[#46c2a8]", displaySchedule: "Regular Schedule" };
      }
    }

    if (baseStatus === "Available") return { label: "Available", badgeBg: "bg-[#d9fdd3] dark:bg-[#005c4b]/40", badgeText: "text-[#008069] dark:text-[#46c2a8]", displaySchedule: scheduleString };
    if (baseStatus === "Emergency Only") return { label: "Emergency Only", badgeBg: "bg-yellow-100 dark:bg-yellow-900/30", badgeText: "text-yellow-700 dark:text-yellow-500", displaySchedule: scheduleString };
    if (baseStatus === "Fully Booked") return { label: "Fully Booked", badgeBg: "bg-red-100 dark:bg-red-900/30", badgeText: "text-red-600 dark:text-red-400", displaySchedule: scheduleString };
    
    return { label: baseStatus, badgeBg: "bg-gray-100 dark:bg-[#2a3942]", badgeText: "text-gray-600 dark:text-[#8696a0]", displaySchedule: scheduleString };
  };

  const DoctorCard = ({ name, specialty, subSpecialty, baseStatus, schedule, icon: Icon }) => {
    const { label, badgeBg, badgeText, displaySchedule } = getDynamicStatus(baseStatus, schedule);
    return (
      <div className="border border-gray-200 dark:border-[#222e35] rounded-lg p-3 bg-white dark:bg-[#111b21] transition-colors">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[#111b21] dark:text-[#e9edef] font-medium">{name}</span>
          <span className={`${badgeBg} ${badgeText} text-[11px] px-2 py-0.5 rounded-full font-medium`}>
            {label}
          </span>
        </div>
        <p className="text-[12px] text-[#54656f] dark:text-[#8696a0]">{specialty}</p>
        <p className="text-[11px] text-[#00878A] dark:text-[#00a884] font-medium mb-2">{subSpecialty}</p>
        <div className="flex items-center text-[13px] text-[#667781] dark:text-[#8696a0]">
          <Icon size={14} className="mr-2 flex-shrink-0" /> 
          <span className="truncate">{displaySchedule}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="w-[30%] min-w-[320px] max-w-[400px] border-l border-gray-200 dark:border-[#222e35] flex flex-col bg-[#f0f2f5] dark:bg-[#202c33] animate-fade-in transition-colors">
      <div className="h-[60px] bg-[#f0f2f5] dark:bg-[#202c33] flex items-center px-6 border-b border-gray-200 dark:border-[#222e35] flex-shrink-0 transition-colors">
        <X size={24} className="cursor-pointer text-[#54656f] dark:text-[#aebac1] hover:text-[#111b21] dark:hover:text-[#e9edef]" onClick={onClose} />
        <span className="ml-6 text-[16px] text-[#111b21] dark:text-[#e9edef] font-medium">Contact info</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="bg-white dark:bg-[#111b21] py-8 flex flex-col items-center justify-center shadow-sm mb-2 transition-colors">
          <div className="w-48 h-48 rounded-full overflow-hidden flex items-center justify-center bg-[#00a884] dark:bg-[#00a884] border border-gray-200 dark:border-[#111b21] shadow-sm mb-4">
            <img src="/favicon.svg" alt="Contexta Health" className="w-full h-full object-cover" />
          </div>
          <a href="https://contexta-demo.vercel.app" target="_blank" rel="noopener noreferrer" className="text-[20px] text-[#111b21] dark:text-[#e9edef] font-normal hover:text-[#00878A] dark:hover:text-[#00a884] transition-colors no-underline">Contexta Health</a>
          <p className="text-[15px] text-[#667781] dark:text-[#8696a0] mt-1">AI Clinical Assistant</p>
          <a href="https://contexta-demo.vercel.app" target="_blank" rel="noopener noreferrer" className="text-[12px] text-[#00878A] dark:text-[#00a884] hover:underline mt-1 block">Website</a>
        </div>

        <div className="bg-white dark:bg-[#111b21] px-6 py-4 shadow-sm mb-2 transition-colors">
          {/* General Physician */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Stethoscope size={14} className="text-teal-400" /> General Physician
          </h3>
          <div className="space-y-3 mb-6">
            <DoctorCard name="Dr. Amit Patel" specialty="General Physician" subSpecialty="General Practice" baseStatus="Available" schedule="All days: 9 AM - 9 PM (Morning, Afternoon & Evening)" icon={Clock} />
            <DoctorCard name="Dr. Rithik" specialty="General Physician" subSpecialty="Internal Medicine" baseStatus="Available" schedule="Weekdays: Morning, Afternoon & Evening" icon={Clock} />
            <DoctorCard name="Dr. Kavitha Rao" specialty="General Physician" subSpecialty="Family Medicine" baseStatus="Available" schedule="Weekends: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Arjun Sharma" specialty="General Physician" subSpecialty="Internal Medicine" baseStatus="Fully Booked" schedule="Weekdays: Morning, Afternoon & Evening" icon={Clock} />
          </div>

          {/* Cardiology */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Heart size={14} className="text-red-400" /> Cardiology
          </h3>
          <div className="space-y-3 mb-6">
            <DoctorCard name="Dr. Rajesh Kapoor" specialty="Cardiology" subSpecialty="Preventive Cardiology" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Ananya Reddy" specialty="Cardiology" subSpecialty="Interventional Cardiology" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Vikram Mehta" specialty="Cardiology" subSpecialty="Cardiac Imaging" baseStatus="Available" schedule="Weekdays: Morning only" icon={Clock} />
          </div>

          {/* Pulmonology */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Wind size={14} className="text-blue-400" /> Pulmonology
          </h3>
          <div className="space-y-3 mb-6">
            <DoctorCard name="Dr. Priya Nair" specialty="Pulmonology" subSpecialty="Interventional Pulmonology" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Sanjay Deshmukh" specialty="Pulmonology" subSpecialty="Lung Cancer" baseStatus="Available" schedule="Weekdays: Morning only" icon={Clock} />
            <DoctorCard name="Dr. Meera Krishnan" specialty="Pulmonology" subSpecialty="Pulmonary Hypertension" baseStatus="On Leave" schedule="June 13th - June 26th" icon={Calendar} />
          </div>

          {/* Orthopedics */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Bone size={14} className="text-orange-400" /> Orthopedics
          </h3>
          <div className="space-y-3 mb-6">
            <DoctorCard name="Dr. Nikhil Verma" specialty="Orthopedics" subSpecialty="Joint Replacement Surgery" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Shreya Joshi" specialty="Orthopedics" subSpecialty="Sports Medicine & Arthroscopy" baseStatus="Available" schedule="Weekdays: Afternoon & Evening" icon={Clock} />
          </div>

          {/* Dermatology */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Sparkles size={14} className="text-pink-400" /> Dermatology
          </h3>
          <div className="space-y-3 mb-6">
            <DoctorCard name="Dr. Ritu Malhotra" specialty="Dermatology" subSpecialty="Cosmetic Dermatology" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Aditya Saxena" specialty="Dermatology" subSpecialty="Clinical Dermatology & Psoriasis" baseStatus="Available" schedule="Weekdays: Afternoon & Evening" icon={Clock} />
          </div>

          {/* Neurology */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Brain size={14} className="text-purple-400" /> Neurology
          </h3>
          <div className="space-y-3 mb-6">
            <DoctorCard name="Dr. Deepak Iyer" specialty="Neurology" subSpecialty="Epilepsy & Stroke" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
            <DoctorCard name="Dr. Sunita Bhat" specialty="Neurology" subSpecialty="Movement Disorders & Parkinson's" baseStatus="Emergency Only" schedule="Weekends On-Call" icon={AlertCircle} />
          </div>

          {/* ENT */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Ear size={14} className="text-amber-400" /> ENT
          </h3>
          <div className="space-y-3">
            <DoctorCard name="Dr. Farhan Qureshi" specialty="ENT" subSpecialty="Head & Neck Surgery" baseStatus="Available" schedule="Weekdays: Morning, Afternoon & Evening" icon={Clock} />
            <DoctorCard name="Dr. Nandini Das" specialty="ENT" subSpecialty="Audiology & Vertigo" baseStatus="Available" schedule="Weekdays: Morning & Afternoon" icon={Clock} />
          </div>
        </div>
      </div>
    </div>
  );
}
