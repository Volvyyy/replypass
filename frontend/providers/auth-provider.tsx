/**
 * Authentication Provider for Reply Pass
 * Compatible with Supabase Auth, Next.js 15, and React 19
 *
 * @description Provides Supabase client and manages authentication state
 * @security Handles authentication events and state synchronization
 */

"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { useAuthStore } from "@/lib/store/auth-store";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { User } from "@/types/auth";

interface AuthContextValue {
  supabase: SupabaseClient;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [supabase] = useState(() => createClient());
  const { setUser, setSession, setLoading, initialize } = useAuthStore();

  useEffect(() => {
    // Initialize auth state
    const initializeAuth = async () => {
      setLoading(true);

      try {
        // Get initial session
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          console.error("Error getting session:", error.message);
        } else {
          setSession(session);
          setUser(session?.user as User | null);
        }

        await initialize();
      } catch (error) {
        console.error("Auth initialization failed:", error);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log("Auth state changed:", event, session?.user?.email);

      setSession(session);
      setUser(session?.user as User | null);
      setLoading(false);

      // Handle specific auth events
      switch (event) {
        case "SIGNED_IN":
          console.log("User signed in:", session?.user?.email);
          break;
        case "SIGNED_OUT":
          console.log("User signed out");
          setUser(null);
          setSession(null);
          break;
        case "TOKEN_REFRESHED":
          console.log("Token refreshed for user:", session?.user?.email);
          break;
        case "USER_UPDATED":
          console.log("User updated:", session?.user?.email);
          break;
        default:
          break;
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase, setUser, setSession, setLoading, initialize]);

  const value = {
    supabase,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useSupabase() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useSupabase must be used within an AuthProvider");
  }

  return context;
}
