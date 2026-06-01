export type UserRole = "User" | "Staff" | "Admin";
export type FlightStatus = "Scheduled" | "Boarding" | "In-Air" | "Landed";
export type SeatClass = "Economy" | "Business" | "First";

export type PilotRank = "Trainee" | "First Officer" | "Captain" | "Senior Captain";
export type PirepStatus = "Pending" | "Approved" | "Rejected";

export interface User {
  id: string;
  discord_id: string;
  username: string;
  won_balance: number;
  role: UserRole;
  total_flight_minutes?: number;
  total_flight_hours?: number;
  pilot_rank?: PilotRank;
  created_at: string;
  updated_at: string;
}

export interface EligibleFlight {
  flight_id: string;
  flight_number: string;
  departure: string;
  arrival: string;
  booking_id: string;
  seat_number: string;
}

export interface Pirep {
  id: string;
  user_id: string;
  flight_id: string;
  flight_time_minutes: number;
  landing_rate_fpm: number;
  fuel_used_lbs: number | null;
  notes: string | null;
  status: PirepStatus;
  won_bonus: number | null;
  estimated_bonus?: number | null;
  rejection_reason?: string | null;
  created_at: string;
  flight?: Flight;
  user?: User;
}

export interface LeaderboardHoursEntry {
  rank: number;
  username: string;
  discord_id: string;
  pilot_rank: string;
  total_hours: number;
  total_flight_minutes: number;
}

export interface LeaderboardWealthEntry {
  rank: number;
  username: string;
  discord_id: string;
  won_balance: number;
  pilot_rank: string;
}

export interface LeaderboardData {
  top_pilots_by_hours: LeaderboardHoursEntry[];
  top_pilots_by_wealth: LeaderboardWealthEntry[];
  cached_seconds: number;
}

export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  type: string;
  timestamp: string;
  reference_id: string | null;
}

export interface Flight {
  id: string;
  flight_number: string;
  departure: string;
  arrival: string;
  aircraft: string | null;
  status: FlightStatus;
  departure_time: string;
  created_at: string;
  updated_at: string;
}

export interface Booking {
  id: string;
  user_id: string;
  flight_id: string;
  seat_number: string;
  seat_class: SeatClass;
  price_won: number;
  booked_at: string;
  boarding_pass_path?: string | null;
  has_boarding_pass?: boolean;
  flight?: Flight;
}

export interface StaffShift {
  id: string;
  user_id: string;
  clock_in: string;
  clock_out: string | null;
  created_at: string;
  duration_seconds: number | null;
  user?: User;
}

export interface StaffDutySummary {
  user_id: string;
  discord_id: string;
  username: string;
  role: string;
  total_shifts: number;
  total_seconds: number;
  is_clocked_in: boolean;
}

export interface SeatMapSeat {
  seat_number: string;
  seat_class: SeatClass | null;
  available: boolean;
  booked_by: string | null;
}

export interface SeatMap {
  flight_id: string;
  rows: number;
  seats_per_row: number;
  seats: SeatMapSeat[];
}

export interface AnalyticsSummary {
  total_users: number;
  active_users_7d: number;
  total_bookings: number;
  total_revenue_won: number;
  won_in_circulation: number;
  flights_scheduled: number;
  flights_active: number;
}
