
export interface UpdateEntryPreview {
  siteId: string;
  siteUrl: string;
  siteName: string;
  registeredAt: string;
}

export interface BareUpdateEntry {
  registeredAt: string;
  change: string; //todo
}

export interface SiteDetails {
  siteInfo: Site;
  updates: BareUpdateEntry[];
  trackedSince: string; //readonly
  description: string;
}

export interface Site {
  siteId: string; //readonly
  siteName: string;
  siteUrl: string; //readonly
  lastUpdateAt: string; //readonly
}
