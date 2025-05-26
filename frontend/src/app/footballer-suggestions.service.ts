import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { FootballerSuggestion, FootballerGuess, Clue } from './footballer-suggestions.model';

@Injectable({
  providedIn: 'root'
})

export class FootballerSuggestionsService {

  private apiUrl = 'http://localhost:5000/';

  constructor(private http: HttpClient) { }

  setDifficulty(league: String, mode: String) {
    return this.http.post(`${this.apiUrl}/set-difficulty`, { league: league, difficulty: mode });
  }

  getPlayerData(id: string): Observable<FootballerGuess> {
    return this.http.get<FootballerGuess>(`${this.apiUrl}/player-data?id=${id}`);
  }

  getSuggestions(query: string): Observable<FootballerSuggestion[]> {
    return this.http.get<FootballerSuggestion[]>(`${this.apiUrl}/suggestions?query=${query}`);
  }

  getClue(): Observable<Clue> {
    return this.http.get<Clue>(`${this.apiUrl}/clue`);
  }
}