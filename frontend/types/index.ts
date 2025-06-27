// Reply Pass 共通型定義

export interface User {
  id: string;
  email: string;
  profile: {
    display_name: string;
    avatar_url?: string;
    timezone: string;
    locale: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Case {
  id: string;
  user_id: string;
  name: string;
  partner_name: string;
  partner_type?: string;
  my_position?: string;
  conversation_purpose?: string;
  created_at: string;
  updated_at: string;
}

export interface ReplySuggestion {
  id: string;
  category: string;
  suggestion: string;
  was_sent: boolean;
  partner_reaction?: "positive" | "negative" | null;
  created_at: string;
}
