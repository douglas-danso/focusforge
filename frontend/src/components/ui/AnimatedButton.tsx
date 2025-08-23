import React, { useState, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { Button } from './Button';
import { Loader2 } from 'lucide-react';

interface AnimatedButtonProps {
  children: React.ReactNode;
  onClick?: () => void | Promise<void>;
  variant?: 'default' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  ripple?: boolean;
  hoverEffect?: 'scale' | 'lift' | 'glow' | 'bounce';
  className?: string;
  fullWidth?: boolean;
  success?: boolean;
  error?: boolean;
}

export const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  onClick,
  variant = 'default',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  ripple = true,
  hoverEffect = 'scale',
  className = '',
  fullWidth = false,
  success = false,
  error = false,
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [ripples, setRipples] = useState<Array<{ id: number; x: number; y: number }>>([]);
  const buttonRef = useRef<HTMLButtonElement>(null);
  
  // Motion values for advanced effects
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const scale = useSpring(isHovered ? 1.05 : 1, { stiffness: 400, damping: 25 });
  const y = useSpring(isHovered ? -2 : 0, { stiffness: 400, damping: 25 });
  const glow = useSpring(isHovered ? 1 : 0, { stiffness: 400, damping: 25 });

  const handleClick = async (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return;

    // Create ripple effect
    if (ripple && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      const newRipple = {
        id: Date.now(),
        x,
        y,
      };
      
      setRipples(prev => [...prev, newRipple]);
      
      // Remove ripple after animation
      setTimeout(() => {
        setRipples(prev => prev.filter(r => r.id !== newRipple.id));
      }, 600);
    }

    // Handle press state
    setIsPressed(true);
    setTimeout(() => setIsPressed(false), 150);

    // Execute onClick
    if (onClick) {
      try {
        await onClick();
      } catch (error) {
        console.error('Button click error:', error);
      }
    }
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      mouseX.set(event.clientX - rect.left);
      mouseY.set(event.clientY - rect.top);
    }
  };

  const getHoverEffect = () => {
    switch (hoverEffect) {
      case 'scale':
        return { scale: isHovered ? 1.05 : 1 };
      case 'lift':
        return { scale: isHovered ? 1.05 : 1, y: isHovered ? -2 : 0 };
      case 'glow':
        return { 
          scale: isHovered ? 1.05 : 1, 
          boxShadow: `0 8px 32px rgba(0, 102, 255, ${isHovered ? 0.4 : 0})` 
        };
      case 'bounce':
        return { 
          scale: isHovered ? 1.1 : 1,
          y: isHovered ? -4 : 0,
          transition: { type: 'spring', stiffness: 400, damping: 10 }
        };
      default:
        return {};
    }
  };

  const getButtonStyles = () => {
    let baseStyles = 'relative overflow-hidden transition-all duration-200';
    
    if (fullWidth) {
      baseStyles += ' w-full';
    }
    
    if (success) {
      baseStyles += ' bg-green-600 hover:bg-green-700 text-white';
    } else if (error) {
      baseStyles += ' bg-red-600 hover:bg-red-700 text-white';
    }
    
    return `${baseStyles} ${className}`;
  };

  const getIconStyles = () => {
    const iconSize = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5';
    return `${iconSize} ${iconPosition === 'right' ? 'ml-2' : 'mr-2'}`;
  };

  return (
    <motion.button
      ref={buttonRef}
      className={getButtonStyles()}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
      disabled={disabled || loading}
      whileHover={!disabled && !loading ? getHoverEffect() : {}}
      whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
      animate={{
        scale: isPressed ? 0.98 : 1,
        y: isPressed ? 0 : 0,
      }}
      transition={{ duration: 0.1 }}
    >
      {/* Background gradient for glow effect */}
      {hoverEffect === 'glow' && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 opacity-0 rounded-lg"
          style={{ opacity: glow }}
          initial={false}
        />
      )}
      
      {/* Content */}
      <div className="relative z-10 flex items-center justify-center">
        {loading ? (
          <Loader2 className={`${getIconStyles()} animate-spin`} />
        ) : (
          <>
            {icon && iconPosition === 'left' && (
              <span className={getIconStyles()}>{icon}</span>
            )}
            <span>{children}</span>
            {icon && iconPosition === 'right' && (
              <span className={getIconStyles()}>{icon}</span>
            )}
          </>
        )}
      </div>

      {/* Ripple effects */}
      <AnimatePresence>
        {ripples.map((ripple) => (
          <motion.div
            key={ripple.id}
            className="absolute bg-white/30 rounded-full pointer-events-none"
            style={{
              left: ripple.x,
              top: ripple.y,
              width: 0,
              height: 0,
            }}
            initial={{ scale: 0, opacity: 1 }}
            animate={{ scale: 4, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        ))}
      </AnimatePresence>

      {/* Success/Error state overlay */}
      <AnimatePresence>
        {success && (
          <motion.div
            className="absolute inset-0 bg-green-500/20 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 500 }}
              className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </motion.div>
          </motion.div>
        )}
        
        {error && (
          <motion.div
            className="absolute inset-0 bg-red-500/20 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 500 }}
              className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center"
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
};

// Specialized button variants
export const PrimaryButton: React.FC<Omit<AnimatedButtonProps, 'variant'> & { 
  gradient?: 'blue' | 'purple' | 'green' 
}> = ({ gradient = 'blue', ...props }) => {
  const gradientClasses = {
    blue: 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800',
    purple: 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800',
    green: 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800',
  };

  return (
    <AnimatedButton
      {...props}
      className={`${gradientClasses[gradient]} text-white border-0 ${props.className || ''}`}
      hoverEffect="glow"
    />
  );
};

export const FloatingButton: React.FC<Omit<AnimatedButtonProps, 'variant' | 'size'> & {
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
}> = ({ position = 'bottom-right', ...props }) => {
  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  };

  return (
    <motion.div
      className={`fixed ${positionClasses[position]} z-50`}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ delay: 0.5, type: 'spring', stiffness: 500 }}
    >
      <AnimatedButton
        {...props}
        size="lg"
        className="w-14 h-14 rounded-full shadow-2xl bg-blue-600 hover:bg-blue-700 text-white"
        hoverEffect="bounce"
      >
        {props.children}
      </AnimatedButton>
    </motion.div>
  );
};

export const IconButton: React.FC<Omit<AnimatedButtonProps, 'children' | 'size'> & {
  icon: React.ReactNode;
  tooltip?: string;
}> = ({ icon, tooltip, ...props }) => {
  return (
    <div className="relative group">
      <AnimatedButton
        {...props}
        size="sm"
        className="w-10 h-10 p-0 rounded-full flex items-center justify-center"
        hoverEffect="scale"
      >
        {icon}
      </AnimatedButton>
      
      {tooltip && (
        <motion.div
          className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 pointer-events-none whitespace-nowrap"
          initial={{ opacity: 0, y: 5 }}
          whileHover={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {tooltip}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
        </motion.div>
      )}
    </div>
  );
};
