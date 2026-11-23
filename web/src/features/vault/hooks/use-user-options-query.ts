"use client";

import { useQuery } from "@tanstack/react-query";
import { userDirectoryService } from "../services/user-directory-service";

export const USER_OPTIONS_QUERY_KEY = ["users", "options"] as const;

export function useUserOptionsQuery() {
  return useQuery({
    queryKey: USER_OPTIONS_QUERY_KEY,
    queryFn: () => userDirectoryService.listUserOptions(),
    staleTime: 5 * 60 * 1000,
  });
}
