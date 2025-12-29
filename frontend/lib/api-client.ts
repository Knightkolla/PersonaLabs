import type {
    CreateExperimentRequest,
    ExperimentResponse,
    Experiment,
    FeatureDescription
} from './api-types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;

        const config: RequestInit = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // Experiment endpoints
    async createExperiment(data: CreateExperimentRequest): Promise<ExperimentResponse> {
        return this.request<ExperimentResponse>('/api/v1/experiments/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async listExperiments(skip: number = 0, limit: number = 20): Promise<Experiment[]> {
        return this.request<Experiment[]>(`/api/v1/experiments/?skip=${skip}&limit=${limit}`);
    }

    async getExperiment(experimentId: string): Promise<ExperimentResponse> {
        return this.request<ExperimentResponse>(`/api/v1/experiments/${experimentId}`);
    }

    async runSimulation(experimentId: string): Promise<ExperimentResponse> {
        return this.request<ExperimentResponse>(`/api/v1/experiments/${experimentId}/simulate`, {
            method: 'POST',
        });
    }

    async forkExperiment(experimentId: string, newFeature: FeatureDescription): Promise<ExperimentResponse> {
        return this.request<ExperimentResponse>(`/api/v1/experiments/${experimentId}/fork`, {
            method: 'POST',
            body: JSON.stringify(newFeature),
        });
    }

    async shareExperiment(experimentId: string): Promise<{ share_token: string; share_url: string; message: string }> {
        return this.request(`/api/v1/experiments/${experimentId}/share`, {
            method: 'POST',
        });
    }

    async getSharedExperiment(shareToken: string): Promise<ExperimentResponse> {
        return this.request<ExperimentResponse>(`/api/v1/experiments/shared/${shareToken}`);
    }

    async revokeShare(experimentId: string): Promise<{ message: string }> {
        return this.request(`/api/v1/experiments/${experimentId}/share`, {
            method: 'DELETE',
        });
    }

    async exportCSV(experimentId: string): Promise<Blob> {
        const url = `${this.baseURL}/api/v1/experiments/${experimentId}/export/csv`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.blob();
    }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
