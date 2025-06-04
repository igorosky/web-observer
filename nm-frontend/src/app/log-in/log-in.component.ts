import {Component, Inject, inject, OnInit, PLATFORM_ID} from '@angular/core';
import {AuthService} from '../auth/auth.service';
import {Router} from '@angular/router';
import {HOME_ROUTE} from '../app.routes';
import {FormGroup, NonNullableFormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {animate, keyframes, state, style, transition, trigger} from '@angular/animations';
import {AuthData} from '../auth/models/auth-data';
import {HomeLoaderService} from '../home/home-loader.service';
import {isPlatformBrowser} from '@angular/common';

const ANIMATION_HOLD_MS = 3000;

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
          opacity: 0,
        })
      ),
      state(
        'end',
        style({
          opacity: 1,
          zIndex: 1000,
        })
      ),
      transition('start => end', [
        animate(
          `${ANIMATION_HOLD_MS}ms ease-in`,
          keyframes([
            style({opacity: 0, zIndex: -1, offset: 0}),
            style({opacity: 1, zIndex: 1000, offset: 0.15}),
            style({opacity: 1, zIndex: 1000, offset: 1}),
          ])
        )
      ]),
    ]),
  ]
})
export class LogInComponent implements OnInit {
  private authService: AuthService = inject(AuthService);
  private router: Router = inject(Router);
  protected logInForm?: FormGroup = undefined;

  constructor(@Inject(PLATFORM_ID) private platformId: object, private fb: NonNullableFormBuilder, private homeLoaderService: HomeLoaderService) {
    this.renderLogInForm();
  }

  ngOnInit() {
    if (isPlatformBrowser(this.platformId) && this.authService.isLoggedIn()) void this.router.navigate([HOME_ROUTE]);
  }

  private renderLogInForm() {
    this.logInForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  protected welcomeMessage?: string = undefined;
  protected logInErrorMessage?: string = undefined;
  private isFetching: boolean = false;

  submitLogInForm() {
    if (this.isFetching || this.logInForm === undefined || this.logInForm.invalid) return;
    this.isFetching = true;
    const logInData = this.logInForm.value;
    this.authService.attemptLogIn(logInData).subscribe({
      next: async (authData: AuthData) => {
        this.logInErrorMessage = undefined;
        this.welcomeMessage = `Welcome back ${authData.username}!`
        this.homeLoaderService.preloadHomeView();
        await this.triggerLogInAnimation();
        this.isFetching = false;
        void this.router.navigate([HOME_ROUTE]);
      },
      error: (errorMessage: string) => {
        this.logInErrorMessage = errorMessage;
        this.isFetching = false;
      }
    });
  }

  private isAnimating: boolean = false;
  protected animationState: string = 'start';

  private async triggerLogInAnimation(): Promise<void> {
    if (this.isAnimating) return;
    this.isAnimating = true;
    this.animationState = 'end';
    await new Promise(resolve => setTimeout(resolve, ANIMATION_HOLD_MS));
    this.isAnimating = false;
  }

  get logInFormPristine(): boolean {
    return this.logInForm?.pristine ?? true;
  }

  get email() {
    return this.logInForm?.get('email')!;
  }

}
