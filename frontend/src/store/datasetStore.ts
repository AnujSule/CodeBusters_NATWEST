/** Zustand dataset store for managing dataset state and query history. */

import { create } from 'zustand';
import type { DatasetResponse, QueryResponse } from '../types/api';

interface DatasetState {
    datasets: DatasetResponse[];
    selectedDataset: DatasetResponse | null;
    queryHistory: QueryResponse[];
    setDatasets: (datasets: DatasetResponse[]) => void;
    addDataset: (dataset: DatasetResponse) => void;
    updateDataset: (id: string, updates: Partial<DatasetResponse>) => void;
    removeDataset: (id: string) => void;
    selectDataset: (dataset: DatasetResponse | null) => void;
    addQueryResult: (result: QueryResponse) => void;
    clearQueryHistory: () => void;
}

export const useDatasetStore = create<DatasetState>((set) => ({
    datasets: [],
    selectedDataset: null,
    queryHistory: [],

    setDatasets: (datasets: DatasetResponse[]) => set({ datasets }),

    addDataset: (dataset: DatasetResponse) =>
        set((state) => ({ datasets: [dataset, ...state.datasets] })),

    updateDataset: (id: string, updates: Partial<DatasetResponse>) =>
        set((state) => ({
            datasets: state.datasets.map((d) =>
                d.id === id ? { ...d, ...updates } : d
            ),
            selectedDataset:
                state.selectedDataset?.id === id
                    ? { ...state.selectedDataset, ...updates }
                    : state.selectedDataset,
        })),

    removeDataset: (id: string) =>
        set((state) => ({
            datasets: state.datasets.filter((d) => d.id !== id),
            selectedDataset:
                state.selectedDataset?.id === id ? null : state.selectedDataset,
        })),

    selectDataset: (dataset: DatasetResponse | null) =>
        set({ selectedDataset: dataset, queryHistory: [] }),

    addQueryResult: (result: QueryResponse) =>
        set((state) => ({
            queryHistory: [result, ...state.queryHistory].slice(0, 20),
        })),

    clearQueryHistory: () => set({ queryHistory: [] }),
}));
