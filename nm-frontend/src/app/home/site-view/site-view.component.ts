import {Component, inject, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {HomeLoaderService} from '../home-loader.service';
import {SiteDetails} from '../models/site';
import {BareUpdateBoxComponent} from '../bare-update-box/bare-update-box.component';
import {FormGroup, NonNullableFormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';

@Component({
  selector: 'app-site-view',
  imports: [
    BareUpdateBoxComponent,
    ReactiveFormsModule,
  ],
  templateUrl: './site-view.component.html',
  styleUrl: './site-view.component.css'
})
export class SiteViewComponent implements OnInit {

  private homeLoaderService: HomeLoaderService = inject(HomeLoaderService);

  constructor(private activatedRoute: ActivatedRoute, private fb: NonNullableFormBuilder) {
  }

  siteFetchErrorMessage?: string = undefined;
  currentSite?: SiteDetails = undefined;

  isInEditMode: boolean = false;

  ngOnInit(): void {
    this.activatedRoute.params.subscribe(params => {
      const siteId: string | undefined = params['site_id'];
      if(siteId === undefined) {
        this.currentSite = undefined;
        this.siteFetchErrorMessage = 'Site ID not provided. Cannot fetch details.';
        return;
      }
      this.fetchSiteDetails(siteId);
    })
  }

  toggleEditMode(){
    if (this.currentSite === undefined){
      this.isInEditMode = false;
      return;
    }
    this.isInEditMode = !this.isInEditMode;
    if(this.isInEditMode){
      this.siteEditForm = this.fb.group({
        siteName: [this.currentSite.siteInfo.siteName, [Validators.required, Validators.maxLength(30)]],
        siteDesc: [this.currentSite.description, [Validators.maxLength(300)]],
      })
    }else{
      this.siteEditForm = undefined;
    }
  }

  private fetchSiteDetails(siteId: string){
    this.homeLoaderService.fetchSiteInfo(siteId).subscribe({
      next: (site) => {
        this.currentSite = site;
      },
      error: (errorMessage: string) => {
        this.siteFetchErrorMessage = errorMessage;
        this.currentSite = undefined;
      },
    })
  }

  refetchCurrentSiteDetails(){
    if(this.currentSite === undefined) return;
    this.fetchSiteDetails(this.currentSite.siteInfo.siteId);
  }

  attemptSiteRemoval(){
    if(this.currentSite === undefined) return;
    this.homeLoaderService.removeSite(this.currentSite.siteInfo.siteId)
      .subscribe({
        next: () => {
          this.siteFetchErrorMessage = "Site removed successfully."
          this.currentSite = undefined;
        },
        error: (errorMessage: string) => {
          alert(errorMessage);
        }
      })
  }

  siteEditForm?: FormGroup;
  siteEditErrorMessage?: string = undefined;

  get siteEditFormPristine() {
    return this.siteEditForm !== undefined && this.siteEditForm.pristine;
  }

  attemptSiteEdit(){
    if(this.siteEditForm === undefined || this.siteEditForm.pristine || this.currentSite === undefined) return;
    const editData: FormData = new FormData();
    const value = this.siteEditForm.value;
    editData.set('siteName', value.siteName)
    editData.set('siteDescription', value.siteDesc)
    this.homeLoaderService.editSite(editData).subscribe({
      next: () => {
        this.siteEditErrorMessage = undefined;
        this.currentSite!.siteInfo.siteName = value.siteName;
        this.currentSite!.description = value.siteDesc;
        this.toggleEditMode();
      },
      error: (errorMessage: string) => {
        this.siteEditErrorMessage = errorMessage;
      }
    })
  }
}
