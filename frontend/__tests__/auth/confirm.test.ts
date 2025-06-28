/**
 * Auth Confirmation Route Tests
 * 
 * @description Tests for authentication confirmation API route
 * @follows t-wada TDD best practices
 */

import { GET } from '@/app/auth/confirm/route';
import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

// Mock dependencies
jest.mock('@/lib/supabase/server', () => ({
  createClient: jest.fn(),
}));

jest.mock('next/navigation', () => ({
  redirect: jest.fn(),
}));

describe('/auth/confirm route', () => {
  const mockVerifyOtp = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    (createClient as jest.Mock).mockResolvedValue({
      auth: {
        verifyOtp: mockVerifyOtp,
      },
    });
  });

  it('should redirect to error page when token_hash is missing', async () => {
    const request = new Request('http://localhost/auth/confirm?type=recovery');
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/error?error=missing_parameters');
  });

  it('should redirect to error page when type is missing', async () => {
    const request = new Request('http://localhost/auth/confirm?token_hash=abc123');
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/error?error=missing_parameters');
  });

  it('should verify OTP token with correct parameters', async () => {
    mockVerifyOtp.mockResolvedValue({ error: null });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=recovery'
    );
    
    await GET(request);
    
    expect(mockVerifyOtp).toHaveBeenCalledWith({
      type: 'recovery',
      token_hash: 'abc123',
    });
  });

  it('should redirect to update-password for recovery type', async () => {
    mockVerifyOtp.mockResolvedValue({ error: null });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=recovery'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/update-password');
  });

  it('should redirect to dashboard for signup type', async () => {
    mockVerifyOtp.mockResolvedValue({ error: null });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=signup'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/dashboard?welcome=true');
  });

  it('should redirect to settings for email_change type', async () => {
    mockVerifyOtp.mockResolvedValue({ error: null });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=email_change'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/settings?email_updated=true');
  });

  it('should use custom next parameter when provided', async () => {
    mockVerifyOtp.mockResolvedValue({ error: null });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=invite&next=/team'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/dashboard?invited=true');
  });

  it('should handle expired token error', async () => {
    mockVerifyOtp.mockResolvedValue({
      error: { message: 'Token has expired' },
    });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=expired&type=recovery'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/error?error=token_expired');
  });

  it('should handle invalid token error', async () => {
    mockVerifyOtp.mockResolvedValue({
      error: { message: 'Invalid token provided' },
    });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=invalid&type=recovery'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/error?error=invalid_token');
  });

  it('should handle generic verification error', async () => {
    mockVerifyOtp.mockResolvedValue({
      error: { message: 'Verification failed' },
    });
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=recovery'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/error?error=verification_failed');
  });

  it('should handle unexpected errors', async () => {
    mockVerifyOtp.mockRejectedValue(new Error('Network error'));
    
    const request = new Request(
      'http://localhost/auth/confirm?token_hash=abc123&type=recovery'
    );
    
    await GET(request);
    
    expect(redirect).toHaveBeenCalledWith('/auth/error?error=unexpected_error');
  });
});