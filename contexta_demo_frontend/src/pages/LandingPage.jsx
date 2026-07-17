import React from 'react';
import { useNavigate } from 'react-router-dom';

// Contexta Health SVG Logo (extracted from contextaemr.com)
const ContextaLogo = ({ className = '' }) => (
  <svg height="32" viewBox="0 0 2842 410" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M184.693 281.275C199.425 281.275 211.367 293.218 211.367 307.949L211.368 383.291C211.368 398.022 199.425 409.965 184.693 409.965C169.961 409.965 158.019 398.022 158.019 383.29L158.018 307.949C158.019 293.218 169.962 281.275 184.693 281.275ZM184.692 0C198.898 0.000161361 210.414 11.5161 210.414 25.7217V153.729C210.414 178.914 223.85 202.187 245.662 214.78L356.519 278.784C368.822 285.887 373.037 301.617 365.934 313.92C358.832 326.223 343.1 330.438 330.798 323.335L219.939 259.33C198.128 246.737 171.254 246.738 149.442 259.331L38.5868 323.334C26.2842 330.437 10.553 326.222 3.4501 313.919C-3.65243 301.616 0.562839 285.886 12.8651 278.783L123.723 214.779C145.534 202.186 158.971 178.913 158.971 153.728V25.7217C158.971 11.516 170.487 0 184.692 0ZM6.99404 106.592C14.3599 93.834 30.6735 89.4627 43.4315 96.8281L108.68 134.499C121.437 141.865 125.808 158.179 118.442 170.937C111.076 183.694 94.7628 188.065 82.0048 180.699L16.7577 143.029C3.99978 135.663 -0.37171 119.35 6.99404 106.592ZM325.785 96.8271C338.543 89.4618 354.857 93.8331 362.223 106.591C369.588 119.349 365.217 135.662 352.459 143.028L287.212 180.699C274.454 188.065 258.14 183.693 250.774 170.936C243.409 158.177 247.78 141.864 260.538 134.498L325.785 96.8271Z" fill="#00878A"></path>
    <path d="M624.238 325.769C595.55 325.769 573.04 316.137 556.707 296.872C540.374 277.398 532.207 249.234 532.207 212.38C532.207 193.953 534.301 177.725 538.489 163.695C542.677 149.665 548.749 137.834 556.707 128.202C564.664 118.57 574.296 111.345 585.604 106.529C597.12 101.504 609.998 98.9908 624.238 98.9908C643.293 98.9908 659.207 103.179 671.98 111.555C684.963 119.931 695.119 132.285 702.448 148.618L672.609 164.951C668.839 154.481 662.976 146.21 655.019 140.138C647.271 133.856 637.011 130.715 624.238 130.715C607.276 130.715 593.98 136.473 584.347 147.99C574.715 159.507 569.899 175.421 569.899 195.733V229.027C569.899 249.339 574.715 265.253 584.347 276.77C593.98 288.287 607.276 294.045 624.238 294.045C637.43 294.045 648.109 290.695 656.276 283.994C664.651 277.084 670.829 268.289 674.807 257.61L703.39 274.885C696.061 290.8 685.801 303.259 672.609 312.263C659.416 321.267 643.293 325.769 624.238 325.769ZM802.579 325.769C791.271 325.769 780.906 323.78 771.483 319.801C762.27 315.823 754.417 310.169 747.926 302.84C741.434 295.302 736.409 286.298 732.849 275.828C729.289 265.148 727.509 253.317 727.509 240.335C727.509 227.352 729.289 215.626 732.849 205.156C736.409 194.476 741.434 185.472 747.926 178.143C754.417 170.605 762.27 164.847 771.483 160.868C780.906 156.889 791.271 154.9 802.579 154.9C813.886 154.9 824.147 156.889 833.36 160.868C842.783 164.847 850.74 170.605 857.232 178.143C863.723 185.472 868.749 194.476 872.308 205.156C875.868 215.626 877.648 227.352 877.648 240.335C877.648 253.317 875.868 265.148 872.308 275.828C868.749 286.298 863.723 295.302 857.232 302.84C850.74 310.169 842.783 315.823 833.36 319.801C824.147 323.78 813.886 325.769 802.579 325.769ZM802.579 297.5C814.305 297.5 823.728 293.941 830.847 286.821C837.967 279.492 841.527 268.603 841.527 254.155V226.514C841.527 212.066 837.967 201.282 830.847 194.162C823.728 186.833 814.305 183.169 802.579 183.169C790.852 183.169 781.429 186.833 774.31 194.162C767.19 201.282 763.631 212.066 763.631 226.514V254.155C763.631 268.603 767.19 279.492 774.31 286.821C781.429 293.941 790.852 297.5 802.579 297.5ZM915.796 322V158.669H950.033V185.682H951.603C955.163 176.887 960.503 169.558 967.622 163.695C974.951 157.832 984.898 154.9 997.461 154.9C1014.21 154.9 1027.2 160.449 1036.41 171.547C1045.83 182.436 1050.54 198.036 1050.54 218.348V322H1016.31V222.745C1016.31 197.199 1006.05 184.425 985.526 184.425C981.128 184.425 976.731 185.053 972.334 186.31C968.146 187.357 964.377 189.032 961.026 191.335C957.676 193.639 954.954 196.57 952.86 200.13C950.975 203.69 950.033 207.878 950.033 212.694V322H915.796ZM1143.23 322C1131.29 322 1122.29 318.964 1116.21 312.891C1110.14 306.609 1107.11 297.814 1107.11 286.507V186.624H1081.66V158.669H1095.48C1101.14 158.669 1105.01 157.413 1107.11 154.9C1109.41 152.387 1110.56 148.304 1110.56 142.65V114.067H1141.34V158.669H1175.58V186.624H1141.34V294.045H1173.07V322H1143.23ZM1275.57 325.769C1263.84 325.769 1253.37 323.78 1244.16 319.801C1234.94 315.823 1227.09 310.169 1220.6 302.84C1214.11 295.302 1209.08 286.298 1205.52 275.828C1202.17 265.148 1200.5 253.317 1200.5 240.335C1200.5 227.352 1202.17 215.626 1205.52 205.156C1209.08 194.476 1214.11 185.472 1220.6 178.143C1227.09 170.605 1234.94 164.847 1244.16 160.868C1253.37 156.889 1263.84 154.9 1275.57 154.9C1287.5 154.9 1297.97 156.994 1306.98 161.182C1316.19 165.37 1323.83 171.233 1329.9 178.772C1335.98 186.1 1340.48 194.686 1343.41 204.528C1346.55 214.369 1348.12 224.944 1348.12 236.251V249.129H1235.99V254.469C1235.99 267.033 1239.65 277.398 1246.98 285.565C1254.52 293.522 1265.2 297.5 1279.02 297.5C1289.07 297.5 1297.55 295.302 1304.46 290.904C1311.37 286.507 1317.24 280.539 1322.05 273.001L1342.15 292.789C1336.08 302.84 1327.29 310.902 1315.77 316.974C1304.25 322.838 1290.85 325.769 1275.57 325.769ZM1275.57 181.598C1269.7 181.598 1264.26 182.645 1259.23 184.739C1254.42 186.833 1250.23 189.765 1246.67 193.534C1243.32 197.303 1240.7 201.805 1238.82 207.04C1236.93 212.275 1235.99 218.034 1235.99 224.316V226.514H1312V223.373C1312 210.809 1308.75 200.758 1302.26 193.22C1295.77 185.472 1286.87 181.598 1275.57 181.598ZM1363.51 322L1420.99 239.392L1365.08 158.669H1404.66L1441.41 215.521H1442.35L1480.04 158.669H1516.48L1460.57 239.078L1517.42 322H1477.84L1440.15 262.636H1439.21L1399.95 322H1363.51ZM1593.52 322C1581.58 322 1572.58 318.964 1566.5 312.891C1560.43 306.609 1557.39 297.814 1557.39 286.507V186.624H1531.95V158.669H1545.77C1551.43 158.669 1555.3 157.413 1557.39 154.9C1559.7 152.387 1560.85 148.304 1560.85 142.65V114.067H1591.63V158.669H1625.87V186.624H1591.63V294.045H1623.35V322H1593.52Z" fill="#1a1a1a"></path>
    <path d="M1782.68 322C1773.67 322 1766.76 319.487 1761.95 314.462C1757.13 309.227 1754.2 302.631 1753.15 294.674H1751.58C1748.44 304.934 1742.68 312.682 1734.3 317.917C1725.93 323.152 1715.77 325.769 1703.84 325.769C1686.88 325.769 1673.79 321.372 1664.57 312.577C1655.57 303.782 1651.07 291.951 1651.07 277.084C1651.07 260.751 1656.93 248.501 1668.66 240.335C1680.59 232.168 1697.97 228.085 1720.8 228.085H1750.32V214.265C1750.32 204.213 1747.6 196.466 1742.16 191.021C1736.71 185.577 1728.23 182.855 1716.72 182.855C1707.08 182.855 1699.23 184.949 1693.16 189.137C1687.09 193.325 1681.96 198.664 1677.77 205.156L1657.35 186.624C1662.8 177.41 1670.44 169.872 1680.28 164.009C1690.12 157.936 1703 154.9 1718.91 154.9C1740.06 154.9 1756.29 159.821 1767.6 169.663C1778.91 179.504 1784.56 193.639 1784.56 212.066V294.045H1801.84V322H1782.68ZM1713.57 299.699C1724.25 299.699 1733.05 297.396 1739.96 292.789C1746.87 287.973 1750.32 281.586 1750.32 273.629V250.072H1721.43C1697.76 250.072 1685.93 257.401 1685.93 272.058V277.712C1685.93 285.041 1688.34 290.59 1693.16 294.359C1698.18 297.919 1704.99 299.699 1713.57 299.699Z" fill="#1a1a1a"></path>
    <path d="M2046.88 226.514H1947.63V322H1912.13V102.76H1947.63V195.105H2046.88V102.76H2082.37V322H2046.88V226.514ZM2197.92 325.769C2186.19 325.769 2175.72 323.78 2166.51 319.801C2157.3 315.823 2149.44 310.169 2142.95 302.84C2136.46 295.302 2131.44 286.298 2127.88 275.828C2124.53 265.148 2122.85 253.317 2122.85 240.335C2122.85 227.352 2124.53 215.626 2127.88 205.156C2131.44 194.476 2136.46 185.472 2142.95 178.143C2149.44 170.605 2157.3 164.847 2166.51 160.868C2175.72 156.889 2186.19 154.9 2197.92 154.9C2209.86 154.9 2220.33 156.994 2229.33 161.182C2238.54 165.37 2246.19 171.233 2252.26 178.772C2258.33 186.1 2262.83 194.686 2265.76 204.528C2268.91 214.369 2270.48 224.944 2270.48 236.251V249.129H2158.34V254.469C2158.34 267.033 2162.01 277.398 2169.34 285.565C2176.88 293.522 2187.55 297.5 2201.37 297.5C2211.43 297.5 2219.91 295.302 2226.82 290.904C2233.73 286.507 2239.59 280.539 2244.41 273.001L2264.51 292.789C2258.44 302.84 2249.64 310.902 2238.12 316.974C2226.61 322.838 2213.21 325.769 2197.92 325.769ZM2197.92 181.598C2192.06 181.598 2186.61 182.645 2181.59 184.739C2176.77 186.833 2172.58 189.765 2169.02 193.534C2165.67 197.303 2163.06 201.805 2161.17 207.04C2159.29 212.275 2158.34 218.034 2158.34 224.316V226.514H2234.36V223.373C2234.36 210.809 2231.11 200.758 2224.62 193.22C2218.13 185.472 2209.23 181.598 2197.92 181.598ZM2428.05 322C2419.04 322 2412.13 319.487 2407.32 314.462C2402.5 309.227 2399.57 302.631 2398.52 294.674H2396.95C2393.81 304.934 2388.05 312.682 2379.68 317.917C2371.3 323.152 2361.15 325.769 2349.21 325.769C2332.25 325.769 2319.16 321.372 2309.95 312.577C2300.94 303.782 2296.44 291.951 2296.44 277.084C2296.44 260.751 2302.3 248.501 2314.03 240.335C2325.97 232.168 2343.35 228.085 2366.17 228.085H2395.7V214.265C2395.7 204.213 2392.97 196.466 2387.53 191.021C2382.08 185.577 2373.6 182.855 2362.09 182.855C2352.46 182.855 2344.6 184.949 2338.53 189.137C2332.46 193.325 2327.33 198.664 2323.14 205.156L2302.72 186.624C2308.17 177.41 2315.81 169.872 2325.65 164.009C2335.49 157.936 2348.37 154.9 2364.29 154.9C2385.44 154.9 2401.66 159.821 2412.97 169.663C2424.28 179.504 2429.93 193.639 2429.93 212.066V294.045H2447.21V322H2428.05ZM2358.95 299.699C2369.63 299.699 2378.42 297.396 2385.33 292.789C2392.24 287.973 2395.7 281.586 2395.7 273.629V250.072H2366.8C2343.14 250.072 2331.31 257.401 2331.31 272.058V277.712C2331.31 285.041 2333.71 290.59 2338.53 294.359C2343.56 297.919 2350.36 299.699 2358.95 299.699ZM2515.63 322C2503.9 322 2495.11 319.068 2489.24 313.205C2483.59 307.133 2480.76 298.757 2480.76 288.077V89.5679H2515V294.045H2537.61V322H2515.63ZM2614.03 322C2602.09 322 2593.09 318.964 2587.01 312.891C2580.94 306.609 2577.9 297.814 2577.9 286.507V186.624H2552.46V158.669H2566.28C2571.94 158.669 2575.81 157.413 2577.9 154.9C2580.21 152.387 2581.36 148.304 2581.36 142.65V114.067H2612.14V158.669H2646.38V186.624H2612.14V294.045H2643.86V322H2614.03ZM2683.51 89.5679H2717.75V185.682H2719.32C2722.88 176.887 2728.22 169.558 2735.34 163.695C2742.67 157.832 2752.62 154.9 2765.18 154.9C2781.93 154.9 2794.91 160.449 2804.13 171.547C2813.55 182.436 2818.26 198.036 2818.26 218.348V322H2784.03V222.431C2784.03 197.094 2773.77 184.425 2753.24 184.425C2748.85 184.425 2744.45 185.053 2740.05 186.31C2735.86 187.357 2732.09 189.032 2728.74 191.335C2725.39 193.639 2722.67 196.57 2720.58 200.13C2718.69 203.69 2717.75 207.773 2717.75 212.38V322H2683.51V89.5679Z" fill="#00878A"></path>
  </svg>
);

const ContextaIcon = () => (
  <svg width="48" height="48" viewBox="0 0 370 410" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M184.693 281.275C199.425 281.275 211.367 293.218 211.367 307.949L211.368 383.291C211.368 398.022 199.425 409.965 184.693 409.965C169.961 409.965 158.019 398.022 158.019 383.29L158.018 307.949C158.019 293.218 169.962 281.275 184.693 281.275ZM184.692 0C198.898 0.000161361 210.414 11.5161 210.414 25.7217V153.729C210.414 178.914 223.85 202.187 245.662 214.78L356.519 278.784C368.822 285.887 373.037 301.617 365.934 313.92C358.832 326.223 343.1 330.438 330.798 323.335L219.939 259.33C198.128 246.737 171.254 246.738 149.442 259.331L38.5868 323.334C26.2842 330.437 10.553 326.222 3.4501 313.919C-3.65243 301.616 0.562839 285.886 12.8651 278.783L123.723 214.779C145.534 202.186 158.971 178.913 158.971 153.728V25.7217C158.971 11.516 170.487 0 184.692 0ZM6.99404 106.592C14.3599 93.834 30.6735 89.4627 43.4315 96.8281L108.68 134.499C121.437 141.865 125.808 158.179 118.442 170.937C111.076 183.694 94.7628 188.065 82.0048 180.699L16.7577 143.029C3.99978 135.663 -0.37171 119.35 6.99404 106.592ZM325.785 96.8271C338.543 89.4618 354.857 93.8331 362.223 106.591C369.588 119.349 365.217 135.662 352.459 143.028L287.212 180.699C274.454 188.065 258.14 183.693 250.774 170.936C243.409 158.177 247.78 141.864 260.538 134.498L325.785 96.8271Z" fill="#00878A" />
  </svg>
);

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-teal-50/30 flex flex-col">
      
      {/* ─── FLOATING PARTICLES BACKGROUND ─── */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-teal-200/20 rounded-full blur-3xl float-animation"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-200/15 rounded-full blur-3xl float-animation" style={{ animationDelay: '1.5s' }}></div>
        <div className="absolute top-1/2 left-1/3 w-48 h-48 bg-emerald-200/10 rounded-full blur-2xl float-animation" style={{ animationDelay: '0.8s' }}></div>
      </div>

      {/* ─── TOP NAVBAR ─── */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-slate-200/60 px-6 py-4">
        <div className="flex items-center justify-center max-w-[1400px] mx-auto">
          <a href="/" className="flex items-center gap-3 no-underline cursor-pointer">
            <ContextaLogo className="h-[28px] w-auto" />
          </a>
        </div>
      </nav>

      {/* ─── HERO + CARDS ─── */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-12 relative z-10">
        
        {/* Hero Section */}
        <div className="text-center mb-16 max-w-2xl">
          <div className="flex justify-center mb-6">
            <div className="bg-white p-5 rounded-3xl shadow-xl shadow-teal-100/40 border border-white/80 float-animation">
              <ContextaIcon />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 tracking-tight mb-4 leading-tight">
            AI-Powered <span className="bg-gradient-to-r from-teal-600 to-emerald-500 bg-clip-text text-transparent">Clinical Intelligence</span>
          </h1>
          <p className="text-lg text-slate-500 max-w-lg mx-auto leading-relaxed">
            Streamline your healthcare workflow with intelligent documentation and an AI-powered patient assistant.
          </p>
        </div>

        {/* ─── FOUR BIG CARDS ─── */}
        {/* 2-up on tablet, 4-up from lg. Container widened from 1200 to 1400 so
            the fourth card doesn't squeeze the copy in every card. */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 max-w-[1400px] w-full">
          
          {/* Visit Notes Card */}
          <button
            id="card-visit-notes"
            onClick={() => navigate('/visit-notes')}
            className="group relative bg-white/60 backdrop-blur-xl rounded-[2rem] p-8 flex flex-col border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_-15px_rgba(20,184,166,0.4)] transition-all duration-500 hover:-translate-y-3 text-left cursor-pointer overflow-hidden"
          >
            {/* Glowing background effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 via-transparent to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-teal-400/20 rounded-full blur-3xl group-hover:bg-teal-400/40 transition-all duration-500 group-hover:scale-150"></div>
            
            <div className="relative z-10 flex flex-col flex-1">
              {/* Icon */}
              <div className="bg-gradient-to-br from-teal-400 to-emerald-600 text-white p-4 rounded-2xl shadow-lg shadow-teal-500/30 inline-flex self-start mb-8 group-hover:scale-110 group-hover:-rotate-3 transition-transform duration-500">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>

              <h2 className="text-[26px] font-extrabold text-slate-800 mb-4 group-hover:bg-gradient-to-r group-hover:from-teal-600 group-hover:to-emerald-600 group-hover:bg-clip-text group-hover:text-transparent transition-all">
                Visit Notes
              </h2>
              
              <p /* min-h, not a fixed h: the cards narrow at 4-up and a fixed height
                 clipped the longer blurbs. The CTA row bottom-aligns via mt-auto, so
                 this only needs to be a floor, not an exact match. */
              className="text-slate-500 text-[15px] leading-relaxed mb-8 min-h-[65px] font-medium">
                AI-powered voice dictation that automatically extracts clinical data and fills EMR templates.
              </p>

              <div className="space-y-4 mb-10">
                {['Voice-to-EMR dictation', 'Multi-specialty templates', 'Intelligent slot filling'].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-[14px] text-slate-600 font-semibold group-hover:text-slate-900 transition-colors">
                    <div className="w-6 h-6 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 group-hover:bg-teal-500 group-hover:text-white transition-colors duration-300">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    {feature}
                  </div>
                ))}
              </div>

              <div className="mt-auto flex items-center gap-2 text-teal-600 font-bold text-[15px] group-hover:text-teal-700 transition-colors">
                Open Visit Notes
                <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>
          </button>

          {/* Contexta Health Product Card */}
          <a
            id="card-product"
            href="https://contexta-product-design-lime.vercel.app/queue"
            target="_blank"
            rel="noopener noreferrer"
            className="group relative bg-white/60 backdrop-blur-xl rounded-[2rem] p-8 flex flex-col border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_-15px_rgba(168,85,247,0.4)] transition-all duration-500 hover:-translate-y-3 text-left cursor-pointer overflow-hidden no-underline"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-fuchsia-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-purple-400/20 rounded-full blur-3xl group-hover:bg-purple-400/40 transition-all duration-500 group-hover:scale-150"></div>

            <div className="relative z-10 flex flex-col flex-1">
              {/* Icon */}
              <div className="bg-gradient-to-br from-purple-500 to-fuchsia-600 text-white p-4 rounded-2xl shadow-lg shadow-purple-500/30 inline-flex self-start mb-8 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-500">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>

              <h2 className="text-[26px] font-extrabold text-slate-800 mb-4 group-hover:bg-gradient-to-r group-hover:from-purple-600 group-hover:to-fuchsia-600 group-hover:bg-clip-text group-hover:text-transparent transition-all">
                Contexta Health
              </h2>
              
              <p /* min-h, not a fixed h: the cards narrow at 4-up and a fixed height
                 clipped the longer blurbs. The CTA row bottom-aligns via mt-auto, so
                 this only needs to be a floor, not an exact match. */
              className="text-slate-500 text-[15px] leading-relaxed mb-8 min-h-[65px] font-medium">
                Our full-featured healthcare platform — the production product powering clinical workflows at scale.
              </p>

              <div className="space-y-4 mb-10">
                {['Live production EMR', 'Full clinical suite', 'Enterprise-grade platform'].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-[14px] text-slate-600 font-semibold group-hover:text-slate-900 transition-colors">
                    <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 group-hover:bg-purple-500 group-hover:text-white transition-colors duration-300">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    {feature}
                  </div>
                ))}
              </div>

              <div className="mt-auto flex items-center gap-2 text-purple-600 font-bold text-[15px] group-hover:text-purple-700 transition-colors">
                Visit Product
                <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
            </div>
          </a>

          {/* ChatBot Card */}
          <button
            id="card-chatbot"
            onClick={() => navigate('/chatbot')}
            className="group relative bg-white/60 backdrop-blur-xl rounded-[2rem] p-8 flex flex-col border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_-15px_rgba(59,130,246,0.4)] transition-all duration-500 hover:-translate-y-3 text-left cursor-pointer overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-400/20 rounded-full blur-3xl group-hover:bg-blue-400/40 transition-all duration-500 group-hover:scale-150"></div>

            <div className="relative z-10 flex flex-col flex-1">
              {/* Icon */}
              <div className="bg-gradient-to-br from-blue-400 to-indigo-600 text-white p-4 rounded-2xl shadow-lg shadow-blue-500/30 inline-flex self-start mb-8 group-hover:scale-110 group-hover:-rotate-3 transition-transform duration-500">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                </svg>
              </div>

              <h2 className="text-[26px] font-extrabold text-slate-800 mb-4 group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-indigo-600 group-hover:bg-clip-text group-hover:text-transparent transition-all">
                WhatsApp ChatBot
              </h2>
              
              <p /* min-h, not a fixed h: the cards narrow at 4-up and a fixed height
                 clipped the longer blurbs. The CTA row bottom-aligns via mt-auto, so
                 this only needs to be a floor, not an exact match. */
              className="text-slate-500 text-[15px] leading-relaxed mb-8 min-h-[65px] font-medium">
                Intelligent clinical assistant for patients — book appointments, check doctor availability, and get health guidance.
              </p>

              <div className="space-y-4 mb-10">
                {['AI-powered patient assistant', 'Appointment booking', 'Doctor availability'].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-[14px] text-slate-600 font-semibold group-hover:text-slate-900 transition-colors">
                    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 group-hover:bg-blue-500 group-hover:text-white transition-colors duration-300">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    {feature}
                  </div>
                ))}
              </div>

              <div className="mt-auto flex items-center gap-2 text-blue-600 font-bold text-[15px] group-hover:text-blue-700 transition-colors">
                Open WhatsApp ChatBot
                <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>
          </button>

          {/* Doctors Chat Card */}
          <button
            id="card-doctors-chat"
            onClick={() => navigate('/doctor')}
            className="group relative bg-white/60 backdrop-blur-xl rounded-[2rem] p-8 flex flex-col border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_-15px_rgba(99,102,241,0.4)] transition-all duration-500 hover:-translate-y-3 text-left cursor-pointer overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-violet-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-indigo-400/20 rounded-full blur-3xl group-hover:bg-indigo-400/40 transition-all duration-500 group-hover:scale-150"></div>

            <div className="relative z-10 flex flex-col flex-1">
              {/* Icon */}
              <div className="bg-gradient-to-br from-indigo-400 to-violet-600 text-white p-4 rounded-2xl shadow-lg shadow-indigo-500/30 inline-flex self-start mb-8 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-500">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>

              <h2 className="text-[26px] font-extrabold text-slate-800 mb-4 group-hover:bg-gradient-to-r group-hover:from-indigo-600 group-hover:to-violet-600 group-hover:bg-clip-text group-hover:text-transparent transition-all">
                Doctors Chat
              </h2>

              <p /* min-h, not a fixed h: the cards narrow at 4-up and a fixed height
                 clipped the longer blurbs. The CTA row bottom-aligns via mt-auto, so
                 this only needs to be a floor, not an exact match. */
              className="text-slate-500 text-[15px] leading-relaxed mb-8 min-h-[65px] font-medium">
                Ask your own patient records in plain language — trends, history and your surgery schedule, answered from the chart.
              </p>

              <div className="space-y-4 mb-10">
                {['Chat over patient records', 'Trends & visit history', 'Ask by voice'].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-[14px] text-slate-600 font-semibold group-hover:text-slate-900 transition-colors">
                    <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 group-hover:bg-indigo-500 group-hover:text-white transition-colors duration-300">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    {feature}
                  </div>
                ))}
              </div>

              <div className="mt-auto flex items-center gap-2 text-indigo-600 font-bold text-[15px] group-hover:text-indigo-700 transition-colors">
                Open Doctors Chat
                <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>
          </button>

        </div>
      </main>

      {/* ─── FOOTER ─── */}
      <footer className="border-t border-slate-200/60 bg-white/60 backdrop-blur-sm px-6 py-4 relative z-10">
        <div className="flex items-center justify-between max-w-[1400px] mx-auto">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Powered by</span>
            <ContextaLogo className="h-[14px] w-auto opacity-40" />
          </div>
          <div className="text-[10px] text-slate-300 font-medium tracking-wide">
            AI-Powered Clinical Intelligence
          </div>
        </div>
      </footer>
    </div>
  );
}
