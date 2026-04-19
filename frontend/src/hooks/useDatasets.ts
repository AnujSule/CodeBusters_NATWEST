/** TanStack Query hooks for dataset operations. */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../config/api';
import { useDatasetStore } from '../store/datasetStore';
import { toast } from 'sonner';
import type { DatasetResponse } from '../types/api';

export const useDatasets = () => {
    const { setDatasets } = useDatasetStore();

    return useQuery<DatasetResponse[]>({
        queryKey: ['datasets'],
        queryFn: async () => {
            const { data } = await api.get<DatasetResponse[]>('/datasets/');
            // Normalize: ensure each dataset has an 'id' field
            const normalized = data.map((d: any) => ({
                ...d,
                id: d.id || d.dataset_id,
            }));
            setDatasets(normalized);
            return normalized;
        },
        refetchInterval: 5000,
    });
};

export const useUploadDataset = () => {
    const queryClient = useQueryClient();
    const { addDataset, selectDataset } = useDatasetStore();

    return useMutation({
        mutationFn: async ({ file, name, description }: { file: File; name: string; description?: string }) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('name', name);
            if (description) formData.append('description', description);

            const { data } = await api.post<DatasetResponse>('/datasets/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000,  // 2 min timeout for upload + processing
            });
            // Normalize id
            return { ...data, id: data.id || (data as any).dataset_id } as DatasetResponse;
        },
        onSuccess: (data) => {
            addDataset(data);
            selectDataset(data);
            queryClient.invalidateQueries({ queryKey: ['datasets'] });
            toast.success('Dataset uploaded and processed successfully!');
        },
        onError: (error: any) => {
            toast.error(error.message || 'Failed to upload dataset');
        },
    });
};

export const useDeleteDataset = () => {
    const queryClient = useQueryClient();
    const { removeDataset } = useDatasetStore();

    return useMutation({
        mutationFn: async (datasetId: string) => {
            await api.delete(`/datasets/${datasetId}`);
            return datasetId;
        },
        onSuccess: (datasetId) => {
            removeDataset(datasetId);
            queryClient.invalidateQueries({ queryKey: ['datasets'] });
            toast.success('Dataset deleted');
        },
        onError: (error: any) => {
            toast.error(error.message || 'Failed to delete dataset');
        },
    });
};
