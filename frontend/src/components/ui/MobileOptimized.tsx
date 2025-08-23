import React, { useState, useRef, useEffect } from 'react';
import { motion, PanInfo, useMotionValue, useTransform, useSpring, AnimatePresence } from 'framer-motion';
import { useMediaQuery } from '../../hooks/useMediaQuery';

// Swipeable card component
interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number;
  className?: string;
  disabled?: boolean;
}

export const SwipeableCard: React.FC<SwipeableCardProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 100,
  className = '',
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-15, 15]);
  const opacity = useTransform(x, [-200, 200], [0.8, 0.8]);
  
  const springConfig = { stiffness: 300, damping: 30 };
  const springX = useSpring(x, springConfig);
  const springY = useSpring(y, springConfig);

  const handleDragStart = () => {
    if (disabled) return;
    setIsDragging(true);
  };

  const handleDragEnd = (event: any, info: PanInfo) => {
    if (disabled) return;
    
    setIsDragging(false);
    const { offset, velocity } = info;
    
    // Check if swipe meets threshold
    if (Math.abs(offset.x) > threshold || Math.abs(offset.y) > threshold) {
      if (Math.abs(offset.x) > Math.abs(offset.y)) {
        // Horizontal swipe
        if (offset.x > 0 && onSwipeRight) {
          onSwipeRight();
        } else if (offset.x < 0 && onSwipeLeft) {
          onSwipeLeft();
        }
      } else {
        // Vertical swipe
        if (offset.y > 0 && onSwipeDown) {
          onSwipeDown();
        } else if (offset.y < 0 && onSwipeUp) {
          onSwipeUp();
        }
      }
    }
    
    // Reset position
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      className={`relative ${className}`}
      drag={!disabled}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.1}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      style={{
        x: springX,
        y: springY,
        rotate,
        opacity,
        cursor: disabled ? 'default' : isDragging ? 'grabbing' : 'grab',
      }}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
    >
      {children}
      
      {/* Swipe indicators */}
      {!disabled && (
        <div className="absolute inset-0 pointer-events-none">
          <motion.div
            className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-500 opacity-0"
            style={{ opacity: useTransform(x, [0, 50], [0, 0.5]) }}
          >
            ✓
          </motion.div>
          <motion.div
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-red-500 opacity-0"
            style={{ opacity: useTransform(x, [0, -50], [0, 0.5]) }}
          >
            ✗
          </motion.div>
        </div>
      )}
    </motion.div>
  );
};

// Pull to refresh component
interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
  threshold?: number;
  className?: string;
}

export const PullToRefresh: React.FC<PullToRefreshProps> = ({
  onRefresh,
  children,
  threshold = 80,
  className = '',
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullProgress, setPullProgress] = useState(0);
  const y = useMotionValue(0);
  const rotate = useTransform(y, [0, threshold], [0, 180]);
  const scale = useTransform(y, [0, threshold], [0.8, 1]);

  const handleDragEnd = async (event: any, info: PanInfo) => {
    if (info.offset.y > threshold && !isRefreshing) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
      }
    }
    y.set(0);
    setPullProgress(0);
  };

  const handleDrag = (event: any, info: PanInfo) => {
    if (info.offset.y > 0) {
      setPullProgress(Math.min(info.offset.y / threshold, 1));
    }
  };

  return (
    <motion.div
      className={`relative overflow-hidden ${className}`}
      drag="y"
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={0.1}
      onDrag={handleDrag}
      onDragEnd={handleDragEnd}
      style={{ y }}
    >
      {/* Pull indicator */}
      <motion.div
        className="absolute top-0 left-0 right-0 flex items-center justify-center py-4 bg-gray-50"
        style={{
          opacity: pullProgress,
          y: useTransform(y, [0, threshold], [-50, 0]),
        }}
      >
        <motion.div
          className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full"
          style={{ rotate, scale }}
          animate={isRefreshing ? { rotate: 360 } : {}}
          transition={isRefreshing ? { duration: 1, repeat: Infinity, ease: 'linear' } : {}}
        />
        <span className="ml-2 text-sm text-gray-600">
          {isRefreshing ? 'Refreshing...' : 'Pull to refresh'}
        </span>
      </motion.div>

      {children}
    </motion.div>
  );
};

// Touch-friendly list item
interface TouchListItemProps {
  children: React.ReactNode;
  onTap?: () => void;
  onLongPress?: () => void;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
  disabled?: boolean;
}

export const TouchListItem: React.FC<TouchListItemProps> = ({
  children,
  onTap,
  onLongPress,
  onSwipeLeft,
  onSwipeRight,
  className = '',
  disabled = false,
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [longPressTimer, setLongPressTimer] = useState<ReturnType<typeof setTimeout> | null>(null);
  const x = useMotionValue(0);
  const opacity = useTransform(x, [-100, 100], [0.8, 0.8]);

  const handleTouchStart = () => {
    if (disabled) return;
    
    setIsPressed(true);
    
    // Start long press timer
    const timer = setTimeout(() => {
      if (onLongPress) {
        onLongPress();
      }
    }, 500);
    
    setLongPressTimer(timer);
  };

  const handleTouchEnd = () => {
    if (disabled) return;
    
    setIsPressed(false);
    
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
  };

  const handleTap = () => {
    if (disabled || !onTap) return;
    onTap();
  };

  const handleDragEnd = (event: any, info: PanInfo) => {
    if (disabled) return;
    
    const { offset } = info;
    if (Math.abs(offset.x) > 50) {
      if (offset.x > 0 && onSwipeRight) {
        onSwipeRight();
      } else if (offset.x < 0 && onSwipeLeft) {
        onSwipeLeft();
      }
    }
    
    x.set(0);
  };

  return (
    <motion.div
      className={`relative ${className}`}
      style={{ x, opacity }}
      onTapStart={handleTouchStart}
      onClick={handleTap}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.1}
      onDragEnd={handleDragEnd}
      whileHover={!disabled ? { scale: 1.01 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      animate={{
        scale: isPressed ? 0.98 : 1,
        backgroundColor: isPressed ? 'rgba(0, 0, 0, 0.05)' : 'rgba(0, 0, 0, 0)',
      }}
      transition={{ duration: 0.1 }}
    >
      {children}
    </motion.div>
  );
};

// Mobile-optimized bottom sheet
interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  className?: string;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
  isOpen,
  onClose,
  children,
  title,
  className = '',
}) => {
  const y = useMotionValue(0);
  const opacity = useTransform(y, [0, 100], [1, 0]);

  const handleDragEnd = (event: any, info: PanInfo) => {
    if (info.offset.y > 100) {
      onClose();
    }
    y.set(0);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          
          {/* Bottom sheet */}
          <motion.div
            className={`fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl z-50 ${className}`}
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.1}
            onDragEnd={handleDragEnd}
            style={{ y, opacity }}
          >
            {/* Handle */}
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-12 h-1 bg-gray-300 rounded-full" />
            </div>
            
            {/* Header */}
            {title && (
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              </div>
            )}
            
            {/* Content */}
            <div className="px-6 py-4 max-h-[80vh] overflow-y-auto">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// Mobile-optimized floating action button
interface FloatingActionButtonProps {
  icon: React.ReactNode;
  onClick: () => void;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  icon,
  onClick,
  position = 'bottom-right',
  size = 'md',
  className = '',
}) => {
  const isMobile = useMediaQuery('(max-width: 768px)');
  
  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  };

  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-14 h-14',
    lg: 'w-16 h-16',
  };

  return (
    <motion.button
      className={`fixed ${positionClasses[position]} ${sizeClasses[size]} rounded-full bg-blue-600 text-white shadow-2xl z-50 flex items-center justify-center ${className}`}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      onClick={onClick}
      style={{
        touchAction: 'manipulation',
      }}
    >
      <motion.div
        animate={isMobile ? { rotate: [0, 10, -10, 0] } : {}}
        transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
      >
        {icon}
      </motion.div>
    </motion.button>
  );
};

// Mobile-optimized gesture handler
interface GestureHandlerProps {
  children: React.ReactNode;
  onSwipe?: (direction: 'left' | 'right' | 'up' | 'down') => void;
  onPinch?: (scale: number) => void;
  onRotate?: (rotation: number) => void;
  className?: string;
}

export const GestureHandler: React.FC<GestureHandlerProps> = ({
  children,
  onSwipe,
  onPinch,
  onRotate,
  className = '',
}) => {
  const [gesture, setGesture] = useState({ scale: 1, rotation: 0 });
  
  // Touch gesture handling
  const handleTouchStart = (event: React.TouchEvent) => {
    if (event.touches.length === 2) {
      // Two finger gesture
      const touch1 = event.touches[0];
      const touch2 = event.touches[1];
      
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      
      const angle = Math.atan2(
        touch2.clientY - touch1.clientY,
        touch2.clientX - touch1.clientX
      );
      
      setGesture({ scale: distance / 100, rotation: angle });
    }
  };

  const handleTouchMove = (event: React.TouchEvent) => {
    if (event.touches.length === 2) {
      const touch1 = event.touches[0];
      const touch2 = event.touches[1];
      
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      
      const angle = Math.atan2(
        touch2.clientY - touch1.clientY,
        touch2.clientX - touch1.clientX
      );
      
      const newScale = distance / 100;
      const newRotation = angle;
      
      if (onPinch) onPinch(newScale);
      if (onRotate) onRotate(newRotation);
      
      setGesture({ scale: newScale, rotation: newRotation });
    }
  };

  return (
    <div
      className={`touch-manipulation ${className}`}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      style={{
        touchAction: 'none',
        userSelect: 'none',
        WebkitUserSelect: 'none',
      }}
    >
      <motion.div
        style={{
          scale: gesture.scale,
          rotate: gesture.rotation * (180 / Math.PI),
        }}
        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
      >
        {children}
      </motion.div>
    </div>
  );
};
