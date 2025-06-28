/**
 * Auth Error Page Tests
 * 
 * @description Tests for authentication error page display and navigation
 * @follows t-wada TDD best practices
 */

import { render, screen } from '@testing-library/react';
import AuthErrorPage from '@/app/auth/error/page';

describe('AuthErrorPage', () => {
  it('should render default error message when no error code is provided', () => {
    render(<AuthErrorPage searchParams={{}} />);
    
    expect(screen.getByText('エラーが発生しました')).toBeInTheDocument();
    expect(screen.getByText('不明なエラーが発生しました。もう一度お試しください。')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'ログインページに戻る' })).toBeInTheDocument();
  });

  it('should render missing parameters error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'missing_parameters' }} />);
    
    expect(screen.getByText('リンクが無効です')).toBeInTheDocument();
    expect(screen.getByText(/必要なパラメータが不足しています/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'パスワードリセットをやり直す' })).toBeInTheDocument();
  });

  it('should render invalid token error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'invalid_token' }} />);
    
    expect(screen.getByText('無効なトークンです')).toBeInTheDocument();
    expect(screen.getByText(/リンクが無効または既に使用されています/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: '新しいリンクを要求する' })).toBeInTheDocument();
  });

  it('should render token expired error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'token_expired' }} />);
    
    expect(screen.getByText('リンクの有効期限が切れています')).toBeInTheDocument();
    expect(screen.getByText(/パスワードリセットリンクの有効期限が切れました/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: '新しいリンクを要求する' })).toBeInTheDocument();
  });

  it('should render verification failed error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'verification_failed' }} />);
    
    expect(screen.getByText('認証に失敗しました')).toBeInTheDocument();
    expect(screen.getByText(/認証プロセスでエラーが発生しました/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'ログインページに戻る' })).toBeInTheDocument();
  });

  it('should render auth session missing error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'auth_session_missing' }} />);
    
    expect(screen.getByText('認証セッションが見つかりません')).toBeInTheDocument();
    expect(screen.getByText(/認証セッションが失効しています/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'パスワードリセットをやり直す' })).toBeInTheDocument();
  });

  it('should render signup disabled error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'signup_disabled' }} />);
    
    expect(screen.getByText('新規登録が無効です')).toBeInTheDocument();
    expect(screen.getByText(/現在、新規登録を受け付けていません/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'ログインページに戻る' })).toBeInTheDocument();
  });

  it('should render unexpected error message', () => {
    render(<AuthErrorPage searchParams={{ error: 'unexpected_error' }} />);
    
    expect(screen.getByText('予期しないエラーが発生しました')).toBeInTheDocument();
    expect(screen.getByText(/システムエラーが発生しました/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'ホームページに戻る' })).toBeInTheDocument();
  });

  it('should always show alternative navigation links', () => {
    render(<AuthErrorPage searchParams={{ error: 'invalid_token' }} />);
    
    // Check for alternative links
    const loginLinks = screen.getAllByText('ログインページに戻る');
    const homeLinks = screen.getAllByText('ホームページに戻る');
    
    expect(loginLinks.length).toBeGreaterThan(0);
    expect(homeLinks.length).toBeGreaterThan(0);
  });

  it('should show support contact information', () => {
    render(<AuthErrorPage searchParams={{ error: 'unexpected_error' }} />);
    
    expect(screen.getByText(/問題が解決しない場合は/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'サポートチーム' })).toBeInTheDocument();
  });

  it('should show debug info in development environment', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    render(<AuthErrorPage searchParams={{ error: 'invalid_token' }} />);
    
    expect(screen.getByText('Error Code: invalid_token')).toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  it('should not show debug info in production environment', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';
    
    render(<AuthErrorPage searchParams={{ error: 'invalid_token' }} />);
    
    expect(screen.queryByText('Error Code: invalid_token')).not.toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  it('should handle unknown error codes gracefully', () => {
    render(<AuthErrorPage searchParams={{ error: 'some_unknown_error' }} />);
    
    expect(screen.getByText('エラーが発生しました')).toBeInTheDocument();
    expect(screen.getByText('不明なエラーが発生しました。もう一度お試しください。')).toBeInTheDocument();
  });
});