/**
 * Authentication Confirmation Route Handler
 * 
 * @description Handles email confirmation and password recovery tokens
 * @security Validates tokens and prevents unauthorized access
 */

import { type EmailOtpType } from "@supabase/supabase-js";
import { redirect } from "next/navigation";
import { type NextRequest } from "next/server";

import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const token_hash = searchParams.get("token_hash");
  const type = searchParams.get("type") as EmailOtpType | null;
  const next = searchParams.get("next") ?? "/dashboard";

  // Validate required parameters
  if (!token_hash || !type) {
    console.error("Missing token_hash or type parameter");
    redirect("/auth/error?error=missing_parameters");
  }

  try {
    const supabase = await createClient();

    // Verify the OTP token
    const { error } = await supabase.auth.verifyOtp({
      type,
      token_hash,
    });

    if (error) {
      console.error("Token verification failed:", error.message);
      
      // Handle specific error types
      const errorCode = error.message.toLowerCase().includes("expired")
        ? "token_expired"
        : error.message.toLowerCase().includes("invalid")
        ? "invalid_token"
        : "verification_failed";
      
      redirect(`/auth/error?error=${errorCode}`);
    }

    // Successful verification - removed console.log for production

    // Handle different verification types
    switch (type) {
      case "signup":
        // Email confirmation for new user
        redirect("/dashboard?welcome=true");
        break;
        
      case "recovery":
        // Password recovery - redirect to update password page
        redirect("/auth/update-password");
        break;
        
      case "email_change":
        // Email change confirmation
        redirect("/settings?email_updated=true");
        break;
        
      case "invite":
        // Team invitation
        redirect("/dashboard?invited=true");
        break;
        
      default:
        // Default redirect
        redirect(next);
    }
  } catch (error) {
    console.error("Unexpected error during token verification:", error);
    redirect("/auth/error?error=unexpected_error");
  }
}