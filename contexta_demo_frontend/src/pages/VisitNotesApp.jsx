import React, { useState, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || '';

// Section order mirrors ortho templates_6699.md exactly:
//   Chief Complaint -> Diagnosis (ICD-10) -> History & Complaints ->
//   Examination & Findings -> Impression/Diagnosis -> Management Plan ->
//   Prescriptions -> Lab Orders -> Imaging Orders -> Follow-up Plan
// `complaints` / `advice` / `plan` only exist for the older non-ortho templates
// (Diabetes / Asthma / Pediatrics); they render empty for ortho and are hidden.
const systemAttributeHeaders = {
  chief_complaint: 'Chief Complaint',
  diagnosis: 'Diagnosis (ICD-10)',
  history_complaints: 'History & Complaints',
  examination_findings: 'Examination & Findings',
  impression: 'Impression / Diagnosis',
  management_plan: 'Management Plan',
  complaints: 'Complaints',
  advice: 'Advice',
  prescription: 'Prescription (Rx)',
  lab_orders: 'Lab Orders',
  imaging_orders: 'Imaging Orders',
  plan: 'Plan',
  follow_up_plan: 'Follow-up Plan'
};

const sectionThemes = {
  diagnosis: { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200', highlight: 'border-l-teal-500', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' },
  chief_complaint: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', highlight: 'border-l-rose-500', icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  history_complaints: { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200', highlight: 'border-l-pink-500', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  examination_findings: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', highlight: 'border-l-purple-500', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  impression: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', highlight: 'border-l-indigo-500', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  management_plan: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', highlight: 'border-l-amber-500', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
  complaints: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', highlight: 'border-l-rose-500', icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  advice: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', highlight: 'border-l-amber-500', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
  prescription: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', highlight: 'border-l-emerald-500', icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
  lab_orders: { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200', highlight: 'border-l-cyan-500', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  imaging_orders: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200', highlight: 'border-l-orange-500', icon: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9zM15 13a3 3 0 11-6 0 3 3 0 016 0z' },
  plan: { bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200', highlight: 'border-l-sky-500', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
  follow_up_plan: { bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200', highlight: 'border-l-violet-500', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' }
};

// Contexta Health SVG Logo (extracted from contextaemr.com)
const ContextaLogo = ({ className = '' }) => (
  <svg height="22" viewBox="0 0 2842 410" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M184.693 281.275C199.425 281.275 211.367 293.218 211.367 307.949L211.368 383.291C211.368 398.022 199.425 409.965 184.693 409.965C169.961 409.965 158.019 398.022 158.019 383.29L158.018 307.949C158.019 293.218 169.962 281.275 184.693 281.275ZM184.692 0C198.898 0.000161361 210.414 11.5161 210.414 25.7217V153.729C210.414 178.914 223.85 202.187 245.662 214.78L356.519 278.784C368.822 285.887 373.037 301.617 365.934 313.92C358.832 326.223 343.1 330.438 330.798 323.335L219.939 259.33C198.128 246.737 171.254 246.738 149.442 259.331L38.5868 323.334C26.2842 330.437 10.553 326.222 3.4501 313.919C-3.65243 301.616 0.562839 285.886 12.8651 278.783L123.723 214.779C145.534 202.186 158.971 178.913 158.971 153.728V25.7217C158.971 11.516 170.487 0 184.692 0ZM6.99404 106.592C14.3599 93.834 30.6735 89.4627 43.4315 96.8281L108.68 134.499C121.437 141.865 125.808 158.179 118.442 170.937C111.076 183.694 94.7628 188.065 82.0048 180.699L16.7577 143.029C3.99978 135.663 -0.37171 119.35 6.99404 106.592ZM325.785 96.8271C338.543 89.4618 354.857 93.8331 362.223 106.591C369.588 119.349 365.217 135.662 352.459 143.028L287.212 180.699C274.454 188.065 258.14 183.693 250.774 170.936C243.409 158.177 247.78 141.864 260.538 134.498L325.785 96.8271Z" fill="#00878A"></path>
    <path d="M624.238 325.769C595.55 325.769 573.04 316.137 556.707 296.872C540.374 277.398 532.207 249.234 532.207 212.38C532.207 193.953 534.301 177.725 538.489 163.695C542.677 149.665 548.749 137.834 556.707 128.202C564.664 118.57 574.296 111.345 585.604 106.529C597.12 101.504 609.998 98.9908 624.238 98.9908C643.293 98.9908 659.207 103.179 671.98 111.555C684.963 119.931 695.119 132.285 702.448 148.618L672.609 164.951C668.839 154.481 662.976 146.21 655.019 140.138C647.271 133.856 637.011 130.715 624.238 130.715C607.276 130.715 593.98 136.473 584.347 147.99C574.715 159.507 569.899 175.421 569.899 195.733V229.027C569.899 249.339 574.715 265.253 584.347 276.77C593.98 288.287 607.276 294.045 624.238 294.045C637.43 294.045 648.109 290.695 656.276 283.994C664.651 277.084 670.829 268.289 674.807 257.61L703.39 274.885C696.061 290.8 685.801 303.259 672.609 312.263C659.416 321.267 643.293 325.769 624.238 325.769ZM802.579 325.769C791.271 325.769 780.906 323.78 771.483 319.801C762.27 315.823 754.417 310.169 747.926 302.84C741.434 295.302 736.409 286.298 732.849 275.828C729.289 265.148 727.509 253.317 727.509 240.335C727.509 227.352 729.289 215.626 732.849 205.156C736.409 194.476 741.434 185.472 747.926 178.143C754.417 170.605 762.27 164.847 771.483 160.868C780.906 156.889 791.271 154.9 802.579 154.9C813.886 154.9 824.147 156.889 833.36 160.868C842.783 164.847 850.74 170.605 857.232 178.143C863.723 185.472 868.749 194.476 872.308 205.156C875.868 215.626 877.648 227.352 877.648 240.335C877.648 253.317 875.868 265.148 872.308 275.828C868.749 286.298 863.723 295.302 857.232 302.84C850.74 310.169 842.783 315.823 833.36 319.801C824.147 323.78 813.886 325.769 802.579 325.769ZM802.579 297.5C814.305 297.5 823.728 293.941 830.847 286.821C837.967 279.492 841.527 268.603 841.527 254.155V226.514C841.527 212.066 837.967 201.282 830.847 194.162C823.728 186.833 814.305 183.169 802.579 183.169C790.852 183.169 781.429 186.833 774.31 194.162C767.19 201.282 763.631 212.066 763.631 226.514V254.155C763.631 268.603 767.19 279.492 774.31 286.821C781.429 293.941 790.852 297.5 802.579 297.5ZM915.796 322V158.669H950.033V185.682H951.603C955.163 176.887 960.503 169.558 967.622 163.695C974.951 157.832 984.898 154.9 997.461 154.9C1014.21 154.9 1027.2 160.449 1036.41 171.547C1045.83 182.436 1050.54 198.036 1050.54 218.348V322H1016.31V222.745C1016.31 197.199 1006.05 184.425 985.526 184.425C981.128 184.425 976.731 185.053 972.334 186.31C968.146 187.357 964.377 189.032 961.026 191.335C957.676 193.639 954.954 196.57 952.86 200.13C950.975 203.69 950.033 207.878 950.033 212.694V322H915.796ZM1143.23 322C1131.29 322 1122.29 318.964 1116.21 312.891C1110.14 306.609 1107.11 297.814 1107.11 286.507V186.624H1081.66V158.669H1095.48C1101.14 158.669 1105.01 157.413 1107.11 154.9C1109.41 152.387 1110.56 148.304 1110.56 142.65V114.067H1141.34V158.669H1175.58V186.624H1141.34V294.045H1173.07V322H1143.23ZM1275.57 325.769C1263.84 325.769 1253.37 323.78 1244.16 319.801C1234.94 315.823 1227.09 310.169 1220.6 302.84C1214.11 295.302 1209.08 286.298 1205.52 275.828C1202.17 265.148 1200.5 253.317 1200.5 240.335C1200.5 227.352 1202.17 215.626 1205.52 205.156C1209.08 194.476 1214.11 185.472 1220.6 178.143C1227.09 170.605 1234.94 164.847 1244.16 160.868C1253.37 156.889 1263.84 154.9 1275.57 154.9C1287.5 154.9 1297.97 156.994 1306.98 161.182C1316.19 165.37 1323.83 171.233 1329.9 178.772C1335.98 186.1 1340.48 194.686 1343.41 204.528C1346.55 214.369 1348.12 224.944 1348.12 236.251V249.129H1235.99V254.469C1235.99 267.033 1239.65 277.398 1246.98 285.565C1254.52 293.522 1265.2 297.5 1279.02 297.5C1289.07 297.5 1297.55 295.302 1304.46 290.904C1311.37 286.507 1317.24 280.539 1322.05 273.001L1342.15 292.789C1336.08 302.84 1327.29 310.902 1315.77 316.974C1304.25 322.838 1290.85 325.769 1275.57 325.769ZM1275.57 181.598C1269.7 181.598 1264.26 182.645 1259.23 184.739C1254.42 186.833 1250.23 189.765 1246.67 193.534C1243.32 197.303 1240.7 201.805 1238.82 207.04C1236.93 212.275 1235.99 218.034 1235.99 224.316V226.514H1312V223.373C1312 210.809 1308.75 200.758 1302.26 193.22C1295.77 185.472 1286.87 181.598 1275.57 181.598ZM1363.51 322L1420.99 239.392L1365.08 158.669H1404.66L1441.41 215.521H1442.35L1480.04 158.669H1516.48L1460.57 239.078L1517.42 322H1477.84L1440.15 262.636H1439.21L1399.95 322H1363.51ZM1593.52 322C1581.58 322 1572.58 318.964 1566.5 312.891C1560.43 306.609 1557.39 297.814 1557.39 286.507V186.624H1531.95V158.669H1545.77C1551.43 158.669 1555.3 157.413 1557.39 154.9C1559.7 152.387 1560.85 148.304 1560.85 142.65V114.067H1591.63V158.669H1625.87V186.624H1591.63V294.045H1623.35V322H1593.52Z" fill="#1a1a1a"></path>
    <path d="M1782.68 322C1773.67 322 1766.76 319.487 1761.95 314.462C1757.13 309.227 1754.2 302.631 1753.15 294.674H1751.58C1748.44 304.934 1742.68 312.682 1734.3 317.917C1725.93 323.152 1715.77 325.769 1703.84 325.769C1686.88 325.769 1673.79 321.372 1664.57 312.577C1655.57 303.782 1651.07 291.951 1651.07 277.084C1651.07 260.751 1656.93 248.501 1668.66 240.335C1680.59 232.168 1697.97 228.085 1720.8 228.085H1750.32V214.265C1750.32 204.213 1747.6 196.466 1742.16 191.021C1736.71 185.577 1728.23 182.855 1716.72 182.855C1707.08 182.855 1699.23 184.949 1693.16 189.137C1687.09 193.325 1681.96 198.664 1677.77 205.156L1657.35 186.624C1662.8 177.41 1670.44 169.872 1680.28 164.009C1690.12 157.936 1703 154.9 1718.91 154.9C1740.06 154.9 1756.29 159.821 1767.6 169.663C1778.91 179.504 1784.56 193.639 1784.56 212.066V294.045H1801.84V322H1782.68ZM1713.57 299.699C1724.25 299.699 1733.05 297.396 1739.96 292.789C1746.87 287.973 1750.32 281.586 1750.32 273.629V250.072H1721.43C1697.76 250.072 1685.93 257.401 1685.93 272.058V277.712C1685.93 285.041 1688.34 290.59 1693.16 294.359C1698.18 297.919 1704.99 299.699 1713.57 299.699Z" fill="#1a1a1a"></path>
    <path d="M2046.88 226.514H1947.63V322H1912.13V102.76H1947.63V195.105H2046.88V102.76H2082.37V322H2046.88V226.514ZM2197.92 325.769C2186.19 325.769 2175.72 323.78 2166.51 319.801C2157.3 315.823 2149.44 310.169 2142.95 302.84C2136.46 295.302 2131.44 286.298 2127.88 275.828C2124.53 265.148 2122.85 253.317 2122.85 240.335C2122.85 227.352 2124.53 215.626 2127.88 205.156C2131.44 194.476 2136.46 185.472 2142.95 178.143C2149.44 170.605 2157.3 164.847 2166.51 160.868C2175.72 156.889 2186.19 154.9 2197.92 154.9C2209.86 154.9 2220.33 156.994 2229.33 161.182C2238.54 165.37 2246.19 171.233 2252.26 178.772C2258.33 186.1 2262.83 194.686 2265.76 204.528C2268.91 214.369 2270.48 224.944 2270.48 236.251V249.129H2158.34V254.469C2158.34 267.033 2162.01 277.398 2169.34 285.565C2176.88 293.522 2187.55 297.5 2201.37 297.5C2211.43 297.5 2219.91 295.302 2226.82 290.904C2233.73 286.507 2239.59 280.539 2244.41 273.001L2264.51 292.789C2258.44 302.84 2249.64 310.902 2238.12 316.974C2226.61 322.838 2213.21 325.769 2197.92 325.769ZM2197.92 181.598C2192.06 181.598 2186.61 182.645 2181.59 184.739C2176.77 186.833 2172.58 189.765 2169.02 193.534C2165.67 197.303 2163.06 201.805 2161.17 207.04C2159.29 212.275 2158.34 218.034 2158.34 224.316V226.514H2234.36V223.373C2234.36 210.809 2231.11 200.758 2224.62 193.22C2218.13 185.472 2209.23 181.598 2197.92 181.598ZM2428.05 322C2419.04 322 2412.13 319.487 2407.32 314.462C2402.5 309.227 2399.57 302.631 2398.52 294.674H2396.95C2393.81 304.934 2388.05 312.682 2379.68 317.917C2371.3 323.152 2361.15 325.769 2349.21 325.769C2332.25 325.769 2319.16 321.372 2309.95 312.577C2300.94 303.782 2296.44 291.951 2296.44 277.084C2296.44 260.751 2302.3 248.501 2314.03 240.335C2325.97 232.168 2343.35 228.085 2366.17 228.085H2395.7V214.265C2395.7 204.213 2392.97 196.466 2387.53 191.021C2382.08 185.577 2373.6 182.855 2362.09 182.855C2352.46 182.855 2344.6 184.949 2338.53 189.137C2332.46 193.325 2327.33 198.664 2323.14 205.156L2302.72 186.624C2308.17 177.41 2315.81 169.872 2325.65 164.009C2335.49 157.936 2348.37 154.9 2364.29 154.9C2385.44 154.9 2401.66 159.821 2412.97 169.663C2424.28 179.504 2429.93 193.639 2429.93 212.066V294.045H2447.21V322H2428.05ZM2358.95 299.699C2369.63 299.699 2378.42 297.396 2385.33 292.789C2392.24 287.973 2395.7 281.586 2395.7 273.629V250.072H2366.8C2343.14 250.072 2331.31 257.401 2331.31 272.058V277.712C2331.31 285.041 2333.71 290.59 2338.53 294.359C2343.56 297.919 2350.36 299.699 2358.95 299.699ZM2515.63 322C2503.9 322 2495.11 319.068 2489.24 313.205C2483.59 307.133 2480.76 298.757 2480.76 288.077V89.5679H2515V294.045H2537.61V322H2515.63ZM2614.03 322C2602.09 322 2593.09 318.964 2587.01 312.891C2580.94 306.609 2577.9 297.814 2577.9 286.507V186.624H2552.46V158.669H2566.28C2571.94 158.669 2575.81 157.413 2577.9 154.9C2580.21 152.387 2581.36 148.304 2581.36 142.65V114.067H2612.14V158.669H2646.38V186.624H2612.14V294.045H2643.86V322H2614.03ZM2683.51 89.5679H2717.75V185.682H2719.32C2722.88 176.887 2728.22 169.558 2735.34 163.695C2742.67 157.832 2752.62 154.9 2765.18 154.9C2781.93 154.9 2794.91 160.449 2804.13 171.547C2813.55 182.436 2818.26 198.036 2818.26 218.348V322H2784.03V222.431C2784.03 197.094 2773.77 184.425 2753.24 184.425C2748.85 184.425 2744.45 185.053 2740.05 186.31C2735.86 187.357 2732.09 189.032 2728.74 191.335C2725.39 193.639 2722.67 196.57 2720.58 200.13C2718.69 203.69 2717.75 207.773 2717.75 212.38V322H2683.51V89.5679Z" fill="#00878A"></path>
  </svg>
);

const ContextaIcon = () => (
  <svg width="28" height="28" viewBox="0 0 370 410" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M184.693 281.275C199.425 281.275 211.367 293.218 211.367 307.949L211.368 383.291C211.368 398.022 199.425 409.965 184.693 409.965C169.961 409.965 158.019 398.022 158.019 383.29L158.018 307.949C158.019 293.218 169.962 281.275 184.693 281.275ZM184.692 0C198.898 0.000161361 210.414 11.5161 210.414 25.7217V153.729C210.414 178.914 223.85 202.187 245.662 214.78L356.519 278.784C368.822 285.887 373.037 301.617 365.934 313.92C358.832 326.223 343.1 330.438 330.798 323.335L219.939 259.33C198.128 246.737 171.254 246.738 149.442 259.331L38.5868 323.334C26.2842 330.437 10.553 326.222 3.4501 313.919C-3.65243 301.616 0.562839 285.886 12.8651 278.783L123.723 214.779C145.534 202.186 158.971 178.913 158.971 153.728V25.7217C158.971 11.516 170.487 0 184.692 0ZM6.99404 106.592C14.3599 93.834 30.6735 89.4627 43.4315 96.8281L108.68 134.499C121.437 141.865 125.808 158.179 118.442 170.937C111.076 183.694 94.7628 188.065 82.0048 180.699L16.7577 143.029C3.99978 135.663 -0.37171 119.35 6.99404 106.592ZM325.785 96.8271C338.543 89.4618 354.857 93.8331 362.223 106.591C369.588 119.349 365.217 135.662 352.459 143.028L287.212 180.699C274.454 188.065 258.14 183.693 250.774 170.936C243.409 158.177 247.78 141.864 260.538 134.498L325.785 96.8271Z" fill="#00878A" />
  </svg>
);

const TemplateLibrary = ({ onBack }) => {
  const specialties = [
    {
      name: "Orthopedics",
      diagnosis: "Total Knee Replacement (TKR)",
      rxGroups: [
        { name: "Standard", trigger: "standard, TKR prescription" },
        { name: "Plantar Fascia", trigger: "plantar fascia, plantar" },
        { name: "High Pain", trigger: "high pain, severe pain, pain score > 7" }
      ],
      fuGroups: ["Post-operative (Wound review, X-ray)", "Conservative (Review, MRI if no improvement)"]
    },
    {
      name: "Diabetology",
      diagnosis: "Type 2 Diabetes Mellitus (T2DM)",
      rxGroups: [
        { name: "Metformin based", trigger: "metformin, standard" },
        { name: "SGLT2 add-on", trigger: "SGLT2, empagliflozin, cardiac history" },
        { name: "Insulin initiation", trigger: "insulin, poorly controlled, HbA1c > 10" }
      ],
      fuGroups: ["Routine review (HbA1c at 3 months)", "Intensive monitoring (Sugar diary)"]
    },
    {
      name: "Pulmonology",
      diagnosis: "Bronchial Asthma",
      rxGroups: [
        { name: "Mild intermittent", trigger: "mild, intermittent" },
        { name: "Moderate persistent", trigger: "moderate, persistent, MMRC 2+" },
        { name: "Acute exacerbation", trigger: "acute, exacerbation, SpO2 < 92" }
      ],
      fuGroups: ["Stable asthma (Review with PFT)", "Post exacerbation (Review in 1 week, CXR)"]
    },
    {
      name: "Pediatrics",
      diagnosis: "Acute Respiratory Infection (ARI)",
      rxGroups: [
        { name: "Viral, no antibiotic", trigger: "viral, no antibiotic" },
        { name: "Bacterial, with antibiotic", trigger: "bacterial, antibiotic, throat congested" },
        { name: "With bronchospasm", trigger: "bronchospasm, wheeze, SpO2 < 95" }
      ],
      fuGroups: ["Routine review (Review in 3 days)", "Respiratory concern (Check SpO2 in 24-48 hrs)"]
    }
  ];

  return (
    <div className="w-full bg-white/90 backdrop-blur-sm p-6 md:p-8 shadow-lg shadow-slate-200/40 border border-white/80 rounded-2xl h-[calc(100vh-7.5rem)] overflow-y-auto">
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-100">
        <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
          <span className="bg-gradient-to-br from-teal-500 to-teal-600 text-white p-2.5 rounded-xl shadow-sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
          </span>
          Template Library
        </h2>
        <button onClick={onBack} className="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-sm font-semibold hover:bg-slate-200 transition-all flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          Back to Dictation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {specialties.map((spec, idx) => (
          <div key={idx} className="bg-slate-50 rounded-xl p-5 border border-slate-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] uppercase font-bold text-teal-700 tracking-widest bg-teal-50 border border-teal-200 px-2 py-0.5 rounded-md">{spec.name}</span>
            </div>
            <h3 className="text-lg font-bold text-slate-800 mb-4">{spec.diagnosis}</h3>
            
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Prescription Triggers (Rx)</h4>
              <div className="space-y-2">
                {spec.rxGroups.map((rx, rIdx) => (
                  <div key={rIdx} className="bg-white p-3 rounded-lg border border-slate-200 text-sm">
                    <span className="font-semibold text-slate-700">{rx.name}</span>
                    <p className="text-xs text-slate-500 mt-1">Say: <span className="text-emerald-600 font-medium">"{rx.trigger}"</span></p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Follow-up Plans</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-slate-600 bg-white p-3 rounded-lg border border-slate-200">
                {spec.fuGroups.map((fu, fIdx) => (
                  <li key={fIdx}>{fu}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Renders a template line whose "___" blank(s) become inline fields. The line
// always shows, whether or not the dictation supplied the value.
const SlotLine = ({ item, onChange }) => {
  const parts = (item.line || '').split('___');
  return (
    <div className="text-[14px] text-slate-700 leading-relaxed font-medium flex flex-wrap items-center">
      {parts.map((part, i) => (
        <React.Fragment key={i}>
          <span className="whitespace-pre-wrap">{part}</span>
          {i < parts.length - 1 && (
            <input
              type="text"
              value={item.value || ''}
              onChange={e => onChange(e.target.value)}
              placeholder="___"
              title={item.value ? 'Dictated value — click to edit' : 'Not dictated — click to fill in'}
              className={`mx-1 px-2 py-0.5 w-24 text-[13px] text-center rounded-md border outline-none transition-all focus:ring-2 focus:ring-teal-500/20 focus:border-teal-400 ${
                item.value
                  ? 'bg-teal-50 border-teal-200 text-teal-800 font-semibold'
                  : 'bg-amber-50/70 border-amber-200 border-dashed text-slate-600 placeholder:text-amber-400'
              }`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

const specialtyOptions = [
  { value: '', label: 'Select Specialty' },
  { value: 'orthopedics', label: 'Orthopedics' },
  { value: 'diabetology', label: 'Diabetology' },
  { value: 'pulmonology', label: 'Pulmonology' },
  { value: 'pediatrics', label: 'Pediatrics' },
];

export default function VisitNotesApp() {
  const [voiceNote, setVoiceNote] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });
  const [documentData, setDocumentData] = useState(null);
  const [editingItem, setEditingItem] = useState(null); 
  const [addingToSection, setAddingToSection] = useState(null); 
  const [addItemText, setAddItemText] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [metadata, setMetadata] = useState(() => ({
    visit_date: new Date().toLocaleDateString('en-CA'),
    doctor: 'Dr. Priya'
  }));

  // Ref for MediaRecorder (records mic audio → sends to Groq Whisper via backend)
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const showNotification = (message, type) => {
    setNotification({ show: true, message, type });
    setTimeout(() => setNotification({ show: false, message: '', type: '' }), 4000);
  };

  const handleMicClick = async () => {
    if (isListening) {
      // ── STOP recording ──
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      return;
    }

    // ── START recording ──
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')
            ? 'audio/ogg;codecs=opus'
            : 'audio/mp4';
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        setIsListening(false);

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        
        if (audioBlob.size < 100) {
          showNotification('Recording too short. Please try again.', 'error');
          return;
        }

        showNotification(' Transcribing audio...', 'success');

        try {
          const ext = mimeType.includes('webm') ? 'webm' : mimeType.includes('ogg') ? 'ogg' : 'mp4';
          const formData = new FormData();
          formData.append('file', audioBlob, `recording.${ext}`);

          const res = await fetch(`${API_URL}/api/transcribe`, {
            method: 'POST',
            body: formData,
          });

          if (!res.ok) {
            let errMsg = `Transcription failed (${res.status})`;
            try {
              const err = await res.json();
              errMsg = err.detail || errMsg;
            } catch (_) {
              errMsg = `Transcription server error: ${res.status}`;
            }
            throw new Error(errMsg);
          }

          const data = await res.json();
          if (data.text && data.text.trim()) {
            setVoiceNote(prev => prev + (prev ? ' ' : '') + data.text.trim());
            showNotification(' Transcription complete!', 'success');
          } else {
            showNotification('No speech detected. Try again.', 'error');
          }
        } catch (e) {
          showNotification(`Transcription error: ${e.message}`, 'error');
        }
      };

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event.error);
        stream.getTracks().forEach(track => track.stop());
        setIsListening(false);
        showNotification('Recording error. Please try again.', 'error');
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsListening(true);
      showNotification('🎙️ Recording... Click mic again to stop', 'success');
    } catch (err) {
      console.error('Microphone access error:', err);
      if (err.name === 'NotAllowedError') {
        showNotification('Microphone access denied. Please allow mic access in browser settings.', 'error');
      } else {
        showNotification(`Microphone error: ${err.message}`, 'error');
      }
    }
  };

  const handleAnalyze = async () => {
    if (!voiceNote.trim()) return;
    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_URL}/api/parse-note`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_note: voiceNote })
      });
      if (!res.ok) {
        let errorMsg = `Server error (${res.status})`;
        try {
          const errorData = await res.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (_) {
          errorMsg = `Server error: ${res.status} ${res.statusText}`;
        }
        throw new Error(errorMsg);
      }
      const data = await res.json();
      setDocumentData(data);
      showNotification('Extraction successful', 'success');
    } catch (e) {
      showNotification(e.message || 'Failed to process. Check backend connection.', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handlePrint = async () => {
    if (!documentData) return;
    try {
      const res = await fetch(`${API_URL}/api/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ visit_date: metadata.visit_date, doctor: metadata.doctor, clinical_data: documentData.document })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to generate PDF');
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `EMR_Note_${metadata.visit_date}.pdf`;
      link.click();
      showNotification(' PDF downloaded!', 'success');
    } catch (e) {
      showNotification(e.message || 'Failed to generate PDF.', 'error');
    }
  };

  const handleNewPatient = () => {
    setDocumentData(null);
    setVoiceNote('');
    showNotification('Ready for new patient', 'success');
  };

  const handleRemoveItem = (sectionKey, itemIndex) => {
    setDocumentData(prev => {
      const doc = { ...prev.document };
      doc[sectionKey] = doc[sectionKey].filter((_, i) => i !== itemIndex);
      return { ...prev, document: doc };
    });
  };

  const handleEditItem = (sectionKey, itemIndex, newText) => {
    if (!newText.trim()) return;
    setDocumentData(prev => {
      const doc = { ...prev.document };
      doc[sectionKey] = doc[sectionKey].map((item, i) =>
        i === itemIndex ? { ...item, rendered_line: newText.trim() } : item
      );
      return { ...prev, document: doc };
    });
    setEditingItem(null);
  };

  // A slot line always renders; its "___" blank is an inline field the doctor
  // fills by hand when the dictation didn't supply the value.
  const handleSlotChange = (sectionKey, itemIndex, newValue) => {
    setDocumentData(prev => {
      const doc = { ...prev.document };
      doc[sectionKey] = doc[sectionKey].map((item, i) => {
        if (i !== itemIndex) return item;
        const blank = newValue || '___';
        if (item.type === 'rx_slot') {
          const filledDose = (item.dose || '').split('___').join(blank);
          return { ...item, value: newValue, dosage: filledDose, rendered_line: `${item.drug} | ${filledDose} | ${item.instructions || ''}` };
        }
        return { ...item, value: newValue, rendered_line: (item.line || '').split('___').join(blank) };
      });
      return { ...prev, document: doc };
    });
  };

  const handleAddItem = (sectionKey) => {
    if (!addItemText.trim()) return;
    setDocumentData(prev => {
      const doc = { ...prev.document };
      const newItem = sectionKey === 'prescription'
        ? { drug: addItemText.trim(), composition: '', dosage: '', frequency: '', duration: '', instructions: '', type: 'manual', rendered_line: addItemText.trim() }
        : { rendered_line: addItemText.trim(), type: 'manual' };
      doc[sectionKey] = [...(doc[sectionKey] || []), newItem];
      return { ...prev, document: doc };
    });
    setAddItemText('');
    setAddingToSection(null);
    showNotification(' Item added', 'success');
  };

  const getTypeStyle = (type) => {
    if (type.includes('manual')) return 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold';
    if (type.includes('extracted')) return 'bg-sky-50 text-sky-700 border border-sky-200 font-semibold';
    if (type.includes('fixed') || type.includes('rx_fixed')) return 'bg-slate-100 text-slate-500 border border-slate-200';
    if (type.includes('slot')) return 'bg-teal-50 text-teal-700 border border-teal-200 font-semibold';
    if (type.includes('extended')) return 'bg-fuchsia-100 text-fuchsia-700 border border-fuchsia-200 font-semibold';
    return 'bg-slate-100 text-slate-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-teal-50/30 flex flex-col">

      {/* ─── TOP NAVBAR ─── */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-slate-200/60 px-6 py-3">
        <div className="flex items-center justify-between max-w-[1800px] mx-auto">
          <div className="flex items-center gap-3">
            <a href="/" className="px-3 py-2 bg-slate-100 text-slate-600 rounded-xl text-sm font-semibold hover:bg-slate-200 transition-all flex items-center gap-1.5 no-underline">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
              Home
            </a>
            <ContextaLogo className="h-[22px] w-auto" />
            <div className="h-5 w-px bg-slate-200 mx-1"></div>
            <span className="text-xs font-semibold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full tracking-wide uppercase">
              EMR Demo
            </span>
          </div>
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className={`px-3 sm:px-4 py-2 border rounded-xl text-sm font-semibold shadow-sm transition-all flex items-center gap-2 ${showTemplates ? 'bg-teal-50 border-teal-200 text-teal-700 hover:bg-teal-100' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2-2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
              <span className="hidden sm:inline">Templates</span>
            </button>
            <button
              id="btn-new-patient"
              onClick={handleNewPatient}
              className="px-3 sm:px-4 py-2 bg-white border border-slate-200 rounded-xl text-slate-600 text-sm font-semibold hover:bg-slate-50 hover:border-slate-300 shadow-sm transition-all active:scale-[0.97] flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
              <span className="hidden sm:inline">New Patient</span>
            </button>
            {/* PDF Download is disabled for now as the code isn't working for it */}
            {/* <button
              id="btn-print-pdf"
              onClick={handlePrint}
              disabled={!documentData}
              className="px-3 sm:px-4 py-2 bg-gradient-to-r from-teal-600 to-teal-500 disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 disabled:shadow-none text-white rounded-xl text-sm font-semibold hover:from-teal-700 hover:to-teal-600 shadow-md shadow-teal-500/20 transition-all active:scale-[0.97] flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
              <span className="hidden sm:inline">Print PDF</span>
            </button> */}
          </div>
        </div>
      </nav>

      {/* ─── NOTIFICATION TOAST ─── */}
      {notification.show && (
        <div className={`fixed top-16 right-4 px-5 py-3 rounded-xl shadow-2xl text-white font-medium z-[60] notification-enter flex items-center gap-2.5 text-sm ${notification.type === 'error' ? 'bg-gradient-to-r from-rose-500 to-red-500 shadow-rose-500/25' : 'bg-gradient-to-r from-teal-600 to-emerald-500 shadow-teal-500/25'}`}>
          {notification.type === 'error' ? (
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          ) : (
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          )}
          {notification.message}
        </div>
      )}

      {/* ─── MAIN CONTENT ─── */}
      <main className="flex-1 p-4 lg:p-6 flex flex-col-reverse lg:flex-row gap-5 max-w-[1800px] mx-auto w-full">

        {showTemplates ? (
          <TemplateLibrary onBack={() => setShowTemplates(false)} />
        ) : (
          <>
            {/* ─── LEFT PANEL: Document View ─── */}
            <div className="w-full lg:w-2/3 bg-white/90 backdrop-blur-sm p-4 sm:p-6 md:p-8 shadow-lg shadow-slate-200/40 border border-white/80 rounded-2xl h-[500px] lg:h-[calc(100vh-7.5rem)] overflow-y-auto">

          {/* Panel Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-100 pb-5 mb-6 gap-3">
            <div>
              <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
                <span className="bg-gradient-to-br from-teal-500 to-teal-600 text-white p-2 rounded-xl shadow-sm">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                </span>
                Clinical Document
              </h1>
              <p className="text-xs text-slate-400 mt-1.5 ml-[46px]">Auto-generated from voice dictation</p>
            </div>
            {documentData && (
              <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                Template: {documentData.template_id}
              </span>
            )}
          </div>

          {/* Specialty Dropdown */}
          <div className="mb-5">
            <div className="group">
              <label className="text-[11px] font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider group-hover:text-teal-600 transition-colors">Specialty</label>
              <div className="relative">
                <select
                  id="select-specialty"
                  value={selectedSpecialty}
                  onChange={e => setSelectedSpecialty(e.target.value)}
                  className="w-full border border-slate-200 p-3 rounded-xl text-sm bg-white outline-none text-slate-700 shadow-sm focus:border-teal-400 focus:ring-2 focus:ring-teal-500/10 transition-all appearance-none cursor-pointer pr-10"
                >
                  {specialtyOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-slate-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                </div>
              </div>
            </div>
          </div>

          {/* Metadata fields */}
          <div className="grid grid-cols-2 gap-5 mb-6">
            <div className="group">
              <label className="text-[11px] font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider group-hover:text-teal-600 transition-colors">Visit Date</label>
              <input id="input-visit-date" type="date" className="w-full border border-slate-200 p-3 rounded-xl text-sm bg-slate-50/50 outline-none text-slate-700 shadow-inner focus:border-teal-400 focus:ring-2 focus:ring-teal-500/10 transition-all" value={metadata.visit_date} readOnly />
            </div>
            <div className="group">
              <label className="text-[11px] font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider group-hover:text-teal-600 transition-colors">Doctor</label>
              <p id="select-doctor" className="w-full border border-slate-200 p-3 rounded-xl text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/10 text-slate-700 shadow-sm transition-all bg-white" value={metadata.doctor} onChange={e => setMetadata({...metadata, doctor: e.target.value})}>
                Dr.Priya
              </p>
            </div>
          </div>

          {/* Document Body */}
          {!documentData ? (
            <div className="border-2 border-dashed border-slate-200 h-[calc(100%-12rem)] min-h-[300px] flex flex-col items-center justify-center rounded-2xl bg-gradient-to-b from-slate-50/30 to-teal-50/20 text-slate-400 shimmer-bg">
              <div className="float-animation mb-5">
                <div className="bg-white p-5 rounded-2xl shadow-lg shadow-slate-100 border border-slate-100">
                  <ContextaIcon />
                </div>
              </div>
              <p className="text-sm font-semibold text-slate-500 mb-1">No document yet</p>
              <p className="text-xs text-slate-400 max-w-xs text-center leading-relaxed">
                Dictate your clinical findings on the right panel and click <strong className="text-teal-600">"Extract & Fill"</strong> to generate the EMR document.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.keys(systemAttributeHeaders).map(sectionKey => {
                const items = documentData.document[sectionKey];
                const hasItems = items && items.length > 0;

                // A section the active template doesn't define comes back empty
                // (e.g. `plan` for the ortho templates, `chief_complaint` for
                // the older ones). Don't render an empty shell for it.
                if (!hasItems) return null;

                const theme = sectionThemes[sectionKey] || sectionThemes.plan;
                const isEditable = sectionKey !== 'diagnosis';

                return (
                  <div key={sectionKey} className={`rounded-xl overflow-hidden bg-white shadow-sm border ${theme.border} transition-all hover:shadow-md group`}>
                    <div className={`${theme.bg} px-5 py-3 text-xs font-bold ${theme.text} uppercase tracking-[0.08em] border-b ${theme.border} flex items-center gap-2`}>
                      <svg className="w-4 h-4 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={theme.icon} /></svg>
                      {systemAttributeHeaders[sectionKey]}
                      {hasItems && <span className="ml-auto text-[10px] font-medium opacity-50">{items.length} {items.length === 1 ? 'item' : 'items'}</span>}
                    </div>
                    {sectionKey === 'prescription' ? (
                      /* ── PRESCRIPTION TABLE (matches the source doc's own columns) ── */
                      <div className="p-2.5">
                        {hasItems && (
                          <div className="overflow-x-auto rounded-lg border border-slate-100 mb-2">
                            <table className="w-full text-[13px] text-left border-collapse">
                              <thead>
                                <tr className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider">
                                  <th className="px-3 py-2 font-semibold">Drug</th>
                                  <th className="px-3 py-2 font-semibold">Composition</th>
                                  <th className="px-3 py-2 font-semibold">Dosage</th>
                                  <th className="px-3 py-2 font-semibold">Frequency</th>
                                  <th className="px-3 py-2 font-semibold">Duration</th>
                                  <th className="px-3 py-2 font-semibold">Instructions</th>
                                  <th className="px-3 py-2 font-semibold w-8"></th>
                                </tr>
                              </thead>
                              <tbody>
                                {items.map((item, idx) => (
                                  <tr key={idx} className="border-t border-slate-100 hover:bg-slate-50/60 transition-colors">
                                    <td className="px-3 py-2 font-medium text-slate-700">{item.drug}</td>
                                    <td className="px-3 py-2 text-slate-600">{item.composition || '—'}</td>
                                    <td className="px-3 py-2 text-slate-600">
                                      {item.type === 'rx_slot' ? (
                                        <SlotLine
                                          item={{ line: item.dose, value: item.value }}
                                          onChange={val => handleSlotChange(sectionKey, idx, val)}
                                        />
                                      ) : (item.dosage || '—')}
                                    </td>
                                    <td className="px-3 py-2 text-slate-600">{item.frequency || '—'}</td>
                                    <td className="px-3 py-2 text-slate-600">{item.duration || '—'}</td>
                                    <td className="px-3 py-2 text-slate-600">{item.instructions || '—'}</td>
                                    <td className="px-3 py-2">
                                      <button onClick={() => handleRemoveItem(sectionKey, idx)} className="text-slate-300 hover:text-rose-500 hover:bg-rose-50 p-1 rounded-lg transition-all" title="Remove item">
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                                      </button>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {addingToSection === sectionKey ? (
                          <div className="flex items-center gap-2 p-2">
                            <input
                              autoFocus
                              className="flex-1 text-[13px] text-slate-700 bg-white border border-teal-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-400 transition-all placeholder:text-slate-300"
                              placeholder="Drug name..."
                              value={addItemText}
                              onChange={e => setAddItemText(e.target.value)}
                              onKeyDown={e => {
                                if (e.key === 'Enter') handleAddItem(sectionKey);
                                if (e.key === 'Escape') { setAddingToSection(null); setAddItemText(''); }
                              }}
                            />
                            <button onClick={() => handleAddItem(sectionKey)} className="text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 p-1.5 rounded-lg transition-all" title="Add">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" /></svg>
                            </button>
                            <button onClick={() => { setAddingToSection(null); setAddItemText(''); }} className="text-slate-400 hover:text-rose-500 hover:bg-rose-50 p-1.5 rounded-lg transition-all" title="Cancel">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => { setAddingToSection(sectionKey); setAddItemText(''); }}
                            className="w-full flex items-center justify-center gap-1.5 p-2 text-xs font-semibold text-slate-400 hover:text-teal-600 hover:bg-teal-50/50 rounded-lg border border-dashed border-slate-200 hover:border-teal-300 transition-all"
                          >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                            Add Prescription
                          </button>
                        )}
                      </div>
                    ) : (
                    <div className="p-2.5 space-y-1.5">
                      {hasItems && items.map((item, idx) => {
                        const isSlot = item.type === 'slot';
                        const isEditing = !isSlot && editingItem && editingItem.sectionKey === sectionKey && editingItem.itemIndex === idx;

                        return (
                          <div key={idx} className={`flex items-center justify-between p-3 rounded-lg border-l-[3px] ${theme.highlight} ${item.type === 'extended' ? 'bg-fuchsia-50/40 border border-fuchsia-100' : item.type === 'manual' ? 'bg-indigo-50/40 border border-indigo-100' : 'bg-slate-50/40 border border-slate-100/60 hover:bg-slate-50'} transition-all`}>
                            {isEditing ? (
                              /* ── EDIT MODE ── */
                              <div className="flex items-center gap-2 w-full">
                                <input
                                  autoFocus
                                  className="flex-1 text-[14px] text-slate-700 font-medium bg-white border border-teal-300 rounded-lg px-3 py-1.5 outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-400 transition-all"
                                  value={editingItem.text}
                                  onChange={e => setEditingItem({ ...editingItem, text: e.target.value })}
                                  onKeyDown={e => {
                                    if (e.key === 'Enter') handleEditItem(sectionKey, idx, editingItem.text);
                                    if (e.key === 'Escape') setEditingItem(null);
                                  }}
                                />
                                {/* Save */}
                                <button onClick={() => handleEditItem(sectionKey, idx, editingItem.text)} className="text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 p-1.5 rounded-lg transition-all" title="Save">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" /></svg>
                                </button>
                                {/* Cancel */}
                                <button onClick={() => setEditingItem(null)} className="text-slate-400 hover:text-rose-500 hover:bg-rose-50 p-1.5 rounded-lg transition-all" title="Cancel">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                                </button>
                              </div>
                            ) : (
                              /* ── VIEW MODE ── */
                              <>
                                {isSlot ? (
                                  <SlotLine item={item} onChange={val => handleSlotChange(sectionKey, idx, val)} />
                                ) : (
                                  <div className="text-[14px] text-slate-700 leading-relaxed font-medium">
                                    {item.rendered_line}
                                  </div>
                                )}
                                <div className="flex items-center gap-2 ml-4 shrink-0">
                                  <span className={`text-[9px] uppercase tracking-wider px-2 py-0.5 rounded-md ${getTypeStyle(item.type)}`}>
                                    {item.type === 'rx_fixed' ? 'template' : item.type === 'rx_slot' ? 'template' : item.type.replace('_', ' ')}
                                  </span>
                                  {/* Edit button (pen icon) — slot lines are edited via their inline blank */}
                                  {isEditable && !isSlot && (
                                    <button
                                      onClick={() => setEditingItem({ sectionKey, itemIndex: idx, text: item.rendered_line })}
                                      className="text-slate-300 hover:text-teal-500 hover:bg-teal-50 p-1 rounded-lg transition-all"
                                      title="Edit item"
                                    >
                                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                                    </button>
                                  )}
                                  {/* Remove button */}
                                  {isEditable && (
                                    <button onClick={() => handleRemoveItem(sectionKey, idx)} className="text-slate-300 hover:text-rose-500 hover:bg-rose-50 p-1 rounded-lg transition-all" title="Remove item">
                                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                                    </button>
                                  )}
                                </div>
                              </>
                            )}
                          </div>
                        );
                      })}

                      {/* ── ADD NEW ITEM ── */}
                      {isEditable && (
                        addingToSection === sectionKey ? (
                          <div className="flex items-center gap-2 p-2 mt-1">
                            <input
                              autoFocus
                              className="flex-1 text-[13px] text-slate-700 bg-white border border-teal-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-400 transition-all placeholder:text-slate-300"
                              placeholder={`Add new ${systemAttributeHeaders[sectionKey].toLowerCase()} item...`}
                              value={addItemText}
                              onChange={e => setAddItemText(e.target.value)}
                              onKeyDown={e => {
                                if (e.key === 'Enter') handleAddItem(sectionKey);
                                if (e.key === 'Escape') { setAddingToSection(null); setAddItemText(''); }
                              }}
                            />
                            <button onClick={() => handleAddItem(sectionKey)} className="text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 p-1.5 rounded-lg transition-all" title="Add">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" /></svg>
                            </button>
                            <button onClick={() => { setAddingToSection(null); setAddItemText(''); }} className="text-slate-400 hover:text-rose-500 hover:bg-rose-50 p-1.5 rounded-lg transition-all" title="Cancel">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => { setAddingToSection(sectionKey); setAddItemText(''); }}
                            className="w-full flex items-center justify-center gap-1.5 p-2 mt-1 text-xs font-semibold text-slate-400 hover:text-teal-600 hover:bg-teal-50/50 rounded-lg border border-dashed border-slate-200 hover:border-teal-300 transition-all"
                          >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                            Add {systemAttributeHeaders[sectionKey]}
                          </button>
                        )
                      )}
                    </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ─── RIGHT PANEL: Voice Input ─── */}
        <div className="w-full lg:w-1/3 bg-white/90 backdrop-blur-sm p-4 sm:p-6 md:p-8 shadow-lg shadow-slate-200/40 border border-white/80 rounded-2xl min-h-[400px] lg:h-[calc(100vh-7.5rem)] flex flex-col relative overflow-hidden">

          {/* Decorative background accent */}
          <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-bl from-teal-50/80 to-transparent rounded-bl-full -z-0 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-teal-50/50 to-transparent rounded-tr-full -z-0 pointer-events-none"></div>
          
          <h2 className="text-lg font-bold text-slate-800 mb-4 tracking-tight relative z-10 flex items-center">
            <span className="bg-gradient-to-br from-teal-500 to-teal-600 text-white p-2 rounded-xl mr-3 shadow-sm">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
            </span>
            Doctor's Dictation
          </h2>
          
          <textarea
            id="textarea-dictation"
            className="w-full flex-grow border border-slate-200 p-4 rounded-xl bg-white/60 backdrop-blur-sm resize-none text-[14px] mb-5 focus:ring-2 focus:ring-teal-500/15 focus:border-teal-400 outline-none transition-all leading-relaxed shadow-inner relative z-10 text-slate-700 placeholder:text-slate-300"
            value={voiceNote}
            onChange={e => setVoiceNote(e.target.value)}
            placeholder="Type clinical note here or use the microphone to dictate..."
          />
          
          <div className="space-y-4 relative z-10">
            {/* Mic & Clear Buttons */}
            <div className="flex justify-center items-center gap-4 relative">
              {isListening && (
                <>
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="w-20 h-20 bg-rose-400 rounded-full mic-pulse-ring"></div>
                  </div>
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="w-16 h-16 bg-rose-400 rounded-full mic-pulse-ring" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </>
              )}
              <button
                id="btn-mic"
                onClick={handleMicClick}
                title={isListening ? 'Click to stop recording' : 'Click to start dictating'}
                className={`p-4 rounded-full text-white shadow-xl transition-all duration-300 relative z-10 ${isListening ? 'bg-gradient-to-br from-rose-500 to-red-600 scale-110 cursor-pointer' : 'bg-gradient-to-br from-slate-800 to-slate-700 hover:scale-105 hover:shadow-2xl active:scale-95'}`}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
              </button>
              {/* Clear Button */}
              <button
                id="btn-clear-dictation"
                onClick={() => { setVoiceNote(''); showNotification('Dictation cleared', 'success'); }}
                title="Clear dictation"
                disabled={!voiceNote.trim() || isListening}
                className="p-3 rounded-full text-white shadow-lg transition-all duration-300 relative z-10 bg-gradient-to-br from-slate-500 to-slate-400 hover:from-rose-500 hover:to-red-500 hover:scale-105 hover:shadow-xl active:scale-95 disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 disabled:shadow-none disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
            
            {/* Status Text */}
            <div className="text-center font-semibold text-xs transition-colors">
              {isListening ? (
                <span className="text-rose-500 animate-pulse flex items-center justify-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-ping"></span>
                  Recording... Click mic to stop
                </span>
              ) : (
                <span className="text-slate-400">Tap microphone to start dictating</span>
              )}
            </div>
            
            {/* Extract Button */}
            <button
              id="btn-extract"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !voiceNote.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-200 disabled:to-slate-300 disabled:text-slate-400 disabled:shadow-none text-white p-3.5 rounded-xl font-bold transition-all shadow-lg shadow-blue-500/20 text-sm active:scale-[0.98] flex justify-center items-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Processing...
                </>
              ) : (
                <>
                  Extract & Fill EMR Data
                </>
              )}
            </button>
          </div>
        </div>
          </>
        )}
      </main>

      {/* ─── FOOTER ─── */}
      <footer className="border-t border-slate-200/60 bg-white/60 backdrop-blur-sm px-6 py-3">
        <div className="flex items-center justify-between max-w-[1800px] mx-auto">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Powered by</span>
            <ContextaLogo className="h-[14px] w-auto opacity-40" />
          </div>
          <div className="text-[10px] text-slate-300 font-medium tracking-wide">
            AI-Assisted Clinical Documentation Engine
          </div>
        </div>
      </footer>
    </div>
  );
}