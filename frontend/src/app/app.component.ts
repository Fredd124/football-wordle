import {
  Component,
  ViewChildren,
  ElementRef,
  QueryList,
  ViewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FootballerSuggestionsService } from './footballer-suggestions.service';
import {
  FootballerGuess,
  FootballerSuggestion,
  Clue,
} from './footballer-suggestions.model';
import confetti from 'canvas-confetti';

@Component({
  selector: 'app-root',
  imports: [FormsModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'football-wordle';
  query = '';
  suggestions: FootballerSuggestion[] = [];
  activeSuggestionIndex: number = -1;
  players: any[] = [];
  isSubmitted = false;
  submitPlayer: FootballerGuess | null = null;
  clues: Clue[] = [];
  isHidden = true;
  difficulty = 'super_easy';
  isWinner = false;
  noMoreClues = false;
  submitNumber: number = 0;
  league: string = 'champions_league';

  constructor(
    private footballerSuggestionsService: FootballerSuggestionsService
  ) {}

  @ViewChildren('lastPlayerRow') playerRows!: QueryList<ElementRef>;
  @ViewChild('inputWrapper') inputWrapper!: ElementRef;

  handleDocumentClick = (event: MouseEvent) => {
    if (
      this.inputWrapper &&
      !this.inputWrapper.nativeElement.contains(event.target)
    ) {
      this.suggestions = [];
      this.activeSuggestionIndex = -1;
    }
  };

  ngAfterViewInit() {
    document.addEventListener('click', this.handleDocumentClick, true);
  }

  ngOnDestroy() {
    document.removeEventListener('click', this.handleDocumentClick, true);
  }

  triggerConfettiAtElement(element: HTMLElement): void {
    const rect = element.getBoundingClientRect();
    const x = (rect.left + rect.right) / 2 / window.innerWidth;
    const y = (rect.top + rect.bottom) / 2 / window.innerHeight;

    confetti({
      particleCount: 300,
      spread: 80,
      origin: { x, y },
    });
  }

  setLeague(league: string) {
    this.league = league;
  }

  setDifficulty(league: string, mode: string) {
    this.difficulty = mode;
    this.footballerSuggestionsService
      .setDifficulty(this.league, mode)
      .subscribe((result) => {
        this.query = '';
        this.players = [];
      });
    this.isSubmitted = false;
    this.activeSuggestionIndex = -1;
    this.isWinner = false;
    this.noMoreClues = false;
    this.submitNumber = 0;
    this.clues = [];
  }

  getSuggestions(): void {
    if (this.query == '') {
      this.suggestions = [];
      this.activeSuggestionIndex = -1;
      return;
    }
    this.footballerSuggestionsService
      .getSuggestions(this.query)
      .subscribe((suggestions: FootballerSuggestion[]) => {
        this.suggestions = suggestions;
      });
    this.activeSuggestionIndex = -1;
  }

  submitGuess(playerId: string): void {
    console.log(playerId)
    this.submitNumber += 1;
    this.footballerSuggestionsService
      .getPlayerData(playerId)
      .subscribe((data) => {
        this.submitPlayer = {
          image: data.image,
          age: {
            value: data.age?.value || '',
            color: data.age?.color || 'red',
            direction: data.age?.direction || '',
          },
          club_logo: data.club_logo,
          position: {
            value: data.position?.value || '',
            color: data.position?.color || 'red',
          },
          best_foot: {
            value: data.best_foot?.value || '',
            color: data.best_foot?.color || 'red',
          },
          number: {
            value: data.number?.value || '',
            color: data.number?.color || 'red',
            direction: data.number?.direction || '',
          },
          nationality_names: {
            value: data.country?.value || '',
            color: data.country?.color || 'red',
          },
          market_value: {
            value: data.market_value?.value || '',
            color: data.market_value?.color || 'red',
            direction: data.market_value?.direction || '',
          },
          is_winner: data.is_winner,
        };
        this.isWinner = this.submitPlayer.is_winner;
        this.players.push(this.submitPlayer);
        this.scrollToLastPlayer();
      });
    if (!this.isWinner && this.submitNumber % 5 === 0) {
      this.getClue();
    }
    this.query = '';
    this.suggestions = [];
    this.activeSuggestionIndex = -1;
    this.isSubmitted = true;
  }

  onInputKeyDown(event: KeyboardEvent) {
    if (this.suggestions.length === 0) return;

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (this.activeSuggestionIndex < this.suggestions.length - 1) {
        this.activeSuggestionIndex++;
      } else {
        this.activeSuggestionIndex = 0;
      }
      this.scrollActiveSuggestionIntoView();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (this.activeSuggestionIndex > 0) {
        this.activeSuggestionIndex--;
      } else {
        this.activeSuggestionIndex = this.suggestions.length - 1;
      }
      this.scrollActiveSuggestionIntoView();
    } else if (event.key === 'Enter') {
      this.submitGuess(this.suggestions[this.activeSuggestionIndex].id);
    }
  }

  scrollActiveSuggestionIntoView() {
    setTimeout(() => {
      const items = document.querySelectorAll('.suggestions-dropdown li');
      if (items[this.activeSuggestionIndex]) {
        (items[this.activeSuggestionIndex] as HTMLElement).scrollIntoView({
          block: 'nearest',
        });
      }
    });
  }

  scrollToLastPlayer(): void {
    setTimeout(() => {
      const el = this.playerRows.last?.nativeElement;
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'end' });

        if (this.isWinner) {
          setTimeout(() => {
            this.triggerConfettiAtElement(el);
          }, 4000);
        }
      }
    });
  }

  getArrowImage(): string {
    return 'assets/arrow.png';
  }

  getArrowRotation(direction: string): string {
    if (direction === 'up') return 'rotate(270deg)';
    if (direction === 'down') return 'rotate(90deg)';
    return 'rotate(0deg)';
  }

  getClue(): void {
    if (this.noMoreClues) return;
    this.footballerSuggestionsService.getClue().subscribe((clue: Clue) => {
      if (clue['type'] != '') this.clues.push(clue);
      else this.noMoreClues = true;
    });
  }
}
