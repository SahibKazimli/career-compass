import axios from "axios";
import type { User, ParsedResume, RecommendationsResponse } from "../types";

const API_BASE = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
});

export const createUser = async (email: string, name: string): Promise<User> => {
  const response = await api.post(`/users?email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}`);
  return response.data;
};

export const getUser = async (userId: number): Promise<User> => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

export const uploadResume = async (userId: number, file: File): Promise<ParsedResume> => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post(`/resume/upload?user_id=${userId}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const getRecommendations = async (
  userId: number,
  userInterests?: string,
  currentRole?: string
): Promise<RecommendationsResponse> => {
  const params = new URLSearchParams();
  if (userInterests) params.append("user_interests", userInterests);
  if (currentRole) params.append("current_role", currentRole);
  const response = await api.get(`/recommendations/${userId}?${params}`);
  return response.data;
};