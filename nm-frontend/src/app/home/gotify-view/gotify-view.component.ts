import {Component, inject, OnInit} from '@angular/core';
import {GotifyData, GotifyService} from './gotify.service';
import {FormGroup, FormsModule, NonNullableFormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {urlValidator} from '../utils/utils';
import {NgOptimizedImage} from '@angular/common';

@Component({
  selector: 'app-gotify-view',
  imports: [
    NgOptimizedImage,
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './gotify-view.component.html',
  styleUrl: './gotify-view.component.css'
})
export class GotifyViewComponent implements OnInit {

  private gotifyService: GotifyService = inject(GotifyService);
  protected gotifyData?: GotifyData | null; //undefined = not fetched, null = no data
  protected gotifyFetchErrorMessage?: string;

  protected gotifyUpdateForm?: FormGroup;

  constructor(private fb: NonNullableFormBuilder) {
  }


  ngOnInit(): void {
    this.gotifyService.getGotifyData().subscribe({
        next: (data) => {
          this.gotifyData = data;
          this.createGotifyForm(data);
        },
        error: (errMsg: string) => this.gotifyFetchErrorMessage = errMsg,
      }
    );
  }

  private createGotifyForm(gotifyData: GotifyData | null){
    if(gotifyData === null){
      this.gotifyUpdateForm = this.fb.group({
        url: ['', [Validators.required, urlValidator()]],
        token: ['', Validators.required]
      });
    }else{
      this.gotifyUpdateForm = this.fb.group({
        url: [gotifyData.url, [Validators.required, urlValidator(), Validators.maxLength(100)]],
        token: ['[REENTER TOKEN]', Validators.required]
      });
    }
  }

  protected gotifyUpdateErrorMessage?: string;

  attemptGotifyDataUpdate(){
    if(this.gotifyUpdateForm === undefined || this.gotifyUpdateForm.invalid || this.gotifyUpdateForm.pristine) return;
    const data = this.gotifyUpdateForm.value;
    const formData = new FormData();
    formData.set('url', data.url);
    formData.set('token', data.token);
    this.gotifyService.updateGotifyData(formData).subscribe({
      next: () => this.gotifyData = data,
      error: (errMsg: string) => this.gotifyUpdateErrorMessage = errMsg,
    });
  }

  resetUpdateForm(){
    this.gotifyUpdateForm?.reset();
    this.gotifyUpdateErrorMessage = undefined;
  }

  get gotifyFormPristine(){
    return this.gotifyUpdateForm!.pristine;
  }

  get url(){
    return this.gotifyUpdateForm!.get('url')!;
  }

  attemptGotifyRemoval(){
    this.gotifyService.removeGotifyData().subscribe({
      next: () => this.gotifyData = null,
      error: (errMsg: string) => alert(`Could not delete Gotify data. Reason: ${errMsg}`),
    });
  }
}
