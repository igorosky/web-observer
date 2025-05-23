import { Component } from '@angular/core';
import {FormGroup, NonNullableFormBuilder, Validators} from '@angular/forms';
import {HomeLoaderService, SiteRegisterResponse} from '../home-loader.service';

@Component({
  selector: 'app-site-register',
  imports: [],
  templateUrl: './site-register.component.html',
  styleUrl: './site-register.component.css'
})
export class SiteRegisterComponent {

  protected siteRegisterForm: FormGroup;

  constructor(private fb: NonNullableFormBuilder, private homeLoaderService: HomeLoaderService) {
    this.siteRegisterForm = this.fb.group({
      siteName: ['', [Validators.required, Validators.maxLength(30)]],
      siteUrl: ['', [Validators.required, Validators.maxLength(100)]],
      siteDescription: ['', Validators.maxLength(300)],
      elementName: ['', [Validators.required, Validators.maxLength(255)]],
      cssSelector: ['', [Validators.required, Validators.maxLength(255)]],
    })
  }

  get isPristine(): boolean{
    return this.siteRegisterForm.pristine;
  }

  protected siteRegisterErrorMessage?: string = undefined

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
      next: (registerData: SiteRegisterResponse) => {
        this.siteRegisterErrorMessage = undefined;
        //todo
      },
      error: (errorMessage: string) => {this.siteRegisterErrorMessage = errorMessage;},
    });
  }

}
