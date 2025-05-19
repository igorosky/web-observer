import {Site} from './site';

// export interface LastUpdatesResponseDto {
//   lastUpdates: UpdateEntry[];
// }

export interface SitePageRequestDto {
  pageSize: number;
  isByLetter: boolean;
  index: number | string;
}

export interface SitePageResponseDto {
  pageNumber: number;
  totalPages: number;
  pageSize: number;
  entries: Record<string, Site[]>; //first letter -> sites; sum of Site[].length = pageSize
}
