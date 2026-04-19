/** TanStack Query hook for audit log. */

import { useQuery } from '@tanstack/react-query';
import api from '../config/api';
import type { AuditLogEntry } from '../types/api';

interface AuditData {
    entries: AuditLogEntry[];
    total: number;
    page: number;
    page_size: number;
}

export const useAuditLog = (page: number = 1, pageSize: number = 50, datasetId?: string) => {
    return useQuery<AuditData>({
        queryKey: ['auditLog', page, pageSize, datasetId],
        queryFn: async () => {
            const { data } = await api.get('/audit/');
            // Backend returns a flat array — wrap it in the expected structure
            const entries: AuditLogEntry[] = Array.isArray(data) ? data : (data as any).entries || [];
            return {
                entries,
                total: entries.length,
                page: 1,
                page_size: entries.length,
            };
        },
    });
};
