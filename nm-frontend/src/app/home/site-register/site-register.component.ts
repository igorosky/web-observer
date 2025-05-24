import { Component } from '@angular/core';
import {FormGroup, NonNullableFormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {HomeLoaderService, SiteRegisterResponse} from '../home-loader.service';
import {animate, keyframes, state, style, transition, trigger} from '@angular/animations';
import {HOME_ROUTE} from '../../app.routes';
import {Router} from '@angular/router';
import {urlValidator} from '../utils/utils';

const ANIMATION_HOLD_MS = 3000;

interface SiteAnimationData{
  siteName: string,
  siteId: string
}

@Component({
  selector: 'app-site-register',
  imports: [
    ReactiveFormsModule
  ],
  templateUrl: './site-register.component.html',
  styleUrl: './site-register.component.css',
  animations: [
    trigger('registerAnimation', [
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
export class SiteRegisterComponent {

  protected siteRegisterForm: FormGroup;

  constructor(private fb: NonNullableFormBuilder, private homeLoaderService: HomeLoaderService, private router: Router) {
    this.siteRegisterForm = this.fb.group({
      siteName: ['', [Validators.required, Validators.maxLength(30)]],
      siteUrl: ['', [Validators.required, Validators.maxLength(100), urlValidator()]],
      siteDesc: ['', Validators.maxLength(900)],
      elementName: ['', [Validators.required, Validators.maxLength(30)]],
      cssSelector: ['', [Validators.required, Validators.maxLength(255)]],
    })
  }

  get siteRegisterFormPristine(): boolean{
    return this.siteRegisterForm.pristine;
  }

  protected siteRegisterErrorMessage?: string = undefined

  private isAnimating: boolean = false;
  protected animationState: string = 'start';
  protected siteAnimationData?: SiteAnimationData = undefined;

  private async triggerSiteRegisterAnimation(): Promise<void> {
    if (this.isAnimating || this.siteAnimationData === undefined) return;
    this.isAnimating = true;
    this.animationState = 'end';
    await new Promise(resolve => setTimeout(resolve, ANIMATION_HOLD_MS));
    this.isAnimating = false;
  }

  attemptSiteRegistrations(){
    if(this.siteRegisterForm.invalid || this.siteRegisterForm.pristine) return;
    const value = this.siteRegisterForm.value;
    const registerData: FormData = new FormData();
    registerData.set('siteName', value.siteName);
    registerData.set('siteDescription', value.siteDesc);
    registerData.set('siteUrl', value.siteUrl);
    registerData.set('elementName', value.elementName);
    registerData.set('cssSelector', value.cssSelector);
    this.homeLoaderService.registerSite(registerData).subscribe({
      next: async (registerData: SiteRegisterResponse) => {
        this.siteRegisterErrorMessage = undefined;
        this.siteAnimationData = {
          siteName: value.siteName,
          siteId: registerData.siteId
        };
        await this.triggerSiteRegisterAnimation();
        void this.router.navigate([HOME_ROUTE, 'site', registerData.siteId]);
      },
      error: (errorMessage: string) => {
        this.siteRegisterErrorMessage = errorMessage;
        },
    });
  }

  resetSiteRegisterForm() {
    this.siteRegisterForm.reset();
    this.siteRegisterErrorMessage = undefined;
    this.siteAnimationData = undefined;
  }

  get siteName() {
    return this.siteRegisterForm.get('siteName')!;
  }

  get siteUrl() {
    return this.siteRegisterForm.get('siteUrl')!;
  }

  get cssSelector(){
    return this.siteRegisterForm.get('cssSelector')!;
  }

  get elementName(){
    return this.siteRegisterForm.get('elementName')!;
  }

  get siteDesc(){
    return this.siteRegisterForm.get('siteDesc')!;
  }
}
