export function getStatusClass(statusCode: number): string {
  if(statusCode < 400) return 'successU';
  else if(statusCode < 500) return 'clientEU';
  else return 'serverEU';
}
