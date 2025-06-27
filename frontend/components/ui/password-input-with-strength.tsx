/**
 * Password Input with Strength Indicator
 * Integrated component for React Hook Form with Zod validation
 *
 * @description Complete password input solution with strength indicator
 * @integration Works seamlessly with React Hook Form and existing validation
 */

"use client";

import { Eye, EyeOff } from "lucide-react";
import { forwardRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  PasswordStrength,
  PasswordStrengthCompact,
} from "@/components/ui/password-strength";
import { cn } from "@/lib/utils";

interface PasswordInputWithStrengthProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  showStrengthIndicator?: boolean;
  compactStrength?: boolean;
  showToggle?: boolean;
  strengthClassName?: string;
}

/**
 * Password input with integrated strength indicator and show/hide toggle
 */
export const PasswordInputWithStrength = forwardRef<
  HTMLInputElement,
  PasswordInputWithStrengthProps
>(
  (
    {
      className,
      showStrengthIndicator = true,
      compactStrength = false,
      showToggle = true,
      strengthClassName,
      value = "",
      onChange,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const passwordValue = typeof value === "string" ? value : "";

    const togglePasswordVisibility = () => {
      setShowPassword(!showPassword);
    };

    return (
      <div className="space-y-2">
        {/* Password Input with Toggle */}
        <div className="relative">
          <Input
            {...props}
            ref={ref}
            type={showPassword ? "text" : "password"}
            className={cn("pr-10", className)}
            value={value}
            onChange={onChange}
          />
          {showToggle && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute top-0 right-0 h-full px-3 py-2 hover:bg-transparent"
              onClick={togglePasswordVisibility}
              aria-label={
                showPassword ? "パスワードを隠す" : "パスワードを表示"
              }
            >
              {showPassword ? (
                <EyeOff className="text-muted-foreground h-4 w-4" />
              ) : (
                <Eye className="text-muted-foreground h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        {/* Strength Indicator */}
        {showStrengthIndicator && passwordValue && (
          <div className={strengthClassName}>
            {compactStrength ? (
              <PasswordStrengthCompact password={passwordValue} />
            ) : (
              <PasswordStrength password={passwordValue} />
            )}
          </div>
        )}
      </div>
    );
  }
);

PasswordInputWithStrength.displayName = "PasswordInputWithStrength";

export default PasswordInputWithStrength;
