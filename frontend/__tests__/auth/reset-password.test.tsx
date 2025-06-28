/**
 * Password Reset Request Page Tests
 * 
 * @description Tests for password reset request functionality
 * @follows t-wada TDD best practices
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/navigation';
import ResetPasswordPage from '@/app/auth/reset-password/page';
import { useAuth } from '@/hooks/use-auth';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/hooks/use-auth', () => ({
  useAuth: jest.fn(),
}));

describe('ResetPasswordPage', () => {
  const mockPush = jest.fn();
  const mockResetPassword = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    
    (useAuth as jest.Mock).mockReturnValue({
      resetPassword: mockResetPassword,
      loading: false,
    });
  });

  it('should render password reset form', () => {
    render(<ResetPasswordPage />);
    
    expect(screen.getByRole('heading', { name: /パスワードリセット/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/メールアドレス/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /リセットメールを送信/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /ログインに戻る/i })).toBeInTheDocument();
  });

  it('should show validation error for invalid email', async () => {
    const user = userEvent.setup();
    render(<ResetPasswordPage />);
    
    const emailInput = screen.getByLabelText(/メールアドレス/i);
    const submitButton = screen.getByRole('button', { name: /リセットメールを送信/i });
    
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/有効なメールアドレスを入力してください/i)).toBeInTheDocument();
    });
  });

  it('should submit form with valid email', async () => {
    const user = userEvent.setup();
    mockResetPassword.mockResolvedValue({ error: null });
    
    render(<ResetPasswordPage />);
    
    const emailInput = screen.getByLabelText(/メールアドレス/i);
    const submitButton = screen.getByRole('button', { name: /リセットメールを送信/i });
    
    await user.type(emailInput, 'test@example.com');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockResetPassword).toHaveBeenCalledWith('test@example.com');
    });
  });

  it('should show success message after sending reset email', async () => {
    const user = userEvent.setup();
    mockResetPassword.mockResolvedValue({ error: null });
    
    render(<ResetPasswordPage />);
    
    const emailInput = screen.getByLabelText(/メールアドレス/i);
    const submitButton = screen.getByRole('button', { name: /リセットメールを送信/i });
    
    await user.type(emailInput, 'test@example.com');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/パスワードリセットのメールを送信しました/i)).toBeInTheDocument();
      expect(screen.getByText(/メールをご確認ください/i)).toBeInTheDocument();
    });
  });

  it('should show error message when reset fails', async () => {
    const user = userEvent.setup();
    mockResetPassword.mockResolvedValue({ 
      error: new Error('User not found') 
    });
    
    render(<ResetPasswordPage />);
    
    const emailInput = screen.getByLabelText(/メールアドレス/i);
    const submitButton = screen.getByRole('button', { name: /リセットメールを送信/i });
    
    await user.type(emailInput, 'notfound@example.com');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/エラーが発生しました/i)).toBeInTheDocument();
    });
  });

  it('should disable form while loading', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      resetPassword: mockResetPassword,
      loading: true,
    });
    
    render(<ResetPasswordPage />);
    
    const emailInput = screen.getByLabelText(/メールアドレス/i);
    const submitButton = screen.getByRole('button', { name: /送信中.../i });
    
    expect(emailInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });
});