/**
 * Authentication Types for Reply Pass
 * Compatible with Supabase Auth and Next.js 15
 */

import type { User as SupabaseUser, Session } from "@supabase/supabase-js";

/**
 * Extended user type based on Supabase User
 */
export interface User extends SupabaseUser {
  // Supabase user already has all required fields
  // id, email, user_metadata, app_metadata, etc.
}

/**
 * Authentication state interface
 */
export interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  initialized: boolean;
}

/**
 * Authentication actions interface
 */
export interface AuthActions {
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>;
  signUp: (email: string, password: string) => Promise<{ error: Error | null }>;
  signOut: () => Promise<{ error: Error | null }>;
  resetPassword: (email: string) => Promise<{ error: Error | null }>;
  setUser: (user: User | null) => void;
  setSession: (session: Session | null) => void;
  setLoading: (loading: boolean) => void;
  initialize: () => Promise<void>;
}

/**
 * Combined auth store interface
 */
export interface AuthStore extends AuthState, AuthActions {}

/**
 * Auth context value interface
 */
export interface AuthContextValue {
  // Supabase client instance will be provided via context
  // State management will be handled by Zustand
}
