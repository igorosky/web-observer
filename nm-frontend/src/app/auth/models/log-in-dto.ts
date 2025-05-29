export interface LogInDto {
  email: string;
  password: string;
}
export interface LogInResponse {
  username: string;
  lastLoginAt: string;
}
