import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, FileText, X } from 'lucide-react';

interface FileUploadZoneProps {
    onFileSelect: (file: File) => void;
    isUploading: boolean;
    selectedFile: File | null;
    onClear: () => void;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({
    onFileSelect,
    isUploading,
    selectedFile,
    onClear,
}) => {
    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            if (acceptedFiles.length > 0) {
                onFileSelect(acceptedFiles[0]);
            }
        },
        [onFileSelect]
    );

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/pdf': ['.pdf'],
        },
        maxFiles: 1,
        maxSize: 50 * 1024 * 1024,
        disabled: isUploading,
    });

    const formatSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes}B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    };

    if (selectedFile) {
        const isCSV = selectedFile.name.endsWith('.csv');
        return (
            <div className="border border-border rounded-xl p-6 bg-surface">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        {isCSV ? (
                            <FileSpreadsheet className="h-8 w-8 text-accent-green" />
                        ) : (
                            <FileText className="h-8 w-8 text-accent-blue" />
                        )}
                        <div>
                            <div className="text-sm font-medium text-text-primary">{selectedFile.name}</div>
                            <div className="text-xs text-text-secondary mt-0.5">
                                {formatSize(selectedFile.size)} · {isCSV ? 'CSV' : 'PDF'}
                            </div>
                        </div>
                    </div>
                    {!isUploading && (
                        <button
                            onClick={onClear}
                            className="p-1.5 rounded-lg hover:bg-elevated text-text-muted hover:text-text-primary transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${isDragActive
                    ? 'border-accent-amber bg-accent-amber/5'
                    : isDragReject
                        ? 'border-accent-red bg-accent-red/5'
                        : 'border-border hover:border-border-active hover:bg-elevated/50'
                }`}
        >
            <input {...getInputProps()} />
            <Upload className={`h-10 w-10 mx-auto mb-4 ${isDragActive ? 'text-accent-amber' : 'text-text-muted'}`} />
            <p className="text-text-primary font-medium mb-1">
                {isDragActive ? 'Drop your file here' : 'Drag & drop a file here'}
            </p>
            <p className="text-sm text-text-secondary">
                or click to browse · CSV or PDF · Max 50MB
            </p>
        </div>
    );
};
