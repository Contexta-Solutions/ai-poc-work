import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '';

// Contexta Health SVG Logo (extracted from contextaemr.com) -- copied from
// VisitNotesApp rather than imported, so this POC stays self-contained and can be
// lifted out or dropped without touching the shipped page.
const ContextaLogo = ({ className = '' }) => (
  <svg height="20" viewBox="0 0 2842 410" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M184.693 281.275C199.425 281.275 211.367 293.218 211.367 307.949L211.368 383.291C211.368 398.022 199.425 409.965 184.693 409.965C169.961 409.965 158.019 398.022 158.019 383.29L158.018 307.949C158.019 293.218 169.962 281.275 184.693 281.275ZM184.692 0C198.898 0.000161361 210.414 11.5161 210.414 25.7217V153.729C210.414 178.914 223.85 202.187 245.662 214.78L356.519 278.784C368.822 285.887 373.037 301.617 365.934 313.92C358.832 326.223 343.1 330.438 330.798 323.335L219.939 259.33C198.128 246.737 171.254 246.738 149.442 259.331L38.5868 323.334C26.2842 330.437 10.553 326.222 3.4501 313.919C-3.65243 301.616 0.562839 285.886 12.8651 278.783L123.723 214.779C145.534 202.186 158.971 178.913 158.971 153.728V25.7217C158.971 11.516 170.487 0 184.692 0ZM6.99404 106.592C14.3599 93.834 30.6735 89.4627 43.4315 96.8281L108.68 134.499C121.437 141.865 125.808 158.179 118.442 170.937C111.076 183.694 94.7628 188.065 82.0048 180.699L16.7577 143.029C3.99978 135.663 -0.37171 119.35 6.99404 106.592ZM325.785 96.8271C338.543 89.4618 354.857 93.8331 362.223 106.591C369.588 119.349 365.217 135.662 352.459 143.028L287.212 180.699C274.454 188.065 258.14 183.693 250.774 170.936C243.409 158.177 247.78 141.864 260.538 134.498L325.785 96.8271Z" fill="#00878A" />
    <path d="M624.238 325.769C595.55 325.769 573.04 316.137 556.707 296.872C540.374 277.398 532.207 249.234 532.207 212.38C532.207 193.953 534.301 177.725 538.489 163.695C542.677 149.665 548.749 137.834 556.707 128.202C564.664 118.57 574.296 111.345 585.604 106.529C597.12 101.504 609.998 98.9908 624.238 98.9908C643.293 98.9908 659.207 103.179 671.98 111.555C684.963 119.931 695.119 132.285 702.448 148.618L672.609 164.951C668.839 154.481 662.976 146.21 655.019 140.138C647.271 133.856 637.011 130.715 624.238 130.715C607.276 130.715 593.98 136.473 584.347 147.99C574.715 159.507 569.899 175.421 569.899 195.733V229.027C569.899 249.339 574.715 265.253 584.347 276.77C593.98 288.287 607.276 294.045 624.238 294.045C637.43 294.045 648.109 290.695 656.276 283.994C664.651 277.084 670.829 268.289 674.807 257.61L703.39 274.885C696.061 290.8 685.801 303.259 672.609 312.263C659.416 321.267 643.293 325.769 624.238 325.769ZM802.579 325.769C791.271 325.769 780.906 323.78 771.483 319.801C762.27 315.823 754.417 310.169 747.926 302.84C741.434 295.302 736.409 286.298 732.849 275.828C729.289 265.148 727.509 253.317 727.509 240.335C727.509 227.352 729.289 215.626 732.849 205.156C736.409 194.476 741.434 185.472 747.926 178.143C754.417 170.605 762.27 164.847 771.483 160.868C780.906 156.889 791.271 154.9 802.579 154.9C813.886 154.9 824.147 156.889 833.36 160.868C842.783 164.847 850.74 170.605 857.232 178.143C863.723 185.472 868.749 194.476 872.308 205.156C875.868 215.626 877.648 227.352 877.648 240.335C877.648 253.317 875.868 265.148 872.308 275.828C868.749 286.298 863.723 295.302 857.232 302.84C850.74 310.169 842.783 315.823 833.36 319.801C824.147 323.78 813.886 325.769 802.579 325.769ZM802.579 297.5C814.305 297.5 823.728 293.941 830.847 286.821C837.967 279.492 841.527 268.603 841.527 254.155V226.514C841.527 212.066 837.967 201.282 830.847 194.162C823.728 186.833 814.305 183.169 802.579 183.169C790.852 183.169 781.429 186.833 774.31 194.162C767.19 201.282 763.631 212.066 763.631 226.514V254.155C763.631 268.603 767.19 279.492 774.31 286.821C781.429 293.941 790.852 297.5 802.579 297.5ZM915.796 322V158.669H950.033V185.682H951.603C955.163 176.887 960.503 169.558 967.622 163.695C974.951 157.832 984.898 154.9 997.461 154.9C1014.21 154.9 1027.2 160.449 1036.41 171.547C1045.83 182.436 1050.54 198.036 1050.54 218.348V322H1016.31V222.745C1016.31 197.199 1006.05 184.425 985.526 184.425C981.128 184.425 976.731 185.053 972.334 186.31C968.146 187.357 964.377 189.032 961.026 191.335C957.676 193.639 954.954 196.57 952.86 200.13C950.975 203.69 950.033 207.878 950.033 212.694V322H915.796ZM1143.23 322C1131.29 322 1122.29 318.964 1116.21 312.891C1110.14 306.609 1107.11 297.814 1107.11 286.507V186.624H1081.66V158.669H1095.48C1101.14 158.669 1105.01 157.413 1107.11 154.9C1109.41 152.387 1110.56 148.304 1110.56 142.65V114.067H1141.34V158.669H1175.58V186.624H1141.34V294.045H1173.07V322H1143.23ZM1275.57 325.769C1263.84 325.769 1253.37 323.78 1244.16 319.801C1234.94 315.823 1227.09 310.169 1220.6 302.84C1214.11 295.302 1209.08 286.298 1205.52 275.828C1202.17 265.148 1200.5 253.317 1200.5 240.335C1200.5 227.352 1202.17 215.626 1205.52 205.156C1209.08 194.476 1214.11 185.472 1220.6 178.143C1227.09 170.605 1234.94 164.847 1244.16 160.868C1253.37 156.889 1263.84 154.9 1275.57 154.9C1287.5 154.9 1297.97 156.994 1306.98 161.182C1316.19 165.37 1323.83 171.233 1329.9 178.772C1335.98 186.1 1340.48 194.686 1343.41 204.528C1346.55 214.369 1348.12 224.944 1348.12 236.251V249.129H1235.99V254.469C1235.99 267.033 1239.65 277.398 1246.98 285.565C1254.52 293.522 1265.2 297.5 1279.02 297.5C1289.07 297.5 1297.55 295.302 1304.46 290.904C1311.37 286.507 1317.24 280.539 1322.05 273.001L1342.15 292.789C1336.08 302.84 1327.29 310.902 1315.77 316.974C1304.25 322.838 1290.85 325.769 1275.57 325.769ZM1275.57 181.598C1269.7 181.598 1264.26 182.645 1259.23 184.739C1254.42 186.833 1250.23 189.765 1246.67 193.534C1243.32 197.303 1240.7 201.805 1238.82 207.04C1236.93 212.275 1235.99 218.034 1235.99 224.316V226.514H1312V223.373C1312 210.809 1308.75 200.758 1302.26 193.22C1295.77 185.472 1286.87 181.598 1275.57 181.598ZM1363.51 322L1420.99 239.392L1365.08 158.669H1404.66L1441.41 215.521H1442.35L1480.04 158.669H1516.48L1460.57 239.078L1517.42 322H1477.84L1440.15 262.636H1439.21L1399.95 322H1363.51ZM1593.52 322C1581.58 322 1572.58 318.964 1566.5 312.891C1560.43 306.609 1557.39 297.814 1557.39 286.507V186.624H1531.95V158.669H1545.77C1551.43 158.669 1555.3 157.413 1557.39 154.9C1559.7 152.387 1560.85 148.304 1560.85 142.65V114.067H1591.63V158.669H1625.87V186.624H1591.63V294.045H1623.35V322H1593.52Z" fill="#1a1a1a" />
    <path d="M1782.68 322C1773.67 322 1766.76 319.487 1761.95 314.462C1757.13 309.227 1754.2 302.631 1753.15 294.674H1751.58C1748.44 304.934 1742.68 312.682 1734.3 317.917C1725.93 323.152 1715.77 325.769 1703.84 325.769C1686.88 325.769 1673.79 321.372 1664.57 312.577C1655.57 303.782 1651.07 291.951 1651.07 277.084C1651.07 260.751 1656.93 248.501 1668.66 240.335C1680.59 232.168 1697.97 228.085 1720.8 228.085H1750.32V214.265C1750.32 204.213 1747.6 196.466 1742.16 191.021C1736.71 185.577 1728.23 182.855 1716.72 182.855C1707.08 182.855 1699.23 184.949 1693.16 189.137C1687.09 193.325 1681.96 198.664 1677.77 205.156L1657.35 186.624C1662.8 177.41 1670.44 169.872 1680.28 164.009C1690.12 157.936 1703 154.9 1718.91 154.9C1740.06 154.9 1756.29 159.821 1767.6 169.663C1778.91 179.504 1784.56 193.639 1784.56 212.066V294.045H1801.84V322H1782.68ZM1713.57 299.699C1724.25 299.699 1733.05 297.396 1739.96 292.789C1746.87 287.973 1750.32 281.586 1750.32 273.629V250.072H1721.43C1697.76 250.072 1685.93 257.401 1685.93 272.058V277.712C1685.93 285.041 1688.34 290.59 1693.16 294.359C1698.18 297.919 1704.99 299.699 1713.57 299.699Z" fill="#1a1a1a" />
    <path d="M2046.88 226.514H1947.63V322H1912.13V102.76H1947.63V195.105H2046.88V102.76H2082.37V322H2046.88V226.514ZM2197.92 325.769C2186.19 325.769 2175.72 323.78 2166.51 319.801C2157.3 315.823 2149.44 310.169 2142.95 302.84C2136.46 295.302 2131.44 286.298 2127.88 275.828C2124.53 265.148 2122.85 253.317 2122.85 240.335C2122.85 227.352 2124.53 215.626 2127.88 205.156C2131.44 194.476 2136.46 185.472 2142.95 178.143C2149.44 170.605 2157.3 164.847 2166.51 160.868C2175.72 156.889 2186.19 154.9 2197.92 154.9C2209.86 154.9 2220.33 156.994 2229.33 161.182C2238.54 165.37 2246.19 171.233 2252.26 178.772C2258.33 186.1 2262.83 194.686 2265.76 204.528C2268.91 214.369 2270.48 224.944 2270.48 236.251V249.129H2158.34V254.469C2158.34 267.033 2162.01 277.398 2169.34 285.565C2176.88 293.522 2187.55 297.5 2201.37 297.5C2211.43 297.5 2219.91 295.302 2226.82 290.904C2233.73 286.507 2239.59 280.539 2244.41 273.001L2264.51 292.789C2258.44 302.84 2249.64 310.902 2238.12 316.974C2226.61 322.838 2213.21 325.769 2197.92 325.769ZM2197.92 181.598C2192.06 181.598 2186.61 182.645 2181.59 184.739C2176.77 186.833 2172.58 189.765 2169.02 193.534C2165.67 197.303 2163.06 201.805 2161.17 207.04C2159.29 212.275 2158.34 218.034 2158.34 224.316V226.514H2234.36V223.373C2234.36 210.809 2231.11 200.758 2224.62 193.22C2218.13 185.472 2209.23 181.598 2197.92 181.598ZM2428.05 322C2419.04 322 2412.13 319.487 2407.32 314.462C2402.5 309.227 2399.57 302.631 2398.52 294.674H2396.95C2393.81 304.934 2388.05 312.682 2379.68 317.917C2371.3 323.152 2361.15 325.769 2349.21 325.769C2332.25 325.769 2319.16 321.372 2309.95 312.577C2300.94 303.782 2296.44 291.951 2296.44 277.084C2296.44 260.751 2302.3 248.501 2314.03 240.335C2325.97 232.168 2343.35 228.085 2366.17 228.085H2395.7V214.265C2395.7 204.213 2392.97 196.466 2387.53 191.021C2382.08 185.577 2373.6 182.855 2362.09 182.855C2352.46 182.855 2344.6 184.949 2338.53 189.137C2332.46 193.325 2327.33 198.664 2323.14 205.156L2302.72 186.624C2308.17 177.41 2315.81 169.872 2325.65 164.009C2335.49 157.936 2348.37 154.9 2364.29 154.9C2385.44 154.9 2401.66 159.821 2412.97 169.663C2424.28 179.504 2429.93 193.639 2429.93 212.066V294.045H2447.21V322H2428.05ZM2358.95 299.699C2369.63 299.699 2378.42 297.396 2385.33 292.789C2392.24 287.973 2395.7 281.586 2395.7 273.629V250.072H2366.8C2343.14 250.072 2331.31 257.401 2331.31 272.058V277.712C2331.31 285.041 2333.71 290.59 2338.53 294.359C2343.56 297.919 2350.36 299.699 2358.95 299.699ZM2515.63 322C2503.9 322 2495.11 319.068 2489.24 313.205C2483.59 307.133 2480.76 298.757 2480.76 288.077V89.5679H2515V294.045H2537.61V322H2515.63ZM2614.03 322C2602.09 322 2593.09 318.964 2587.01 312.891C2580.94 306.609 2577.9 297.814 2577.9 286.507V186.624H2552.46V158.669H2566.28C2571.94 158.669 2575.81 157.413 2577.9 154.9C2580.21 152.387 2581.36 148.304 2581.36 142.65V114.067H2612.14V158.669H2646.38V186.624H2612.14V294.045H2643.86V322H2614.03ZM2683.51 89.5679H2717.75V185.682H2719.32C2722.88 176.887 2728.22 169.558 2735.34 163.695C2742.67 157.832 2752.62 154.9 2765.18 154.9C2781.93 154.9 2794.91 160.449 2804.13 171.547C2813.55 182.436 2818.26 198.036 2818.26 218.348V322H2784.03V222.431C2784.03 197.094 2773.77 184.425 2753.24 184.425C2748.85 184.425 2744.45 185.053 2740.05 186.31C2735.86 187.357 2732.09 189.032 2728.74 191.335C2725.39 193.639 2722.67 196.57 2720.58 200.13C2718.69 203.69 2717.75 207.773 2717.75 212.38V322H2683.51V89.5679Z" fill="#00878A" />
  </svg>
);

const ContextaIcon = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 370 410" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M184.693 281.275C199.425 281.275 211.367 293.218 211.367 307.949L211.368 383.291C211.368 398.022 199.425 409.965 184.693 409.965C169.961 409.965 158.019 398.022 158.019 383.29L158.018 307.949C158.019 293.218 169.962 281.275 184.693 281.275ZM184.692 0C198.898 0.000161361 210.414 11.5161 210.414 25.7217V153.729C210.414 178.914 223.85 202.187 245.662 214.78L356.519 278.784C368.822 285.887 373.037 301.617 365.934 313.92C358.832 326.223 343.1 330.438 330.798 323.335L219.939 259.33C198.128 246.737 171.254 246.738 149.442 259.331L38.5868 323.334C26.2842 330.437 10.553 326.222 3.4501 313.919C-3.65243 301.616 0.562839 285.886 12.8651 278.783L123.723 214.779C145.534 202.186 158.971 178.913 158.971 153.728V25.7217C158.971 11.516 170.487 0 184.692 0ZM6.99404 106.592C14.3599 93.834 30.6735 89.4627 43.4315 96.8281L108.68 134.499C121.437 141.865 125.808 158.179 118.442 170.937C111.076 183.694 94.7628 188.065 82.0048 180.699L16.7577 143.029C3.99978 135.663 -0.37171 119.35 6.99404 106.592ZM325.785 96.8271C338.543 89.4618 354.857 93.8331 362.223 106.591C369.588 119.349 365.217 135.662 352.459 143.028L287.212 180.699C274.454 188.065 258.14 183.693 250.774 170.936C243.409 158.177 247.78 141.864 260.538 134.498L325.785 96.8271Z" fill="currentColor" />
  </svg>
);

// ─────────────────────────────────────────────────────────────────────────────
// COSMETIC ONLY. This is the static chart the assistant sits inside -- it exists
// so a visiting doctor sees where the widget lives in their workflow. It is NOT
// what the bot reads. The bot's source of truth is doctor_data.py on the backend
// (generated from the markdown). If these ever disagree, only the chart is stale;
// the answers stay correct.
// ─────────────────────────────────────────────────────────────────────────────
const PATIENTS = [
  {
    id: 'vr',
    name: 'Venkata Ramana',
    age: 58, sex: 'M', dob: '14-Mar-1968',
    condition: 'Hypertension',
    allergies: 'None reported',
    nextVisit: '15-Aug-2026',
    lastSeen: '10-Feb-2026',
    vitals: [
      { label: 'BP', value: '130/84', unit: 'mmHg' },
      { label: 'Weight', value: '82', unit: 'kg' },
      { label: 'BMI', value: '29.1', unit: '' },
      { label: 'Creatinine', value: '1.0', unit: 'mg/dL' },
    ],
    meds: ['Tab Amlodipine 10mg OD', 'Tab Atorvastatin 10mg OD (night)'],
    visits: [
      { date: '10-Feb-2026', note: 'BP well controlled, continue current regimen' },
      { date: '20-Aug-2025', note: 'BP still mildly elevated, dose increased' },
      { date: '15-Feb-2025', note: 'BP improving, continue same regimen' },
      { date: '12-Aug-2024', note: 'Newly diagnosed hypertension; lifestyle advice given' },
    ],
  },
  {
    id: 'ld',
    name: 'Lakshmi Devi',
    age: 52, sex: 'F', dob: '22-Jul-1974',
    condition: 'Type 2 Diabetes Mellitus',
    allergies: 'Penicillin — rash',
    nextVisit: '20-Sep-2026',
    lastSeen: '12-Mar-2026',
    vitals: [
      { label: 'HbA1c', value: '6.8', unit: '%' },
      { label: 'Weight', value: '68', unit: 'kg' },
      { label: 'BMI', value: '28.3', unit: '' },
      { label: 'BP', value: '122/78', unit: 'mmHg' },
    ],
    meds: ['Tab Metformin 500mg BD', 'Tab Glimepiride 1mg OD'],
    visits: [
      { date: '12-Mar-2026', note: 'Good glycemic control achieved' },
      { date: '25-Sep-2025', note: 'Improving steadily, continue' },
      { date: '18-Mar-2025', note: 'Sugar still above target, added second agent' },
      { date: '05-Sep-2024', note: 'Newly diagnosed Type 2 DM; dietary counseling given' },
    ],
  },
  {
    id: 'gp',
    name: 'Ganesan Pillai',
    age: 64, sex: 'M', dob: '05-Nov-1961',
    condition: 'Chronic Kidney Disease (Stage 3)',
    allergies: 'None reported',
    nextVisit: '05-Aug-2026',
    lastSeen: '28-Jan-2026',
    vitals: [
      { label: 'Creatinine', value: '1.9', unit: 'mg/dL' },
      { label: 'eGFR', value: '41', unit: 'mL/min' },
      { label: 'Hb', value: '11.1', unit: 'g/dL' },
      { label: 'BP', value: '132/84', unit: 'mmHg' },
    ],
    meds: ['Tab Telmisartan 80mg OD', 'Tab Sodium Bicarbonate 500mg BD', 'Tab Ferrous Ascorbate + Folic Acid OD'],
    visits: [
      { date: '28-Jan-2026', note: 'Creatinine stable, anemia improving, continue management' },
      { date: '15-Jul-2025', note: 'Creatinine trending up slowly, mild anemia noted, iron started' },
      { date: '05-Jan-2025', note: 'Stable, continue monitoring' },
      { date: '20-Jul-2024', note: 'CKD Stage 3 secondary to hypertension; nephrology referral' },
    ],
  },
];

const SUGGESTIONS = [
  "How has Venkata Ramana's weight changed over his last few visits?",
  'How is the serum creatinine changing for Ganesan Pillai?',
  "Summarize Lakshmi Devi's diabetes control over the past year",
  "How's my next week looking?",
  'How many surgeries did I perform last month?',
  'Which upcoming patients still need pre-op clearance?',
];

// ─── Markdown rendering ──────────────────────────────────────────────────────
// The model is constrained to bold + tables + plain lines, so a small purpose-
// built renderer beats pulling in a markdown dependency for three constructs.

const renderInline = (text) =>
  text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') ? (
      <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>
    ) : (
      <React.Fragment key={i}>{part}</React.Fragment>
    )
  );

const firstNumber = (cell) => {
  const m = String(cell).match(/-?\d+(?:\.\d+)?/);
  return m ? parseFloat(m[0]) : null;
};

// A cell counts as a measurement only if the WHOLE cell is a number, optionally
// followed by a short unit -- "85 kg", "30.1", "7200/uL", "130/84" (charts as
// systolic). Testing "does this cell contain a number" instead is wrong and not
// subtle: "12-Aug-2024" yields 12, so every trend table renders a second
// sparkline of day-of-month noise beside the real one, and "Jan 2026" yields a
// flat line of years.
const MEASUREMENT = /^-?\d+(?:\.\d+)?(?:\s*[a-zA-Z%/µ][\w%/.²³-]{0,9})?$/;

// A trend needs at least 3 points; two values are a pair, not a direction.
const numericSeries = (rows, col) => {
  const cells = rows.map((r) => String(r[col] ?? '').trim());
  if (cells.length < 3 || !cells.every((c) => MEASUREMENT.test(c))) return null;
  return cells.map(firstNumber);
};

const Sparkline = ({ values }) => {
  const w = 88, h = 22, pad = 2;
  const min = Math.min(...values), max = Math.max(...values);
  const span = max - min || 1;
  const pts = values.map((v, i) => {
    const x = pad + (i * (w - pad * 2)) / (values.length - 1);
    const y = h - pad - ((v - min) / span) * (h - pad * 2);
    return [x, y];
  });
  const rising = values[values.length - 1] >= values[0];
  const stroke = rising ? '#0d9488' : '#e11d48';
  return (
    <svg width={w} height={h} className="overflow-visible flex-shrink-0">
      <polyline
        points={pts.map((p) => p.join(',')).join(' ')}
        fill="none" stroke={stroke} strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round"
      />
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r="2.5" fill={stroke} />
    </svg>
  );
};

const MarkdownTable = ({ headers, rows }) => {
  const trends = headers
    .map((h, i) => ({ label: h, values: numericSeries(rows, i) }))
    .filter((t) => t.values);

  return (
    <div className="my-2.5">
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-[12.5px] border-collapse">
          <thead>
            <tr className="bg-slate-50/80">
              {headers.map((h, i) => (
                <th key={i} className="text-left font-semibold text-slate-500 uppercase tracking-wide text-[10px] px-3 py-2 border-b border-slate-200 whitespace-nowrap">
                  {renderInline(h)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, ri) => (
              <tr key={ri} className="border-b border-slate-100 last:border-0 hover:bg-teal-50/30 transition-colors">
                {r.map((c, ci) => (
                  <td key={ci} className={`px-3 py-1.5 text-slate-700 whitespace-nowrap ${ci === 0 ? 'font-medium text-slate-800' : ''}`}>
                    {renderInline(c)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {trends.length > 0 && (
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2 px-1">
          {trends.map((t, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">{t.label}</span>
              <Sparkline values={t.values} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const splitRow = (line) =>
  line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());

const isDivider = (line) => /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(line) && line.includes('-');

const Markdown = ({ text }) => {
  const lines = (text || '').split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // A table is a header row, a divider, then body rows.
    if (line.trim().startsWith('|') && isDivider(lines[i + 1] || '')) {
      const headers = splitRow(line);
      const rows = [];
      i += 2;
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        rows.push(splitRow(lines[i]));
        i += 1;
      }
      blocks.push(<MarkdownTable key={blocks.length} headers={headers} rows={rows} />);
      continue;
    }

    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ''));
        i += 1;
      }
      blocks.push(
        <ul key={blocks.length} className="my-1.5 space-y-1">
          {items.map((it, k) => (
            <li key={k} className="flex items-start gap-2 text-[13px] text-slate-700">
              <span className="mt-[7px] w-1 h-1 rounded-full bg-teal-400 flex-shrink-0" />
              <span>{renderInline(it)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    if (line.trim()) {
      blocks.push(
        <p key={blocks.length} className="text-[13px] leading-relaxed text-slate-700 my-1">
          {renderInline(line)}
        </p>
      );
    }
    i += 1;
  }

  return <div>{blocks}</div>;
};

// ─── EMR chart (static backdrop) ─────────────────────────────────────────────

const VitalCard = ({ label, value, unit }) => (
  <div className="bg-white rounded-xl border border-slate-200/80 px-3.5 py-2.5 shadow-sm">
    <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">{label}</p>
    <p className="text-slate-800 font-bold text-lg leading-tight mt-0.5">
      {value}
      {unit && <span className="text-[11px] font-medium text-slate-400 ml-1">{unit}</span>}
    </p>
  </div>
);

const PatientChart = ({ patient }) => (
  <div className="bg-white/90 backdrop-blur-sm border border-white/80 rounded-2xl shadow-lg shadow-slate-200/40 p-5 sm:p-6">
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
      <div className="min-w-0">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-800 truncate">{patient.name}</h1>
        <p className="text-xs text-slate-400 mt-1">
          {patient.age}{patient.sex} · DOB {patient.dob} · Last seen {patient.lastSeen}
        </p>
      </div>
      <span className="px-2.5 py-1 rounded-lg bg-teal-50 border border-teal-200 text-teal-700 text-[11px] font-bold uppercase tracking-wider whitespace-nowrap flex-shrink-0">
        {patient.condition}
      </span>
    </div>

    {/* These breakpoints track the PANE, not the viewport. Below lg the records
        pane is full width, so it widens with the screen; from lg up the split
        gives it only ~42%, which is narrower than the tablet pane -- hence the
        step back down at lg. Without it, 4 vitals get ~95px each and the
        creatinine card clips its own value. */}
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-2 2xl:grid-cols-4 gap-2.5 mt-4">
      {patient.vitals.map((v) => <VitalCard key={v.label} {...v} />)}
    </div>

    <div className="grid md:grid-cols-2 lg:grid-cols-1 gap-5 mt-5">
      <div>
        <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 mb-2">Current medication</p>
        <ul className="space-y-1.5">
          {patient.meds.map((m) => (
            <li key={m} className="text-[13px] text-slate-700 bg-emerald-50/60 border border-emerald-100 rounded-lg px-3 py-1.5">{m}</li>
          ))}
        </ul>
        <div className="mt-3.5 flex flex-wrap gap-x-5 gap-y-1.5 text-[12px]">
          <span className="text-slate-400">Allergies <span className={`font-semibold ml-1 ${patient.allergies === 'None reported' ? 'text-slate-600' : 'text-rose-600'}`}>{patient.allergies}</span></span>
          <span className="text-slate-400">Next visit <span className="font-semibold text-slate-600 ml-1">{patient.nextVisit}</span></span>
        </div>
      </div>

      <div>
        <p className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 mb-2">Visit history · {patient.visits.length} visits</p>
        <ul className="space-y-1.5">
          {patient.visits.map((v) => (
            <li key={v.date} className="flex items-start gap-2.5">
              <span className="text-[11px] font-semibold text-slate-400 tabular-nums whitespace-nowrap mt-px w-[76px] flex-shrink-0">{v.date}</span>
              <span className="text-[12.5px] text-slate-600 leading-snug">{v.note}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  </div>
);

// ─── Assistant panel (persistent split-screen column) ───────────────────────

const AssistantPanel = ({ doctor, className = '' }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Warm the prompt cache while the doctor is still reading the chart, so the
  // first question reads a hot cache instead of paying the cold write.
  useEffect(() => {
    fetch(`${API_URL}/api/doctor/warm`, { method: 'POST' }).catch(() => {});
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const ask = async (question) => {
    const q = (question ?? input).trim();
    if (!q || loading) return;

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: 'user', content: q }]);
    setInput('');
    setError('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/doctor/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, history }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setMessages((m) => [...m, { role: 'bot', content: data.answer, usage: data.usage }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Voice input -- same flow as the WhatsApp ChatBot: record -> /api/transcribe
  // -> ask the transcribed question. Whisper auto-detects the language; the
  // doctor bot only needs the text, and the audio goes through the backend so
  // the Groq key never reaches the browser.
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data);
      mediaRecorderRef.current.onstop = async () => {
        setIsTranscribing(true);
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const fd = new FormData();
        fd.append('file', blob, 'audio.webm');
        try {
          const res = await fetch(`${API_URL}/api/transcribe`, { method: 'POST', body: fd });
          if (!res.ok) throw new Error(`Transcription failed (${res.status})`);
          const data = await res.json();
          const text = (data.text || '').trim();
          if (text) ask(text);
          else setError("I couldn't catch that — please try again.");
        } catch {
          setError('Voice input failed — please type your question instead.');
        } finally {
          setIsTranscribing(false);
          stream.getTracks().forEach((t) => t.stop());
        }
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError('');
    } catch {
      setError('Please allow microphone access to use voice input.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const hasConversation = messages.length > 0 || loading || error;
  const busy = loading || isTranscribing;
  const placeholder = isRecording
    ? 'Listening…'
    : isTranscribing
    ? 'Transcribing…'
    : `Ask about your patients or schedule, ${doctor.split(' ')[1] || 'Doctor'}…`;

  return (
    <aside className={`${className} flex-col bg-white/55 backdrop-blur-sm min-h-0`}>
      {/* Panel header */}
      <div className="flex-shrink-0 flex items-center gap-2.5 px-4 py-3 border-b border-slate-200/70 bg-white/70">
        <span className="bg-gradient-to-br from-teal-500 to-teal-600 text-white p-1.5 rounded-lg shadow-sm flex-shrink-0">
          <ContextaIcon size={14} />
        </span>
        <span className="text-[13px] font-bold text-slate-700">Clinical Assistant</span>
        <span className="text-[10px] font-semibold text-teal-700 bg-teal-50 border border-teal-200 px-1.5 py-0.5 rounded uppercase tracking-wide">Beta</span>
        {hasConversation && (
          <button
            onClick={() => { setMessages([]); setError(''); }}
            className="ml-auto text-[11px] font-semibold text-slate-400 hover:text-slate-600 transition-colors"
          >
            Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 min-h-0">
        {!hasConversation && (
          <div>
            <p className="text-[12px] text-slate-400 mb-2.5">
              Ask about your patients or your schedule. Try one of these:
            </p>
            <div className="flex flex-col gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => ask(s)}
                  className="text-[12.5px] text-slate-600 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 hover:border-teal-200 border border-slate-200 rounded-lg px-3 py-2 transition-colors text-left"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) =>
          m.role === 'user' ? (
            <div key={i} className="flex justify-end mb-3">
              <p className="bg-gradient-to-r from-teal-600 to-teal-500 text-white text-[13px] font-medium px-3.5 py-2 rounded-2xl rounded-br-md max-w-[85%] shadow-sm shadow-teal-500/20">
                {m.content}
              </p>
            </div>
          ) : (
            <div key={i} className="mb-4 last:mb-1">
              <Markdown text={m.content} />
              {m.usage && (
                <p className="text-[10px] text-slate-300 mt-1.5 tabular-nums">
                  {m.usage.cache_read > 0
                    ? `${m.usage.cache_read.toLocaleString()} tokens read from cache`
                    : 'cache cold — first request'}
                  {' · '}{m.usage.output} out
                </p>
              )}
            </div>
          )
        )}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 py-1.5">
            <span className="flex gap-1">
              <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce" />
            </span>
            <span className="text-[12px]">Checking the record…</span>
          </div>
        )}

        {error && (
          <p className="text-[12.5px] text-rose-600 bg-rose-50 border border-rose-200 rounded-xl px-3 py-2 mt-1">
            {error}
          </p>
        )}
      </div>

      {/* Composer */}
      <div className="flex-shrink-0 flex items-center gap-2 p-3 border-t border-slate-200/70 bg-white/80">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isTranscribing || loading}
          className={`flex-shrink-0 p-2.5 rounded-xl border transition-all active:scale-[0.97] disabled:opacity-40 ${
            isRecording
              ? 'bg-rose-50 border-rose-200 text-rose-600 animate-pulse'
              : 'bg-slate-50 border-slate-200 text-slate-500 hover:text-teal-700 hover:border-teal-200'
          }`}
          aria-label={isRecording ? 'Stop recording' : 'Record a question'}
        >
          {isRecording ? <Square size={16} fill="currentColor" /> : <Mic size={16} />}
        </button>
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') ask(); }}
          disabled={isRecording || isTranscribing}
          placeholder={placeholder}
          /* 16px on phones so iOS Safari doesn't zoom the page on focus. */
          className="flex-1 min-w-0 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-[16px] sm:text-[13px] text-slate-700 outline-none placeholder:text-slate-400 focus:border-teal-400 focus:ring-2 focus:ring-teal-500/10 focus:bg-white transition-all disabled:opacity-60"
        />
        <button
          onClick={() => ask()}
          disabled={!input.trim() || busy}
          className="bg-gradient-to-r from-teal-600 to-teal-500 disabled:from-slate-200 disabled:to-slate-300 disabled:shadow-none text-white p-2.5 rounded-xl shadow-md shadow-teal-500/20 hover:from-teal-700 hover:to-teal-600 transition-all active:scale-[0.97] flex-shrink-0"
          aria-label="Ask"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </button>
      </div>
    </aside>
  );
};

// ─── Page ────────────────────────────────────────────────────────────────────

export default function DoctorBotApp() {
  const [activeId, setActiveId] = useState(PATIENTS[0].id);
  const [doctor, setDoctor] = useState('Dr. Suresh Kumar Nair');
  // Phone/tablet show one pane at a time; from lg up both are on screen.
  const [mobileView, setMobileView] = useState('records'); // 'records' | 'assistant'
  const patient = PATIENTS.find((p) => p.id === activeId);

  useEffect(() => {
    fetch(`${API_URL}/api/doctor/context`)
      .then((r) => r.json())
      .then((d) => d.doctor && setDoctor(d.doctor))
      .catch(() => {});
  }, []);

  return (
    // 100dvh, not 100vh: on mobile browsers 100vh includes the address bar, so
    // the composer would sit below the fold.
    <div className="h-[100dvh] flex flex-col overflow-hidden bg-gradient-to-br from-slate-50 via-gray-50 to-teal-50/30">
      {/* Back to Home bar -- same control as the ChatBot page. */}
      <div className="h-[44px] flex-shrink-0 bg-white border-b border-slate-200/70 flex items-center px-4 z-20">
        <a
          href="/"
          className="flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-teal-700 transition-colors no-underline"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Home
        </a>
      </div>

      <header className="flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/70 z-20">
        <div className="px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <ContextaLogo />
            <span className="hidden sm:inline text-slate-200">|</span>
            <span className="hidden sm:inline text-[13px] font-semibold text-slate-500 whitespace-nowrap">Patient Records</span>
          </div>
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="text-right min-w-0">
              <p className="text-[13px] font-semibold text-slate-700 truncate">{doctor}</p>
              {/* Hidden on phones: it wraps to three lines and shoves the header around. */}
              <p className="hidden sm:block text-[10.5px] text-slate-400 -mt-0.5 whitespace-nowrap">Joint Replacement &amp; Sports Injury</p>
            </div>
            <span className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 text-white text-[11px] font-bold flex items-center justify-center flex-shrink-0 shadow-sm">
              SK
            </span>
          </div>
        </div>

        {/* Records / Assistant switch -- phone & tablet only. From lg up the
            split shows both panes at once, so this is hidden. */}
        <div className="lg:hidden flex gap-1 px-4 pb-2">
          {[['records', 'Records'], ['assistant', 'Assistant']].map(([id, label]) => (
            <button
              key={id}
              onClick={() => setMobileView(id)}
              className={`flex-1 py-1.5 rounded-lg text-[12.5px] font-semibold transition-colors ${
                mobileView === id
                  ? 'bg-teal-50 text-teal-700 border border-teal-200'
                  : 'text-slate-500 border border-transparent hover:bg-slate-50'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Assistant column -- on the left: it's the thing the doctor drives, and
            the chart is the reference they glance at. */}
        <AssistantPanel
          doctor={doctor}
          className={`${mobileView === 'assistant' ? 'flex' : 'hidden'} lg:flex w-full lg:w-[58%] lg:border-r border-slate-200/70`}
        />

        {/* Records column */}
        <section className={`${mobileView === 'records' ? 'flex' : 'hidden'} lg:flex flex-col w-full lg:w-[42%] overflow-y-auto`}>
          <div className="w-full max-w-3xl mx-auto px-4 sm:px-6 py-5">
            <div className="flex gap-1.5 mb-4 overflow-x-auto">
              {PATIENTS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setActiveId(p.id)}
                  className={`px-3.5 py-2 rounded-xl text-[13px] font-semibold whitespace-nowrap transition-all ${
                    p.id === activeId
                      ? 'bg-white text-teal-700 shadow-sm border border-teal-200'
                      : 'text-slate-500 hover:text-slate-700 hover:bg-white/60 border border-transparent'
                  }`}
                >
                  {p.name}
                </button>
              ))}
            </div>

            <PatientChart patient={patient} />
          </div>
        </section>
      </div>
    </div>
  );
}
