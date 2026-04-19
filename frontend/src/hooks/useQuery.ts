/** TanStack Query hook for submitting questions. */

import { useMutation } from '@tanstack/react-query';
import api from '../config/api';
import { useDatasetStore } from '../store/datasetStore';
import { toast } from 'sonner';
import type { QueryResponse } from '../types/api';

export const useSubmitQuery = () => {
    const { addQueryResult } = useDatasetStore();

    return useMutation({
        mutationFn: async ({ datasetId, question }: { datasetId: string; question: string }) => {
            const { data } = await api.post<QueryResponse>(`/queries/${datasetId}`, { question });
            return data;
        },
        onSuccess: (data) => {
            addQueryResult(data);
        },
        onError: (error: any) => {
            toast.error(error.message || 'Failed to process query');
        },
    });
};
