import { motion, HTMLMotionProps } from "framer-motion"
import { cn } from "@/lib/utils"

// Fade In Animation
export function FadeIn({ 
  children, 
  className,
  delay = 0,
  duration = 0.3,
  ...props 
}: HTMLMotionProps<"div"> & { delay?: number; duration?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration, delay }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Slide In Animation
export function SlideIn({ 
  children, 
  className,
  direction = "up",
  delay = 0,
  duration = 0.3,
  ...props 
}: HTMLMotionProps<"div"> & { 
  direction?: "up" | "down" | "left" | "right"
  delay?: number
  duration?: number 
}) {
  const directionOffset = {
    up: { y: 20 },
    down: { y: -20 },
    left: { x: 20 },
    right: { x: -20 }
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, ...directionOffset[direction] }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      exit={{ opacity: 0, ...directionOffset[direction] }}
      transition={{ duration, delay, ease: "easeOut" }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Scale Animation
export function ScaleIn({ 
  children, 
  className,
  delay = 0,
  duration = 0.3,
  ...props 
}: HTMLMotionProps<"div"> & { delay?: number; duration?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration, delay, ease: "easeOut" }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Stagger Children Animation
export function StaggerChildren({ 
  children, 
  className,
  staggerDelay = 0.1,
  ...props 
}: HTMLMotionProps<"div"> & { staggerDelay?: number }) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      exit="hidden"
      variants={{
        visible: {
          transition: {
            staggerChildren: staggerDelay
          }
        }
      }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Stagger Item
export function StaggerItem({ 
  children, 
  className,
  ...props 
}: HTMLMotionProps<"div">) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
      }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Hover Scale Effect
export function HoverScale({ 
  children, 
  className,
  scale = 1.05,
  ...props 
}: HTMLMotionProps<"div"> & { scale?: number }) {
  return (
    <motion.div
      whileHover={{ scale }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={cn("cursor-pointer", className)}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Page Transition Wrapper
export function PageTransition({ 
  children, 
  className,
  ...props 
}: HTMLMotionProps<"div">) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4, ease: "easeInOut" }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Loading Skeleton Animation
export function Skeleton({ 
  className,
  ...props 
}: HTMLMotionProps<"div">) {
  return (
    <motion.div
      animate={{
        backgroundPosition: ["200% 0", "-200% 0"]
      }}
      transition={{
        duration: 1.5,
        ease: "linear",
        repeat: Infinity
      }}
      className={cn(
        "relative overflow-hidden rounded-md bg-muted",
        "before:absolute before:inset-0",
        "before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent",
        "before:translate-x-[-200%] before:animate-shimmer",
        className
      )}
      style={{
        backgroundImage: "linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)",
        backgroundSize: "200% 100%"
      }}
      {...props}
    />
  )
}