export interface Site {
  siteId: string;
  siteName: string;
  siteUrl: string;
  lastUpdateAt: string;
}

export interface UpdateEntryPreview {
  siteId: string;
  siteUrl: string;
  siteName: string;
  registeredAt: string;
}

export interface BareUpdateEntry {
  registeredAt: string;
  change: string;
}

export interface SiteDetails {
  siteInfo: Site;
  updates: BareUpdateEntry[];
  trackedSince: string;
  description: string;
}
