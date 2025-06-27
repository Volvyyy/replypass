/**
 * Password Strength Indicator Component
 * Following 2025 UX best practices with accessibility and real-time validation
 *
 * @description Real-time password strength visualization with comprehensive feedback
 * @accessibility WCAG 2.1 AA compliant with screen reader support
 * @security Client-side validation only - never sends passwords to external services
 */

"use client";

import { useMemo } from "react";

import { cn } from "@/lib/utils";

interface PasswordStrengthProps {
  password: string;
  className?: string;
  showCriteria?: boolean;
  ariaLabel?: string;
}

interface StrengthResult {
  score: number; // 0-4 (Very Weak to Very Strong)
  feedback: string;
  color: string;
  bgColor: string;
  percentage: number;
  criteria: CriteriaResult[];
}

interface CriteriaResult {
  label: string;
  met: boolean;
  description: string;
}

/**
 * Calculate password strength based on comprehensive criteria
 * Uses modern security guidelines (NIST SP 800-63B, OWASP 2024)
 */
const calculatePasswordStrength = (password: string): StrengthResult => {
  if (!password) {
    return {
      score: 0,
      feedback: "パスワードを入力してください",
      color: "text-muted-foreground",
      bgColor: "bg-muted",
      percentage: 0,
      criteria: getCriteria(password),
    };
  }

  const criteria = getCriteria(password);
  const metCriteria = criteria.filter((c) => c.met).length;
  const totalCriteria = criteria.length;

  // Enhanced scoring algorithm
  let score = 0;
  let feedback = "";
  let color = "";
  let bgColor = "";

  // Base scoring on criteria completion
  const completionRatio = metCriteria / totalCriteria;

  // Additional scoring factors
  const hasVariety = [
    /[a-z]/.test(password), // lowercase
    /[A-Z]/.test(password), // uppercase
    /\d/.test(password), // digits
    /[^a-zA-Z\d]/.test(password), // special chars
  ].filter(Boolean).length;

  const entropyBonus = Math.min(password.length / 12, 1); // Length entropy
  const varietyBonus = hasVariety / 4; // Character variety

  // Calculate final score (0-4)
  const rawScore =
    completionRatio * 0.6 + entropyBonus * 0.2 + varietyBonus * 0.2;
  score = Math.floor(rawScore * 4);

  // Ensure minimum requirements for higher scores
  if (password.length < 8) score = Math.min(score, 1);
  if (hasVariety < 3) score = Math.min(score, 2);

  // Set feedback and colors based on score
  switch (score) {
    case 0:
      feedback = "非常に弱い";
      color = "text-red-600";
      bgColor = "bg-red-500";
      break;
    case 1:
      feedback = "弱い";
      color = "text-orange-600";
      bgColor = "bg-orange-500";
      break;
    case 2:
      feedback = "普通";
      color = "text-yellow-600";
      bgColor = "bg-yellow-500";
      break;
    case 3:
      feedback = "強い";
      color = "text-blue-600";
      bgColor = "bg-blue-500";
      break;
    case 4:
      feedback = "非常に強い";
      color = "text-green-600";
      bgColor = "bg-green-500";
      break;
    default:
      feedback = "評価中";
      color = "text-muted-foreground";
      bgColor = "bg-muted";
  }

  return {
    score,
    feedback,
    color,
    bgColor,
    percentage: Math.max((score / 4) * 100, password.length > 0 ? 10 : 0),
    criteria,
  };
};

/**
 * Get password strength criteria with status
 */
const getCriteria = (password: string): CriteriaResult[] => [
  {
    label: "8文字以上",
    met: password.length >= 8,
    description: "最低8文字の長さが必要です",
  },
  {
    label: "小文字を含む",
    met: /[a-z]/.test(password),
    description: "小文字 (a-z) を含める必要があります",
  },
  {
    label: "大文字を含む",
    met: /[A-Z]/.test(password),
    description: "大文字 (A-Z) を含める必要があります",
  },
  {
    label: "数字を含む",
    met: /\d/.test(password),
    description: "数字 (0-9) を含める必要があります",
  },
  {
    label: "特殊文字を含む",
    met: /[^a-zA-Z\d]/.test(password),
    description: "記号や特殊文字 (!@#$%^&* など) を含めることを推奨します",
  },
  {
    label: "12文字以上推奨",
    met: password.length >= 12,
    description: "より高いセキュリティのため12文字以上を推奨します",
  },
];

/**
 * Password Strength Indicator Component
 */
export function PasswordStrength({
  password,
  className,
  showCriteria = true,
  ariaLabel = "パスワード強度インジケーター",
}: PasswordStrengthProps) {
  const strength = useMemo(
    () => calculatePasswordStrength(password),
    [password]
  );

  return (
    <div className={cn("space-y-3", className)}>
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground text-sm font-medium">
            パスワード強度
          </span>
          <span className={cn("text-sm font-semibold", strength.color)}>
            {strength.feedback}
          </span>
        </div>

        <div
          className="bg-muted relative h-2 overflow-hidden rounded-full"
          role="progressbar"
          aria-label={ariaLabel}
          aria-valuenow={strength.score}
          aria-valuemin={0}
          aria-valuemax={4}
          aria-valuetext={`${strength.feedback}, ${strength.score + 1}/5レベル`}
        >
          <div
            className={cn(
              "h-full rounded-full transition-all duration-300 ease-out",
              strength.bgColor
            )}
            style={{ width: `${strength.percentage}%` }}
          />
        </div>
      </div>

      {/* Criteria List */}
      {showCriteria && password && (
        <div className="space-y-2">
          <p className="text-muted-foreground text-sm font-medium">
            パスワード要件:
          </p>
          <ul className="space-y-1" role="list">
            {strength.criteria.map((criterion, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm"
                role="listitem"
              >
                <span
                  className={cn(
                    "mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold",
                    criterion.met
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-muted text-muted-foreground"
                  )}
                  aria-hidden="true"
                >
                  {criterion.met ? "✓" : "○"}
                </span>
                <span
                  className={cn(
                    "flex-1",
                    criterion.met
                      ? "text-green-700 dark:text-green-400"
                      : "text-muted-foreground"
                  )}
                  title={criterion.description}
                >
                  {criterion.label}
                </span>
                <span className="sr-only">
                  {criterion.met
                    ? "条件を満たしています"
                    : "条件を満たしていません"}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Security Tips */}
      {password && strength.score < 3 && (
        <div className="rounded-md border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-950/30">
          <div className="flex items-start gap-2">
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
              💡 ヒント:
            </span>
            <div className="text-sm text-blue-700 dark:text-blue-300">
              {strength.score === 0 &&
                "パスワードは大文字、小文字、数字を組み合わせて8文字以上にしてください。"}
              {strength.score === 1 &&
                "文字の種類を増やし、長さを12文字以上にすることでセキュリティが向上します。"}
              {strength.score === 2 &&
                "特殊文字を追加し、長さを増やすとより安全になります。"}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact version for inline use
 */
export function PasswordStrengthCompact({
  password,
  className,
}: Pick<PasswordStrengthProps, "password" | "className">) {
  const strength = useMemo(
    () => calculatePasswordStrength(password),
    [password]
  );

  if (!password) return null;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="bg-muted h-1 flex-1 overflow-hidden rounded-full">
        <div
          className={cn(
            "h-full transition-all duration-300 ease-out",
            strength.bgColor
          )}
          style={{ width: `${strength.percentage}%` }}
        />
      </div>
      <span className={cn("text-xs font-medium", strength.color)}>
        {strength.feedback}
      </span>
    </div>
  );
}

export default PasswordStrength;
