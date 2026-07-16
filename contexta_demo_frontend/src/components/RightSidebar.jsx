import React from 'react';
import { X, MapPin, Phone, Clock, Stethoscope, Star, Scan, ScanLine, Droplet, Waves } from 'lucide-react';

// OrthoCare Clinic reference data. Mirrors the backend's ortho_clinic_data.py
// (LOCATIONS + DOCTORS + DIAGNOSTICS_TEXT) -- keep them in sync when the clinic
// data changes.
const LOCATIONS = [
  {
    name: 'KPHB', timings: '9 AM – 5 PM',
    address: 'Plot No. 24, KPHB Colony Main Road, Near KPHB Bus Stop, Kukatpally – 500072',
    contact: 'Mr. Bhanu Chandra', phone: '9988661122',
  },
  {
    name: 'Gachibowli', timings: '10 AM – 8 PM',
    address: '2nd Floor, Gachibowli Main Road, Near DLF Cyber City – 500032',
    contact: 'Ms. Swathi Reddy', phone: '9988662233', note: 'MRI & CT Scan available here',
  },
  {
    name: 'Dilsukhnagar', timings: '11 AM – 6 PM',
    address: 'Dilsukhnagar Main Road, Near Chaitanyapuri Metro Station – 500060',
    contact: 'Mr. Ravi Teja', phone: '9988663344',
  },
];

const PRIMARY_DOCTORS = [
  {
    name: 'Dr. Srinivasa Rao', qualification: 'MBBS, MS (Ortho)',
    specialty: 'General Orthopaedics & Trauma',
    availability: ['KPHB · Mon–Sat, 9 AM – 5 PM (lunch 1–2 PM)'],
  },
  {
    name: 'Dr. Ramesh Babu', qualification: 'MBBS, D. Ortho',
    specialty: 'General Orthopaedics & Joint Care',
    availability: ['Gachibowli · Mon–Sat, 10 AM – 8 PM (lunch 2–3 PM)'],
  },
  {
    name: 'Dr. Padmaja Reddy', qualification: 'MBBS, MS (Ortho)',
    specialty: 'General Orthopaedics & Sports Injury',
    availability: ['Dilsukhnagar · Mon–Sat, 11 AM – 6 PM (lunch 2–3 PM)'],
  },
];

const VISITING_DOCTORS = [
  {
    name: 'Dr. Suresh Kumar Nair', qualification: 'MBBS, MS, DNB (Ortho)',
    specialty: 'Joint Replacement Surgeon (Knee & Hip)',
    availability: [
      'Gachibowli · Mon & Thu, 12 – 3 PM',
      'KPHB · Tue & Fri, 11 AM – 2 PM',
      'Dilsukhnagar · Wed & Sat, 1 – 4 PM',
    ],
  },
  {
    name: 'Dr. Kavitha Subramaniam', qualification: 'MBBS, MS (Ortho), Fellowship Spine',
    specialty: 'Spine Surgeon',
    availability: [
      'KPHB · Mon & Thu, 10 AM – 1 PM',
      'Dilsukhnagar · Tue & Fri, 12 – 3 PM',
      'Gachibowli · Wed & Sat, 11 AM – 2 PM',
    ],
  },
];

// Diagnostic services -- reference only (NOT bookable via the chat; patients
// call the branch to schedule). Mirrors ortho_clinic_data.py DIAGNOSTICS_TEXT.
const DIAGNOSTICS = [
  {
    title: 'X-Ray', icon: ScanLine, badge: 'All branches',
    subtitle: 'Walk-in · Mon–Sat',
    rows: [
      { loc: 'KPHB', sub: 'Mr. Bhaskar Reddy', time: '9 AM – 5 PM' },
      { loc: 'Gachibowli', sub: 'Mr. Naveen Kumar', time: '10 AM – 8 PM' },
      { loc: 'Dilsukhnagar', sub: 'Mr. Prasad Rao', time: '11 AM – 6 PM' },
    ],
  },
  {
    title: 'Blood Work / Lab', icon: Droplet, badge: 'All branches',
    subtitle: 'Sample collection · Mon–Sat',
    rows: [
      { loc: 'KPHB', sub: 'Ms. Divya Sree', time: '9 AM – 5 PM' },
      { loc: 'Gachibowli', sub: 'Mr. Kiran Kumar', time: '10 AM – 8 PM' },
      { loc: 'Dilsukhnagar', sub: 'Ms. Anitha Rani', time: '11 AM – 6 PM' },
    ],
  },
  {
    title: 'Ultrasound', icon: Waves, badge: 'Visiting',
    subtitle: 'Dr. Ganesh Iyer (Sonologist)',
    rows: [
      { loc: 'KPHB', sub: 'Mon & Thu', time: '11 AM – 3 PM' },
      { loc: 'Gachibowli', sub: 'Tue & Fri', time: '12 – 6 PM' },
      { loc: 'Dilsukhnagar', sub: 'Wed & Sat', time: '1 – 5 PM' },
    ],
  },
  {
    title: 'MRI & CT Scan', icon: Scan, badge: 'Gachibowli only',
    subtitle: 'Mr. Arjun Menon · Mon–Sat',
    rows: [
      { loc: 'MRI', time: '10 AM – 4 PM' },
      { loc: 'CT Scan', time: '10 AM – 8 PM' },
    ],
  },
];

function LocationCard({ name, timings, address, contact, phone, note }) {
  return (
    <div className="border border-gray-200 dark:border-[#222e35] rounded-lg p-3 bg-white dark:bg-[#111b21] transition-colors">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[#111b21] dark:text-[#e9edef] font-medium flex items-center gap-1.5">
          <MapPin size={15} className="text-[#00a884] flex-shrink-0" /> {name}
        </span>
        <span className="bg-[#d9fdd3] dark:bg-[#005c4b]/40 text-[#008069] dark:text-[#46c2a8] text-[11px] px-2 py-0.5 rounded-full font-medium">
          {timings}
        </span>
      </div>
      <p className="text-[12px] text-[#54656f] dark:text-[#8696a0] leading-snug mb-2">{address}</p>
      {note && (
        <p className="text-[11px] text-[#00878A] dark:text-[#00a884] font-medium flex items-center gap-1.5 mb-2">
          <Scan size={12} className="flex-shrink-0" /> {note}
        </p>
      )}
      <div className="flex items-center text-[13px] text-[#667781] dark:text-[#8696a0]">
        <Phone size={13} className="mr-2 flex-shrink-0" />
        <span className="truncate">{contact} · {phone}</span>
      </div>
    </div>
  );
}

function DoctorCard({ name, qualification, specialty, availability, visiting }) {
  return (
    <div className="border border-gray-200 dark:border-[#222e35] rounded-lg p-3 bg-white dark:bg-[#111b21] transition-colors">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[#111b21] dark:text-[#e9edef] font-medium">{name}</span>
        <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1 ${
          visiting
            ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-500'
            : 'bg-[#d9fdd3] dark:bg-[#005c4b]/40 text-[#008069] dark:text-[#46c2a8]'
        }`}>
          {visiting ? <Star size={11} /> : null}
          {visiting ? 'Visiting' : 'Primary'}
        </span>
      </div>
      <p className="text-[12px] text-[#54656f] dark:text-[#8696a0]">{qualification}</p>
      <p className="text-[11px] text-[#00878A] dark:text-[#00a884] font-medium mb-2">{specialty}</p>
      <div className="space-y-1">
        {availability.map((line, i) => (
          <div key={i} className="flex items-start text-[13px] text-[#667781] dark:text-[#8696a0]">
            <Clock size={13} className="mr-2 mt-0.5 flex-shrink-0" />
            <span>{line}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function DiagnosticCard({ title, subtitle, rows, badge, icon: Icon }) {
  const highlight = badge && badge.toLowerCase().includes('only');
  return (
    <div className="border border-gray-200 dark:border-[#222e35] rounded-lg p-3 bg-white dark:bg-[#111b21] transition-colors">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[#111b21] dark:text-[#e9edef] font-medium flex items-center gap-1.5">
          <Icon size={15} className="text-[#00a884] flex-shrink-0" /> {title}
        </span>
        {badge && (
          <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
            highlight
              ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-500'
              : 'bg-gray-100 dark:bg-[#2a3942] text-gray-600 dark:text-[#8696a0]'
          }`}>
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="text-[11px] text-[#00878A] dark:text-[#00a884] font-medium mb-2">{subtitle}</p>}
      <div className="space-y-1.5">
        {rows.map((r, i) => (
          <div key={i} className="flex items-center justify-between gap-3 text-[13px]">
            <span className="text-[#111b21] dark:text-[#e9edef] truncate min-w-0">
              <span className="font-medium">{r.loc}</span>
              {r.sub && <span className="text-[#667781] dark:text-[#8696a0]"> · {r.sub}</span>}
            </span>
            <span className="text-[#667781] dark:text-[#8696a0] whitespace-nowrap flex-shrink-0">{r.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function RightSidebar({ onClose, className = '' }) {
  return (
    // Width/position come from `className`: a full-screen overlay on phone and
    // tablet, a plain third column from lg up.
    <div className={`${className} border-l border-gray-200 dark:border-[#222e35] flex flex-col bg-[#f0f2f5] dark:bg-[#202c33] animate-fade-in transition-colors`}>
      <div className="h-[60px] bg-[#f0f2f5] dark:bg-[#202c33] flex items-center px-4 sm:px-6 border-b border-gray-200 dark:border-[#222e35] flex-shrink-0 transition-colors">
        <X size={24} className="cursor-pointer text-[#54656f] dark:text-[#aebac1] hover:text-[#111b21] dark:hover:text-[#e9edef] flex-shrink-0" onClick={onClose} />
        <span className="ml-4 sm:ml-6 text-[16px] text-[#111b21] dark:text-[#e9edef] font-medium">Contact info</span>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        <div className="bg-white dark:bg-[#111b21] py-6 sm:py-8 flex flex-col items-center justify-center shadow-sm mb-2 transition-colors">
          <div className="w-32 h-32 sm:w-48 sm:h-48 rounded-full overflow-hidden flex items-center justify-center bg-[#00a884] dark:bg-[#00a884] border border-gray-200 dark:border-[#111b21] shadow-sm mb-4">
            <img src="/favicon.svg" alt="Contexta Health" className="w-full h-full object-cover" />
          </div>
          <a href="https://contexta-demo.vercel.app" target="_blank" rel="noopener noreferrer" className="text-[20px] text-[#111b21] dark:text-[#e9edef] font-normal hover:text-[#00878A] dark:hover:text-[#00a884] transition-colors no-underline">Contexta Health</a>
          <p className="text-[15px] text-[#667781] dark:text-[#8696a0] mt-1">AI Clinical Assistant</p>
          <p className="text-[12px] text-[#667781] dark:text-[#8696a0] mt-1">OrthoCare Multi-Speciality Clinic · Hyderabad</p>
          <a href="https://contexta-demo.vercel.app" target="_blank" rel="noopener noreferrer" className="text-[12px] text-[#00878A] dark:text-[#00a884] hover:underline mt-1 block">Website</a>
        </div>

        <div className="bg-white dark:bg-[#111b21] px-4 sm:px-6 py-4 shadow-sm mb-2 transition-colors">
          {/* Locations */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <MapPin size={14} className="text-teal-400" /> Locations
          </h3>
          <div className="space-y-3 mb-6">
            {LOCATIONS.map((loc) => <LocationCard key={loc.name} {...loc} />)}
          </div>

          {/* Doctors (primary + visiting, distinguished by the badge on each card) */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-3 uppercase tracking-wide flex items-center gap-2">
            <Stethoscope size={14} className="text-teal-400" /> Doctors
          </h3>
          <div className="space-y-3 mb-6">
            {PRIMARY_DOCTORS.map((doc) => <DoctorCard key={doc.name} {...doc} visiting={false} />)}
            {VISITING_DOCTORS.map((doc) => <DoctorCard key={doc.name} {...doc} visiting={true} />)}
          </div>

          {/* Diagnostic Services (reference only -- not bookable via chat) */}
          <h3 className="text-[14px] text-[#54656f] dark:text-[#8696a0] mb-2 uppercase tracking-wide flex items-center gap-2">
            <Scan size={14} className="text-indigo-400" /> Diagnostic Services
          </h3>
          <p className="text-[11px] text-[#667781] dark:text-[#8696a0] mb-3">
            Lab & scan appointments aren't booked here — call the branch contact to schedule.
          </p>
          <div className="space-y-3">
            {DIAGNOSTICS.map((svc) => <DiagnosticCard key={svc.title} {...svc} />)}
          </div>
        </div>
      </div>
    </div>
  );
}
