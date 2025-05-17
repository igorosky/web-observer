import {Component, inject, OnInit} from '@angular/core';
import {AuthService} from '../auth/auth.service';
import {Router} from '@angular/router';
import {HOME_ROUTE} from '../app.routes';
import {FormGroup, NonNullableFormBuilder, Validators} from '@angular/forms';

@Component({
  selector: 'app-log-in',
  imports: [],
  templateUrl: './log-in.component.html',
  styleUrl: './log-in.component.css'
})
export class LogInComponent implements OnInit {
  private authService: AuthService = inject(AuthService);
  private router: Router = inject(Router);
  protected logInForm?: FormGroup = undefined;

  constructor(private fb: NonNullableFormBuilder) {
    this.renderLogInForm();
  }

  ngOnInit() {
    this.authService.isLoggedIn().subscribe(
      {
          next: (status) => {
            if (status) void this.router.navigate([HOME_ROUTE]);
          }
      }
    )
  }

  private renderLogInForm() {
    this.logInForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  submitLogInForm(){
    if(this.logInForm === undefined || this.logInForm.invalid) return;
  }
}
