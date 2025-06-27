import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  // Base configurations
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  
  // Prettier integration
  ...compat.extends("prettier"),
  
  {
    rules: {
      // TypeScript specific rules
      "@typescript-eslint/no-unused-vars": [
        "error",
        { 
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          ignoreRestSiblings: true
        }
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-non-null-assertion": "warn",
      
      // React/Next.js optimization
      "react-hooks/exhaustive-deps": "warn",
      "react/no-unescaped-entities": "off",
      "react/display-name": "off",
      "react/prop-types": "off",
      
      // Import organization
      "import/order": [
        "error",
        {
          groups: [
            "builtin",   // Node.js modules
            "external",  // npm packages
            "internal",  // Absolute imports
            "parent",    // Relative parent imports
            "sibling",   // Relative sibling imports
            "index"      // Index imports
          ],
          "newlines-between": "always",
          alphabetize: {
            order: "asc",
            caseInsensitive: true
          }
        }
      ],
      "import/no-duplicates": "error",
      "import/no-unused-modules": "warn",
      
      // General code quality
      "prefer-const": "error",
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-debugger": "error",
      "no-alert": "error",
      "no-var": "error",
      "object-shorthand": "error",
      "prefer-template": "error",
      
      // Accessibility
      "jsx-a11y/alt-text": "error",
      "jsx-a11y/anchor-has-content": "error",
      "jsx-a11y/anchor-is-valid": "error",
      "jsx-a11y/aria-props": "error",
      "jsx-a11y/aria-proptypes": "error",
      "jsx-a11y/aria-unsupported-elements": "error",
      "jsx-a11y/role-has-required-aria-props": "error",
      "jsx-a11y/role-supports-aria-props": "error",
      
      // Performance
      "react/jsx-no-bind": ["warn", {
        "allowArrowFunctions": true,
        "allowFunctions": false,
        "allowBind": false
      }],
      
      // Code style (handled by Prettier, but some logical rules)
      "prefer-arrow-callback": "error",
      "arrow-body-style": ["error", "as-needed"]
    }
  },
  
  {
    files: ["**/*.test.{ts,tsx}", "**/*.spec.{ts,tsx}"],
    rules: {
      // More relaxed rules for test files
      "@typescript-eslint/no-explicit-any": "off",
      "no-console": "off"
    }
  }
];

export default eslintConfig;
