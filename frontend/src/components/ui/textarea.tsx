import * as React from "react"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  hint?: string
  showCharCount?: boolean
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, hint, showCharCount, maxLength, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false)
    const [charCount, setCharCount] = React.useState(0)
    
    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setCharCount(e.target.value.length)
      props.onChange?.(e)
    }
    
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-foreground mb-2">
            {label}
            {props.required && <span className="text-destructive ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          <textarea
            className={cn(
              "flex min-h-[120px] w-full rounded-lg border bg-background px-4 py-3 text-sm",
              "transition-all duration-200 ease-in-out resize-none",
              "placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "hover:border-muted-foreground/50",
              "scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent",
              error && "border-destructive focus:ring-destructive/20",
              isFocused && !error && "border-primary shadow-soft",
              className
            )}
            ref={ref}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onChange={handleChange}
            maxLength={maxLength}
            {...props}
          />
          
          {/* Animated border glow */}
          {isFocused && (
            <motion.div
              className="absolute inset-0 rounded-lg pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="absolute inset-0 rounded-lg bg-primary/5" />
            </motion.div>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-1.5">
          <div>
            {hint && !error && (
              <p className="text-sm text-muted-foreground">{hint}</p>
            )}
            
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-destructive"
              >
                {error}
              </motion.p>
            )}
          </div>
          
          {showCharCount && maxLength && (
            <span className={cn(
              "text-xs",
              charCount > maxLength * 0.9 ? "text-destructive" : "text-muted-foreground"
            )}>
              {charCount}/{maxLength}
            </span>
          )}
        </div>
      </div>
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }