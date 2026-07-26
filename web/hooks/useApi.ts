/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiService } from "@/services/api";
import { PredictionRequest, PredictionResponse } from "@/types/api";

export function useHealthQuery() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiService.getHealth(),
    refetchInterval: 30000, // Refetch every 30s
    retry: 1,
  });
}

export function useModelsQuery() {
  return useQuery({
    queryKey: ["models"],
    queryFn: () => apiService.getModels(),
    staleTime: 60000, // Cache for 1 minute
  });
}

export function usePredictMutation(options?: {
  onSuccess?: (data: PredictionResponse) => void;
  onError?: (error: Error) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PredictionRequest) => apiService.predict(request),
    onSuccess: (data) => {
      queryClient.setQueryData(["lastPrediction", data.tipping_element], data);
      options?.onSuccess?.(data);
    },
    onError: (err: any) => {
      options?.onError?.(err instanceof Error ? err : new Error(String(err)));
    },
  });
}
