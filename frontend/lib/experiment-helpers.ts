// Helper functions for experiment management

import { apiClient } from './api-client';
import { BusinessModel, CompanySize, type Experiment } from './api-types';

export async function createExperimentFromDescription(
    description: string,
    numberOfPersonas: number = 5
): Promise<Experiment> {
    const experimentData = {
        company_input: {
            name: "User's Company",
            industry: "Technology",
            target_market: description,
            business_model: BusinessModel.B2B,
            company_size: CompanySize.STARTUP,
            description: description
        },
        feature_description: {
            name: "Feature Validation",
            description: description,
            value_proposition: "Test market fit for this concept",
            target_user: description,
            pricing_model: "TBD"
        }
    };

    const response = await apiClient.createExperiment(experimentData);
    return response.experiment;
}

export async function getCurrentExperiment(): Promise<Experiment | null> {
    const experimentId = localStorage.getItem("currentExperimentId");
    if (!experimentId) return null;

    try {
        const response = await apiClient.getExperiment(experimentId);
        return response.experiment;
    } catch (error) {
        console.error("Error fetching experiment:", error);
        return null;
    }
}

export async function runCurrentSimulation(): Promise<Experiment | null> {
    const experimentId = localStorage.getItem("currentExperimentId");
    if (!experimentId) return null;

    try {
        const response = await apiClient.runSimulation(experimentId);
        return response.experiment;
    } catch (error) {
        console.error("Error running simulation:", error);
        throw error;
    }
}

export function saveExperimentToLocalStorage(experiment: Experiment) {
    localStorage.setItem("currentExperimentId", experiment.id);
    localStorage.setItem("currentExperiment", JSON.stringify(experiment));
}

export function getExperimentFromLocalStorage(): Experiment | null {
    const data = localStorage.getItem("currentExperiment");
    if (!data) return null;

    try {
        return JSON.parse(data);
    } catch {
        return null;
    }
}
