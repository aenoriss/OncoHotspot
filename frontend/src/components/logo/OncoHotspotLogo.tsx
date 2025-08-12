import React from 'react';

interface OncoHotspotLogoProps {
  size?: number;
  variant?: 'full' | 'icon';
}

const OncoHotspotLogo: React.FC<OncoHotspotLogoProps> = ({ 
  size = 32, 
  variant = 'icon' 
}) => {
  // Icon-only version for favicon and small displays
  if (variant === 'icon') {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Background circle */}
        <circle cx="32" cy="32" r="30" fill="#1976d2" opacity="0.1" />
        
        {/* DNA helix-inspired grid pattern */}
        <g opacity="0.8">
          {/* Vertical strands */}
          <rect x="16" y="12" width="4" height="40" rx="2" fill="#1976d2" />
          <rect x="44" y="12" width="4" height="40" rx="2" fill="#1976d2" />
          
          {/* Horizontal connections representing mutation hotspots */}
          <rect x="20" y="18" width="24" height="4" rx="2" fill="#ffeb3b" />
          <rect x="20" y="26" width="24" height="4" rx="2" fill="#ff9800" />
          <rect x="20" y="34" width="24" height="4" rx="2" fill="#d32f2f" />
          <rect x="20" y="42" width="24" height="4" rx="2" fill="#ff9800" />
        </g>
        
        {/* Center hotspot indicator */}
        <circle cx="32" cy="32" r="8" fill="#d32f2f" opacity="0.9" />
        <circle cx="32" cy="32" r="4" fill="#ffffff" />
        
        {/* Small mutation dots */}
        <circle cx="24" cy="20" r="2" fill="#1976d2" />
        <circle cx="40" cy="20" r="2" fill="#1976d2" />
        <circle cx="24" cy="44" r="2" fill="#1976d2" />
        <circle cx="40" cy="44" r="2" fill="#1976d2" />
      </svg>
    );
  }

  // Full version with text for navbar
  return (
    <svg
      width={size * 5}
      height={size}
      viewBox="0 0 160 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Icon part */}
      <g transform="scale(0.5)">
        {/* Background circle */}
        <circle cx="32" cy="32" r="30" fill="#1976d2" opacity="0.1" />
        
        {/* DNA helix-inspired grid pattern */}
        <g opacity="0.8">
          {/* Vertical strands */}
          <rect x="16" y="12" width="4" height="40" rx="2" fill="#1976d2" />
          <rect x="44" y="12" width="4" height="40" rx="2" fill="#1976d2" />
          
          {/* Horizontal connections representing mutation hotspots */}
          <rect x="20" y="18" width="24" height="4" rx="2" fill="#ffeb3b" />
          <rect x="20" y="26" width="24" height="4" rx="2" fill="#ff9800" />
          <rect x="20" y="34" width="24" height="4" rx="2" fill="#d32f2f" />
          <rect x="20" y="42" width="24" height="4" rx="2" fill="#ff9800" />
        </g>
        
        {/* Center hotspot indicator */}
        <circle cx="32" cy="32" r="8" fill="#d32f2f" opacity="0.9" />
        <circle cx="32" cy="32" r="4" fill="#ffffff" />
        
        {/* Small mutation dots */}
        <circle cx="24" cy="20" r="2" fill="#1976d2" />
        <circle cx="40" cy="20" r="2" fill="#1976d2" />
        <circle cx="24" cy="44" r="2" fill="#1976d2" />
        <circle cx="40" cy="44" r="2" fill="#1976d2" />
      </g>
      
      {/* Text part */}
      <text
        x="40"
        y="20"
        fontFamily="Inter, Arial, sans-serif"
        fontSize="18"
        fontWeight="700"
        fill="#212121"
      >
        OncoHotspot
      </text>
    </svg>
  );
};

export default OncoHotspotLogo;