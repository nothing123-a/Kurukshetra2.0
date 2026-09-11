import React from 'react';

/**
 * SudarshanChakraLoader — Reusable SVG spinning Sudarshan Chakra.
 * Scalable discus with radiating blades around a circular hub.
 * Styled in brilliant light yellow with gleaming metallic shine and radiant glow.
 */
export default function SudarshanChakraLoader({ 
  size = 120, 
  spinning = true, 
  glowing = true, 
  theme = 'light-yellow',
  className = '' 
}) {
  const bladeCount = 18;
  const blades = Array.from({ length: bladeCount }, (_, i) => i);

  return (
    <div className={`inline-flex items-center justify-center relative ${className}`} style={{ width: size, height: size }}>
      {/* Radiant Shiny Glow Effect */}
      {glowing && (
        <div
          className="absolute rounded-full pointer-events-none"
          style={{
            width: size * 1.45,
            height: size * 1.45,
            background: 'radial-gradient(circle, rgba(254, 249, 195, 0.55) 0%, rgba(250, 204, 21, 0.3) 38%, rgba(234, 179, 8, 0.1) 58%, transparent 72%)',
            animation: 'chakraGlow 2.2s ease-in-out infinite alternate',
          }}
        />
      )}

      {/* Sparkling Ambient Sheen */}
      {glowing && (
        <div
          className="absolute rounded-full pointer-events-none"
          style={{
            width: size * 0.9,
            height: size * 0.9,
            boxShadow: '0 0 20px 4px rgba(254, 240, 138, 0.7), inset 0 0 12px 2px rgba(255, 255, 255, 0.8)',
            animation: 'chakraShinePulse 3s ease-in-out infinite',
          }}
        />
      )}

      <svg
        viewBox="0 0 200 200"
        width={size}
        height={size}
        style={{
          animation: spinning ? 'chakraSpin 2.4s linear infinite' : 'none',
          filter: 'drop-shadow(0 0 8px rgba(250, 204, 21, 0.75)) drop-shadow(0 0 2px rgba(255, 255, 255, 0.9))',
        }}
      >
        <defs>
          {/* Luminous Light Yellow Ring Gradient */}
          <radialGradient id="chakraRingGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#FFFFEE" />
            <stop offset="45%" stopColor="#FEF08A" />
            <stop offset="85%" stopColor="#FACC15" />
            <stop offset="100%" stopColor="#EAB308" />
          </radialGradient>

          {/* Shiny Center Hub Gradient */}
          <radialGradient id="chakraHubGrad" cx="40%" cy="40%" r="60%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="30%" stopColor="#FEF9C3" />
            <stop offset="70%" stopColor="#FDE047" />
            <stop offset="100%" stopColor="#EAB308" />
          </radialGradient>

          {/* Gleaming Light Yellow Blade Gradient */}
          <linearGradient id="chakraBladeGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="25%" stopColor="#FEF08A" />
            <stop offset="75%" stopColor="#FACC15" />
            <stop offset="100%" stopColor="#CA8A04" />
          </linearGradient>

          {/* Specular Highlight Sheen */}
          <linearGradient id="chakraSheen" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(255, 255, 255, 0.9)" />
            <stop offset="50%" stopColor="rgba(254, 240, 138, 0.3)" />
            <stop offset="100%" stopColor="rgba(234, 179, 8, 0.1)" />
          </linearGradient>
        </defs>

        {/* Outer Shiny Halo Ring */}
        <circle cx="100" cy="100" r="93" fill="none" stroke="url(#chakraRingGrad)" strokeWidth="2.5" opacity="0.9" />
        <circle cx="100" cy="100" r="88" fill="none" stroke="#FEF9C3" strokeWidth="1.2" opacity="0.8" strokeDasharray="6 3" />

        {/* Radiating 18 Blades in Polished Light Yellow */}
        {blades.map((i) => {
          const angle = (i * 360) / bladeCount;
          return (
            <g key={i} transform={`rotate(${angle} 100 100)`}>
              {/* Sharp Blade */}
              <polygon
                points="100,16 93.5,58 106.5,58"
                fill="url(#chakraBladeGrad)"
                stroke="#FEF08A"
                strokeWidth="0.6"
              />
              {/* Blade Ridge Specular Highlight Line */}
              <line x1="100" y1="18" x2="100" y2="56" stroke="#FFFFFF" strokeWidth="0.8" opacity="0.85" />
              {/* Decorative Golden Notch */}
              <circle cx="100" cy="62" r="2.2" fill="#FFFFFF" stroke="#EAB308" strokeWidth="0.6" />
            </g>
          );
        })}

        {/* Inner Ornamental Ring */}
        <circle cx="100" cy="100" r="39" fill="none" stroke="#FACC15" strokeWidth="2.2" />
        <circle cx="100" cy="100" r="34" fill="none" stroke="#FEF9C3" strokeWidth="1.2" opacity="0.9" strokeDasharray="3 2" />

        {/* Center Golden Hub */}
        <circle cx="100" cy="100" r="26" fill="url(#chakraHubGrad)" stroke="#CA8A04" strokeWidth="1.5" />

        {/* Center Sacred Spoke Lines */}
        {[0, 45, 90, 135].map((a) => (
          <line 
            key={a} 
            x1="100" 
            y1="76" 
            x2="100" 
            y2="124" 
            stroke="#CA8A04" 
            strokeWidth="1.2" 
            opacity="0.4" 
            transform={`rotate(${a} 100 100)`} 
          />
        ))}

        {/* Bright Center Diamond Specular Dot */}
        <circle cx="100" cy="100" r="6.5" fill="#FFFFFF" stroke="#EAB308" strokeWidth="1.2" />
        <circle cx="100" cy="100" r="3" fill="#FEF08A" />
      </svg>

      <style>{`
        @keyframes chakraSpin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes chakraGlow {
          0% { opacity: 0.65; transform: scale(0.95); }
          100% { opacity: 1; transform: scale(1.06); }
        }
        @keyframes chakraShinePulse {
          0%, 100% { opacity: 0.5; transform: scale(0.98); }
          50% { opacity: 0.85; transform: scale(1.02); }
        }
      `}</style>
    </div>
  );
}
