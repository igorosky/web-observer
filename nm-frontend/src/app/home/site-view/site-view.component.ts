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
        elementName: [this.currentSite.siteInfo.elementName, [Validators.required, Validators.maxLength(30)]],
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

  refetchCurrentSiteUpdates(){
    if(this.currentSite === undefined) return;
    this.fetchSiteUpdates(this.currentSite.siteInfo.siteId);
  }

  private fetchSiteUpdates(siteId: string){
    if(this.currentSite === undefined) return;
    this.homeLoaderService.fetchSiteUpdates(siteId).subscribe({
      next: (updates) => {
        if(this.currentSite === undefined) return;
        this.currentSite.updates = updates;
      },
      error: (errorMessage: string) => {
        this.siteFetchErrorMessage = errorMessage;
        this.currentSite = undefined;
      },
    })
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
    if(this.siteEditForm === undefined || this.siteEditForm.pristine) return;
    const editData: FormData = new FormData();
    const value = this.siteEditForm.value;
    editData.set('siteName', value.siteName)
    editData.set('siteDescription', value.siteDesc)
    editData.set('elementName', value.elementName)
    this.homeLoaderService.editSite(editData).subscribe({
      next: () => {
        if(this.currentSite === undefined) return;
        this.siteEditErrorMessage = undefined;
        this.currentSite.siteInfo.siteName = value.siteName;
        this.currentSite.description = value.siteDesc;
        this.currentSite.siteInfo.elementName = value.elementName;
        this.toggleEditMode();
      },
      error: (errorMessage: string) => {
        this.siteEditErrorMessage = errorMessage;
      }
    })
  }

  get siteName(){
    return this.siteEditForm?.get('siteName')!;
  }

  get siteDesc() {
    return this.siteEditForm?.get('siteDesc')!;
  }

  get elementName(){
    return this.siteEditForm?.get('elementName')!;
  }
}
