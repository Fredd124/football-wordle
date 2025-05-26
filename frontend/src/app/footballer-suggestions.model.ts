export interface FootballerSuggestion {
  id: string;
  name: string;
  image: string;
}

export interface FootballerGuess {
  image: string;
  age?: { value: string, color: string, direction: string };
  club_logo: string;
  club?: { value: string, color: string };
  position?: { value: string, color: string };
  best_foot?: { value: string, color: string };
  number?: { value: string, color: string, direction: string };
  country?: { value: string, color: string };
  nationality_names?: { value: string, color: string };
  market_value?: { value: string, color: string, direction: string };
  is_winner: boolean;
}

export interface Clue {
  type: string;
  clue: string;
}
