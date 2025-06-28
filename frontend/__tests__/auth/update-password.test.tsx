/**
 * Password Update Page Tests
 * 
 * @description Tests for password update functionality after reset
 * @follows t-wada TDD best practices
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/navigation';
import UpdatePasswordPage from '@/app/auth/update-password/page';
import { useSupabase } from '@/providers/auth-provider';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/providers/auth-provider', () => ({
  useSupabase: jest.fn(),
}));

describe('UpdatePasswordPage', () => {
  const mockPush = jest.fn();
  const mockUpdateUser = jest.fn();
  const mockOnAuthStateChange = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    
    (useSupabase as jest.Mock).mockReturnValue({
      supabase: {
        auth: {
          updateUser: mockUpdateUser,
          onAuthStateChange: mockOnAuthStateChange.mockReturnValue({
            data: {
              subscription: {
                unsubscribe: jest.fn(),
              },
            },
          }),
        },
      },
    });
  });

  it('should show access denied when not in recovery mode', () => {
    render(<UpdatePasswordPage />);
    
    expect(screen.getByText(/アクセス権限がありません/i)).toBeInTheDocument();
    expect(screen.queryByRole('form')).not.toBeInTheDocument();
  });

  it('should render password update form in recovery mode', () => {
    // Simulate PASSWORD_RECOVERY event
    mockOnAuthStateChange.mockImplementation((callback) => {
      callback('PASSWORD_RECOVERY', { user: { id: 'test-user' } });
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    render(<UpdatePasswordPage />);
    
    expect(screen.getByRole('heading', { name: /新しいパスワードを設定/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/新しいパスワード/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/パスワード確認/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /パスワードを更新/i })).toBeInTheDocument();
  });

  it('should validate password strength', async () => {
    const user = userEvent.setup();
    
    // Set recovery mode
    mockOnAuthStateChange.mockImplementation((callback) => {
      callback('PASSWORD_RECOVERY', { user: { id: 'test-user' } });
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    render(<UpdatePasswordPage />);
    
    const passwordInput = screen.getByLabelText(/新しいパスワード/i);
    const submitButton = screen.getByRole('button', { name: /パスワードを更新/i });
    
    // Test weak password
    await user.type(passwordInput, 'weak');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/パスワードは8文字以上で入力してください/i)).toBeInTheDocument();
    });
  });

  it('should validate password confirmation match', async () => {
    const user = userEvent.setup();
    
    // Set recovery mode
    mockOnAuthStateChange.mockImplementation((callback) => {
      callback('PASSWORD_RECOVERY', { user: { id: 'test-user' } });
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    render(<UpdatePasswordPage />);
    
    const passwordInput = screen.getByLabelText(/新しいパスワード/i);
    const confirmInput = screen.getByLabelText(/パスワード確認/i);
    const submitButton = screen.getByRole('button', { name: /パスワードを更新/i });
    
    await user.type(passwordInput, 'StrongPass123');
    await user.type(confirmInput, 'DifferentPass123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/パスワードが一致しません/i)).toBeInTheDocument();
    });
  });

  it('should update password successfully', async () => {
    const user = userEvent.setup();
    mockUpdateUser.mockResolvedValue({ error: null });
    
    // Set recovery mode
    mockOnAuthStateChange.mockImplementation((callback) => {
      callback('PASSWORD_RECOVERY', { user: { id: 'test-user' } });
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    render(<UpdatePasswordPage />);
    
    const passwordInput = screen.getByLabelText(/新しいパスワード/i);
    const confirmInput = screen.getByLabelText(/パスワード確認/i);
    const submitButton = screen.getByRole('button', { name: /パスワードを更新/i });
    
    await user.type(passwordInput, 'StrongPass123');
    await user.type(confirmInput, 'StrongPass123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockUpdateUser).toHaveBeenCalledWith({
        password: 'StrongPass123',
      });
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should show error message when update fails', async () => {
    const user = userEvent.setup();
    mockUpdateUser.mockResolvedValue({ 
      error: { message: 'Invalid token' } 
    });
    
    // Set recovery mode
    mockOnAuthStateChange.mockImplementation((callback) => {
      callback('PASSWORD_RECOVERY', { user: { id: 'test-user' } });
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    render(<UpdatePasswordPage />);
    
    const passwordInput = screen.getByLabelText(/新しいパスワード/i);
    const confirmInput = screen.getByLabelText(/パスワード確認/i);
    const submitButton = screen.getByRole('button', { name: /パスワードを更新/i });
    
    await user.type(passwordInput, 'StrongPass123');
    await user.type(confirmInput, 'StrongPass123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/パスワードの更新に失敗しました/i)).toBeInTheDocument();
    });
  });

  it('should show password strength indicator', async () => {
    const user = userEvent.setup();
    
    // Set recovery mode
    mockOnAuthStateChange.mockImplementation((callback) => {
      callback('PASSWORD_RECOVERY', { user: { id: 'test-user' } });
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    render(<UpdatePasswordPage />);
    
    const passwordInput = screen.getByLabelText(/新しいパスワード/i);
    
    // Type weak password
    await user.type(passwordInput, 'weak');
    expect(screen.getByText(/弱い/i)).toBeInTheDocument();
    
    // Type medium password
    await user.clear(passwordInput);
    await user.type(passwordInput, 'Medium123');
    expect(screen.getByText(/普通/i)).toBeInTheDocument();
    
    // Type strong password
    await user.clear(passwordInput);
    await user.type(passwordInput, 'StrongPass123!');
    expect(screen.getByText(/強い/i)).toBeInTheDocument();
  });
});