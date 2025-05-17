import {Component, inject, OnInit} from '@angular/core';
import {AuthService} from '../auth/auth.service';
import {Router} from '@angular/router';
import {HOME_ROUTE} from '../app.routes';
import {FormGroup, NonNullableFormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {animate, state, style, transition, trigger} from '@angular/animations';
import {AuthData} from '../auth/models/auth-data';

const ANIMATION_LENGTH_MS = 500;

@Component({
  selector: 'app-log-in',
  imports: [
    ReactiveFormsModule
  ],
  templateUrl: './log-in.component.html',
  styleUrl: './log-in.component.css',
  animations: [
    trigger('logInAnimation', [
      state(
        'start',
        style({
          width: '0',
          height: '0',
          opacity: 0,
          zIndex: -1,
        })
      ),
      state(
        'end',
        style({
          width: '100vw',
          height: '100vh',
          opacity: 1,
          zIndex: 1000,
        })
      ),
      transition('start => end', [
        animate(`${ANIMATION_LENGTH_MS}ms ease-in-out`)
      ]),
    ]),
  ]
})
export class LogInComponent implements OnInit {
  private authService: AuthService = inject(AuthService);
  private router: Router = inject(Router);
  protected logInForm?: FormGroup = undefined;

  constructor(private fb: NonNullableFormBuilder) {
    this.renderLogInForm();
  }

  ngOnInit() {
    if(this.authService.isLoggedIn()) void this.router.navigate([HOME_ROUTE]);
  }

  private renderLogInForm() {
    this.logInForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  protected welcomeMessage?: string = undefined;
  protected logInErrorMessage?: string = undefined;

  submitLogInForm(){
    if(this.logInForm === undefined || this.logInForm.invalid) return;
    const logInData = this.logInForm.value;
    this.authService.attemptLogIn(logInData).subscribe({
      next: async (authData: AuthData) => {
        this.logInErrorMessage = undefined;
        this.welcomeMessage = `Welcome back ${authData.username}!`
        await this.triggerLogInAnimation(); //todo fetch home data here
        void this.router.navigate([HOME_ROUTE]);
      },
      error: (errorMessage: string) => {
        this.logInErrorMessage = errorMessage;
      }
    })
  }

  private isAnimating: boolean = false;
  protected animationState: string = 'start';

  private async triggerLogInAnimation(): Promise<void> {
    if(this.isAnimating) return;
    this.isAnimating = true;
    this.animationState = 'end';
    await new Promise(resolve => setTimeout(resolve, ANIMATION_LENGTH_MS));
    this.isAnimating = false;
  }


}
