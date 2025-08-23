import React, { useState } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { Card } from './Card';

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverEffect?: 'lift' | 'scale' | 'glow' | 'tilt';
  delay?: number;
  duration?: number;
  interactive?: boolean;
  variant?: 'default' | 'elevated' | 'glass' | 'gradient';
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className = '',
  onClick,
  hoverEffect = 'lift',
  delay = 0,
  duration = 0.3,
  interactive = true,
  variant = 'default'
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  
  // Motion values for advanced effects
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const rotateX = useTransform(mouseY, [-300, 300], [15, -15]);
  const rotateY = useTransform(mouseX, [-300, 300], [-15, 15]);
  
  // Spring animations for smooth transitions
  const springConfig = { stiffness: 300, damping: 30 };
  const scale = useSpring(isHovered ? 1.02 : 1, springConfig);
  const y = useSpring(isHovered ? -8 : 0, springConfig);
  const shadow = useSpring(isHovered ? 24 : 8, springConfig);
  const glow = useSpring(isHovered ? 1 : 0, springConfig);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (hoverEffect === 'tilt' && interactive) {
      const rect = event.currentTarget.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      mouseX.set(event.clientX - centerX);
      mouseY.set(event.clientY - centerY);
    }
  };

  const handleMouseLeave = () => {
    if (hoverEffect === 'tilt') {
      mouseX.set(0);
      mouseY.set(0);
    }
  };

  const getVariantStyles = () => {
    let baseStyles = '';
    switch (variant) {
      case 'elevated':
        baseStyles = 'bg-white border-0 shadow-lg';
        break;
      case 'glass':
        baseStyles = 'bg-white/80 backdrop-blur-md border border-white/20 shadow-lg';
        break;
      case 'gradient':
        baseStyles = 'bg-gradient-to-br from-white to-gray-50 border-0 shadow-lg';
        break;
      default:
        baseStyles = 'bg-white border border-gray-200 shadow-sm';
    }
    
    if (interactive) {
      baseStyles += ' cursor-pointer';
    }
    
    return baseStyles;
  };

  const getHoverEffect = () => {
    switch (hoverEffect) {
      case 'lift':
        return {
          scale: isHovered ? 1.02 : 1,
          y: isHovered ? -8 : 0,
          boxShadow: `0 ${isHovered ? 24 : 8}px 40px rgba(0, 0, 0, 0.12)`,
        };
      case 'scale':
        return {
          scale: isHovered ? 1.02 : 1,
          boxShadow: `0 ${isHovered ? 24 : 8}px 40px rgba(0, 0, 0, 0.12)`,
        };
      case 'glow':
        return {
          scale: isHovered ? 1.02 : 1,
          boxShadow: `0 8px 32px rgba(0, 102, 255, ${isHovered ? 0.3 : 0})`,
        };
      case 'tilt':
        return {
          scale: isHovered ? 1.02 : 1,
          rotateX: isHovered ? 15 : 0,
          rotateY: isHovered ? -15 : 0,
          boxShadow: `0 ${isHovered ? 24 : 8}px 40px rgba(0, 0, 0, 0.12)`,
        };
      default:
        return {};
    }
  };

  const getPressEffect = () => {
    if (!interactive) return {};
    
    return {
      scale: isPressed ? 0.98 : 1,
      y: isPressed ? -2 : 0,
    };
  };

  return (
    <motion.div
      className={`${getVariantStyles()} ${className}`}
      style={{
        transformStyle: 'preserve-3d',
        perspective: 1000,
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration, delay, ease: 'easeOut' }}
      whileHover={interactive ? getHoverEffect() : {}}
      whileTap={interactive ? getPressEffect() : {}}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onTapStart={() => setIsPressed(true)}
      onClick={onClick}
    >
      {/* Glow effect overlay */}
      {hoverEffect === 'glow' && (
        <motion.div
          className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-400/20 to-purple-400/20 opacity-0"
          style={{ opacity: glow }}
          initial={false}
        />
      )}
      
      {/* Content with 3D transform for tilt effect */}
      <motion.div
        style={{
          transformStyle: 'preserve-3d',
          z: isHovered ? 50 : 0,
        }}
        className="relative z-10"
      >
        {children}
      </motion.div>
      
      {/* Ripple effect on click */}
      <AnimatePresence>
        {isPressed && (
          <motion.div
            className="absolute inset-0 rounded-2xl bg-blue-500/20"
            initial={{ scale: 0, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Specialized animated card variants
export const ElevatedCard: React.FC<Omit<AnimatedCardProps, 'variant'> & { elevation?: 'low' | 'medium' | 'high' }> = ({
  elevation = 'medium',
  ...props
}) => {
  const elevationClasses = {
    low: 'shadow-md',
    medium: 'shadow-lg',
    high: 'shadow-2xl',
  };

  return (
    <AnimatedCard
      {...props}
      variant="elevated"
      className={`${elevationClasses[elevation]} ${props.className || ''}`}
      hoverEffect="lift"
    />
  );
};

export const GlassCard: React.FC<Omit<AnimatedCardProps, 'variant'>> = (props) => (
  <AnimatedCard
    {...props}
    variant="glass"
    hoverEffect="glow"
    className="backdrop-blur-md bg-white/80 border border-white/20"
  />
);

export const GradientCard: React.FC<Omit<AnimatedCardProps, 'variant'> & { 
  gradient?: 'blue' | 'purple' | 'green' | 'orange' 
}> = ({ gradient = 'blue', ...props }) => {
  const gradientClasses = {
    blue: 'from-blue-500/10 to-purple-500/10',
    purple: 'from-purple-500/10 to-pink-500/10',
    green: 'from-green-500/10 to-blue-500/10',
    orange: 'from-orange-500/10 to-red-500/10',
  };

  return (
    <AnimatedCard
      {...props}
      variant="gradient"
      className={`bg-gradient-to-br ${gradientClasses[gradient]} ${props.className || ''}`}
      hoverEffect="scale"
    />
  );
};
