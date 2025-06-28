/**
 * Authentication Hook for Reply Pass
 * Compatible with Supabase Auth and Zustand store
 *
 * @description Custom hook that combines Supabase client and Zustand store
 * @security Provides secure authentication methods and state access
 */

"use client";

import { useCallback } from "react";
import { useSupabase } from "@/providers/auth-provider";
import { useAuthStore } from "@/lib/store/auth-store";
import type { User } from "@/types/auth";

export function useAuth() {
  const { supabase } = useSupabase();
  const {
    user,
    session,
    loading,
    initialized,
    setUser,
    setSession,
    setLoading,
  } = useAuthStore();

  /**
   * Sign in with email and password
   */
  const signIn = useCallback(
    async (email: string, password: string) => {
      setLoading(true);

      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) {
          console.error("Sign in error:", error.message);
          return { error };
        }

        // State will be updated via onAuthStateChange listener
        console.log("Sign in successful:", data.user?.email);
        return { error: null };
      } catch (error) {
        console.error("Sign in failed:", error);
        return { error: error as Error };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading]
  );

  /**
   * Sign up with email and password
   */
  const signUp = useCallback(
    async (email: string, password: string) => {
      setLoading(true);

      try {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });

        if (error) {
          console.error("Sign up error:", error.message);
          return { error };
        }

        console.log("Sign up successful:", data.user?.email);
        return { error: null };
      } catch (error) {
        console.error("Sign up failed:", error);
        return { error: error as Error };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading]
  );

  /**
   * Sign out current user
   */
  const signOut = useCallback(async () => {
    setLoading(true);

    try {
      const { error } = await supabase.auth.signOut();

      if (error) {
        console.error("Sign out error:", error.message);
        return { error };
      }

      // Clear state immediately (also handled by onAuthStateChange)
      setUser(null);
      setSession(null);

      console.log("Sign out successful");
      return { error: null };
    } catch (error) {
      console.error("Sign out failed:", error);
      return { error: error as Error };
    } finally {
      setLoading(false);
    }
  }, [supabase, setUser, setSession, setLoading]);

  /**
   * Reset password for email
   */
  const resetPassword = useCallback(
    async (email: string) => {
      setLoading(true);

      try {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/auth/confirm?next=/auth/update-password`,
        });

        if (error) {
          console.error("Reset password error:", error.message);
          return { error };
        }

        console.log("Reset password email sent to:", email);
        return { error: null };
      } catch (error) {
        console.error("Reset password failed:", error);
        return { error: error as Error };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading]
  );

  /**
   * Update user password
   */
  const updatePassword = useCallback(
    async (password: string) => {
      setLoading(true);

      try {
        const { error } = await supabase.auth.updateUser({
          password,
        });

        if (error) {
          console.error("Update password error:", error.message);
          return { error };
        }

        console.log("Password updated successfully");
        return { error: null };
      } catch (error) {
        console.error("Update password failed:", error);
        return { error: error as Error };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading]
  );

  /**
   * Get current user profile
   */
  const getCurrentUser = useCallback(async (): Promise<User | null> => {
    try {
      const {
        data: { user },
        error,
      } = await supabase.auth.getUser();

      if (error) {
        console.error("Get user error:", error.message);
        return null;
      }

      return user as User;
    } catch (error) {
      console.error("Get user failed:", error);
      return null;
    }
  }, [supabase]);

  /**
   * Check if user is authenticated
   */
  const isAuthenticated = Boolean(user && session);

  /**
   * Check if user email is verified
   */
  const isEmailVerified = Boolean(user?.email_confirmed_at);

  return {
    // State
    user,
    session,
    loading,
    initialized,
    isAuthenticated,
    isEmailVerified,

    // Actions
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    getCurrentUser,
  };
}
