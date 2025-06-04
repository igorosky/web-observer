import {AbstractControl, ValidationErrors, ValidatorFn} from '@angular/forms';
import {SITE_TYPE} from '../site-register/site-register.component';

export function getStatusClass(statusCode: number): string {
  if(statusCode === -1) return 'errorU'
  else if(statusCode < 400) return 'successU';
  else if(statusCode < 500) return 'clientEU';
  else return 'serverEU';
}

export function urlValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const urlPattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)([\/?]?.*)$/i;
    const value: string | null | undefined = control.value;
    if (typeof value !== 'string' || value.length === 0) {
      return null;
    }
    const isValid = urlPattern.test(value);
    return isValid ? null : { invalidUrl: true };
  };
}

export function siteTypeValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value;
    return (SITE_TYPE.includes(value)) ? null : { invalidSiteType: true };
  };
}
